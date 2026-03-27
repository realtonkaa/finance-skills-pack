"""Yahoo Finance data wrapper with caching."""

import time
from typing import Optional

import pandas as pd
import yfinance as yf

from lib.cache import get_cached, get_stale, set_cached

# Rate limiting: minimum seconds between API calls
_last_call_time = 0.0
_MIN_DELAY = 0.5


def _rate_limit():
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < _MIN_DELAY:
        time.sleep(_MIN_DELAY - elapsed)
    _last_call_time = time.time()


def get_history(
    symbol: str,
    period: str = "2y",
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch OHLCV history for a symbol. Uses cache to avoid redundant API calls.

    Args:
        symbol: Ticker symbol (e.g., "SPY", "AAPL", "BTC-USD")
        period: Data period (e.g., "1y", "2y", "5y", "max")
        interval: Data interval (e.g., "1d", "1wk", "1mo")

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    cache_key = f"history:{symbol}:{period}:{interval}"

    # Check cache first
    cached = get_cached(cache_key, ttl_hours=24.0)
    if cached is not None:
        df = pd.DataFrame(cached)
        df.index = pd.to_datetime(df.index)
        return df

    # Fetch from yfinance
    try:
        _rate_limit()
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            # Try stale cache as fallback
            stale = get_stale(cache_key)
            if stale is not None:
                df = pd.DataFrame(stale)
                df.index = pd.to_datetime(df.index)
                return df
            raise ValueError(f"No data found for {symbol}")

        # Keep only OHLCV columns
        df = df[["Open", "High", "Low", "Close", "Volume"]]

        # Cache the result (convert Timestamp index to strings for JSON)
        cache_df = df.copy()
        cache_df.index = cache_df.index.astype(str)
        cache_data = cache_df.to_dict()
        set_cached(cache_key, cache_data, ttl_hours=24.0)

        return df

    except Exception as e:
        # Fallback to stale cache
        stale = get_stale(cache_key)
        if stale is not None:
            df = pd.DataFrame(stale)
            df.index = pd.to_datetime(df.index)
            return df
        raise RuntimeError(f"Failed to fetch data for {symbol}: {e}")


def get_ticker_info(symbol: str) -> dict:
    """Fetch basic ticker info (name, sector, market cap, etc.)."""
    cache_key = f"info:{symbol}"

    cached = get_cached(cache_key, ttl_hours=1.0)
    if cached is not None:
        return cached

    try:
        _rate_limit()
        ticker = yf.Ticker(symbol)
        info = ticker.info

        result = {
            "symbol": symbol,
            "name": info.get("shortName", symbol),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "previous_close": info.get("previousClose"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "volume": info.get("volume"),
        }

        set_cached(cache_key, result, ttl_hours=1.0)
        return result

    except Exception as e:
        stale = get_stale(cache_key)
        if stale is not None:
            return stale
        raise RuntimeError(f"Failed to fetch info for {symbol}: {e}")
