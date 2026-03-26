"""SMA Crossover Strategy.

Buy when the fast SMA crosses above the slow SMA.
Sell when the fast SMA crosses below the slow SMA.

Adjust FAST_PERIOD and SLOW_PERIOD to customize.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.indicators import sma

# === PARAMETERS (adjust these) ===
FAST_PERIOD = 10
SLOW_PERIOD = 50


def strategy(row, history, shares, cash):
    if len(history) < SLOW_PERIOD + 1:
        return {"action": "hold"}

    close = history["Close"]
    fast_sma = sma(close, FAST_PERIOD)
    slow_sma = sma(close, SLOW_PERIOD)

    fast_now = fast_sma.iloc[-1]
    fast_prev = fast_sma.iloc[-2]
    slow_now = slow_sma.iloc[-1]
    slow_prev = slow_sma.iloc[-2]

    # Fast crosses above slow → buy
    if fast_prev <= slow_prev and fast_now > slow_now and shares == 0:
        return {"action": "buy", "pct_of_cash": 1.0}

    # Fast crosses below slow → sell
    if fast_prev >= slow_prev and fast_now < slow_now and shares > 0:
        return {"action": "sell", "pct_of_position": 1.0}

    return {"action": "hold"}
