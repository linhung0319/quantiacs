"""
Strategy 5: MA Market Timing (200-day Moving Average)
------------------------------------------------------
【策略邏輯】
  目標配置：二元切換（全倉股票 or 全部現金）
  訊號來源：SPX 指數 200 日簡單移動平均線（SMA）
  規則：
    SPX 收盤 > 200 日 MA（多頭趨勢）→ 持有 100% S&P 500 成分股籃
    SPX 收盤 < 200 日 MA（空頭趨勢）→ 全部轉為現金
  執行時機：當日收盤訊號，次日開盤執行（避免前視偏差）

【與其他策略的差異】
  S1/S3/S4/S6/S7 維持 50/50 配置，做小幅調整；
  本策略是「all-in / all-out」，波動度和潛在報酬都更高。
  前 200 個交易日（~10 個月）因 MA 尚未成形，保守持現金。
"""

import numpy as np
import xarray as xr

from strategies.base import (
    load_market_data, calc_cap_weights, build_output, run_stats,
    calc_metrics, print_metrics, save_md, plot_strategy,
    RESULTS_DIR, START_DATE,
)

NAME        = "Strategy 5: MA Market Timing (200-day)"
DESCRIPTION = (
    "Use the SPX 200-day simple moving average as a market regime filter. "
    "When SPX is above the 200d MA (bullish trend), hold 100% in an "
    "equal-weight S&P 500 basket. When SPX is below (bearish), move "
    "entirely to cash. Signal is computed at close and executed at the "
    "next open. Unlike Strategies 1-4 there is no fixed 50/50 split — "
    "this is a binary 'risk-on / risk-off' approach."
)
PARAMS = {
    "Bull Allocation":    "100% stocks (SPX > 200d MA)",
    "Bear Allocation":    "0% stocks / 100% cash (SPX < 200d MA)",
    "MA Period":          "200 trading days (~10 months)",
    "Signal":             "SPX daily close vs. 200-day SMA",
    "Execution":          "Signal at close t → trade at open t+1",
    "Stock Universe":     "S&P 500 constituents (market-cap proxy weight, liquid only)",
}

MA_PERIOD = 200


# ─────────────────────────────────────────────
# 核心邏輯
# ─────────────────────────────────────────────

def compute_total_etf_weight(
    spx_prices: np.ndarray,
    ma_period: int = MA_PERIOD,
) -> tuple[np.ndarray, np.ndarray]:
    """
    根據 SPX 與 200 日移動平均線的關係，決定每日配置（1.0 或 0.0）。

    - SPX > 200d MA → weights[i] = 1.0（全部押股票）
    - SPX < 200d MA → weights[i] = 0.0（全部持現金）
    - 前 200 天 MA 資料不足 → 保守持現金（0.0）

    flags 標記每次「多頭↔空頭」的切換日（即訊號反轉點）。
    """
    n = len(spx_prices)
    weights = np.zeros(n)
    flags   = np.zeros(n, dtype=bool)
    prev_regime = None   # 追蹤上一個交易日的市場狀態

    for i in range(n):
        p = spx_prices[i]
        if np.isnan(p) or p <= 0:
            weights[i] = weights[i - 1] if i > 0 else 0.0
            continue

        if i < ma_period - 1:
            # MA 尚未有足夠歷史資料，保守持現金
            weights[i] = 0.0
            regime = "bear"
        else:
            # 計算 200 日均值（包含當日）
            ma = float(np.nanmean(spx_prices[i - ma_period + 1 : i + 1]))
            regime = "bull" if p > ma else "bear"
            weights[i] = 1.0 if regime == "bull" else 0.0

        # 偵測市場狀態切換，標記為 rebalance flag
        if prev_regime is not None and regime != prev_regime:
            flags[i] = True
        prev_regime = regime

    return weights, flags


# ─────────────────────────────────────────────
# 策略執行入口
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
            f"{RESULTS_DIR}/strategy_05_results.md")
    plot_strategy(NAME, spx_data, spx_index, output, stats, flags,
                  f"{RESULTS_DIR}/strategy_05_chart.png")

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
