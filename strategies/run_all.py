"""
run_all.py — Run all 5 strategies and produce a comparison report
-----------------------------------------------------------------
Data is loaded ONCE and shared across all strategies to avoid
redundant network downloads.

Usage:
    uv run python strategies/run_all.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tabulate import tabulate

from strategies.base import load_market_data, RESULTS_DIR, START_DATE
import strategies.strategy_01_rebalance_10pct   as s1
import strategies.strategy_02_buy_hold          as s2
import strategies.strategy_03_dynamic_threshold as s3
import strategies.strategy_04_monthly_rebalance as s4
import strategies.strategy_05_ma_timing         as s5
import strategies.strategy_06_rebalance_5pct    as s6
import strategies.strategy_07_rebalance_20pct   as s7


# ─────────────────────────────────────────────
# Comparison helpers
# ─────────────────────────────────────────────

METRIC_DEFS = [
    # (key,           display name,               higher_is_better, format)
    ("sharpe_ratio",  "Sharpe Ratio",              True,  ".4f"),
    ("mean_return",   "Annual Return",             True,  ".2%"),
    ("volatility",    "Volatility",                False, ".2%"),
    ("max_drawdown",  "Max Drawdown",              False, ".2%"),
    ("calmar_ratio",  "Calmar Ratio",              True,  ".4f"),
    ("sortino_ratio", "Sortino Ratio",             True,  ".4f"),
    ("avg_turnover",  "Avg Turnover",              False, ".2%"),
    ("total_return",  "Total Return",              True,  ".2%"),
    ("n_rebalances",  "# Rebalances / Switches",   False, "d"),
]


def _fmt(val, fmt):
    if np.isnan(val):
        return "N/A"
    if fmt == "d":
        return str(int(val))
    return format(val, fmt)


def print_comparison(results: list[dict]):
    headers = ["Metric"] + [r["name_short"] for r in results]
    rows = []
    for key, label, higher_is_better, fmt in METRIC_DEFS:
        row = [label]
        vals = [r["metrics"][key] for r in results]
        valid = [v for v in vals if not np.isnan(v)]
        best = (max(valid) if higher_is_better else min(valid)) if valid else None
        for v in vals:
            cell = _fmt(v, fmt)
            if best is not None and not np.isnan(v) and abs(v - best) < 1e-9:
                cell = f"★ {cell}"
            row.append(cell)
        rows.append(row)

    print("\n" + "=" * 70)
    print("STRATEGY COMPARISON SUMMARY")
    print("=" * 70)
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print("(★ = best value for that metric)\n")


def save_comparison_md(results: list[dict], period: str):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = f"{RESULTS_DIR}/comparison.md"

    header_row = "| Metric |" + "".join(f" {r['name_short']} |" for r in results)
    sep_row    = "|--------|" + "".join(" :---: |" for _ in results)

    lines = [
        "# Strategy Comparison",
        "",
        f"**Backtest period:** {period}",
        "",
        "## Performance Summary",
        "",
        header_row,
        sep_row,
    ]

    for key, label, higher_is_better, fmt in METRIC_DEFS:
        vals = [r["metrics"][key] for r in results]
        valid = [v for v in vals if not np.isnan(v)]
        best = (max(valid) if higher_is_better else min(valid)) if valid else None
        row = f"| {label} |"
        for v in vals:
            cell = _fmt(v, fmt)
            if best is not None and not np.isnan(v) and abs(v - best) < 1e-9:
                cell = f"**{cell}** ★"
            row += f" {cell} |"
        lines.append(row)

    lines += ["", "## Strategy Descriptions", ""]
    for r in results:
        lines.append(f"### {r['name']}")
        lines.append("")
        lines.append(r["description"])
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Comparison saved to {path}")


def plot_comparison(results: list[dict]):
    # High-contrast palette for up to 7 strategies
    COLORS = [
        "#1f77b4",  # blue
        "#d62728",  # red
        "#2ca02c",  # green
        "#ff7f0e",  # orange
        "#9467bd",  # purple
        "#8c564b",  # brown
        "#e377c2",  # pink
    ]
    STYLES = ["-", "--", "-.", ":", "-", "--", "-."]

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)

    for i, r in enumerate(results):
        c  = COLORS[i % len(COLORS)]
        ls = STYLES[i % len(STYLES)]
        df = r["stats"].to_pandas()
        equity     = df["equity"].dropna()
        underwater = df["underwater"].dropna()
        axes[0].plot(equity.index, equity.values,
                     label=r["name_short"], color=c, linewidth=1.8, linestyle=ls)
        axes[1].plot(underwater.index, underwater.values,
                     label=r["name_short"], color=c, linewidth=1.5, linestyle=ls)

    axes[0].set_ylabel("Equity (start=1)")
    axes[0].set_title("Equity Curves — All Strategies")
    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_ylabel("Drawdown")
    axes[1].set_title("Drawdown — All Strategies")
    axes[1].legend(loc="lower left", fontsize=8)
    axes[1].grid(True, alpha=0.3)

    for ax in axes:
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(axes[-1].get_xticklabels(), rotation=45, ha="right", fontsize=8)

    plt.tight_layout()
    path = f"{RESULTS_DIR}/comparison_chart.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Comparison chart saved to {path}")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("=" * 70)
    print("RUNNING ALL STRATEGIES")
    print("=" * 70)

    # Load data ONCE
    print("\n[DATA] Loading market data...")
    spx_data, spx_index = load_market_data(START_DATE)

    all_results = []

    strategies = [
        (s1, "S1: 50/50 Threshold 10%"),
        (s2, "S2: Buy & Hold 100%"),
        (s3, "S3: Dynamic 15%/5%"),
        (s4, "S4: Monthly Rebalance"),
        (s5, "S5: MA Timing 200d"),
        (s6, "S6: 50/50 Threshold 5%"),
        (s7, "S7: 50/50 Threshold 20%"),
    ]

    for module, short_name in strategies:
        print(f"\n{'─' * 60}")
        print(f"Running {module.NAME}")
        print("─" * 60)
        _output, _stats, _metrics, _flags = module.run(spx_data, spx_index)
        all_results.append({
            "name":       module.NAME,
            "name_short": short_name,
            "description": module.DESCRIPTION,
            "output":     _output,
            "stats":      _stats,
            "metrics":    _metrics,
            "flags":      _flags,
        })

    # Comparison
    period_start = str(pd.Timestamp(spx_data.time.values[0]) + pd.DateOffset(years=1))[:10]
    period_end   = str(spx_data.time.values[-1])[:10]
    period = f"{period_start} to {period_end}"

    print_comparison(all_results)
    save_comparison_md(all_results, period)
    plot_comparison(all_results)

    print("\nAll done! Results are in the 'results/' directory.")


if __name__ == "__main__":
    main()
