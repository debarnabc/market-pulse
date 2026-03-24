"""
Market Pulse — Global Markets Data Fetcher
============================================
Fetches: Global indices, commodities, FX, crypto, bonds via yfinance.
Returns structured dicts ready for analysis + PDF rendering.

Every function returns data even if some tickers fail —
failed tickers get a None entry so the report can flag stale/missing data.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import yfinance as yf

from config import (
    GLOBAL_INDICES,
    COMMODITIES,
    FOREX,
    CRYPTO,
    BONDS,
    LOOKBACK_1W,
    LOOKBACK_1M,
    LOOKBACK_3M,
    LOOKBACK_52W,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Type alias for a single asset's snapshot
# ─────────────────────────────────────────────
AssetSnapshot = dict[str, Any]
# Keys: name, ticker, price, change_pct, prev_close,
#        avg_volume, last_volume, volume_ratio,
#        week_trend, avg_1m, avg_3m,
#        high_52w, low_52w, pct_from_52w_high, pct_from_52w_low,
#        last_updated, is_stale


def _safe_download(
    ticker: str,
    period: str = "3mo",
    interval: str = "1d",
) -> pd.DataFrame | None:
    """
    Download historical data for a single ticker.
    Returns None if the download fails or returns empty data.
    """
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
            timeout=15,
        )
        if df is None or df.empty:
            logger.warning(f"No data returned for {ticker}")
            return None
        # yfinance sometimes returns MultiIndex columns for single tickers
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        logger.error(f"Failed to download {ticker}: {e}")
        return None


def _build_snapshot(name: str, ticker: str, df: pd.DataFrame) -> AssetSnapshot:
    """
    Build a standardized snapshot dict from a price DataFrame.
    """
    try:
        latest = df.iloc[-1]
        price = float(latest["Close"])

        # Previous close
        if len(df) >= 2:
            prev_close = float(df.iloc[-2]["Close"])
            change_pct = ((price - prev_close) / prev_close) * 100
        else:
            prev_close = None
            change_pct = None

        # Volume metrics (some assets like FX may not have volume)
        has_volume = "Volume" in df.columns and df["Volume"].sum() > 0
        if has_volume and len(df) >= LOOKBACK_1W:
            last_volume = int(latest["Volume"])
            avg_volume = int(df["Volume"].tail(20).mean())
            volume_ratio = (
                round(last_volume / avg_volume, 2) if avg_volume > 0 else None
            )
        else:
            last_volume = None
            avg_volume = None
            volume_ratio = None

        # 1-week trend (last 5 trading days % change)
        if len(df) >= LOOKBACK_1W + 1:
            week_ago_close = float(df.iloc[-(LOOKBACK_1W + 1)]["Close"])
            week_trend = ((price - week_ago_close) / week_ago_close) * 100
        else:
            week_trend = None

        # 1-month and 3-month averages
        avg_1m = (
            round(float(df["Close"].tail(LOOKBACK_1M).mean()), 2)
            if len(df) >= LOOKBACK_1M
            else None
        )
        avg_3m = (
            round(float(df["Close"].tail(LOOKBACK_3M).mean()), 2)
            if len(df) >= LOOKBACK_3M
            else None
        )

        # 52-week high/low (use all available data, up to 1 year)
        high_52w = round(float(df["High"].max()), 2)
        low_52w = round(float(df["Low"].min()), 2)
        pct_from_52w_high = round(((price - high_52w) / high_52w) * 100, 2)
        pct_from_52w_low = round(((price - low_52w) / low_52w) * 100, 2)

        # Timestamp of last data point
        last_updated = str(df.index[-1])

        return {
            "name": name,
            "ticker": ticker,
            "price": round(price, 2),
            "change_pct": round(change_pct, 2) if change_pct is not None else None,
            "prev_close": round(prev_close, 2) if prev_close is not None else None,
            "last_volume": last_volume,
            "avg_volume": avg_volume,
            "volume_ratio": volume_ratio,
            "week_trend": round(week_trend, 2) if week_trend is not None else None,
            "avg_1m": avg_1m,
            "avg_3m": avg_3m,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "pct_from_52w_high": pct_from_52w_high,
            "pct_from_52w_low": pct_from_52w_low,
            "last_updated": last_updated,
            "is_stale": False,
        }
    except Exception as e:
        logger.error(f"Error building snapshot for {name} ({ticker}): {e}")
        return _empty_snapshot(name, ticker)


def _empty_snapshot(name: str, ticker: str) -> AssetSnapshot:
    """Return a placeholder snapshot when data fetch fails."""
    return {
        "name": name,
        "ticker": ticker,
        "price": None,
        "change_pct": None,
        "prev_close": None,
        "last_volume": None,
        "avg_volume": None,
        "volume_ratio": None,
        "week_trend": None,
        "avg_1m": None,
        "avg_3m": None,
        "high_52w": None,
        "low_52w": None,
        "pct_from_52w_high": None,
        "pct_from_52w_low": None,
        "last_updated": None,
        "is_stale": True,
    }


def _fetch_asset_group(
    ticker_map: dict[str, str],
    period: str = "1y",
) -> list[AssetSnapshot]:
    """
    Fetch data for a group of assets defined by a name→ticker dict.
    Downloads all tickers at once for speed, falls back to individual
    downloads if batch fails.
    """
    results = []
    tickers_list = list(ticker_map.values())
    names_list = list(ticker_map.keys())

    # Try batch download first (faster)
    try:
        batch_df = yf.download(
            tickers_list,
            period=period,
            interval="1d",
            progress=False,
            auto_adjust=True,
            group_by="ticker",
            timeout=30,
        )
        if batch_df is not None and not batch_df.empty:
            for name, ticker in ticker_map.items():
                try:
                    if len(tickers_list) == 1:
                        # Single ticker — columns are flat
                        asset_df = batch_df.copy()
                        if isinstance(asset_df.columns, pd.MultiIndex):
                            asset_df.columns = asset_df.columns.get_level_values(0)
                    else:
                        # Multiple tickers — columns are MultiIndex
                        asset_df = batch_df[ticker].copy()
                    asset_df = asset_df.dropna(subset=["Close"])
                    if asset_df.empty:
                        raise ValueError("Empty after dropna")
                    results.append(_build_snapshot(name, ticker, asset_df))
                except Exception as e:
                    logger.warning(
                        f"Batch extraction failed for {name} ({ticker}): {e}. "
                        "Trying individual download..."
                    )
                    # Fallback: individual download
                    ind_df = _safe_download(ticker, period=period)
                    if ind_df is not None:
                        results.append(_build_snapshot(name, ticker, ind_df))
                    else:
                        results.append(_empty_snapshot(name, ticker))
            return results
    except Exception as e:
        logger.warning(f"Batch download failed: {e}. Falling back to individual downloads.")

    # Fallback: download each ticker individually
    for name, ticker in ticker_map.items():
        df = _safe_download(ticker, period=period)
        if df is not None:
            results.append(_build_snapshot(name, ticker, df))
        else:
            results.append(_empty_snapshot(name, ticker))

    return results


# ─────────────────────────────────────────────
# Public API — called by main.py
# ─────────────────────────────────────────────

def fetch_global_indices() -> list[AssetSnapshot]:
    """Fetch all global equity indices."""
    logger.info("Fetching global indices...")
    return _fetch_asset_group(GLOBAL_INDICES, period="1y")


def fetch_commodities() -> list[AssetSnapshot]:
    """Fetch commodities (crude, gold, copper)."""
    logger.info("Fetching commodities...")
    return _fetch_asset_group(COMMODITIES, period="1y")


def fetch_forex() -> list[AssetSnapshot]:
    """Fetch FX rates (DXY, USD/INR, EUR/USD, USD/JPY)."""
    logger.info("Fetching forex...")
    return _fetch_asset_group(FOREX, period="1y")


def fetch_crypto() -> list[AssetSnapshot]:
    """Fetch crypto (BTC, ETH)."""
    logger.info("Fetching crypto...")
    return _fetch_asset_group(CRYPTO, period="1y")


def fetch_bonds() -> list[AssetSnapshot]:
    """Fetch bond yields (US 10Y)."""
    logger.info("Fetching bonds...")
    return _fetch_asset_group(BONDS, period="1y")


def fetch_all_markets() -> dict[str, list[AssetSnapshot]]:
    """
    Master function — fetches everything and returns a single dict.

    Returns:
        {
            "indices": [...],
            "commodities": [...],
            "forex": [...],
            "crypto": [...],
            "bonds": [...],
            "fetch_timestamp": "2025-03-24T07:30:00",
            "failed_count": 2,
            "total_count": 20,
        }
    """
    indices = fetch_global_indices()
    commodities = fetch_commodities()
    forex = fetch_forex()
    crypto = fetch_crypto()
    bonds = fetch_bonds()

    all_assets = indices + commodities + forex + crypto + bonds
    failed = sum(1 for a in all_assets if a["is_stale"])

    result = {
        "indices": indices,
        "commodities": commodities,
        "forex": forex,
        "crypto": crypto,
        "bonds": bonds,
        "fetch_timestamp": datetime.now().isoformat(timespec="seconds"),
        "failed_count": failed,
        "total_count": len(all_assets),
    }

    logger.info(
        f"Markets fetch complete: {result['total_count']} assets, "
        f"{failed} failed"
    )
    return result


# ─────────────────────────────────────────────
# Pretty-print for testing
# ─────────────────────────────────────────────

def print_market_summary(data: dict) -> None:
    """Print a readable summary of fetched market data to console."""
    print(f"\n{'='*70}")
    print(f"  MARKET PULSE — Data Fetch Summary")
    print(f"  Fetched at: {data['fetch_timestamp']}")
    print(f"  Success: {data['total_count'] - data['failed_count']}"
          f"/{data['total_count']}")
    print(f"{'='*70}\n")

    sections = [
        ("GLOBAL INDICES", data["indices"]),
        ("COMMODITIES", data["commodities"]),
        ("FOREX", data["forex"]),
        ("CRYPTO", data["crypto"]),
        ("BONDS", data["bonds"]),
    ]

    for section_name, assets in sections:
        print(f"  ── {section_name} {'─'*(50 - len(section_name))}")
        for a in assets:
            if a["is_stale"]:
                print(f"  ⚠  {a['name']:20s}  DATA UNAVAILABLE")
                continue
            chg = a["change_pct"]
            arrow = "▲" if chg and chg > 0 else "▼" if chg and chg < 0 else "─"
            chg_str = f"{chg:+.2f}%" if chg is not None else "N/A"
            wk_str = f"{a['week_trend']:+.2f}%" if a["week_trend"] is not None else ""
            print(
                f"  {arrow}  {a['name']:20s}  "
                f"{a['price']:>12,.2f}  {chg_str:>8s}  1W: {wk_str:>8s}"
            )
        print()


# ─────────────────────────────────────────────
# Direct execution for testing
# ─────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    data = fetch_all_markets()
    print_market_summary(data)
