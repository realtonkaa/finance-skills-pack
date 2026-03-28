"""Tests for the data module (yfinance wrapper + caching)."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from lib.cache import get_cached, set_cached, get_stale, clear_cache
from lib.data import get_history, get_ticker_info


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def use_temp_cache(tmp_path):
    """Use a temp directory for cache during tests."""
    with patch("lib.cache.CACHE_DIR", tmp_path / "cache"):
        yield tmp_path / "cache"


# ── Cache Tests ──────────────────────────────────────────────────────────────


class TestCache:
    def test_set_and_get(self):
        set_cached("test_key", {"price": 100.0})
        result = get_cached("test_key", ttl_hours=1.0)
        assert result == {"price": 100.0}

    def test_get_missing_key(self):
        result = get_cached("nonexistent", ttl_hours=1.0)
        assert result is None

    def test_expired_returns_none(self):
        set_cached("old_key", {"data": "old"})
        result = get_cached("old_key", ttl_hours=-1.0)
        assert result is None

    def test_stale_returns_expired_data(self):
        set_cached("stale_key", {"data": "stale"})
        result = get_stale("stale_key")
        assert result == {"data": "stale"}

    def test_stale_missing_returns_none(self):
        result = get_stale("nonexistent")
        assert result is None

    def test_clear_cache(self, use_temp_cache):
        set_cached("key1", "data1")
        set_cached("key2", "data2")
        clear_cache()
        assert get_cached("key1", ttl_hours=24.0) is None
        assert get_cached("key2", ttl_hours=24.0) is None

    def test_different_keys_different_data(self):
        set_cached("key_a", {"value": "a"})
        set_cached("key_b", {"value": "b"})
        assert get_cached("key_a", ttl_hours=1.0) == {"value": "a"}
        assert get_cached("key_b", ttl_hours=1.0) == {"value": "b"}

    def test_overwrite_existing_key(self):
        set_cached("overwrite", {"version": 1})
        set_cached("overwrite", {"version": 2})
        result = get_cached("overwrite", ttl_hours=1.0)
        assert result == {"version": 2}


# ── Data Module Tests (mocked yfinance) ─────────────────────────────────────


@pytest.fixture
def spy_fixture_df():
    """Load SPY fixture data as a DataFrame (like yfinance returns)."""
    fixture_path = FIXTURES / "spy_history.json"
    with open(fixture_path) as f:
        raw = json.load(f)
    df = pd.DataFrame(raw).T
    df.index = pd.to_datetime(df.index)
    df = df.astype(float)
    df["Volume"] = df["Volume"].astype(int)
    return df.sort_index()


class TestGetHistory:
    def test_returns_dataframe_from_cache(self):
        """Cache hit should return data without calling yfinance."""
        fake_data = {
            "Open": {"2024-01-01": 100.0},
            "High": {"2024-01-01": 105.0},
            "Low": {"2024-01-01": 99.0},
            "Close": {"2024-01-01": 103.0},
            "Volume": {"2024-01-01": 1000000},
        }
        set_cached("history:TEST:2y:1d", fake_data, ttl_hours=24.0)

        with patch("lib.data.yf") as mock_yf:
            result = get_history("TEST", period="2y")
            mock_yf.Ticker.assert_not_called()

        assert isinstance(result, pd.DataFrame)
        assert "Close" in result.columns

    def test_fetches_from_yfinance_on_cache_miss(self, spy_fixture_df):
        """Cache miss should fetch from yfinance and cache the result."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = spy_fixture_df

        with patch("lib.data.yf.Ticker", return_value=mock_ticker):
            with patch("lib.data._rate_limit"):
                result = get_history("SPY", period="2y")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(spy_fixture_df)
        mock_ticker.history.assert_called_once()

    def test_empty_dataframe_raises(self):
        """Empty yfinance response should raise ValueError."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()

        with patch("lib.data.yf.Ticker", return_value=mock_ticker):
            with patch("lib.data._rate_limit"):
                with pytest.raises((ValueError, RuntimeError)):
                    get_history("FAKE_TICKER", period="2y")

    def test_api_failure_falls_back_to_stale_cache(self):
        """If yfinance raises, should fall back to stale cached data."""
        fake_data = {
            "Open": {"2024-01-01": 100.0},
            "Close": {"2024-01-01": 103.0},
            "High": {"2024-01-01": 105.0},
            "Low": {"2024-01-01": 99.0},
            "Volume": {"2024-01-01": 1000000},
        }
        # Put stale data in cache (expired)
        set_cached("history:FAIL:2y:1d", fake_data, ttl_hours=0.0)

        mock_ticker = MagicMock()
        mock_ticker.history.side_effect = Exception("yfinance error")

        with patch("lib.data.yf.Ticker", return_value=mock_ticker):
            with patch("lib.data._rate_limit"):
                result = get_history("FAIL", period="2y")

        assert isinstance(result, pd.DataFrame)
        assert "Close" in result.columns


class TestGetTickerInfo:
    def test_returns_dict_from_cache(self):
        """Cache hit should return info dict without API call."""
        fake_info = {"symbol": "AAPL", "name": "Apple Inc", "price": 180.0}
        set_cached("info:AAPL", fake_info, ttl_hours=1.0)

        with patch("lib.data.yf") as mock_yf:
            result = get_ticker_info("AAPL")
            mock_yf.Ticker.assert_not_called()

        assert result["name"] == "Apple Inc"

    def test_fetches_from_yfinance_on_cache_miss(self):
        """Cache miss should fetch .info from yfinance."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "shortName": "Apple Inc",
            "sector": "Technology",
            "currentPrice": 180.0,
            "previousClose": 178.0,
            "marketCap": 2800000000000,
            "trailingPE": 28.5,
            "dividendYield": 0.005,
            "fiftyTwoWeekHigh": 200.0,
            "fiftyTwoWeekLow": 140.0,
            "volume": 50000000,
        }

        with patch("lib.data.yf.Ticker", return_value=mock_ticker):
            with patch("lib.data._rate_limit"):
                result = get_ticker_info("AAPL")

        assert result["name"] == "Apple Inc"
        assert result["sector"] == "Technology"
        assert result["price"] == 180.0
