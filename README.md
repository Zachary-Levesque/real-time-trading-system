# Real-Time Trading System

A production-style real-time trading platform that ingests live market data, processes streaming signals, and serves low-latency, risk-aware trade recommendations.

## Phase 1 Scope

This repository now includes the initial runnable scaffold for:

- `backend/`: FastAPI application shell with configuration, API router, and health endpoint
- `frontend/`: React + Vite application shell with a welcome page and dashboard route
- `docker-compose.yml`: local multi-service orchestration for frontend and backend

No trading business logic, ingestion logic, or storage integration has been implemented yet. Those belong to later phases.

## Project Structure

```txt
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── ingestion/
│   │   ├── models/
│   │   ├── processing/
│   │   ├── recommendation/
│   │   ├── storage/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── Implementation.md
├── Instructions.md
└── README.md
```

## Run Locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URLs:

- API root: `http://localhost:8000/`
- OpenAPI docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- App: `http://localhost:5173/`

## Run With Docker

```bash
docker compose up --build
```

## Basic Validation

### Backend test

```bash
cd backend
pytest
```

### Manual check

1. Start the backend and frontend.
2. Open `http://localhost:5173/`.
3. Verify the welcome page renders.
4. Open the dashboard page.
5. Verify `http://localhost:8000/api/v1/health` returns a healthy response.

## Next Phase

Phase 2 should define the first market data contracts and implement a simple `yfinance`-based ingestion module for a small ticker set.
