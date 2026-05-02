from __future__ import annotations

import argparse
import json
import sys

from app.recommendation.exceptions import RecommendationError
from app.recommendation.service import RecommendationService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Buy / Sell / Hold recommendation from processed signals.",
    )
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to evaluate. Defaults to AAPL.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    service = RecommendationService()

    try:
        result = service.generate(args.ticker)
    except RecommendationError as exc:
        print(f"[recommendation-error] {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.recommendation.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
