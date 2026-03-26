"""Bollinger Bands Mean Reversion Strategy.

Buy when price touches or drops below the lower band (oversold).
Sell when price touches or rises above the upper band (overbought).

Adjust PERIOD and STD_DEV to customize.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.indicators import bollinger_bands

# === PARAMETERS (adjust these) ===
PERIOD = 20
STD_DEV = 2.0


def strategy(row, history, shares, cash):
    if len(history) < PERIOD + 1:
        return {"action": "hold"}

    close = history["Close"]
    upper, middle, lower = bollinger_bands(close, PERIOD, STD_DEV)

    price = row["Close"]
    lower_band = lower.iloc[-1]
    upper_band = upper.iloc[-1]

    # Price at or below lower band → buy (mean reversion)
    if price <= lower_band and shares == 0:
        return {"action": "buy", "pct_of_cash": 1.0}

    # Price at or above upper band → sell
    if price >= upper_band and shares > 0:
        return {"action": "sell", "pct_of_position": 1.0}

    return {"action": "hold"}
