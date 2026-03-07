# 🔧 Telecom Coax Rule Engine

An end-to-end AI-powered pipeline for automated analysis of **before/after telecom coax network maps**. The system detects telecom components (nodes, splitters, taps, amplifiers, etc.) using YOLOv8, extracts values via OCR, and applies telecom business rules to generate actionable callouts for field engineers.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Detected Symbol Classes](#detected-symbol-classes)
- [Business Rules](#business-rules)
- [Installation](#installation)
- [Usage](#usage)
- [Pipeline Stages](#pipeline-stages)
- [Output Files](#output-files)
- [Configuration](#configuration)
- [Technologies Used](#technologies-used)

---

## Overview

Telecom operators frequently modify their coaxial cable network maps when upgrading infrastructure. This tool automates the comparison between **before** and **after** versions of these maps by:

1. **Converting** map PDFs to high-resolution images
2. **Aligning** the before/after maps using SIFT feature matching and homography
3. **Tiling** the large maps into 640×640px tiles for efficient processing
4. **Detecting** telecom components using a custom-trained YOLOv8 model
5. **Extracting** text values (tap values, voltages, tag IDs) using EasyOCR
6. **Matching** components across before/after maps using IOU and distance metrics
7. **Applying** telecom business rules to generate standardized callouts

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT (PDF Maps)                         │
│                   Before Map  ←──→  After Map                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  STAGE 1: PDF Extraction & Alignment  (align_maps.py)         │
│  • PDF → Image (PyMuPDF @ 600 DPI)                            │
│  • SIFT Feature Detection → Homography → Universal Canvas     │
│  • Tile Generation (640×640 with 20% overlap)                  │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  STAGE 2: Detection & OCR  (telecom_vision.py)                │
│  • YOLOv8 Object Detection (OBB support)                      │
│  • Multi-pass OCR (Gray, Otsu, Adaptive, Morphological)       │
│  • Voting-based text extraction with class-specific cleaning   │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  STAGE 3: Matching  (main.py)                                 │
│  • IOU-based pairing (strongest match)                        │
│  • Distance-based fallback for same-class objects             │
│  • Classification: Matched / Added / Removed                  │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  STAGE 4: Business Logic  (telecom_rules.py)                  │
│  • 19 telecom-specific rules (see rules section below)        │
│  • Generates standardized callouts (A, B, E, G, H, J, etc.)  │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                        OUTPUT                                  │
│  • final_report.txt (callout report)                          │
│  • results/ (annotated map tiles with callout overlays)       │
│  • detection_images/ (before/after tiles with bounding boxes) │
│  • all_ocr_results.json (full OCR data)                       │
│  • ocr.txt (human-readable OCR report)                        │
└───────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Rule_Engine_coax_merin_final/
│
├── run_pipeline.py          # 🚀 Main entry point — end-to-end pipeline
├── main.py                  # Standalone detection + matching + rules (pre-tiled)
├── align_maps.py            # PDF→Image, SIFT alignment, tiling
├── telecom_vision.py        # TelecomDetector class (YOLO + OCR)
├── telecom_rules.py         # RuleEngine class (19 business rules)
├── telecom_utils.py         # Geometry, text parsing, OCR cleaning helpers
├── process_tiles.py         # Legacy/alternative tile processing script
├── generate_ocr_txt.py      # Generates ocr.txt from all_ocr_results.json
├── test_rules.py            # Unit tests for the rule engine
├── test_yolo_load.py        # YOLO model loading test
│
├── requirements.txt         # Python dependencies
├── model_names.txt          # YOLO model class name reference
├── rule_engine_explanations.txt  # Detailed rule documentation
│
├── models/                  # YOLOv8 trained model weights (.pt)
│   ├── best.pt              # Primary model (22 classes)
│   ├── 3x3_4x4_new_model.pt # Model with enhanced 3x3/4x4 node detection
│   └── power_supply_best.pt # Specialized power supply detection model
│
├── input_maps/              # Input PDF maps (before/after pairs)
│   ├── before1.pdf ... before5.pdf
│   └── after1.pdf  ... after5.pdf
│
├── tiles/                   # Generated tiles (auto-created)
│   ├── before/              # Tiles from the before map
│   └── after/               # Tiles from the after map
│
├── detection_images/        # Visual debug output (bounding box overlays)
├── results/                 # Annotated tiles with callout overlays
│
├── all_ocr_results.json     # Consolidated OCR results (JSON)
├── ocr.txt                  # Human-readable OCR report
└── final_report.txt         # Final callout report
```

---

## Detected Symbol Classes

The YOLOv8 model detects **22 telecom component classes**:

| Class | Description |
|-------|-------------|
| `1x4 Node` | 1×4 Fiber Node |
| `2x2 Node` | 2×2 Fiber Node |
| `3x3 Node` | 3×3 Fiber Node |
| `4x4 Node` | 4×4 Fiber Node |
| `2way_splitter` | 2-Way Splitter |
| `3Way_splitter` | 3-Way Splitter |
| `3_way_amplifier` | 3-Way Amplifier |
| `Block` | Block Component |
| `Booster` | Signal Booster |
| `Dual_Amplifier` | Dual Amplifier |
| `Equalizer` | Signal Equalizer |
| `Int_2way_splitter` | Internal 2-Way Splitter |
| `Line_Extender` | Line Extender |
| `Power_Block` | Power Block |
| `Splice` | Splice Point |
| `Splitter` | Generic Splitter |
| `Splitter_DC` | DC Splitter |
| `Splitter_int_DC` | Internal DC Splitter |
| `Tag_id` | Tag Identifier (yellow box) |
| `Taps` | Tap (with dB value) |
| `Terminator` | Line Terminator |
| `power_supply` | Power Supply Unit |

---

## Business Rules

The rule engine applies **19 distinct rules** organized by change type:

### Global Rules
| Code | Rule | Trigger |
|------|------|---------|
| **A** | Amplifier Present | Any Dual/3-Way amplifier found in After map |

### Matched Object Rules (Before → After)
| Code | Rule | Trigger |
|------|------|---------|
| **B** | LE → Amplifier Upgrade | Line Extender replaced by Amplifier |
| **ADD CE-XX** | Add Equalizer | Tap text contains "EQZ" or "CE" |
| **E, ADD TERM** | Tap Change + Terminator Added | Tap value changed + new Terminator nearby |
| **E, REMOVE TERM** | Tap Change + Terminator Removed | Tap value changed + Terminator removed nearby |
| **E** | Tap Value Change | Tap value changed (no Terminator change) |
| **G** | Splitter Change | Splitter type or value changed |
| — | Node Downgrade (4x4→2x2) | 4x4 Node replaced by 2x2 Node |
| — | Node Downgrade (3x3→2x2) | 3x3 Node replaced by 2x2 Node |
| — | Node Upgrade | Node type upgraded |
| — | Power Supply Upgrade | Power supply voltage changed |
| — | Power Supply Overload | Current draw > 12.0A (>80% capacity) |

### Removed Object Rules
| Code | Rule | Trigger |
|------|------|---------|
| — | Remove Splitter | Splitter removed from map |
| — | Remove Power Block | Power Block removed from map |
| **J** | Equalizer Removed | Equalizer removed (optionally with splice block) |

### Added Object Rules
| Code | Rule | Trigger |
|------|------|---------|
| **H** | New Booster | Booster added to After map |
| **H** | New Line Extender | Line Extender added to After map |
| — | New Int/DC Splitter | Internal DC Splitter added |
| — | New Power Block | Power Block added |
| — | 2-Way inside Amp | 2-Way Splitter added near Amplifier |

---

## Installation

### Prerequisites

- **Python 3.8+**
- **CUDA-compatible GPU** (recommended for faster inference)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd Rule_Engine_coax_merin_final

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `ultralytics` | YOLOv8 object detection framework |
| `opencv-python` | Image processing, feature matching, alignment |
| `numpy` | Numerical operations |
| `paddlepaddle` | PaddlePaddle deep learning framework (OCR backend) |
| `paddleocr` | PaddleOCR text recognition |
| `easyocr` | EasyOCR text recognition (primary OCR engine) |
| `PyMuPDF` | PDF to image conversion (`fitz`) |

---

## Usage

### End-to-End Pipeline (Recommended)

Process a pair of before/after PDF maps through the full pipeline:

```bash
python run_pipeline.py --before input_maps/before1.pdf --after input_maps/after1.pdf
```

This will:
1. Convert PDFs to images at 600 DPI
2. Align the maps using feature matching
3. Generate 640×640 tiles with 20% overlap
4. Run YOLO detection + OCR on each tile pair
5. Apply business rules and generate callouts
6. Save all outputs to their respective directories

### Standalone Detection (Pre-tiled Maps)

If you already have tiled images in `tiles/before/` and `tiles/after/`:

```bash
python main.py
```

### Generate OCR Report from JSON

Convert the JSON OCR results to a human-readable text file:

```bash
python generate_ocr_txt.py
```

---

## Pipeline Stages

### Stage 1: PDF Extraction & Alignment (`align_maps.py`)
- Reads PDF maps using **PyMuPDF** at configurable DPI (default: 600)
- Downsamples images to ~1500px width for efficient **SIFT** feature detection
- Computes **homography** transformation using matched features (RANSAC)
- Rescales the transformation matrix back to native resolution
- Warps both maps onto a **universal canvas** so tiles correspond spatially
- Generates **overlapping tiles** (640×640, 20% overlap) for border-region coverage

### Stage 2: Detection & OCR (`telecom_vision.py`)
- **Multi-model inference**: Primary model for all 22 classes, plus specialized models for power supply detection
- **Oriented Bounding Box (OBB)** support for rotated symbols
- **Multi-pass OCR pipeline**:
  - Grayscale conversion
  - Otsu thresholding
  - Adaptive thresholding
  - Morphological operations (opening/closing)
  - **Voting** across all passes for consensus
- **Class-specific text cleaning** (tap values, voltages, tag IDs, splitter values)

### Stage 3: Object Matching (`main.py`)
- **IOU matching** (primary): Pairs objects with highest spatial overlap
- **Distance matching** (fallback): Pairs same-class objects by proximity (< 150px)
- Classifies all objects as **Matched**, **Added**, or **Removed**

### Stage 4: Business Logic (`telecom_rules.py`)
- Evaluates 19 rules across all change categories
- Generates standardized **callout codes** (A, B, E, G, H, J, etc.)
- Includes proximity-based checks (e.g., Terminator within 80px of changed Tap)
- Power supply capacity validation (> 80% current draw warnings)

---

## Output Files

| File/Directory | Description |
|---|---|
| `final_report.txt` | Text report with all callouts, locations, and descriptions |
| `results/` | Annotated tile images with callout text overlaid |
| `detection_images/` | Before/after tiles with bounding boxes drawn around detections |
| `all_ocr_results.json` | Complete OCR data in JSON format (per-tile, per-object) |
| `ocr.txt` | Human-readable OCR detection report |
| `ref_before_aligned.png` | Debug: aligned before map (full resolution) |
| `ref_after_aligned.png` | Debug: aligned after map (full resolution) |

---

## Configuration

Key parameters can be adjusted in the respective scripts:

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| DPI | `align_maps.py` | 600 | PDF rendering resolution |
| Tile Size | `align_maps.py` | 640 | Tile dimensions in pixels |
| Overlap | `align_maps.py` | 0.2 | Tile overlap ratio (20%) |
| Confidence | `main.py` / `run_pipeline.py` | 0.25 | YOLO detection confidence threshold |
| IOU Threshold | `main.py` | 0.5 | Minimum IOU for object matching |
| Distance Threshold | `main.py` | 150px | Max distance for fallback matching |
| Proximity (Terminator) | `telecom_rules.py` | 80px | Terminator proximity to tap for rules |
| Proximity (Splice) | `telecom_rules.py` | 100px | Splice proximity for equalizer rules |

---

## Technologies Used

- **[YOLOv8 (Ultralytics)](https://docs.ultralytics.com/)** — Real-time object detection with OBB support
- **[EasyOCR](https://github.com/JaidedAI/EasyOCR)** — Deep learning-based text recognition
- **[OpenCV](https://opencv.org/)** — Image processing, SIFT feature detection, homography
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** — High-fidelity PDF to image conversion
- **[NumPy](https://numpy.org/)** — Numerical array operations
- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** — Alternative OCR engine

---

## License

This project is developed as part of an internship and is intended for internal use.

---

## Authors

Internship Group 3 — Coax Map Analysis Team
