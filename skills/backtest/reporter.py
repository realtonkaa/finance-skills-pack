"""Format backtest results for terminal display."""

import json
import sys
from pathlib import Path

_reporter_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_reporter_dir.parent.parent))  # repo root
sys.path.insert(0, str(_reporter_dir))                 # installed skills dir

from lib.charts import plot_equity_curve, plot_drawdown
from lib.tables import format_stats_box, format_table


def format_results(result_json: str) -> str:
    """Format BacktestResult JSON into a terminal-friendly display."""
    r = json.loads(result_json)
    sections = []

    # Stats box
    stats = {
        "Total Return": f"{r['total_return_pct']:+.2f}%",
        "Buy & Hold Return": f"{r['buy_and_hold_return_pct']:+.2f}%",
        "Annualized Return": f"{r['annualized_return_pct']:+.2f}%",
        "Sharpe Ratio": f"{r['sharpe_ratio']:.2f}",
        "Max Drawdown": f"{r['max_drawdown_pct']:.2f}%",
        "Win Rate": f"{r['win_rate_pct']:.1f}% ({r['winning_trades']}/{r['winning_trades'] + r['losing_trades']})",
        "Total Trades": str(r["total_trades"]),
        "Final Value": f"${r['final_value']:,.2f}",
    }

    title = f"BACKTEST: {r['ticker']}  |  {r['start_date']} -> {r['end_date']}"
    sections.append(format_stats_box(title, stats))

    # Equity curve
    if r.get("equity_curve"):
        sections.append("")
        sections.append(
            plot_equity_curve(r["equity_dates"], r["equity_curve"], "Equity Curve")
        )

    # Drawdown chart
    if r.get("drawdown_curve"):
        sections.append("")
        sections.append(plot_drawdown(r["equity_dates"], r["drawdown_curve"]))

    # Trade log (first 20)
    if r.get("trades"):
        sections.append("")
        sections.append("--- Trade Log (last 20) ---")
        trades = r["trades"][-20:]
        headers = ["Date", "Action", "Shares", "Price", "Value"]
        rows = [
            [
                t["date"],
                t["action"].upper(),
                f"{t['shares']:.4f}",
                f"${t['price']:.2f}",
                f"${t['value']:,.2f}",
            ]
            for t in trades
        ]
        sections.append(format_table(headers, rows))

    return "\n".join(sections)


if __name__ == "__main__":
    # Force UTF-8 output on Windows
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Read JSON from stdin or file argument
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            result_json = f.read()
    else:
        result_json = sys.stdin.read()

    print(format_results(result_json))
