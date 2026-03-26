"""RSI Threshold Strategy.

Buy when RSI drops below the oversold threshold (default 30).
Sell when RSI rises above the overbought threshold (default 70).

Adjust RSI_PERIOD, OVERSOLD, and OVERBOUGHT to customize.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.indicators import rsi

# === PARAMETERS (adjust these) ===
RSI_PERIOD = 14
OVERSOLD = 30
OVERBOUGHT = 70


def strategy(row, history, shares, cash):
    if len(history) < RSI_PERIOD + 1:
        return {"action": "hold"}

    current_rsi = rsi(history["Close"], RSI_PERIOD).iloc[-1]

    # RSI below oversold → buy
    if current_rsi < OVERSOLD and shares == 0:
        return {"action": "buy", "pct_of_cash": 1.0}

    # RSI above overbought → sell
    if current_rsi > OVERBOUGHT and shares > 0:
        return {"action": "sell", "pct_of_position": 1.0}

    return {"action": "hold"}
