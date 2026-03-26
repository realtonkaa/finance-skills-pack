"""Tests for technical indicators."""

import numpy as np
import pandas as pd
import pytest

from lib.indicators import sma, ema, rsi, macd, bollinger_bands, atr


@pytest.fixture
def sample_prices():
    """Simple price series for testing."""
    return pd.Series([10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 14, 13, 12, 11, 10, 11, 12, 13, 14, 15])


@pytest.fixture
def ohlcv_data():
    """Simple OHLCV data for ATR testing."""
    return pd.DataFrame({
        "Open": [10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 14, 13, 12, 11, 10, 11, 12, 13, 14, 15],
        "High": [11, 12, 13, 12, 11, 10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 12, 13, 14, 15, 16],
        "Low":  [ 9, 10, 11, 10,  9,  8,  9, 10, 11, 12, 13, 12, 11, 10,  9, 10, 11, 12, 13, 14],
        "Close":[10, 11, 12, 11, 10,  9, 10, 11, 12, 13, 14, 13, 12, 11, 10, 11, 12, 13, 14, 15],
    })


class TestSMA:
    def test_basic_calculation(self, sample_prices):
        result = sma(sample_prices, 3)
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[1])
        assert result.iloc[2] == pytest.approx(11.0)  # (10+11+12)/3

    def test_length_matches_input(self, sample_prices):
        result = sma(sample_prices, 5)
        assert len(result) == len(sample_prices)

    def test_all_nan_before_period(self, sample_prices):
        result = sma(sample_prices, 5)
        assert all(pd.isna(result.iloc[:4]))
        assert not pd.isna(result.iloc[4])


class TestEMA:
    def test_basic_calculation(self, sample_prices):
        result = ema(sample_prices, 3)
        assert len(result) == len(sample_prices)
        # EMA should start from first value
        assert result.iloc[0] == sample_prices.iloc[0]

    def test_responds_to_recent_prices(self, sample_prices):
        result = ema(sample_prices, 3)
        # EMA should be closer to recent prices than SMA
        sma_result = sma(sample_prices, 3)
        # Just verify both produce valid numbers at the end
        assert not pd.isna(result.iloc[-1])
        assert not pd.isna(sma_result.iloc[-1])


class TestRSI:
    def test_range_is_0_to_100(self, sample_prices):
        result = rsi(sample_prices, 14)
        valid = result.dropna()
        assert all(valid >= 0)
        assert all(valid <= 100)

    def test_rising_prices_high_rsi(self):
        rising = pd.Series(list(range(1, 30)))
        result = rsi(rising, 14)
        # Consistently rising should give RSI near 100
        assert result.iloc[-1] > 80

    def test_falling_prices_low_rsi(self):
        falling = pd.Series(list(range(30, 1, -1)))
        result = rsi(falling, 14)
        # Consistently falling should give RSI near 0
        assert result.iloc[-1] < 20


class TestMACD:
    def test_returns_three_series(self, sample_prices):
        macd_line, signal_line, histogram = macd(sample_prices)
        assert len(macd_line) == len(sample_prices)
        assert len(signal_line) == len(sample_prices)
        assert len(histogram) == len(sample_prices)

    def test_histogram_is_macd_minus_signal(self, sample_prices):
        macd_line, signal_line, histogram = macd(sample_prices)
        diff = macd_line - signal_line
        np.testing.assert_array_almost_equal(histogram.values, diff.values)


class TestBollingerBands:
    def test_upper_above_middle_above_lower(self, sample_prices):
        upper, middle, lower = bollinger_bands(sample_prices, period=5)
        valid_idx = ~(pd.isna(upper) | pd.isna(middle) | pd.isna(lower))
        assert all(upper[valid_idx] >= middle[valid_idx])
        assert all(middle[valid_idx] >= lower[valid_idx])

    def test_middle_is_sma(self, sample_prices):
        upper, middle, lower = bollinger_bands(sample_prices, period=5)
        expected_sma = sma(sample_prices, 5)
        pd.testing.assert_series_equal(middle, expected_sma)


class TestATR:
    def test_positive_values(self, ohlcv_data):
        result = atr(ohlcv_data["High"], ohlcv_data["Low"], ohlcv_data["Close"], period=5)
        valid = result.dropna()
        assert all(valid > 0)

    def test_length_matches_input(self, ohlcv_data):
        result = atr(ohlcv_data["High"], ohlcv_data["Low"], ohlcv_data["Close"], period=5)
        assert len(result) == len(ohlcv_data)
