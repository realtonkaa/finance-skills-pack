"""Tests for the backtesting engine."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from skills.backtest.engine import BacktestEngine, BacktestResult, _validate_strategy


@pytest.fixture
def spy_data():
    """Load SPY fixture data."""
    fixture_path = Path(__file__).parent / "fixtures" / "spy_history.json"
    with open(fixture_path) as f:
        raw = json.load(f)

    df = pd.DataFrame(raw).T
    df.index = pd.to_datetime(df.index)
    df = df.astype(float)
    df["Volume"] = df["Volume"].astype(int)
    df = df.sort_index()
    return df


def buy_and_hold_strategy(row, history, shares, cash):
    """Simple buy-and-hold: buy on first day, hold forever."""
    if shares == 0:
        return {"action": "buy", "pct_of_cash": 1.0}
    return {"action": "hold"}


def never_trade_strategy(row, history, shares, cash):
    """Never trade — stay in cash."""
    return {"action": "hold"}


def alternate_strategy(row, history, shares, cash):
    """Buy and sell on alternating days (for testing trade mechanics)."""
    day = len(history)
    if day % 10 == 1 and shares == 0:
        return {"action": "buy", "pct_of_cash": 1.0}
    if day % 10 == 6 and shares > 0:
        return {"action": "sell", "pct_of_position": 1.0}
    return {"action": "hold"}


class TestBacktestEngine:
    def test_buy_and_hold_matches_market(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(buy_and_hold_strategy)

        # Buy-and-hold should roughly match market return
        market_return = (
            (spy_data["Close"].iloc[-1] - spy_data["Close"].iloc[0])
            / spy_data["Close"].iloc[0]
            * 100
        )
        assert abs(result.total_return_pct - market_return) < 1.0  # within 1%

    def test_never_trade_returns_zero(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(never_trade_strategy)

        assert result.total_return_pct == 0.0
        assert result.final_value == 10000
        assert result.total_trades == 0

    def test_trades_are_recorded(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(alternate_strategy)

        assert result.total_trades > 0
        assert len(result.trades) > 0
        # First trade should be a buy
        assert result.trades[0]["action"] == "buy"

    def test_equity_curve_length(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(buy_and_hold_strategy)

        assert len(result.equity_curve) == len(spy_data)
        assert len(result.equity_dates) == len(spy_data)

    def test_equity_starts_at_initial_cash(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(never_trade_strategy)

        assert result.equity_curve[0] == 10000

    def test_max_drawdown_is_negative_or_zero(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(buy_and_hold_strategy)

        assert result.max_drawdown_pct <= 0

    def test_sharpe_ratio_is_finite(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(buy_and_hold_strategy)

        assert np.isfinite(result.sharpe_ratio)

    def test_win_rate_between_0_and_100(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(alternate_strategy)

        assert 0 <= result.win_rate_pct <= 100

    def test_result_json_is_valid(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=10000)
        result = engine.run(buy_and_hold_strategy)

        json_str = result.to_json()
        parsed = json.loads(json_str)
        assert "total_return_pct" in parsed
        assert "sharpe_ratio" in parsed
        assert "equity_curve" in parsed

    def test_custom_initial_cash(self, spy_data):
        engine = BacktestEngine(spy_data, "SPY", initial_cash=50000)
        result = engine.run(never_trade_strategy)

        assert result.initial_cash == 50000
        assert result.final_value == 50000


class TestStrategyValidation:
    """Tests for the import-scanning security feature."""

    def test_safe_strategy_passes(self, tmp_path):
        safe = tmp_path / "safe.py"
        safe.write_text("from lib.indicators import sma\ndef strategy(row, h, s, c): return {'action': 'hold'}\n")
        _validate_strategy(str(safe))  # Should not raise

    def test_blocks_os_import(self, tmp_path):
        bad = tmp_path / "bad.py"
        bad.write_text("import os\ndef strategy(row, h, s, c): os.system('rm -rf /')\n")
        with pytest.raises(ValueError, match="blocked module"):
            _validate_strategy(str(bad))

    def test_blocks_subprocess(self, tmp_path):
        bad = tmp_path / "bad.py"
        bad.write_text("import subprocess\ndef strategy(row, h, s, c): pass\n")
        with pytest.raises(ValueError, match="blocked module"):
            _validate_strategy(str(bad))

    def test_blocks_from_os_import(self, tmp_path):
        bad = tmp_path / "bad.py"
        bad.write_text("from os import path\ndef strategy(row, h, s, c): pass\n")
        with pytest.raises(ValueError, match="blocked module"):
            _validate_strategy(str(bad))

    def test_blocks_socket(self, tmp_path):
        bad = tmp_path / "bad.py"
        bad.write_text("import socket\ndef strategy(row, h, s, c): pass\n")
        with pytest.raises(ValueError, match="blocked module"):
            _validate_strategy(str(bad))

    def test_allows_numpy_pandas(self, tmp_path):
        safe = tmp_path / "safe.py"
        safe.write_text("import numpy as np\nimport pandas as pd\ndef strategy(row, h, s, c): return {'action': 'hold'}\n")
        _validate_strategy(str(safe))  # Should not raise
