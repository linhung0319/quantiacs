"""
Strategy 4: 50/50 S&P500 + Cash — Calendar Rebalancing (Monthly)
-----------------------------------------------------------------
【策略邏輯】
  目標配置：50% S&P 500 成分股籃 + 50% 現金
  觸發規則：每個月的第一個交易日，無條件再平衡回 50/50
            不管市場漲跌，固定時間執行

【與 S1 的差異】
  S1 是看市場漲跌幅決定是否再平衡（事件驅動）；
  本策略是看月曆決定（時間驅動）。
  兩次再平衡之間同樣讓配置自然漂移。
  目的：測試「固定頻率再平衡」vs「閾值觸發再平衡」哪個更有效。
"""

import numpy as np
import pandas as pd
import xarray as xr

from strategies.base import (
    load_market_data, calc_cap_weights, build_output, run_stats,
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
    "Stock Universe":     "S&P 500 constituents (market-cap proxy weight, liquid only)",
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

def run(spx_data: xr.DataArray, spx_index: xr.DataArray, cap_weights=None):
    times = spx_data.coords["time"].values
    spx_prices = (
        spx_index.sel(asset="SPX")
        .reindex(time=times, method="ffill")
        .values
    )

    if cap_weights is None:
        cap_weights = calc_cap_weights(spx_data)

    total_weights, flags = compute_total_etf_weight(spx_prices, times)
    output = build_output(spx_data, total_weights, cap_weights)
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
    cap_weights = calc_cap_weights(spx_data)
    return run(spx_data, spx_index, cap_weights)


if __name__ == "__main__":
    run_backtest()
