# finance-skills-pack

> Claude Code skills for financial analysis and strategy backtesting.
> Describe a trading strategy in plain English — get real backtest results in your terminal.

[![Tests](https://github.com/realtonkaa/finance-skills-pack/actions/workflows/test.yml/badge.svg)](https://github.com/realtonkaa/finance-skills-pack/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## What is this?

A collection of 4 Claude Code skills that bring financial analysis directly into your terminal. Three skills work with zero dependencies (they use Claude's own search), and the star feature — `/backtest` — lets you describe a trading strategy in plain English and instantly test it against real historical data.

**No API keys. No accounts. No complex setup.**

## Skills

| Skill | What it does | Dependencies |
|-------|-------------|--------------|
| `/stock-check AAPL` | Live stock data + AI analysis | None |
| `/budget` | Interactive budget planner with AI tips | None |
| `/portfolio` | Track holdings, get diversification analysis | None |
| `/backtest` | Plain-English strategy backtesting | Python packages |

## Quick Start

```bash
# Clone
git clone https://github.com/realtonkaa/finance-skills-pack.git
cd finance-skills-pack

# Install skills to Claude Code (global)
cp -r skills/* ~/.claude/skills/

# For /backtest: install Python dependencies
pip install -r requirements.txt
```

Then in Claude Code:
```
/stock-check TSLA
```

## /backtest — The Star Feature

Describe any trading strategy in plain English. Claude translates it to code, runs it against real Yahoo Finance data, and shows you the results.

### Example

```
/backtest Buy SPY when the 10-day SMA crosses above the 50-day SMA, sell when it crosses below
```

**Output:**
```
╔══════════════════════════════════════════════════════════╗
║  BACKTEST: SPY  |  2024-03-26 → 2026-03-26             ║
╠══════════════════════════════════════════════════════════╣
║  Total Return:         +14.32%                          ║
║  Buy & Hold Return:    +22.10%                          ║
║  Annualized Return:    +6.92%                           ║
║  Sharpe Ratio:         0.73                             ║
║  Max Drawdown:         -8.45%                           ║
║  Win Rate:             58.3% (7/12)                     ║
║  Total Trades:         24                               ║
║  Final Value:          $11,432.00                       ║
╚══════════════════════════════════════════════════════════╝
```

Plus an ASCII equity curve, trade log, and AI commentary on what worked and what didn't.

### More Examples

```
/backtest Buy AAPL when RSI drops below 30, sell when it goes above 70

/backtest MACD crossover strategy on MSFT for the last 3 years

/backtest Buy QQQ when price hits the lower Bollinger Band, sell at the upper band

/backtest Buy TSLA when price drops 3% in a day, sell after 5 trading days
```

### How It Works

1. You describe a strategy in plain English
2. Claude matches it to a pre-built template (SMA, RSI, MACD, Bollinger) or writes custom code
3. The engine runs it against real historical data from Yahoo Finance
4. Results are displayed with performance metrics, charts, and AI analysis

**Pre-built templates** handle the most common strategies with near-zero chance of errors. Custom strategies use a simple, constrained function signature that Claude fills in.

## /stock-check

Quick stock lookup with AI-powered analysis. Zero dependencies — uses Claude's web search.

```
/stock-check NVDA
```

Shows: current price, daily change, 52-week range, P/E ratio, market cap, recent news headlines, and a one-paragraph AI outlook.

## /budget

Interactive budget planning assistant. Zero dependencies.

```
/budget
```

Walk through your income and expenses, see a formatted breakdown with allocation bars, and get AI suggestions based on the 50/30/20 rule.

## /portfolio

Track your investment holdings and get diversification analysis. Zero dependencies.

```
/portfolio
```

Add holdings, view allocation charts, get a diversification score (1-10), and receive rebalancing suggestions. Supports stocks and crypto.

## Architecture

```
finance-skills-pack/
├── skills/
│   ├── backtest/
│   │   ├── SKILL.md              # Prompt engineering for plain-English parsing
│   │   ├── engine.py             # Custom backtesting engine
│   │   ├── reporter.py           # ASCII results formatting
│   │   └── templates/            # Pre-built strategy templates
│   │       ├── sma_cross.py      # SMA crossover
│   │       ├── rsi_threshold.py  # RSI overbought/oversold
│   │       ├── macd_signal.py    # MACD signal cross
│   │       └── bollinger_bands.py
│   ├── stock-check/SKILL.md      # Zero-dep: uses web search
│   ├── budget/SKILL.md           # Zero-dep: pure Claude
│   └── portfolio/SKILL.md        # Zero-dep: uses web search
├── lib/                          # Shared Python libraries
│   ├── data.py                   # Yahoo Finance wrapper + caching
│   ├── cache.py                  # File-based cache with TTL
│   ├── indicators.py             # SMA, EMA, RSI, MACD, Bollinger, ATR
│   ├── charts.py                 # ASCII chart generation (plotext)
│   └── tables.py                 # Terminal table formatting (tabulate)
└── tests/                        # 37 tests, all offline (fixture data)
```

## Dependencies

Only `/backtest` needs Python packages. The other 3 skills have zero dependencies.

```
yfinance    — Yahoo Finance data
pandas      — Data manipulation
numpy       — Numerical computing
plotext     — ASCII terminal charts
tabulate    — Terminal table formatting
```

## Contributing

Want to add a new strategy template? Create a file in `skills/backtest/templates/` following the pattern in `base_strategy.py`:

```python
def strategy(row, history, shares, cash):
    # Your logic here
    return {"action": "buy", "pct_of_cash": 1.0}   # or "sell" or "hold"
```

## License

MIT

---

> *This is an educational tool for learning about quantitative finance and AI-assisted development. It is not financial advice. Past performance does not guarantee future results. Always do your own research before making investment decisions.*
