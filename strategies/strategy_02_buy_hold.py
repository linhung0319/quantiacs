"""
Strategy 2: 100% S&P 500 — Buy & Hold (Benchmark)
--------------------------------------------------
Allocation : 100% in equal-weight S&P 500 basket, 0% cash
Rule       : No market-timing, no rebalancing between cash and stocks.
             Serves as the pure-equity benchmark to compare all other
             strategies against.
"""

import numpy as np
import xarray as xr

from strategies.base import (
    load_market_data, build_output, run_stats,
    calc_metrics, print_metrics, save_md, plot_strategy,
    RESULTS_DIR, START_DATE,
)

NAME        = "Strategy 2: 100% S&P500 Buy & Hold (Benchmark)"
DESCRIPTION = (
    "Hold 100% of capital in an equal-weight S&P 500 basket at all times. "
    "No cash buffer, no market-timing, no threshold rebalancing. "
    "This represents the maximum equity exposure and acts as the benchmark "
    "against which risk-managed strategies are evaluated."
)
PARAMS = {
    "Target Allocation":  "100% stocks / 0% cash",
    "Rebalance Rule":     "None (stocks rebalanced to equal-weight daily within index)",
    "Stock Universe":     "S&P 500 constituents (equal-weight, liquid only)",
}


# ─────────────────────────────────────────────
# Core logic
# ─────────────────────────────────────────────

def compute_total_etf_weight(spx_prices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """100% equity at all times. No rebalance events."""
    weights = np.ones(len(spx_prices))
    flags   = np.zeros(len(spx_prices), dtype=bool)
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

    total_weights, flags = compute_total_etf_weight(spx_prices)
    output = build_output(spx_data, total_weights)
    stats, period_start = run_stats(spx_data, output)

    period = f"{period_start} to {str(spx_data.time.values[-1])[:10]}"
    metrics = calc_metrics(stats, flags)
    print_metrics(metrics, period)

    save_md(NAME, DESCRIPTION, PARAMS, metrics, period,
            f"{RESULTS_DIR}/strategy_02_results.md")
    plot_strategy(NAME, spx_data, spx_index, output, stats, flags,
                  f"{RESULTS_DIR}/strategy_02_chart.png")

    return output, stats, metrics, flags


def run_backtest():
    print("=" * 60)
    print(NAME)
    print("=" * 60)
    spx_data, spx_index = load_market_data(START_DATE)
    return run(spx_data, spx_index)


if __name__ == "__main__":
    run_backtest()
