"""ASCII chart generation using plotext."""

from typing import Optional

try:
    import plotext as plt

    HAS_PLOTEXT = True
except ImportError:
    HAS_PLOTEXT = False


def plot_equity_curve(
    dates: list,
    values: list,
    title: str = "Equity Curve",
    width: int = 70,
    height: int = 15,
) -> str:
    """Generate ASCII equity curve chart.

    Returns the chart as a string. Falls back to simple text if plotext unavailable.
    """
    if not HAS_PLOTEXT:
        return _simple_text_chart(values, title)

    plt.clear_figure()
    plt.plot_size(width, height)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Portfolio Value ($)")

    # Convert dates to numeric indices for plotext
    x = list(range(len(values)))
    plt.plot(x, values)

    # Add start/end date labels
    if dates:
        start = str(dates[0])[:10]
        end = str(dates[-1])[:10]
        plt.xlabel(f"{start} -> {end}")

    return plt.build()


def plot_drawdown(
    dates: list,
    drawdown_pct: list,
    width: int = 70,
    height: int = 10,
) -> str:
    """Generate ASCII drawdown chart."""
    if not HAS_PLOTEXT:
        return _simple_text_chart(drawdown_pct, "Drawdown (%)")

    plt.clear_figure()
    plt.plot_size(width, height)
    plt.title("Drawdown")
    plt.ylabel("Drawdown (%)")

    x = list(range(len(drawdown_pct)))
    plt.plot(x, drawdown_pct)

    return plt.build()


def plot_monthly_returns(
    months: list[str],
    returns: list[float],
    width: int = 70,
    height: int = 12,
) -> str:
    """Generate ASCII bar chart of monthly returns."""
    if not HAS_PLOTEXT:
        lines = ["Monthly Returns:"]
        for m, r in zip(months, returns):
            bar = "#" * max(1, int(abs(r) * 2))
            sign = "+" if r >= 0 else "-"
            lines.append(f"  {m}: {sign}{abs(r):.1f}% {bar}")
        return "\n".join(lines)

    plt.clear_figure()
    plt.plot_size(width, height)
    plt.title("Monthly Returns (%)")
    plt.bar(months, returns)

    return plt.build()


def _simple_text_chart(values: list, title: str) -> str:
    """Fallback text-based chart when plotext is not available."""
    if not values:
        return f"{title}: No data"

    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val if max_val != min_val else 1

    chart_width = 50
    lines = [f"  {title}", "  " + "─" * (chart_width + 10)]

    # Sample ~20 points from the data
    step = max(1, len(values) // 20)
    for i in range(0, len(values), step):
        v = values[i]
        bar_len = int((v - min_val) / val_range * chart_width)
        lines.append(f"  {'#' * bar_len} ${v:,.0f}")

    lines.append(f"  Min: ${min_val:,.0f}  Max: ${max_val:,.0f}")
    return "\n".join(lines)
