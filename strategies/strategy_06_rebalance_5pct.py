"""
Strategy 6: 50/50 S&P500 + Cash — Threshold Rebalancing (5%)
-------------------------------------------------------------
Same as Strategy 1 but with a tighter ±5% trigger.
Rebalances more frequently → closer to target allocation,
but incurs higher trading costs.
"""

import xarray as xr
from strategies.base import (
    load_market_data, build_output, run_stats,
    calc_metrics, print_metrics, save_md, plot_strategy,
    RESULTS_DIR, START_DATE,
)
from strategies.strategy_01_rebalance_10pct import compute_total_etf_weight

NAME        = "Strategy 6: 50/50 Threshold Rebalancing (5%)"
DESCRIPTION = (
    "Identical to Strategy 1 but with a tighter ±5% rebalance trigger. "
    "The portfolio rebalances back to 50/50 more frequently, keeping the "
    "allocation closer to target at the cost of more trades."
)
PARAMS = {
    "Target Allocation":  "50% stocks / 50% cash",
    "Rebalance Trigger":  "±5% SPX price move from last rebalance",
    "Stock Universe":     "S&P 500 constituents (equal-weight, liquid only)",
}
THRESHOLD = 0.05


def run(spx_data: xr.DataArray, spx_index: xr.DataArray):
    import numpy as np
    times = spx_data.coords["time"].values
    spx_prices = (
        spx_index.sel(asset="SPX")
        .reindex(time=times, method="ffill")
        .values
    )
    total_weights, flags = compute_total_etf_weight(spx_prices, threshold=THRESHOLD)
    output = build_output(spx_data, total_weights)
    stats, period_start = run_stats(spx_data, output)

    period = f"{period_start} to {str(spx_data.time.values[-1])[:10]}"
    metrics = calc_metrics(stats, flags)
    print_metrics(metrics, period)

    save_md(NAME, DESCRIPTION, PARAMS, metrics, period,
            f"{RESULTS_DIR}/strategy_06_results.md")
    plot_strategy(NAME, spx_data, spx_index, output, stats, flags,
                  f"{RESULTS_DIR}/strategy_06_chart.png")

    return output, stats, metrics, flags


def run_backtest():
    print("=" * 60)
    print(NAME)
    print("=" * 60)
    spx_data, spx_index = load_market_data(START_DATE)
    return run(spx_data, spx_index)


if __name__ == "__main__":
    run_backtest()
