from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class CompanyInfo(TypedDict):
    ticker: str
    name: str


DATA_PATH = Path(__file__).with_name("sp500_companies.json")


def load_sp500_companies() -> list[CompanyInfo]:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return [{"ticker": company["ticker"], "name": company["name"]} for company in payload]


SP500_COMPANIES = load_sp500_companies()
SP500_TICKERS = [company["ticker"] for company in SP500_COMPANIES]

SP500_TOP_100_TICKERS = [
    "NVDA",
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "GOOG",
    "AVGO",
    "META",
    "TSLA",
    "WMT",
    "BRK.B",
    "LLY",
    "JPM",
    "XOM",
    "V",
    "MU",
    "AMD",
    "JNJ",
    "INTC",
    "ORCL",
    "COST",
    "MA",
    "CAT",
    "NFLX",
    "CVX",
    "BAC",
    "ABBV",
    "CSCO",
    "PLTR",
    "PG",
    "KO",
    "UNH",
    "HD",
    "LRCX",
    "AMAT",
    "MS",
    "GE",
    "GEV",
    "MRK",
    "GS",
    "PM",
    "TXN",
    "WFC",
    "LIN",
    "RTX",
    "KLAC",
    "IBM",
    "AXP",
    "ANET",
    "C",
    "PEP",
    "TMUS",
    "MCD",
    "NEE",
    "VZ",
    "ADI",
    "QCOM",
    "DIS",
    "T",
    "BA",
    "AMGN",
    "SNDK",
    "APH",
    "TMO",
    "TJX",
    "ETN",
    "BLK",
    "GILD",
    "STX",
    "ISRG",
    "SCHW",
    "UNP",
    "DE",
    "ABT",
    "BX",
    "APP",
    "WELL",
    "UBER",
    "CRM",
    "COP",
    "PFE",
    "PANW",
    "WDC",
    "DELL",
    "GLW",
    "HON",
    "PLD",
    "BKNG",
    "LOW",
    "CB",
    "SPGI",
    "VRT",
    "MO",
    "DHR",
    "COF",
    "SBUX",
    "BMY",
    "LMT",
    "PGR",
    "NEM",
]
