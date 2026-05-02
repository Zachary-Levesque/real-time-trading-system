# Real-Time Trading System

A production-style real-time trading platform that ingests live market data, processes streaming signals, and serves low-latency, risk-aware trade recommendations.

## Phase 2 Scope

This repository now includes:

- `backend/`: FastAPI application shell with configuration, API router, health endpoint, and a first-pass market data ingestion module
- `frontend/`: React + Vite application shell with a welcome page and dashboard route
- `docker-compose.yml`: local multi-service orchestration for frontend and backend

Still intentionally out of scope:

- signal processing
- recommendation logic
- database integration
- real-time background updates

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
│   ├── data/
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

### Market ingestion

```bash
cd backend
python -m app.ingestion --ticker AAPL
```

Example output:

```json
{
  "ticker": "AAPL",
  "timestamp": "2026-05-02T12:00:00+00:00",
  "points": 35,
  "output_path": "data/market/AAPL/latest.json"
}
```

The ingestion command:

- fetches recent market data from `yfinance`
- normalizes it into a stable JSON contract
- stores the latest result at `backend/data/market/<TICKER>/latest.json`
- returns a non-zero exit code on fetch or persistence failures

### Manual check

1. Start the backend and frontend.
2. Open `http://localhost:5173/`.
3. Verify the welcome page renders.
4. Open the dashboard page.
5. Verify `http://localhost:8000/api/v1/health` returns a healthy response.

## Current Data Contract

Normalized market data is stored as:

```json
{
  "ticker": "AAPL",
  "timestamp": "ISO-8601",
  "data": {
    "source": "yfinance",
    "currency": "USD",
    "exchange_timezone": "America/New_York",
    "period": "5d",
    "interval": "1h",
    "points": [
      {
        "timestamp": "ISO-8601",
        "open": 210.25,
        "high": 212.0,
        "low": 209.75,
        "close": 211.55,
        "volume": 3200100
      }
    ]
  }
}
```

## Next Phase

Phase 3 should take this normalized market data and derive deterministic signals for momentum, trend, volatility, and volume.
