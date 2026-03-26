"""Tests for the backtest reporter."""

import json
import pytest

from skills.backtest.reporter import format_results


@pytest.fixture
def sample_result():
    return json.dumps({
        "ticker": "SPY",
        "start_date": "2022-01-03",
        "end_date": "2023-12-29",
        "initial_cash": 10000,
        "final_value": 11500.50,
        "total_return_pct": 15.01,
        "annualized_return_pct": 7.32,
        "buy_and_hold_return_pct": 12.50,
        "sharpe_ratio": 0.85,
        "max_drawdown_pct": -8.45,
        "win_rate_pct": 58.3,
        "total_trades": 24,
        "winning_trades": 7,
        "losing_trades": 5,
        "equity_curve": [10000, 10100, 10050, 10200, 10300, 10150, 10400, 10500, 11000, 11500],
        "equity_dates": ["2022-01-03", "2022-02-01", "2022-03-01", "2022-04-01", "2022-05-01",
                         "2022-06-01", "2022-07-01", "2022-08-01", "2022-09-01", "2022-10-01"],
        "drawdown_curve": [0, 0, -0.5, 0, 0, -1.5, 0, 0, 0, 0],
        "trades": [
            {"date": "2022-01-10", "action": "buy", "shares": 25.0, "price": 400.0, "value": 10000.0},
            {"date": "2022-03-15", "action": "sell", "shares": 25.0, "price": 420.0, "value": 10500.0},
        ]
    })


class TestReporter:
    def test_format_returns_string(self, sample_result):
        output = format_results(sample_result)
        assert isinstance(output, str)
        assert len(output) > 0

    def test_contains_ticker(self, sample_result):
        output = format_results(sample_result)
        assert "SPY" in output

    def test_contains_return(self, sample_result):
        output = format_results(sample_result)
        assert "15.01" in output

    def test_contains_sharpe(self, sample_result):
        output = format_results(sample_result)
        assert "0.85" in output

    def test_contains_trade_log(self, sample_result):
        output = format_results(sample_result)
        assert "Trade Log" in output
        assert "2022-01-10" in output
