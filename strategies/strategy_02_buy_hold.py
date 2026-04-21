"""
Strategy 2: 100% S&P 500 — Buy & Hold (Benchmark)
--------------------------------------------------
【策略邏輯】
  目標配置：100% 投入 S&P 500 成分股籃，0% 現金
  規則：不擇時、不再平衡，持有到底

【設計目的】
  作為「純股票基準」——最大化股票曝險的情況下，
  報酬理論上最高，但波動與回撤也最大。
  所有其他策略都應與本策略比較，以衡量「現金緩衝」是否值得。
"""

import numpy as np
import xarray as xr

from strategies.base import (
    load_market_data, calc_cap_weights, build_output, run_stats,
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
    "Stock Universe":     "S&P 500 constituents (market-cap proxy weight, liquid only)",
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

def run(spx_data: xr.DataArray, spx_index: xr.DataArray, cap_weights=None):
    times = spx_data.coords["time"].values
    spx_prices = (
        spx_index.sel(asset="SPX")
        .reindex(time=times, method="ffill")
        .values
    )

    if cap_weights is None:
        cap_weights = calc_cap_weights(spx_data)

    total_weights, flags = compute_total_etf_weight(spx_prices)
    output = build_output(spx_data, total_weights, cap_weights)
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
    cap_weights = calc_cap_weights(spx_data)
    return run(spx_data, spx_index, cap_weights)


if __name__ == "__main__":
    run_backtest()
