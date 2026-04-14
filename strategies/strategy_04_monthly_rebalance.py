"""
Strategy 4: 50/50 S&P500 + Cash — Calendar Rebalancing (Monthly)
-----------------------------------------------------------------
Allocation : 50% S&P 500 + 50% Cash
Rule       : Rebalance back to 50/50 on the first trading day of each
             calendar month, regardless of market movement.
             This tests whether time-based rebalancing beats threshold-based.
"""

import numpy as np
import pandas as pd
import xarray as xr

from strategies.base import (
    load_market_data, build_output, run_stats,
    calc_metrics, print_metrics, save_md, plot_strategy,
    RESULTS_DIR, START_DATE,
)

NAME        = "Strategy 4: 50/50 Monthly Calendar Rebalancing"
DESCRIPTION = (
    "Hold 50% in an equal-weight S&P 500 basket and 50% in cash. "
    "Rebalance back to 50/50 on the first trading day of every calendar month, "
    "regardless of how much the market has moved. "
    "Compares fixed-calendar rebalancing against threshold-based approaches."
)
PARAMS = {
    "Target Allocation":  "50% stocks / 50% cash",
    "Rebalance Schedule": "First trading day of each calendar month",
    "Stock Universe":     "S&P 500 constituents (equal-weight, liquid only)",
}


# ─────────────────────────────────────────────
# Core logic
# ─────────────────────────────────────────────

def compute_total_etf_weight(
    spx_prices: np.ndarray,
    trading_dates: np.ndarray,
    target_alloc: float = 0.50,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Drift between rebalances; force rebalance on month-start trading days.
    """
    n = len(spx_prices)
    weights = np.zeros(n)
    flags   = np.zeros(n, dtype=bool)
    last_p  = spx_prices[0]

    dates = pd.DatetimeIndex(trading_dates)

    for i in range(n):
        p = spx_prices[i]
        if np.isnan(p) or p <= 0:
            weights[i] = weights[i - 1] if i > 0 else target_alloc
            continue

        # First trading day of the month: month changes from prior day
        is_month_start = (i == 0) or (dates[i].month != dates[i - 1].month)

        r = p / last_p
        if is_month_start:
            weights[i] = target_alloc
            flags[i]   = True
            last_p     = p
        else:
            weights[i] = (target_alloc * r) / (target_alloc * r + (1.0 - target_alloc))

    return weights, flags


# ─────────────────────────────────────────────
# Strategy runner
# ─────────────────────────────────────────────

def run(spx_data: xr.DataArray, spx_index: xr.DataArray):
    times = spx_data.coords["time"].values
    spx_prices = (
        spx_index.sel(asset="SPX")
        .reindex(time=times, method="ffill")
        .values
    )

    total_weights, flags = compute_total_etf_weight(spx_prices, times)
    output = build_output(spx_data, total_weights)
    stats, period_start = run_stats(spx_data, output)

    period = f"{period_start} to {str(spx_data.time.values[-1])[:10]}"
    metrics = calc_metrics(stats, flags)
    print_metrics(metrics, period)

    save_md(NAME, DESCRIPTION, PARAMS, metrics, period,
            f"{RESULTS_DIR}/strategy_04_results.md")
    plot_strategy(NAME, spx_data, spx_index, output, stats, flags,
                  f"{RESULTS_DIR}/strategy_04_chart.png")

    return output, stats, metrics, flags


def run_backtest():
    print("=" * 60)
    print(NAME)
    print("=" * 60)
    spx_data, spx_index = load_market_data(START_DATE)
    return run(spx_data, spx_index)


if __name__ == "__main__":
    run_backtest()
