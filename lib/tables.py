"""Terminal table formatting using tabulate."""

from typing import Optional

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def format_table(
    headers: list[str],
    rows: list[list],
    fmt: str = "simple",
) -> str:
    """Format data as a terminal table.

    Args:
        headers: Column headers
        rows: List of rows (each row is a list of values)
        fmt: Table format (simple, grid, pipe, github)
    """
    if HAS_TABULATE:
        return tabulate(rows, headers=headers, tablefmt=fmt, floatfmt=".2f")

    # Fallback: simple aligned columns
    all_rows = [headers] + rows
    col_widths = [
        max(len(str(row[i])) for row in all_rows) for i in range(len(headers))
    ]

    lines = []
    for row in all_rows:
        line = "  ".join(str(v).ljust(w) for v, w in zip(row, col_widths))
        lines.append(line)
        if row == headers:
            lines.append("  ".join("─" * w for w in col_widths))

    return "\n".join(lines)


def format_stats_box(title: str, stats: dict[str, str]) -> str:
    """Format key-value stats in a bordered box.

    Args:
        title: Box title
        stats: Dict of label -> value
    """
    max_label = max(len(k) for k in stats)
    max_value = max(len(str(v)) for v in stats.values())
    inner_width = max(max_label + max_value + 4, len(title) + 4)

    lines = [
        "╔" + "═" * inner_width + "╗",
        "║" + title.center(inner_width) + "║",
        "╠" + "═" * inner_width + "╣",
    ]

    for label, value in stats.items():
        padding = inner_width - len(label) - len(str(value)) - 4
        lines.append(f"║  {label}{' ' * padding}{value}  ║")

    lines.append("╚" + "═" * inner_width + "╝")
    return "\n".join(lines)
