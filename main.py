"""
Market Pulse — Main Orchestrator
==================================
CLI entry point for all operations.
Run with: python main.py --test-markets
"""

import argparse
import logging
import sys
from datetime import date

from config import is_trading_day, validate_env


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def cmd_test_markets() -> None:
    """Test global markets data fetch."""
    from data.fetch_markets import fetch_all_markets, print_market_summary

    data = fetch_all_markets()
    print_market_summary(data)

    # Show one detailed asset as example
    example = data["indices"][0]
    print(f"\n  ── DETAILED VIEW: {example['name']} ──")
    for key, val in example.items():
        print(f"    {key:25s}: {val}")


def cmd_dry_run() -> None:
    """Print what would happen without making any API calls."""
    today = date.today()
    print(f"\n  Market Pulse — Dry Run")
    print(f"  Date: {today}")
    print(f"  Trading day: {is_trading_day(today)}")

    missing = validate_env()
    if missing:
        print(f"  ⚠ Missing env vars: {', '.join(missing)}")
    else:
        print(f"  ✓ All env vars configured")

    if not is_trading_day(today):
        print(f"  → Would SKIP (not a trading day)")
    else:
        print(f"  → Would RUN full pipeline")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Market Pulse — Daily Market Intelligence System"
    )
    parser.add_argument("--generate", action="store_true", help="Generate PDF report")
    parser.add_argument("--send", action="store_true", help="Send via email + Telegram")
    parser.add_argument("--edition", choices=["am", "pm"], default="am", help="AM or PM edition")
    parser.add_argument("--test-markets", action="store_true", help="Test global markets data pull")
    parser.add_argument("--test-india", action="store_true", help="Test India data pull")
    parser.add_argument("--test-macro", action="store_true", help="Test macro data pull")
    parser.add_argument("--test-technicals", action="store_true", help="Test TA computation")
    parser.add_argument("--test-ai", action="store_true", help="Test Claude commentary")
    parser.add_argument("--test-pdf-1-2", action="store_true", help="Test PDF pages 1-2")
    parser.add_argument("--no-send", action="store_true", help="Generate without sending")
    parser.add_argument("--dry-run", action="store_true", help="Print plan, no API calls")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.dry_run:
        cmd_dry_run()
    elif args.test_markets:
        cmd_test_markets()
    elif args.test_india:
        print("  ⏳ India data fetch — Coming Day 2")
    elif args.test_macro:
        print("  ⏳ Macro data fetch — Coming Day 3")
    elif args.test_technicals:
        print("  ⏳ Technicals — Coming Day 4")
    elif args.test_ai:
        print("  ⏳ AI commentary — Coming Day 5")
    elif args.test_pdf_1_2:
        print("  ⏳ PDF generation — Coming Day 6")
    elif args.generate:
        print("  ⏳ Full pipeline — Coming Day 9")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
