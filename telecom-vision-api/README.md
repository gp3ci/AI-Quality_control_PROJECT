# Telecom Vision API

A **production-ready FastAPI backend** for automated telecom network map analysis.

Upload paired BEFORE/AFTER PDF maps → get a fully annotated vector PDF report with callouts for every change detected.

---

## Architecture

```
app/
├── api/v1/
│   ├── jobs.py        # POST /jobs, GET /jobs/{id}, GET /jobs/{id}/result
│   └── health.py      # GET /health (Kubernetes readiness probe)
├── core/
│   ├── config.py      # Pydantic-Settings — all config from .env
│   └── logging.py     # Structured logging setup
├── models/
│   └── schemas.py     # Pydantic v2 request/response contracts
├── services/
│   ├── alignment.py   # PDF → image, SIFT alignment, tiling
│   ├── vision.py      # TelecomDetector (4 YOLO models + EasyOCR)
│   ├── matching.py    # 4-pass object matcher
│   ├── rules.py       # Rule engine → callouts
│   ├── reporting.py   # Vector PDF overlay generation
│   └── utils.py       # Pure geometry + OCR text helpers
├── workers/
│   └── pipeline.py    # End-to-end orchestration with progress updates
└── main.py            # FastAPI app factory + lifespan
```

---

## Quick Start

### 1. Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env as needed
```

### 3. Place model weights
Copy your `.pt` files into `model_weights/`:
```
model_weights/
├── best.pt
├── power_supply_best.pt
├── 3x3_4x4_new_model.pt
└── Internal_best.pt
```

### 4. Run the server
```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/jobs` | Submit a new job (multipart: `before_pdf`, `after_pdf`) |
| `GET` | `/api/v1/jobs/{job_id}` | Poll job status + progress % |
| `GET` | `/api/v1/jobs/{job_id}/result` | Get callouts + report URL |
| `GET` | `/api/v1/jobs/{job_id}/download` | Download annotated PDF |
| `GET` | `/api/v1/health` | Service health + model-loaded flag |

---

## Docker

```bash
docker build -t telecom-vision-api:latest .

docker run -p 8000:8000 \
  -v $(pwd)/model_weights:/app/model_weights \
  -v $(pwd)/storage:/app/storage \
  --env-file .env \
  telecom-vision-api:latest
```

---

## Scaling to 1 000 Concurrent Users

See the [System Design document](../system_design_scaling.md) for the full architecture.

**TL;DR:**
1. Replace `asyncio.get_event_loop().run_in_executor(...)` in `jobs.py` with a **Celery** task.
2. Deploy `Vision Workers` on **GPU Kubernetes nodes** (GCP `g2-standard-4` / AWS `g5.xlarge`).
3. Scale `Vision Workers` via **KEDA** based on Redis queue depth.
4. Deploy `Alignment Workers` on **high-memory nodes** (128 GB+ RAM) for 800 DPI warping.
