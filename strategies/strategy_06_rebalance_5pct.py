"""
Strategy 6: 50/50 S&P500 + Cash — Threshold Rebalancing (5%)
-------------------------------------------------------------
【策略邏輯】
  與 Strategy 1 完全相同，唯一差異是再平衡閾值改為 ±5%。
  SPX 每次漲跌超過 5% 就再平衡 → 更頻繁（預計約 200 次），
  配置更貼近 50/50 目標，但交易成本也更高。

【與 S1/S7 的比較】
  S6（5%）> S1（10%）> S7（20%）再平衡頻率
  三者一起比較，觀察「閾值鬆緊」對績效的影響。
"""

import xarray as xr
from strategies.base import (
    load_market_data, calc_cap_weights, build_output, run_stats,
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
    "Stock Universe":     "S&P 500 constituents (market-cap proxy weight, liquid only)",
}
THRESHOLD = 0.05


def run(spx_data: xr.DataArray, spx_index: xr.DataArray, cap_weights=None):
    import numpy as np
    times = spx_data.coords["time"].values
    spx_prices = (
        spx_index.sel(asset="SPX")
        .reindex(time=times, method="ffill")
        .values
    )
    if cap_weights is None:
        cap_weights = calc_cap_weights(spx_data)
    total_weights, flags = compute_total_etf_weight(spx_prices, threshold=THRESHOLD)
    output = build_output(spx_data, total_weights, cap_weights)
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
    cap_weights = calc_cap_weights(spx_data)
    return run(spx_data, spx_index, cap_weights)


if __name__ == "__main__":
    run_backtest()
