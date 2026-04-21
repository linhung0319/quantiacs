"""
Strategy 3: 50/50 S&P500 + Cash — Dynamic Threshold (Bull/Bear Adaptive)
-------------------------------------------------------------------------
【策略邏輯】
  目標配置：50% S&P 500 成分股籃 + 50% 現金
  訊號來源：SPX 200 日移動平均線（判斷多空市場）
  觸發規則（依市場環境動態調整）：
    多頭市場（SPX > 200 日 MA）→ 閾值 ±15%（讓趨勢跑，減少交易）
    空頭市場（SPX < 200 日 MA）→ 閾值 ±5%（更積極防守，早點再平衡）

【與 S1 的差異】
  S1 固定使用 ±10% 閾值；本策略在多/空頭間自動切換 15%/5%，
  試圖在牛市減少摩擦、熊市加強防守。
"""

import numpy as np
import xarray as xr

from strategies.base import (
    load_market_data, calc_cap_weights, build_output, run_stats,
    calc_metrics, print_metrics, save_md, plot_strategy,
    RESULTS_DIR, START_DATE,
)

NAME        = "Strategy 3: 50/50 Dynamic Threshold (Bull 15% / Bear 5%)"
DESCRIPTION = (
    "Same 50/50 allocation as Strategy 1, but the rebalance trigger adapts "
    "to the market regime detected by the 200-day moving average of SPX:\n"
    "- Bull market (SPX > 200d MA): rebalance only when SPX moves ±15% "
    "(let winners run longer).\n"
    "- Bear market (SPX < 200d MA): rebalance at ±5% "
    "(act more defensively to limit drawdown)."
)
PARAMS = {
    "Target Allocation":      "50% stocks / 50% cash",
    "Bull Market Threshold":  "±15% (SPX > 200-day MA)",
    "Bear Market Threshold":  "±5%  (SPX < 200-day MA)",
    "Regime Signal":          "SPX 200-day simple moving average",
    "Stock Universe":         "S&P 500 constituents (market-cap proxy weight, liquid only)",
}

BULL_THRESHOLD = 0.15
BEAR_THRESHOLD = 0.05
MA_PERIOD      = 200


# ─────────────────────────────────────────────
# Core logic
# ─────────────────────────────────────────────

def compute_total_etf_weight(
    spx_prices: np.ndarray,
    bull_threshold: float = BULL_THRESHOLD,
    bear_threshold: float = BEAR_THRESHOLD,
    ma_period: int = MA_PERIOD,
    target_alloc: float = 0.50,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Drift-based rebalancing with regime-adaptive threshold.
    """
    n = len(spx_prices)
    weights = np.zeros(n)
    flags   = np.zeros(n, dtype=bool)
    last_p  = spx_prices[0]

    # Compute 200-day MA (vectorized for speed, then iterate for state)
    ma = np.full(n, np.nan)
    for i in range(ma_period - 1, n):
        ma[i] = np.nanmean(spx_prices[i - ma_period + 1 : i + 1])

    for i in range(n):
        p = spx_prices[i]
        if np.isnan(p) or p <= 0:
            weights[i] = weights[i - 1] if i > 0 else target_alloc
            continue

        # Choose threshold based on regime
        if np.isnan(ma[i]):
            threshold = bear_threshold          # conservative before MA is ready
        else:
            threshold = bull_threshold if p > ma[i] else bear_threshold

        r = p / last_p
        if abs(r - 1.0) >= threshold:
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

    total_weights, flags = compute_total_etf_weight(spx_prices)
    output = build_output(spx_data, total_weights, cap_weights)
    stats, period_start = run_stats(spx_data, output)

    period = f"{period_start} to {str(spx_data.time.values[-1])[:10]}"
    metrics = calc_metrics(stats, flags)
    print_metrics(metrics, period)

    save_md(NAME, DESCRIPTION, PARAMS, metrics, period,
            f"{RESULTS_DIR}/strategy_03_results.md")
    plot_strategy(NAME, spx_data, spx_index, output, stats, flags,
                  f"{RESULTS_DIR}/strategy_03_chart.png")

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
