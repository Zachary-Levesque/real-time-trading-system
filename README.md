# Real-Time Trading System

A production-style real-time trading platform that ingests live market data, processes streaming signals, and serves low-latency, risk-aware trade recommendations.

## Phase 9 Scope

This repository now includes:

- `backend/`: FastAPI application shell with configuration, API router, health endpoint, and a first-pass market data ingestion module
- `backend/processing`: deterministic signal calculation from normalized market data
- `backend/recommendation`: explainable recommendation scoring from processed signals
- `backend/api`: FastAPI endpoints for price, signals, and recommendation reads
- `backend/storage`: PostgreSQL persistence, Redis caching, and storage sync tooling
- `backend/runtime`: background update worker for scheduled pipeline refreshes
- `frontend/`: React + Vite application with a refined welcome page and an API-backed dashboard
- `docker-compose.yml`: local multi-service orchestration for frontend and backend

Still intentionally out of scope:

- WebSocket push updates
- advanced event streaming infrastructure

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

### Signal processing

```bash
cd backend
python -m app.processing --ticker AAPL
```

Example output:

```json
{
  "ticker": "AAPL",
  "timestamp": "2026-05-02T17:15:00+00:00",
  "signals": {
    "momentum": "positive",
    "trend": "bullish",
    "volatility": "stable",
    "volume": "above_average"
  },
  "output_path": "data/signals/AAPL/latest.json"
}
```

The processing command:

- reads normalized market data from `backend/data/market/<TICKER>/latest.json`
- computes momentum, trend, volatility, and volume labels
- stores the latest signal object at `backend/data/signals/<TICKER>/latest.json`
- returns a non-zero exit code if the market data is missing or insufficient

### Recommendation generation

```bash
cd backend
python -m app.recommendation --ticker AAPL
```

Example output:

```json
{
  "ticker": "AAPL",
  "timestamp": "2026-05-02T17:30:00+00:00",
  "recommendation": "BUY",
  "confidence": 0.6,
  "risk": "low",
  "signals": {
    "momentum": "positive",
    "trend": "bullish",
    "volatility": "stable",
    "volume": "average"
  },
  "reason": "Positive momentum with a bullish trend, stable volatility, and average volume supports a buy bias."
}
```

The recommendation command:

- reads processed signals from `backend/data/signals/<TICKER>/latest.json`
- scores them into `BUY`, `HOLD`, or `SELL`
- adds confidence, risk, and reasoning
- stores the latest output at `backend/data/recommendations/<TICKER>/latest.json`

### Storage sync

```bash
cd backend
python -m app.storage --ticker AAPL
```

The storage sync command:

- creates the PostgreSQL tables if they do not exist
- persists the latest market data, signals, and recommendation for a ticker
- caches the latest price snapshot and recommendation in Redis
- prepares the API to read from storage in `hybrid` mode

## Background Updates

Phase 9 adds a background worker that can automatically refresh a configured ticker set.

Default worker environment variables:

- `ENABLE_BACKGROUND_WORKER=true`
- `BACKGROUND_WORKER_INTERVAL_SECONDS=300`
- `BACKGROUND_WORKER_TICKERS=AAPL,MSFT,NVDA,SPY`
- `BACKGROUND_WORKER_RUN_IMMEDIATELY=true`

When enabled, the worker runs:

1. market ingestion
2. signal processing
3. recommendation generation
4. storage sync

This gives the system real-time-style behavior without requiring manual commands for every refresh.

## Storage Layer

Phase 8 introduces:

- PostgreSQL as the persistent system of record for market data, signals, and recommendations
- Redis as a cache for latest price snapshots and recommendations
- a `hybrid` storage mode where the API prefers storage but can fall back to local files

Default storage environment variables:

- local shell default: `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/trading_system`
- local shell default: `REDIS_URL=redis://localhost:6379/0`
- `STORAGE_MODE=hybrid`

When running through Docker Compose, the backend service uses:

- `DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/trading_system`
- `REDIS_URL=redis://redis:6379/0`

## API Endpoints

With the backend running, the current API now exposes:

- `GET /api/v1/health`
- `GET /api/v1/price/{ticker}`
- `GET /api/v1/signals/{ticker}`
- `GET /api/v1/recommendation/{ticker}`

Examples:

```bash
curl http://localhost:8000/api/v1/price/AAPL
curl http://localhost:8000/api/v1/signals/AAPL
curl http://localhost:8000/api/v1/recommendation/AAPL
```

The API behavior now prefers storage when available:

- `/price/{ticker}` checks Redis, then PostgreSQL, then local market files in `hybrid` mode
- `/signals/{ticker}` reads PostgreSQL first, then local signal files in `hybrid` mode
- `/recommendation/{ticker}` checks Redis, then PostgreSQL, then local recommendation files in `hybrid` mode
- missing tickers return `404`

## Frontend Welcome Page

Phase 6 refines the landing experience so the project explains itself before the user reaches the dashboard.

The welcome page now:

- frames the platform as a systems-first trading product
- explains the ingestion, signal, and recommendation layers
- makes the project value clearer for backend and product engineering
- provides direct calls to action for the dashboard and API docs

## Frontend Dashboard

Phase 7 turns the dashboard into a working product surface.

The dashboard now:

- fetches price, signal, and recommendation data from the backend API
- supports ticker search
- displays loading and error states
- renders a price chart using Recharts
- shows recommendation, confidence, risk, signal breakdown, and explanation

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

Processed signals are stored as:

```json
{
  "ticker": "AAPL",
  "timestamp": "ISO-8601",
  "data": {
    "source": "signal_processor_v1",
    "lookback_points": 20,
    "data_points_used": 35,
    "values": {
      "momentum": "positive",
      "trend": "bullish",
      "volatility": "stable",
      "volume": "above_average"
    }
  }
}
```

Recommendations are stored as:

```json
{
  "ticker": "AAPL",
  "timestamp": "ISO-8601",
  "recommendation": "BUY",
  "confidence": 0.6,
  "risk": "low",
  "signals": {
    "momentum": "positive",
    "trend": "bullish",
    "volatility": "stable",
    "volume": "average"
  },
  "reason": "Positive momentum with a bullish trend, stable volatility, and average volume supports a buy bias."
}
```

## Next Phase

Phase 10 should harden deployment and operational setup around the now-automated system.
