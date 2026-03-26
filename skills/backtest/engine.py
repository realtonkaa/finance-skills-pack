"""Lightweight backtesting engine. Runs a strategy against historical OHLCV data."""

import argparse
import importlib.util
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add project root to path so lib/ can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd

from lib.data import get_history


@dataclass
class Trade:
    date: str
    action: str  # "buy" or "sell"
    ticker: str
    shares: float
    price: float
    value: float


@dataclass
class BacktestResult:
    ticker: str
    start_date: str
    end_date: str
    initial_cash: float
    final_value: float
    total_return_pct: float
    annualized_return_pct: float
    buy_and_hold_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    equity_curve: list[float] = field(default_factory=list)
    equity_dates: list[str] = field(default_factory=list)
    drawdown_curve: list[float] = field(default_factory=list)
    trades: list[dict] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, default=str)


class BacktestEngine:
    """Event-driven backtesting engine.

    Iterates through daily OHLCV data, calls the strategy function each day,
    and tracks positions, trades, and equity.
    """

    def __init__(self, data: pd.DataFrame, ticker: str, initial_cash: float = 10000):
        self.data = data
        self.ticker = ticker
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.shares = 0.0
        self.trades: list[Trade] = []
        self.equity_curve: list[float] = []
        self.equity_dates: list[str] = []

    def run(self, strategy_func) -> BacktestResult:
        """Run the backtest.

        Args:
            strategy_func: Function with signature:
                strategy(row, history, position_shares, cash) -> dict
                Returns: {"action": "buy"|"sell"|"hold", "pct_of_cash": 0-1, "pct_of_position": 0-1}
        """
        for i in range(len(self.data)):
            row = self.data.iloc[i]
            history = self.data.iloc[: i + 1]

            signal = strategy_func(row, history, self.shares, self.cash)

            if signal and isinstance(signal, dict):
                action = signal.get("action", "hold")
                price = row["Close"]

                if action == "buy" and self.cash > 0:
                    pct = signal.get("pct_of_cash", 1.0)
                    amount = self.cash * pct
                    shares_to_buy = amount / price
                    self.shares += shares_to_buy
                    self.cash -= amount
                    self.trades.append(
                        Trade(
                            date=str(self.data.index[i])[:10],
                            action="buy",
                            ticker=self.ticker,
                            shares=shares_to_buy,
                            price=price,
                            value=amount,
                        )
                    )

                elif action == "sell" and self.shares > 0:
                    pct = signal.get("pct_of_position", 1.0)
                    shares_to_sell = self.shares * pct
                    amount = shares_to_sell * price
                    self.shares -= shares_to_sell
                    self.cash += amount
                    self.trades.append(
                        Trade(
                            date=str(self.data.index[i])[:10],
                            action="sell",
                            ticker=self.ticker,
                            shares=shares_to_sell,
                            price=price,
                            value=amount,
                        )
                    )

            # Record daily equity
            equity = self.cash + (self.shares * row["Close"])
            self.equity_curve.append(equity)
            self.equity_dates.append(str(self.data.index[i])[:10])

        return self._compile_results()

    def _compile_results(self) -> BacktestResult:
        equity = np.array(self.equity_curve)
        n_days = len(equity)

        # Total return
        final_value = equity[-1] if len(equity) > 0 else self.initial_cash
        total_return = (final_value - self.initial_cash) / self.initial_cash * 100

        # Annualized return
        years = n_days / 252
        if years > 0 and final_value > 0:
            annualized = ((final_value / self.initial_cash) ** (1 / years) - 1) * 100
        else:
            annualized = 0.0

        # Buy and hold return
        if len(self.data) >= 2:
            bh_return = (
                (self.data["Close"].iloc[-1] - self.data["Close"].iloc[0])
                / self.data["Close"].iloc[0]
                * 100
            )
        else:
            bh_return = 0.0

        # Sharpe ratio (daily returns, annualized)
        if len(equity) > 1:
            daily_returns = np.diff(equity) / equity[:-1]
            if np.std(daily_returns) > 0:
                sharpe = (np.mean(daily_returns) / np.std(daily_returns)) * math.sqrt(
                    252
                )
            else:
                sharpe = 0.0
        else:
            sharpe = 0.0

        # Max drawdown
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak * 100
        max_dd = float(np.min(drawdown)) if len(drawdown) > 0 else 0.0

        # Win rate (pair buy/sell trades)
        wins = 0
        losses = 0
        buy_price = None
        for trade in self.trades:
            if trade.action == "buy":
                buy_price = trade.price
            elif trade.action == "sell" and buy_price is not None:
                if trade.price > buy_price:
                    wins += 1
                else:
                    losses += 1
                buy_price = None

        total_round_trips = wins + losses
        win_rate = (wins / total_round_trips * 100) if total_round_trips > 0 else 0.0

        return BacktestResult(
            ticker=self.ticker,
            start_date=self.equity_dates[0] if self.equity_dates else "",
            end_date=self.equity_dates[-1] if self.equity_dates else "",
            initial_cash=self.initial_cash,
            final_value=round(final_value, 2),
            total_return_pct=round(total_return, 2),
            annualized_return_pct=round(annualized, 2),
            buy_and_hold_return_pct=round(bh_return, 2),
            sharpe_ratio=round(sharpe, 2),
            max_drawdown_pct=round(max_dd, 2),
            win_rate_pct=round(win_rate, 1),
            total_trades=len(self.trades),
            winning_trades=wins,
            losing_trades=losses,
            equity_curve=self.equity_curve,
            equity_dates=self.equity_dates,
            drawdown_curve=drawdown.tolist() if len(drawdown) > 0 else [],
            trades=[
                {
                    "date": t.date,
                    "action": t.action,
                    "shares": round(t.shares, 4),
                    "price": round(t.price, 2),
                    "value": round(t.value, 2),
                }
                for t in self.trades
            ],
        )


def load_strategy(path: str):
    """Dynamically load a strategy function from a Python file."""
    spec = importlib.util.spec_from_file_location("strategy_module", path)
    module = importlib.util.module_from_spec(spec)

    # Add project root to the module's namespace so it can import from lib
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    spec.loader.exec_module(module)

    if not hasattr(module, "strategy"):
        raise ValueError(f"Strategy file {path} must define a 'strategy' function")

    return module.strategy


def main():
    parser = argparse.ArgumentParser(description="Run a backtest")
    parser.add_argument("--strategy", required=True, help="Path to strategy .py file")
    parser.add_argument("--ticker", default="SPY", help="Ticker symbol")
    parser.add_argument("--period", default="2y", help="Data period (e.g., 1y, 2y, 5y)")
    parser.add_argument("--cash", type=float, default=10000, help="Starting cash")
    args = parser.parse_args()

    # Load data
    data = get_history(args.ticker, period=args.period)

    # Load strategy
    strategy_func = load_strategy(args.strategy)

    # Run backtest
    engine = BacktestEngine(data, args.ticker, args.cash)
    result = engine.run(strategy_func)

    # Output JSON to stdout
    print(result.to_json())


if __name__ == "__main__":
    main()
