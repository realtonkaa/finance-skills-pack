"""Base strategy template. Claude fills in the strategy() function logic.

The strategy function is called once per day with:
    - row: Current day's OHLCV data (row.Open, row.High, row.Low, row.Close, row.Volume)
    - history: DataFrame of all data up to and including today
    - shares: Current number of shares held (0 if no position)
    - cash: Current cash balance

Return a dict:
    {"action": "buy", "pct_of_cash": 1.0}     # Buy using 100% of cash
    {"action": "sell", "pct_of_position": 1.0}  # Sell 100% of position
    {"action": "hold"}                          # Do nothing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.indicators import sma, ema, rsi, macd, bollinger_bands, atr


def strategy(row, history, shares, cash):
    """Replace this with your strategy logic."""

    # Example: buy and hold
    if shares == 0:
        return {"action": "buy", "pct_of_cash": 1.0}
    return {"action": "hold"}
