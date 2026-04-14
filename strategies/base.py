"""
strategies/base.py
------------------
Shared utilities for all S&P 500 backtest strategies.
"""

import os
from dotenv import load_dotenv
load_dotenv()

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("Agg")          # headless rendering — no GUI window needed
import matplotlib.pyplot as plt

import qnt.data as qndata
import qnt.stats as qnstats
import qnt.output as qnout

START_DATE = "2006-01-01"
RESULTS_DIR = "results"

# ─────────────────────────────────────────────────────────────
# Data loading (shared across all strategies)
# ─────────────────────────────────────────────────────────────

def load_market_data(start_date: str = START_DATE):
    """Load SPX500 constituent stocks + SPX index. Returns (spx_data, spx_index)."""
    print(f"  Loading SPX500 stocks ({start_date} onwards)...")
    spx_data = qndata.stocks_load_spx_data(min_date=start_date)
    print(f"  Loaded {len(spx_data.asset)} stocks, {len(spx_data.time)} trading days")

    print("  Loading SPX index price...")
    spx_index = qndata.index_load_data(assets=["SPX"], min_date=start_date)
    print(f"  SPX: {str(spx_index.time.values[0])[:10]} ~ {str(spx_index.time.values[-1])[:10]}")

    return spx_data, spx_index


# ─────────────────────────────────────────────────────────────
# Output building
# ─────────────────────────────────────────────────────────────

def build_output(
    spx_data: xr.DataArray,
    total_weights: np.ndarray,
) -> xr.DataArray:
    """
    Distribute total_weights[t] equally across liquid stocks at each time t.
    Returns Quantiacs-format weight DataArray.
    """
    close = spx_data.sel(field="close")
    is_liquid = spx_data.sel(field="is_liquid").values
    output_np = np.zeros_like(close.values)

    for i in range(len(spx_data.time)):
        liquid_mask = is_liquid[i] == 1
        n_liquid = liquid_mask.sum()
        if n_liquid > 0:
            output_np[i, liquid_mask] = total_weights[i] / n_liquid

    return xr.DataArray(output_np, dims=close.dims, coords=close.coords)


def run_stats(
    spx_data: xr.DataArray,
    output: xr.DataArray,
    stats_start: str | None = None,
) -> xr.DataArray:
    """Clean output and compute stats. stats_start defaults to 1 year after data start."""
    output = qnout.clean(output, spx_data)
    if stats_start is None:
        stats_start = str(
            pd.Timestamp(spx_data.time.values[0]) + pd.DateOffset(years=1)
        )[:10]
    return qnstats.calc_stat(spx_data, output.sel(time=slice(stats_start, None))), stats_start


# ─────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────

def calc_metrics(
    stats: xr.DataArray,
    rebalance_flags: np.ndarray | None = None,
) -> dict:
    """
    Extract and compute comparison metrics from calc_stat output.

    Metrics included:
    - Sharpe Ratio    : annualized risk-adjusted return (primary metric)
    - Annual Return   : geometric mean annualized return
    - Volatility      : annualized std dev of daily returns
    - Max Drawdown    : worst peak-to-trough decline
    - Calmar Ratio    : Annual Return / |Max Drawdown|
    - Sortino Ratio   : like Sharpe but uses only downside volatility
    - Avg Turnover    : average daily portfolio turnover
    - Total Return    : cumulative return over the full period
    - # Rebalances    : number of rebalancing events (proxy for trading cost)
    """
    df = stats.to_pandas()
    last = df.iloc[-1]

    mean_ret = float(last.get("mean_return", np.nan))
    vol      = float(last.get("volatility", np.nan))
    max_dd   = float(last.get("max_drawdown", np.nan))
    sr       = float(last.get("sharpe_ratio", np.nan))
    turnover = float(last.get("avg_turnover", np.nan))

    equity = df["equity"].dropna()
    total_return = float((equity.iloc[-1] / equity.iloc[0]) - 1.0)

    calmar = mean_ret / abs(max_dd) if max_dd and not np.isnan(max_dd) and max_dd != 0 else np.nan

    rr = df["relative_return"].dropna()
    down = rr[rr < 0]
    sortino_denom = down.std() * np.sqrt(252) if len(down) > 0 else np.nan
    sortino = mean_ret / sortino_denom if sortino_denom and sortino_denom != 0 else np.nan

    n_rebalances = int(rebalance_flags.sum()) if rebalance_flags is not None else 0

    return {
        "sharpe_ratio":  sr,
        "mean_return":   mean_ret,
        "volatility":    vol,
        "max_drawdown":  max_dd,
        "calmar_ratio":  calmar,
        "sortino_ratio": sortino,
        "avg_turnover":  turnover,
        "total_return":  total_return,
        "n_rebalances":  n_rebalances,
    }


def print_metrics(metrics: dict, period: str = ""):
    rows = [
        ("Sharpe Ratio",          f"{metrics['sharpe_ratio']:.4f}"),
        ("Annual Return",         f"{metrics['mean_return']:.2%}"),
        ("Volatility",            f"{metrics['volatility']:.2%}"),
        ("Max Drawdown",          f"{metrics['max_drawdown']:.2%}"),
        ("Calmar Ratio",          f"{metrics['calmar_ratio']:.4f}"),
        ("Sortino Ratio",         f"{metrics['sortino_ratio']:.4f}"),
        ("Avg Turnover",          f"{metrics['avg_turnover']:.2%}"),
        ("Total Return",          f"{metrics['total_return']:.2%}"),
        ("# Rebalances",          str(metrics['n_rebalances'])),
    ]
    if period:
        print(f"\n--- Results ({period}) ---")
    for label, val in rows:
        print(f"  {label:<28}: {val}")


# ─────────────────────────────────────────────────────────────
# Markdown output
# ─────────────────────────────────────────────────────────────

def save_md(
    strategy_name: str,
    description: str,
    params: dict,
    metrics: dict,
    period: str,
    save_path: str,
):
    """Save backtest results as a Markdown file."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    lines = [
        f"# {strategy_name}",
        "",
        "## Description",
        "",
        description,
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
    ]
    for k, v in params.items():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        f"## Backtest Results ({period})",
        "",
        "| Metric | Value | Description |",
        "|--------|-------|-------------|",
        f"| Sharpe Ratio | {metrics['sharpe_ratio']:.4f} | Risk-adjusted return (higher is better) |",
        f"| Annual Return | {metrics['mean_return']:.2%} | Geometric annualized return |",
        f"| Volatility | {metrics['volatility']:.2%} | Annualized std dev of daily returns |",
        f"| Max Drawdown | {metrics['max_drawdown']:.2%} | Worst peak-to-trough loss |",
        f"| Calmar Ratio | {metrics['calmar_ratio']:.4f} | Annual Return / |Max Drawdown| |",
        f"| Sortino Ratio | {metrics['sortino_ratio']:.4f} | Sharpe using downside volatility only |",
        f"| Avg Turnover | {metrics['avg_turnover']:.2%} | Average daily portfolio turnover |",
        f"| Total Return | {metrics['total_return']:.2%} | Cumulative return over full period |",
        f"| # Rebalances | {metrics['n_rebalances']} | Number of rebalancing events |",
        "",
    ]

    with open(save_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Results saved to {save_path}")


# ─────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────

def plot_strategy(
    strategy_title: str,
    spx_data: xr.DataArray,
    spx_index: xr.DataArray,
    output: xr.DataArray,
    stats: xr.DataArray,
    rebalance_flags: np.ndarray | None,
    save_path: str,
):
    """Standard 3-panel plot: equity curve, SPX + rebalance points, allocation."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    df_stats = stats.to_pandas()
    times = spx_data.time.values

    total_etf_weight = output.sum(dim="asset").to_pandas()

    spx_price = (
        spx_index.sel(asset="SPX")
        .reindex(time=spx_data.time, method="ffill")
        .to_pandas()
    )
    spx_norm = spx_price / spx_price.iloc[0]

    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    fig.suptitle(strategy_title, fontsize=13)

    # Panel 1: Equity curve
    ax1 = axes[0]
    equity = df_stats["equity"].dropna()
    ax1.plot(equity.index, equity.values, color="steelblue", linewidth=1.5, label="Strategy Equity")
    ax1.plot(spx_norm.index, spx_norm.values, color="gray", linewidth=1,
             alpha=0.6, linestyle="--", label="SPX (normalized)")
    ax1.set_ylabel("Equity (start=1)")
    ax1.set_title("Equity Curve")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Panel 2: SPX + rebalance points
    ax2 = axes[1]
    ax2.plot(spx_price.index, spx_price.values, color="darkorange",
             linewidth=1, alpha=0.8, label="SPX Close")
    if rebalance_flags is not None and rebalance_flags.sum() > 0:
        rb_dates = pd.to_datetime(times[rebalance_flags])
        rb_prices = spx_price.reindex(rb_dates, method="nearest")
        ax2.scatter(rb_prices.index, rb_prices.values, color="red", s=25,
                    zorder=5, label=f"Rebalance ({rebalance_flags.sum()} times)")
    ax2.set_ylabel("SPX Level")
    ax2.set_title("SPX Index & Rebalance Points")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    # Panel 3: Allocation
    ax3 = axes[2]
    ax3.fill_between(total_etf_weight.index, total_etf_weight.values,
                     alpha=0.55, color="steelblue", label="S&P 500")
    cash = (1 - total_etf_weight).clip(lower=0)
    ax3.fill_between(total_etf_weight.index, cash.values, total_etf_weight.values,
                     alpha=0.3, color="lightgray", label="Cash")
    ax3.axhline(0.5, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
    ax3.set_ylim(0, 1.05)
    ax3.set_ylabel("Allocation")
    ax3.set_title("Equity / Cash Allocation")
    ax3.legend(loc="upper left")
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Chart saved to {save_path}")
