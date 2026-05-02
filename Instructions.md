# INSTRUCTIONS — Real-Time Trading System (AI Build Guide)

## 0. Fixed Tech Stack (DO NOT CHANGE)

Backend:
- Python
- FastAPI

Frontend:
- React (Vite)

Database:
- PostgreSQL (primary)
- Redis (cache)

Data Ingestion:
- yfinance (initial version)

Charts:
- Recharts

Styling:
- Tailwind CSS

Containerization:
- Docker + docker-compose

DO NOT substitute or change these technologies.

---

## 1. Project Objective

Build a production-style real-time trading platform that:

- Ingests live S&P 500 market data
- Processes it into trading signals
- Generates Buy / Sell / Hold recommendations
- Serves results through a backend API
- Displays insights through a clean frontend UI

This project focuses on systems engineering, not ML complexity.

---

## 2. Final Outcome

The finished system must allow a user to:

- Open a Welcome Page
- Navigate to a Dashboard
- Search a stock, such as AAPL
- View price and chart
- Receive a trade recommendation
- See confidence, risk, and reasoning
- View signal breakdown

---

## 3. AI BUILD PROTOCOL

You MUST follow these rules:

1. Build ONE phase at a time.
2. DO NOT implement future phases early.
3. Each phase must produce runnable code.
4. Each phase must include folder structure.
5. Each phase must include dependencies.
6. Each phase must include instructions to run locally.
7. Keep code production-quality but simple.
8. Use modular design.
9. Do not create monolithic files.
10. Ask for confirmation before moving to the next phase.

---

## 4. System Architecture

The system is composed of:

1. Data Ingestion Service
2. Processing Layer
3. Storage Layer
4. Recommendation Engine
5. Backend API
6. Frontend UI
7. Deployment Layer

---

## 5. API CONTRACT

All API responses MUST follow this general structure:

    {
      "ticker": "string",
      "timestamp": "ISO-8601",
      "data": {}
    }

### Recommendation Response Format

    {
      "ticker": "AAPL",
      "recommendation": "BUY",
      "confidence": 0.76,
      "risk": "medium",
      "signals": {
        "momentum": "positive",
        "trend": "bullish",
        "volatility": "stable",
        "volume": "above_average"
      },
      "reason": "Positive momentum with stable volatility and increasing volume."
    }

Allowed values:

recommendation:
- BUY
- SELL
- HOLD

risk:
- low
- medium
- high

momentum:
- positive
- neutral
- negative

trend:
- bullish
- bearish
- neutral

volatility:
- low
- medium
- high
- stable

volume:
- low
- average
- high
- above_average

---

## 6. Implementation Phases

---

### Phase 1 — Project Setup

Goal:

Create a clean, production-ready project structure.

Tasks:

- Create backend with FastAPI
- Create frontend with React Vite
- Set up basic Docker structure
- Organize folders cleanly
- Add clear local run instructions

Definition of Done:

- Project runs locally
- Backend starts successfully
- Frontend starts successfully
- Clean folder structure exists
- No business logic yet

---

### Phase 2 — Data Ingestion

Goal:

Fetch real market data.

Tasks:

- Use yfinance
- Fetch data for AAPL initially
- Normalize data
- Store locally as JSON or CSV
- Handle API errors gracefully

Definition of Done:

- Script fetches real data
- Script handles API failure
- Code is modular
- Can be run with one command

---

### Phase 3 — Signal Processing

Goal:

Convert raw market data into useful trading signals.

Tasks:

- Compute moving average
- Compute momentum
- Compute volatility
- Compute volume change
- Create a structured signal object

Definition of Done:

- Signal object is generated
- Code is modular
- No hardcoded values
- Signal processing can be tested independently

Example signal object:

    {
      "ticker": "AAPL",
      "momentum": "positive",
      "trend": "bullish",
      "volatility": "stable",
      "volume": "above_average"
    }

---

### Phase 4 — Recommendation Engine

Goal:

Generate Buy / Sell / Hold recommendations.

Tasks:

- Create scoring logic
- Combine signals into a final score
- Convert score into recommendation
- Add confidence score
- Add risk level
- Add explanation

Definition of Done:

- Recommendation JSON matches the API contract
- Logic is explainable
- No ML is required
- Recommendation engine can be tested independently

Example scoring idea:

    momentum_score + trend_score + volume_score - volatility_penalty = final_score

Example recommendation logic:

    final_score >= 70 -> BUY
    final_score between 40 and 69 -> HOLD
    final_score < 40 -> SELL

---

### Phase 5 — Backend API

Goal:

Serve data through FastAPI.

Tasks:

- Build FastAPI server
- Implement GET /health
- Implement GET /price/{ticker}
- Implement GET /signals/{ticker}
- Implement GET /recommendation/{ticker}
- Add error handling
- Add response models

Definition of Done:

- API runs locally
- API returns correct JSON
- API handles invalid tickers
- API responses are low latency
- API documentation is available through FastAPI docs

---

### Phase 6 — Frontend Welcome Page

Goal:

Create a clean entry point for users.

Tasks:

- Build landing page
- Explain what the platform does
- Explain how recommendations are generated
- Add call-to-action button to the dashboard
- Use clean, modern styling

Definition of Done:

- Welcome page looks professional
- Navigation to dashboard works
- Page clearly explains the product

---

### Phase 7 — Frontend Dashboard

Goal:

Allow users to interact with the system.

Tasks:

- Add ticker search
- Fetch API data from backend
- Display current price
- Display recommendation
- Display confidence
- Display risk
- Display signal breakdown
- Add chart using Recharts
- Add loading states
- Add error states

Definition of Done:

- User can search a stock
- Data is displayed correctly
- UI is clean and readable
- Frontend communicates with backend API

---

### Phase 8 — Storage Layer

Goal:

Add persistence and production-style data handling.

Tasks:

- Add PostgreSQL
- Add Redis
- Store prices
- Store signals
- Store recommendations
- Update backend to read/write from storage

Definition of Done:

- Backend reads from database
- Data persists after restart
- Redis stores latest recommendations or prices
- Storage logic is separated from API logic

---

### Phase 9 — Real-Time Updates

Goal:

Simulate a real-time system.

Tasks:

- Add background worker
- Poll market data periodically
- Update signals automatically
- Update recommendations automatically
- Optionally add WebSocket updates

Definition of Done:

- Data updates automatically
- Recommendations refresh without manual backend restart
- System behaves like a real-time platform

---

### Phase 10 — Deployment

Goal:

Make the project production-ready.

Tasks:

- Dockerize backend
- Dockerize frontend
- Add docker-compose
- Add environment variables
- Add deployment instructions
- Optional cloud deployment

Definition of Done:

- System runs with docker-compose
- Backend and frontend are containerized
- Project can be started easily by another developer

---

## 7. Frontend UI Requirements

The UI must include two main pages:

### Welcome Page

Purpose:

Introduce the platform and explain what it does.

Must include:

- Project name
- Short explanation
- How recommendations work
- Key benefits
- Button to start using the platform

Suggested welcome text:

Real-Time Trading System transforms live market data into actionable trading insights. It analyzes S&P 500 stocks using market signals, risk metrics, and backend recommendation services to deliver Buy, Sell, or Hold recommendations.

---

### Dashboard Page

Purpose:

Allow users to actually use the product.

Must include:

- Ticker search bar
- Stock price display
- Price chart
- Recommendation card
- Confidence score
- Risk level
- Signal breakdown
- Explanation of recommendation

Suggested dashboard layout:

    ------------------------------------------------
    | Real-Time Trading System                     |
    ------------------------------------------------
    | Search ticker: [ AAPL ] [Analyze]            |
    ------------------------------------------------
    | Price: $___       Change: ___%               |
    | Recommendation: BUY / SELL / HOLD            |
    | Confidence: __%                              |
    | Risk: Low / Medium / High                    |
    ------------------------------------------------
    | Price Chart                                  |
    ------------------------------------------------
    | Signal Breakdown                             |
    | - Momentum                                   |
    | - Volatility                                 |
    | - Trend                                      |
    | - Volume                                     |
    ------------------------------------------------
    | Explanation                                  |
    ------------------------------------------------

---

## 8. UI Design Principles

- Clean
- Modern
- Minimal
- Fast
- Insight-focused
- Easy to understand
- Avoid clutter
- Make recommendations obvious
- Make the product feel useful, not academic

---

## 9. Engineering Design Principles

- Build incrementally
- Keep the system modular
- Prioritize a working system first
- Avoid overengineering early
- Keep recommendation logic explainable
- Separate concerns clearly
- Backend logic should not live in frontend
- Frontend should call backend APIs only
- Storage logic should be separated from API routes
- Each component should be independently testable

---

## 10. Non-Goals

This project is NOT focused on:

- Perfect stock prediction
- Complex deep learning models
- High-frequency trading
- Guaranteed financial returns
- Financial advice
- Overly complex quant strategies

The value of this project is the engineering system, not guaranteed trading performance.

---

## 11. Success Criteria

The project is successful when:

- Backend runs locally
- Frontend runs locally
- User can open the welcome page
- User can navigate to the dashboard
- User can search for a ticker
- Backend returns a recommendation
- UI displays price, recommendation, confidence, risk, and reasoning
- Market data is ingested and processed
- System is modular
- System is deployable
- Architecture is explainable in interviews

---

## 12. Resume Positioning

Potential resume bullet:

Built a production-style real-time trading platform that ingests S&P 500 market data, processes streaming signals, and serves low-latency, risk-aware trade recommendations through backend APIs and an interactive dashboard.

Skills shown:

- Backend engineering
- Data engineering
- Real-time processing
- API design
- Frontend integration
- System design
- Product thinking
- Deployment

---

## 13. AI Collaboration Guidelines

When using AI to build this project:

- Build one phase at a time
- Ask for production-quality code
- Ask for clear folder structure
- Ask for tests with each component
- Validate each service before moving on
- Do not add unnecessary ML early
- Do not overcomplicate the architecture at the start
- Keep the system explainable
- Keep the user experience clean
- Document every major design decision

---

## 14. AI START COMMAND

Start with Phase 1 only.

Create a production-ready folder structure for:

- FastAPI backend
- React frontend using Vite
- Docker setup

Requirements:

- Clean modular structure
- Separate backend and frontend
- Include all dependencies
- Include run instructions
- Do NOT implement business logic yet
- Do NOT implement future phases yet

After completing Phase 1, STOP and wait for confirmation.

---

## 15. Final Product Statement

The final product is a real-time trading platform that gives users actionable S&P 500 trade recommendations through a clean UI while demonstrating strong backend engineering, data engineering, real-time systems, and production-level system design.
