"""
Pipeline Worker
---------------
Orchestrates the end-to-end processing pipeline for a single analysis job.

Batch 1 Optimizations applied here:
  OPT-1  Detector singleton — models passed in from app.state; NOT re-loaded per job.
  OPT-2  SIFT single-pass   — align_and_pad_maps() now returns W so _compute_W_inv()
           is eliminated entirely (was running SIFT twice on the same images).
  OPT-3  Per-stage timing   — every pipeline stage records wall-clock ms so the
           /jobs/{id}/result response includes a perf breakdown dashboard.

Stage flow:
  1. ALIGNING   — PDF → image, SIFT feature match, universal canvas warp
  2. TILING     — Slice canvas into 640×640 tiles
  3. PROCESSING — YOLO detect + OCR for every tile pair
  4. MATCHING   — 4-pass object matcher
  5. REPORTING  — Annotated callouts → vector PDF overlay
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

import cv2
import numpy as np

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

from app.core.config import Settings, BASE_DIR
from app.models.schemas import JobStatus
from app.services.alignment import (
    pdf_to_image,
    align_and_pad_maps,
    iter_tiles,         # OPT-4: streaming generator
    save_tiles,         # kept for saving named tile images to disk
)
from app.services.matching import match_objects
from app.services.rules import RuleEngine
from app.services.reporting import generate_vector_report, generate_final_report
from app.services.fiber_overview import FiberOverviewProcessor

logger = logging.getLogger(__name__)


def run_pipeline_sync(
    job_id: str,
    job_store: dict,
    settings: Settings,
    detector=None,           # OPT-1: injected singleton; None → create locally (fallback)
) -> None:
    """
    Runs the full pipeline synchronously inside a thread-pool executor.
    Updates job_store in-place so the API polling endpoints stay responsive.

    Performance annotations (OPT-N) mark every optimization applied.
    Timing data is written to job_store[job_id]["stage_times"] and appears
    in the /jobs/{id}/result response as a breakdown dashboard.
    """
    job_start = time.perf_counter()

    def _update(status: JobStatus, pct: float, msg: str) -> None:
        job_store[job_id].update({"status": status, "progress": pct, "message": msg})
        logger.info(f"[{job_id}] [{pct:3.0f}%] {msg}")

    def _record(stage: str, t0: float) -> float:
        """Record elapsed ms for a stage and return current time."""
        elapsed = (time.perf_counter() - t0) * 1000
        job_store[job_id]["stage_times"][stage] = round(elapsed, 1)
        logger.info(f"[{job_id}] ⏱  {stage}: {elapsed:.0f} ms")
        return time.perf_counter()

    try:
        job = job_store[job_id]
        before_path = Path(job["before_path"])
        after_path  = Path(job["after_path"])
        output_dir  = Path(job["output_dir"])
        dpi = job.get("dpi", settings.PDF_DPI)
        output_dir.mkdir(parents=True, exist_ok=True)
        job_store[job_id]["stage_times"] = {}

        # OPT-1: Reuse the pre-loaded detector from app.state (passed in).
        # Fallback: create locally only if app started without model weights.
        if detector is None:
            logger.warning(f"[{job_id}] Detector singleton not available; loading models now (slow path).")
            from app.services.vision import TelecomDetector
            detector = TelecomDetector(
                main_model_path=settings.MAIN_MODEL_PATH,
                ps_model_path=settings.PS_MODEL_PATH,
                node_model_path=settings.NODE_MODEL_PATH,
                internal_model_path=settings.INTERNAL_MODEL_PATH,
                use_gpu=settings.USE_GPU,
                dpi=dpi,
            )

        rule_engine = RuleEngine()

        # ── Stage 1: Alignment ────────────────────────────────────
        t0 = time.perf_counter()
        _update(JobStatus.ALIGNING, 5.0, f"Rendering PDFs at {dpi} DPI and aligning maps...")
        img_before = pdf_to_image(before_path, dpi=dpi)
        img_after  = pdf_to_image(after_path,  dpi=dpi)

        # OPT-2: align_and_pad_maps now returns W (the full canvas warp matrix).
        # W_inv is derived directly — SIFT is NOT run a second time.
        final_before, final_after, W = align_and_pad_maps(img_before, img_after)
        W_inv = np.linalg.inv(W) if W is not None else np.eye(3, dtype=np.float32)

        cv2.imwrite(str(output_dir / "aligned_before.png"), final_before)
        cv2.imwrite(str(output_dir / "aligned_after.png"),  final_after)
        t0 = _record("alignment_ms", t0)

        # ── Stage 2: Tiling ───────────────────────────────────────
        _update(JobStatus.TILING, 15.0, "Slicing canvas into tiles (streaming, low RAM)...")

        # OPT-4: Save tile images for before-map up front (needed as a lookup map).
        # We still load all before-tiles because we need random access by index.
        # After-tiles are processed one at a time via iter_tiles to save RAM.
        before_tile_dir = output_dir / "tiles" / "before"
        after_tile_dir  = output_dir / "tiles" / "after"
        before_tile_dir.mkdir(parents=True, exist_ok=True)
        after_tile_dir.mkdir(parents=True, exist_ok=True)

        # Build before-tile lookup (index → numpy array) — one pass over final_before
        before_tiles_map: dict[int, np.ndarray] = {}
        tile_offsets: dict[int, tuple[int, int]] = {}
        for t in iter_tiles(final_before, settings.TILE_SIZE, settings.TILE_OVERLAP):
            before_tiles_map[t["index"]] = t["tile"].copy()  # .copy() detaches view
            tile_offsets[t["index"]] = (t["x"], t["y"])
            cv2.imwrite(str(before_tile_dir / f"before_{t['index']}.png"), t["tile"])

        t0 = _record("tiling_ms", t0)

        # ── Stage 3: Detection + OCR (streaming after-tiles) ─────────────────
        _update(JobStatus.PROCESSING, 25.0, "Running YOLO + OCR on tiles...")
        all_callout_records: list[dict] = []
        all_callouts_flat: list[dict] = []

        # Count total tiles first (cheap — just geometry math)
        h_c, w_c = final_after.shape[:2]
        step = int(settings.TILE_SIZE * (1 - settings.TILE_OVERLAP))
        total = sum(1 for _ in range(0, h_c, step) for _ in range(0, w_c, step))

        # OPT-4: Stream after-tiles one at a time — no list accumulation
        for idx, t_a in enumerate(iter_tiles(final_after, settings.TILE_SIZE, settings.TILE_OVERLAP)):
            tile_idx = t_a["index"]
            img_a    = t_a["tile"]
            img_b    = before_tiles_map.get(tile_idx)
            if img_b is None:
                continue

            # Save after-tile image for audit trail
            cv2.imwrite(str(after_tile_dir / f"after_{tile_idx}.png"), img_a)

            # OPT-1: detector is the warm singleton
            objs_b = detector.detect_objects(img_b, conf_threshold=0.01)
            objs_a = detector.detect_objects(img_a, conf_threshold=0.01)
            objs_b = detector.run_ocr_on_objects(img_b, objs_b)
            objs_a = detector.run_ocr_on_objects(img_a, objs_a)

            matches, removed, added = match_objects(objs_b, objs_a)
            callouts = rule_engine.generate_callouts(
                matches, removed, added,
                before_node_type=job.get("before_node_type"),
                before_node_names=job.get("before_node_names"),
                after_node_type=job.get("after_node_type"),
                after_node_names=job.get("after_node_names"),
            )

            for c in callouts:
                all_callout_records.append({
                    "tile_idx": tile_idx,
                    "lx": c["loc"][0],
                    "ly": c["loc"][1],
                    "text": c["text"],
                })
                all_callouts_flat.append(c)

            pct = 25.0 + (idx / max(total, 1)) * 55.0
            _update(JobStatus.PROCESSING, pct, f"Tile {idx + 1}/{total} processed.")

        t0 = _record("inference_ms", t0)

        # ── Stage 4: Matching summary ─────────────────────────────
        _update(JobStatus.MATCHING, 82.0, "Aggregating match results...")
        t0 = _record("matching_ms", t0)

        # ── Stage 5: Report ───────────────────────────────────────
        _update(JobStatus.REPORTING, 85.0, "Generating annotated vector PDF report...")
        report_path = output_dir / "report.pdf"

        job_data = job_store[job_id]
        generate_vector_report(
            after_pdf_path=after_path,
            callout_records=all_callout_records,
            tile_offsets=tile_offsets,
            W_inv=W_inv,
            output_path=report_path,
            dpi=dpi,
            survey_image_path=job_data.get("survey_image"),
            title_box_data=job_data.get("title_box"),
        )
        t0 = _record("reporting_ms", t0)

        # ── Finalise ─────────────────────────────────────────────
        total_ms = (time.perf_counter() - job_start) * 1000
        stage_times = job_store[job_id]["stage_times"]
        stage_times["total_ms"] = round(total_ms, 1)

        # Human-readable performance summary logged for comparison
        logger.info(
            f"[{job_id}] 📊 PERF SUMMARY | total={total_ms:.0f}ms "
            f"| align={stage_times.get('alignment_ms', 0):.0f}ms "
            f"| tiling={stage_times.get('tiling_ms', 0):.0f}ms "
            f"| inference={stage_times.get('inference_ms', 0):.0f}ms "
            f"| report={stage_times.get('reporting_ms', 0):.0f}ms"
        )

        job_store[job_id].update({
            "status": JobStatus.COMPLETED,
            "progress": 100.0,
            "message": "Pipeline completed successfully.",
            "callouts": all_callouts_flat,
            "report_path": str(report_path.relative_to(settings.BASE_DIR)),
            "stats": {
                "total_tiles": total,
                "total_callouts": len(all_callout_records),
                # OPT-3: Per-stage timing visible in /result response
                "performance_ms": stage_times,
            },
        })
        logger.info(f"[{job_id}] ✅ Pipeline complete in {total_ms:.0f} ms.")

    except Exception as exc:
        logger.exception(f"[{job_id}] ❌ Pipeline failed: {exc}")
        job_store[job_id].update({
            "status": JobStatus.FAILED,
            "message": "Pipeline encountered an error.",
            "error": str(exc),
        })


def run_fiber_overview_pipeline(
    job_id: str,
    job_store: dict,
    settings: Settings,
    processor: FiberOverviewProcessor = None,
) -> None:
    """
    Runs the fiber overview pipeline synchronously.
    Logic: PDF -> Image -> Node Detect -> Cable Trace -> Port Detect -> Report.
    """
    job_start = time.perf_counter()

    def _update(status: JobStatus, pct: float, msg: str) -> None:
        job_store[job_id].update({"status": status, "progress": pct, "message": msg})
        logger.info(f"[{job_id}] [{pct:3.0f}%] {msg}")

    def _record(stage: str, t0: float) -> float:
        elapsed = (time.perf_counter() - t0) * 1000
        job_store[job_id]["stage_times"][stage] = round(elapsed, 1)
        logger.info(f"[{job_id}] ⏱  {stage}: {elapsed:.0f} ms")
        return time.perf_counter()

    try:
        job = job_store[job_id]
        pdf_path = Path(job["pdf_path"])
        output_dir = Path(job["output_dir"])
        dpi = job.get("dpi", settings.PDF_DPI)
        
        # Business Logic Parameters
        is_connected = job.get("is_connected", True)
        hub_name = job.get("hub_name", "")
        port_name = job.get("port_name", "")
        splice_can_name = job.get("splice_can_name", "")
        node_name_input = job.get("title_box", {}).get("node_name", "") or "NODE"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        job_store[job_id]["stage_times"] = {}

        if processor is None:
            logger.warning(f"[{job_id}] Fiber processor not available; loading now.")
            processor = FiberOverviewProcessor(model_path=settings.FIBER_NODE_MODEL_PATH)

        t0 = time.perf_counter()

        # 1. CONVERT PDF -> IMAGE
        _update(JobStatus.PROCESSING, 10, "Converting PDF to image...")
        img = pdf_to_image(pdf_path, dpi=dpi)
        t0 = _record("CONVERSION", t0)

        # 2. NODE DETECTION
        _update(JobStatus.PROCESSING, 30, "Detecting fiber node...")
        bbox, center, conf = processor.detect_node(img)
        if bbox is None:
            raise ValueError("No fiber node detected in the overview map.")
        t0 = _record("DETECTION", t0)

        # 3. CABLE TRACING
        _update(JobStatus.PROCESSING, 50, "Tracing fiber cable...")
        skeleton = processor.extract_cable_skeleton(img, bbox)
        if skeleton is None:
            raise ValueError("Could not extract fiber cable connected to node.")
        
        port_pos = processor.find_port_position(skeleton, bbox)
        if port_pos is None:
            raise ValueError("Could not determine port position on cable.")
        t0 = _record("TRACING", t0)

        # 4. REPORT GENERATION
        _update(JobStatus.PROCESSING, 80, "Generating final report...")
        scale = dpi / 72.0
        pdf_node_pos = (center[0] / scale, center[1] / scale)
        pdf_port_pos = (port_pos[0] / scale, port_pos[1] / scale)

        # Construct Port Callout Text based on Business Logic
        if is_connected:
            port_text = f"HUB : {hub_name}\nPORT/PANEL : {port_name}"
        else:
            port_text = (
                f"TRACE STOPS AT RAW CAN ({splice_can_name}) ; "
                "EXISTING SPLICING UNAVAILABLE , A CAN AUDIT REQUIRED FOR VERIFICATION"
            )

        callouts = [
            {"x": pdf_node_pos[0], "y": pdf_node_pos[1], "text": "NODE"},
            {"x": pdf_port_pos[0], "y": pdf_port_pos[1], "text": port_text},
        ]
        
        report_filename = f"report_{job_id}.pdf"
        report_path = output_dir / report_filename
        
        survey_image_path = job.get("survey_image_path")
        title_box = job.get("title_box")
        
        generate_final_report(
            pdf_path=pdf_path,
            callouts=callouts,
            output_path=report_path,
            dpi=dpi,
            survey_image_path=survey_image_path,
            title_box_data=title_box
        )
        t0 = _record("REPORTING", t0)

        # COMPLETE
        total_ms = (time.perf_counter() - job_start) * 1000
        job_store[job_id].update({
            "status": JobStatus.COMPLETED,
            "progress": 100,
            "message": f"Success! Fiber overview processed in {total_ms/1000:.1f}s.",
            "report_path": str(report_path.relative_to(settings.BASE_DIR)),
            "callouts": callouts
        })

    except Exception as e:
        logger.exception(f"[{job_id}] Pipeline failed: {e}")
        job_store[job_id].update({
            "status": JobStatus.FAILED,
            "message": f"Error: {str(e)}",
            "error": str(e)
        })
