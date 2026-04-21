"""
Strategy 1: 50/50 S&P500 + Cash — Threshold Rebalancing (10%)
--------------------------------------------------------------
【策略邏輯】
  目標配置：50% 投入 S&P 500 成分股籃，50% 持有現金
  訊號來源：SPX 指數收盤價（S&P 500 指數，市值加權）
  觸發規則：當 SPX 從上次再平衡的價格漲跌超過 ±10%，執行再平衡回 50/50
            兩次再平衡之間，配置比例隨市場自然漂移（不每天交易）

【設計目的】
  測試「閾值式再平衡」的效果：在市場大幅移動時才調整，
  減少不必要的交易成本，同時讓組合不要偏離目標太遠。
  S6（5%）與 S7（20%）是本策略的緊/鬆觸發點變體。
"""

import numpy as np
import xarray as xr

from strategies.base import (
    load_market_data, calc_cap_weights, build_output, run_stats,
    calc_metrics, print_metrics, save_md, plot_strategy,
    RESULTS_DIR, START_DATE,
)

NAME        = "Strategy 1: 50/50 Threshold Rebalancing (10%)"
DESCRIPTION = (
    "Hold 50% in a market-cap-weighted S&P 500 basket and 50% in cash. "
    "Rebalance back to 50/50 whenever the SPX index moves ±10% from "
    "the price at the last rebalance. Between rebalance events the "
    "portfolio drifts freely — no daily trading."
)
PARAMS = {
    "Target Allocation":      "50% stocks / 50% cash",
    "Rebalance Trigger":      "±10% SPX price move from last rebalance",
    "Stock Universe":         "S&P 500 constituents (market-cap proxy weight, liquid only)",
    "Benchmark Signal":       "SPX index (daily close)",
}
THRESHOLD = 0.10


# ─────────────────────────────────────────────
# 核心邏輯（純 NumPy，無 Quantiacs 依賴）
# ─────────────────────────────────────────────

def compute_total_etf_weight(
    spx_prices: np.ndarray,
    threshold: float = THRESHOLD,
    target_alloc: float = 0.50,
) -> tuple[np.ndarray, np.ndarray]:
    """
    計算每個交易日的「股票總配置比例」。

    兩次再平衡之間的漂移公式：
        w[t] = target × r / (target × r + (1 - target))
        其中 r = spx[t] / spx[上次再平衡時的價格]

    這個公式模擬的是：上次再平衡後固定股數不動，
    股票部位的市值會隨 SPX 漲跌而改變，現金部位則不變。
    因此配置比例會自然漂移。

    當 |r - 1| >= threshold 時（即 SPX 漲跌超過閾值），
    觸發再平衡：配置比例強制拉回 target_alloc，並重設基準價格。

    回傳：
      weights : shape (n,)，每日股票總配置比例（0~1）
      flags   : shape (n,)，bool，True 表示當日觸發再平衡
    """
    n = len(spx_prices)
    weights = np.zeros(n)
    flags   = np.zeros(n, dtype=bool)
    last_p  = spx_prices[0]   # 記錄上次再平衡時的 SPX 價格

    for i in range(n):
        p = spx_prices[i]
        if np.isnan(p) or p <= 0:
            # SPX 資料缺漏時，維持前一天的配置
            weights[i] = weights[i - 1] if i > 0 else target_alloc
            continue
        r = p / last_p   # 相對於上次再平衡的價格變化倍數
        if abs(r - 1.0) >= threshold:
            # 觸發再平衡：拉回目標配置，重設基準價格
            weights[i] = target_alloc
            flags[i]   = True
            last_p     = p
        else:
            # 未觸發：讓配置自然漂移
            weights[i] = (target_alloc * r) / (target_alloc * r + (1.0 - target_alloc))

    return weights, flags


# ─────────────────────────────────────────────
# 策略執行入口
# ─────────────────────────────────────────────

def run(spx_data: xr.DataArray, spx_index: xr.DataArray, cap_weights=None):
    """
    在已載入的資料上執行策略，回傳 (output, stats, metrics, flags)。

    流程：
    1. 從 spx_index 取出 SPX 每日收盤價，對齊到 spx_data 的時間軸
    2. 若未傳入 cap_weights，自行計算市值代理權重
    3. compute_total_etf_weight：決定每日「要投多少比例在股票」
    4. build_output：將股票比例 × 市值代理權重 → 各股票的最終權重
    5. run_stats：清理輸出並計算績效統計
    """
    times = spx_data.coords["time"].values
    # 將 SPX 指數價格對齊到 spx_data 的日期（前向填充缺漏交易日）
    spx_prices = (
        spx_index.sel(asset="SPX")
        .reindex(time=times, method="ffill")
        .values
    )

    if cap_weights is None:
        cap_weights = calc_cap_weights(spx_data)

    total_weights, flags = compute_total_etf_weight(spx_prices, THRESHOLD)
    output = build_output(spx_data, total_weights, cap_weights)
    stats, period_start = run_stats(spx_data, output)

    period = f"{period_start} to {str(spx_data.time.values[-1])[:10]}"
    metrics = calc_metrics(stats, flags)
    print_metrics(metrics, period)

    save_md(NAME, DESCRIPTION, PARAMS, metrics, period,
            f"{RESULTS_DIR}/strategy_01_results.md")
    plot_strategy(NAME, spx_data, spx_index, output, stats, flags,
                  f"{RESULTS_DIR}/strategy_01_chart.png")

    return output, stats, metrics, flags


def run_backtest():
    """獨立執行入口（直接跑單一策略時使用）"""
    print("=" * 60)
    print(NAME)
    print("=" * 60)
    spx_data, spx_index = load_market_data(START_DATE)
    cap_weights = calc_cap_weights(spx_data)
    return run(spx_data, spx_index, cap_weights)


if __name__ == "__main__":
    run_backtest()
