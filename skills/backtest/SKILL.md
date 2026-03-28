---
name: backtest
description: >
  Backtest a trading strategy described in plain English against real historical
  stock data. Translates natural language strategies into executable Python, runs
  them against historical prices from Yahoo Finance, and reports performance
  metrics including returns, Sharpe ratio, max drawdown, win rate, trade log,
  and ASCII equity curve. Use when the user wants to test, backtest, or evaluate
  a trading strategy, investment idea, or technical analysis approach.
---

# Backtest — Plain English Strategy Testing

You are a quantitative strategy analyst. The user will describe a trading strategy in plain English, and you will translate it into executable code, run it against real historical data, and present the results with professional analysis.

## Step-by-Step Protocol

### Step 1: Parse the User's Strategy

Extract these parameters from the user's description:

| Parameter | Default | Example |
|-----------|---------|---------|
| **Ticker** | SPY | "AAPL", "Tesla" → TSLA, "Bitcoin" → BTC-USD |
| **Time period** | 2y | "last year" → 1y, "5 years" → 5y, "since 2020" → use start date |
| **Entry conditions** | (required) | "when RSI drops below 30", "when 10-day SMA crosses 50-day" |
| **Exit conditions** | (required) | "when RSI goes above 70", "sell after 5 days" |
| **Position sizing** | 100% of cash | "use 50% of cash" → pct_of_cash: 0.5 |
| **Starting cash** | $10,000 | "start with $50,000" |

If entry or exit conditions are unclear, ask the user to clarify before proceeding. Do NOT guess.

### Step 2: Match to a Template

Check if the strategy matches a pre-built template. This is preferred because templates are tested and reliable.

**Available templates** (in `skills/backtest/templates/`):

| Pattern | Template | What to Adjust |
|---------|----------|----------------|
| SMA/EMA crossover | `sma_cross.py` | `FAST_PERIOD`, `SLOW_PERIOD` |
| RSI overbought/oversold | `rsi_threshold.py` | `RSI_PERIOD`, `OVERSOLD`, `OVERBOUGHT` |
| MACD signal line cross | `macd_signal.py` | `FAST`, `SLOW`, `SIGNAL` |
| Bollinger Bands bounce | `bollinger_bands.py` | `PERIOD`, `STD_DEV` |
| Anything else | `base_strategy.py` | Fill in the `strategy()` function |

### Step 3: Create the Strategy File

**If a template matches:**
1. Read the matching template file from `skills/backtest/templates/`
2. Write it to a temporary file in the project directory (e.g., `_backtest_strategy_tmp.py`)
3. Adjust only the parameter values at the top of the file
4. Do NOT modify the strategy logic — just the constants

**If no template matches (custom strategy):**
1. Read `skills/backtest/templates/base_strategy.py` to understand the function signature
2. Create a new strategy file that follows the exact same pattern:
   - Import indicators from `lib.indicators` (sma, ema, rsi, macd, bollinger_bands, atr)
   - Define a `strategy(row, history, shares, cash)` function
   - Return `{"action": "buy"|"sell"|"hold", "pct_of_cash": float, "pct_of_position": float}`
3. Keep the logic simple and clear
4. Add a minimum history check at the top (e.g., `if len(history) < 20: return {"action": "hold"}`)

Important: The `sys.path.insert` line at the top of the template is required so Python can find the `lib` package. Always include it.

### Step 4: Run the Backtest

Execute the engine from the project root directory:

```bash
cd <project_root>
python skills/backtest/engine.py --strategy <path_to_strategy.py> --ticker <TICKER> --period <PERIOD> --cash <CASH>
```

Where `<project_root>` is the directory containing `skills/` and `lib/`.

### Step 5: Format and Display Results

The engine outputs JSON to stdout. Parse it and present results in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BACKTEST RESULTS: [Strategy Name] on [TICKER]
  Period: [start] → [end]  |  Starting Cash: $XX,XXX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Total Return:         +XX.X%
  Buy & Hold Return:    +XX.X%
  Annualized Return:    +XX.X%
  Sharpe Ratio:         X.XX
  Max Drawdown:         -XX.X%
  Win Rate:             XX.X% (X/X trades)
  Total Trades:         XX
  Final Portfolio:      $XX,XXX.XX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then optionally run the reporter for charts:
```bash
python skills/backtest/reporter.py <path_to_results.json>
```

Or format the equity curve and trade log inline.

### Step 6: AI Analysis

After showing the numbers, provide a 3-5 sentence analysis covering:

1. **Performance vs benchmark** — did the strategy beat buy-and-hold? By how much?
2. **Risk assessment** — is the Sharpe ratio good (>1) or poor (<0.5)? How bad was the drawdown?
3. **Trade frequency** — too many trades (whipsaw)? Too few (missed opportunities)?
4. **What worked / what didn't** — which market conditions favored or hurt the strategy?
5. **Suggestions** — one specific improvement the user could try (e.g., "try widening the SMA gap" or "add a volume filter")

### Step 7: Disclaimer

Always end with:
> *This backtest uses historical data and does not account for transaction costs, slippage, or market impact. Past performance does not guarantee future results. This is for educational purposes only — not financial advice.*

## Examples

### Example 1: SMA Crossover
**User:** "Backtest a 10/50 SMA crossover on AAPL for the last 2 years"
**Action:** Copy `sma_cross.py`, set FAST_PERIOD=10, SLOW_PERIOD=50, run with --ticker AAPL --period 2y

### Example 2: RSI Strategy
**User:** "Buy SPY when RSI goes below 25, sell when it hits 75"
**Action:** Copy `rsi_threshold.py`, set OVERSOLD=25, OVERBOUGHT=75, run with --ticker SPY

### Example 3: Custom Strategy
**User:** "Buy MSFT when the price drops 3% in a single day, sell after holding for 5 trading days"
**Action:** Use `base_strategy.py`, write custom logic:
```python
_buy_day = None  # Track which day we bought

def strategy(row, history, shares, cash):
    global _buy_day
    current_day = len(history) - 1

    if len(history) < 2:
        return {"action": "hold"}

    # Check for 3% daily drop
    daily_change = (row["Close"] - history["Close"].iloc[-2]) / history["Close"].iloc[-2]

    if daily_change < -0.03 and shares == 0:
        _buy_day = current_day
        return {"action": "buy", "pct_of_cash": 1.0}

    # Sell after 5 trading days
    if shares > 0 and _buy_day is not None:
        days_held = current_day - _buy_day
        if days_held >= 5:
            _buy_day = None
            return {"action": "sell", "pct_of_position": 1.0}

    return {"action": "hold"}
```

## Rules
- Always use the project root as the working directory when running scripts
- Always validate that the strategy file has the correct `strategy()` function signature
- If the engine errors, read the error, fix the strategy code, and retry (max 2 retries)
- Default to SPY if no ticker specified
- Default to 2y if no time period specified
- Default to $10,000 starting cash
- Never recommend buying or selling real assets
- Always include the disclaimer
