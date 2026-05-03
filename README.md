# Real-Time Trading System

Real-Time Trading System is a full-stack trading analysis platform built to ingest market data, turn it into deterministic signals, and serve an explainable buy, hold, or sell recommendation through a usable web product.

Simple meaning:

- the system fetches recent stock data
- it computes momentum, trend, volatility, and volume signals
- it converts those signals into a recommendation with confidence, risk, and reasoning
- it shows the result in a browser dashboard

This project is not about predicting the market with machine learning. It is about building a complete engineering system around market analysis.

## Goal

The goal of this project is to build something that is both technically valuable and professionally meaningful.

The project focuses on:

- backend service design
- market data ingestion
- signal processing
- explainable recommendation logic
- API design
- frontend product development
- storage and caching architecture
- testing and validation

## Why It Matters

Most stock projects stop at a notebook, a chart, or a toy prediction script.

This project matters because it shows how to build a real software system around financial data:

- how raw market data is fetched and normalized
- how signals are computed in a stable, testable way
- how recommendations are served through an API
- how a frontend turns system output into a usable product
- how local files, PostgreSQL, and Redis fit into one architecture

So this project connects:

- backend engineering
- data engineering
- systems design
- product engineering
- production-style development discipline

## What Was Built

- a FastAPI backend with versioned API routes
- a market ingestion service using `yfinance`
- a signal-processing layer for momentum, trend, volatility, and volume
- an explainable recommendation engine for `BUY`, `HOLD`, and `SELL`
- file-backed local persistence for fast local use
- optional PostgreSQL and Redis integration for hybrid storage
- a React dashboard with live refresh, charting, ticker search, and a company dropdown
- a full S&P 500 constituent snapshot for browsing companies in the UI
- a one-command local launcher for normal users
- automated backend tests and frontend build validation

## Main Folders

- `backend`: API, ingestion, processing, recommendation, storage, runtime worker
- `frontend`: React dashboard and UI
- `backend/data`: saved market, signal, and recommendation outputs
- `backend/tests`: backend test suite
- `docker-compose.yml`: multi-service local stack
- `run-local.sh`: one-command launcher for local use

## Try It

From the repo root:

```bash
./run-local.sh
```

Then open:

```txt
http://localhost:5173
```

Useful routes:

- `http://localhost:8000/api/v1/health`
- `http://localhost:8000/docs`
- `http://localhost:8000/api/v1/tickers`

## What To Do In The UI

- search a ticker like `NVDA`, `AAPL`, or `XOM`
- open the company dropdown and browse the S&P 500 list
- click `Analyze` to run the full pipeline on demand
- inspect the signal breakdown and use `Explain` to understand each signal
- review the recommendation, confidence, risk, and recommendation history

## Results

- the backend can ingest, process, and recommend on demand
- the dashboard can browse and analyze S&P 500 companies
- the recommendation flow is explainable rather than opaque
- the system works in a simple local file mode and can also support a richer storage setup
- tests and build validation pass

## Validation

Backend:

```bash
cd backend
./.venv/bin/pytest
```

Frontend:

```bash
cd frontend
npm run build
```
