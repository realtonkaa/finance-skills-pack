"""MACD Signal Line Crossover Strategy.

Buy when the MACD line crosses above the signal line.
Sell when the MACD line crosses below the signal line.

Adjust FAST, SLOW, and SIGNAL periods to customize.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.indicators import macd

# === PARAMETERS (adjust these) ===
FAST = 12
SLOW = 26
SIGNAL = 9


def strategy(row, history, shares, cash):
    if len(history) < SLOW + SIGNAL + 1:
        return {"action": "hold"}

    close = history["Close"]
    macd_line, signal_line, histogram = macd(close, FAST, SLOW, SIGNAL)

    macd_now = macd_line.iloc[-1]
    macd_prev = macd_line.iloc[-2]
    signal_now = signal_line.iloc[-1]
    signal_prev = signal_line.iloc[-2]

    # MACD crosses above signal → buy
    if macd_prev <= signal_prev and macd_now > signal_now and shares == 0:
        return {"action": "buy", "pct_of_cash": 1.0}

    # MACD crosses below signal → sell
    if macd_prev >= signal_prev and macd_now < signal_now and shares > 0:
        return {"action": "sell", "pct_of_position": 1.0}

    return {"action": "hold"}
