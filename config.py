"""
Market Pulse — Central Configuration
=====================================
All tickers, API keys, schedule settings, and constants live here.
API keys are loaded from environment variables (set via GitHub Secrets).
"""

import os
from datetime import date

# ─────────────────────────────────────────────
# API Keys & Credentials (from environment)
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# Comma-separated list of recipient emails in env var
_raw_recipients = os.getenv("RECIPIENT_EMAILS", "")
RECIPIENT_EMAILS = [e.strip() for e in _raw_recipients.split(",") if e.strip()]

# ─────────────────────────────────────────────
# Claude AI Settings
# ─────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 2048

# ─────────────────────────────────────────────
# Global Indices (yfinance tickers)
# ─────────────────────────────────────────────
GLOBAL_INDICES = {
    "S&P 500":    "^GSPC",
    "Nasdaq":     "^IXIC",
    "Dow Jones":  "^DJI",
    "FTSE 100":   "^FTSE",
    "DAX":        "^GDAXI",
    "CAC 40":     "^FCHI",
    "Nikkei 225": "^N225",
    "Hang Seng":  "^HSI",
    "ASX 200":    "^AXJO",
    "Nifty 50":   "^NSEI",
    "Sensex":     "^BSESN",
}

# ─────────────────────────────────────────────
# Commodities (yfinance tickers)
# ─────────────────────────────────────────────
COMMODITIES = {
    "Brent Crude": "BZ=F",
    "Gold":        "GC=F",
    "Copper":      "HG=F",
}

# ─────────────────────────────────────────────
# Forex (yfinance tickers)
# ─────────────────────────────────────────────
FOREX = {
    "DXY":     "DX-Y.NYB",
    "USD/INR": "USDINR=X",
    "EUR/USD": "EURUSD=X",
    "USD/JPY": "USDJPY=X",
}

# ─────────────────────────────────────────────
# Crypto (yfinance tickers)
# ─────────────────────────────────────────────
CRYPTO = {
    "Bitcoin":  "BTC-USD",
    "Ethereum": "ETH-USD",
}

# ─────────────────────────────────────────────
# Bonds (yfinance tickers)
# ─────────────────────────────────────────────
BONDS = {
    "US 10Y Yield": "^TNX",
}
# India 10Y is scraped separately in fetch_india.py

# ─────────────────────────────────────────────
# India — Nifty Sectoral Indices (yfinance)
# ─────────────────────────────────────────────
NIFTY_SECTORS = {
    "Nifty Bank":              "^NSEBANK",
    "Nifty IT":                "^CNXIT",
    "Nifty Pharma":            "^CNXPHARMA",
    "Nifty Auto":              "^CNXAUTO",
    "Nifty Metal":             "^CNXMETAL",
    "Nifty Realty":            "^CNXREALTY",
    "Nifty FMCG":              "^CNXFMCG",
    "Nifty Energy":            "^CNXENERGY",
    "Nifty PSU Bank":          "^CNXPSUBANK",
    "Nifty Media":             "^CNXMEDIA",
    "Nifty Pvt Bank":          "^CNXPRIVATEBANK",
    "Nifty Fin Services":      "^CNXFINANCE",
}

# India VIX
INDIA_VIX_TICKER = "^INDIAVIX"

# ─────────────────────────────────────────────
# FRED Series IDs (US Macro)
# ─────────────────────────────────────────────
FRED_SERIES = {
    "GDP Growth (Q/Q ann.)":   "A191RL1Q225SBEA",
    "Nonfarm Payrolls":        "PAYEMS",
    "Unemployment Rate":       "UNRATE",
    "CPI (Y/Y)":              "CPIAUCSL",
    "Core PCE (Y/Y)":         "PCEPILFE",
    "ISM Manufacturing":      "MANEMP",
    "ISM Services":           "NMFCI",
    "Retail Sales":           "RSAFS",
    "Housing Starts":         "HOUST",
    "Consumer Confidence":    "UMCSENT",
    "Fed Funds Rate":         "FEDFUNDS",
}

# ─────────────────────────────────────────────
# Technical Analysis Parameters
# ─────────────────────────────────────────────
TA_RSI_PERIOD = 14
TA_RSI_OVERBOUGHT = 70
TA_RSI_OVERSOLD = 30
TA_SHORT_MA = 20
TA_MED_MA = 50
TA_LONG_MA = 200
TA_VOLUME_SPIKE_THRESHOLD = 2.0       # Flag if volume > 2x 20-day avg
TA_VOLUME_BREAKOUT_THRESHOLD = 2.5    # Stronger signal
TA_SUPPORT_RESISTANCE_WINDOW = 20     # Days for pivot calculation
TA_52W_PROXIMITY_PCT = 5.0            # Flag if within 5% of 52w high/low

# ─────────────────────────────────────────────
# Signal Engine Thresholds
# ─────────────────────────────────────────────
SIGNAL_SUPPORT_PROXIMITY_PCT = 2.0    # Price within 2% of support
SIGNAL_RESISTANCE_PROXIMITY_PCT = 2.0

# ─────────────────────────────────────────────
# Indian Market Holidays 2025-2026
# (NSE official calendar — update yearly)
# ─────────────────────────────────────────────
INDIAN_HOLIDAYS = [
    # 2025
    date(2025, 2, 26),   # Mahashivratri
    date(2025, 3, 14),   # Holi
    date(2025, 3, 31),   # Id-Ul-Fitr (Eid)
    date(2025, 4, 10),   # Shri Ram Navami
    date(2025, 4, 14),   # Dr. Ambedkar Jayanti
    date(2025, 4, 18),   # Good Friday
    date(2025, 5, 1),    # Maharashtra Day
    date(2025, 6, 7),    # Eid-Ul-Adha (Bakri Eid)
    date(2025, 8, 15),   # Independence Day
    date(2025, 8, 16),   # Janmashtami
    date(2025, 10, 2),   # Mahatma Gandhi Jayanti
    date(2025, 10, 21),  # Diwali (Lakshmi Puja)
    date(2025, 10, 22),  # Diwali Balipratipada
    date(2025, 11, 5),   # Guru Nanak Jayanti
    date(2025, 12, 25),  # Christmas
    # 2026 (provisional — verify when NSE publishes)
    date(2026, 1, 26),   # Republic Day
    date(2026, 2, 17),   # Mahashivratri
    date(2026, 3, 4),    # Holi
    date(2026, 3, 20),   # Id-Ul-Fitr
    date(2026, 3, 30),   # Shri Ram Navami
    date(2026, 4, 3),    # Good Friday
    date(2026, 4, 14),   # Dr. Ambedkar Jayanti
    date(2026, 5, 1),    # Maharashtra Day
    date(2026, 5, 27),   # Eid-Ul-Adha
    date(2026, 8, 15),   # Independence Day
    date(2026, 10, 2),   # Mahatma Gandhi Jayanti
    date(2026, 10, 10),  # Dussehra
    date(2026, 11, 9),   # Diwali
    date(2026, 11, 25),  # Guru Nanak Jayanti
    date(2026, 12, 25),  # Christmas
]

# ─────────────────────────────────────────────
# Report Settings
# ─────────────────────────────────────────────
REPORT_TITLE = "Market Pulse"
REPORT_SUBTITLE_AM = "Pre-Market Intelligence Brief"
REPORT_SUBTITLE_PM = "End-of-Day Recap & Tomorrow's Setup"
REPORT_FOOTER = (
    "AI-generated · Not financial advice · "
    "Do your own research before investing"
)

# Data staleness threshold — if last data point is older than
# this many hours, flag it as stale in the report
STALE_DATA_HOURS = 24

# ─────────────────────────────────────────────
# Lookback Periods (for context vs averages)
# ─────────────────────────────────────────────
LOOKBACK_1W = 5      # Trading days
LOOKBACK_1M = 22
LOOKBACK_3M = 66
LOOKBACK_52W = 252


def is_trading_day(check_date: date | None = None) -> bool:
    """
    Returns True if the given date is a trading day
    (weekday + not an Indian market holiday).
    """
    if check_date is None:
        check_date = date.today()
    # Saturday = 5, Sunday = 6
    if check_date.weekday() >= 5:
        return False
    if check_date in INDIAN_HOLIDAYS:
        return False
    return True


def validate_env() -> list[str]:
    """
    Check that all required environment variables are set.
    Returns a list of missing variable names (empty = all good).
    """
    required = {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "FRED_API_KEY": FRED_API_KEY,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "GMAIL_ADDRESS": GMAIL_ADDRESS,
        "GMAIL_APP_PASSWORD": GMAIL_APP_PASSWORD,
        "RECIPIENT_EMAILS": _raw_recipients,
    }
    return [name for name, value in required.items() if not value]
