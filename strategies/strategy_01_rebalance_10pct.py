"""
策略一：50/50 定期再平衡（10% 觸發閾值）
-------------------------------------------
配置：50% 現金 + 50% S&P 500（以 SPX500 成分股等權重籃子模擬 ETF）
訊號：使用 SPX 指數價格衡量市場漲跌幅度
規則：當 SPX 指數從上次再平衡後漲跌 ±10%，執行再平衡回到 50/50。
      在兩次再平衡之間，持倉總權重隨指數漂移，不對現金/股票做增減。

API Key 設定：在專案根目錄的 .env 檔案中填入 API_KEY
"""

import os
from dotenv import load_dotenv
load_dotenv()  # 讀取 .env 中的 API_KEY

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

import qnt.data as qndata
import qnt.stats as qnstats
import qnt.output as qnout

# ─────────────────────────────────────────────
# 參數
# ─────────────────────────────────────────────
START_DATE = "2006-01-01"   # 回測起始日（SPX500 資料最早可到 ~2000 年）
LOOKBACK_DAYS = 365         # 載入資料時額外往前的緩衝天數
REBALANCE_THRESHOLD = 0.10  # 再平衡觸發幅度：±10%


# ─────────────────────────────────────────────
# 核心策略邏輯（純計算，不依賴 qnt）
# ─────────────────────────────────────────────
def compute_total_etf_weight(
    spx_prices: np.ndarray,
    threshold: float = 0.10,
    target_alloc: float = 0.50,
) -> tuple[np.ndarray, np.ndarray]:
    """
    根據 SPX 指數價格，計算每日股票部位的「總目標權重」。

    在兩次再平衡之間，總權重隨市場漂移（持股不動）：
        total_weight[t] = r / (r + 1) * 1
        其中 r = spx[t] / spx[last_rebalance]，
        （假設初始 50% 股票 / 50% 現金，cash 不增值）

    當 |r - 1| >= threshold 時觸發再平衡，total_weight 重設為 target_alloc（0.5）。

    Returns
    -------
    total_weights    : 每日「股票部位佔總資產」的目標比例，shape (T,)
    rebalance_flags  : bool 陣列，True 表示當天觸發再平衡，shape (T,)
    """
    n = len(spx_prices)
    total_weights = np.zeros(n)
    rebalance_flags = np.zeros(n, dtype=bool)

    last_rebalance_price = spx_prices[0]

    for i in range(n):
        price = spx_prices[i]
        if np.isnan(price) or price <= 0:
            total_weights[i] = total_weights[i - 1] if i > 0 else target_alloc
            continue

        r = price / last_rebalance_price

        if abs(r - 1.0) >= threshold:
            # 觸發再平衡：回到 50/50
            total_weights[i] = target_alloc
            rebalance_flags[i] = True
            last_rebalance_price = price
        else:
            # 持股不動：計算漂移後的股票部位比例
            # ETF 市值（以上次再平衡後的相對值）= target_alloc * r
            # 現金市值（不增值）               = (1 - target_alloc)
            # 股票佔總資產比例                  = target_alloc * r / (target_alloc * r + (1 - target_alloc))
            total_weights[i] = (target_alloc * r) / (target_alloc * r + (1.0 - target_alloc))

    return total_weights, rebalance_flags


# ─────────────────────────────────────────────
# Quantiacs 策略函數
# ─────────────────────────────────────────────
def strategy(
    spx_data: xr.DataArray,
    spx_index: xr.DataArray,
    threshold: float = REBALANCE_THRESHOLD,
) -> tuple[xr.DataArray, np.ndarray]:
    """
    Parameters
    ----------
    spx_data  : Quantiacs 格式的 SPX500 股票 DataArray（field, time, asset）
    spx_index : SPX 指數價格序列（time, asset），取 asset='SPX'
    threshold : 再平衡觸發幅度

    Returns
    -------
    output          : Quantiacs 格式的權重 DataArray
    rebalance_flags : bool 陣列，True 表示當天再平衡
    """
    close = spx_data.sel(field="close")
    is_liquid = spx_data.sel(field="is_liquid")
    times = spx_data.coords["time"].values

    # 把 SPX 指數對齊到股票交易日（向前填充非交易日）
    spx_prices = (
        spx_index.sel(asset="SPX")
        .reindex(time=times, method="ffill")
        .values
    )

    # 計算每日股票部位「總目標權重」
    total_weights, rebalance_flags = compute_total_etf_weight(spx_prices, threshold)

    # 把總權重平均分配給當天的 liquid 成分股
    is_liquid_np = is_liquid.values  # shape: (time, asset)
    output_np = np.zeros_like(close.values)  # shape: (time, asset)

    for i in range(len(times)):
        liquid_mask = is_liquid_np[i] == 1
        n_liquid = liquid_mask.sum()
        if n_liquid == 0:
            continue
        # 每支成分股分到等量的總目標權重
        output_np[i, liquid_mask] = total_weights[i] / n_liquid

    output = xr.DataArray(
        output_np,
        dims=close.dims,
        coords=close.coords,
    )
    return output, rebalance_flags


# ─────────────────────────────────────────────
# 比較指標計算
# ─────────────────────────────────────────────
def calc_comparison_metrics(
    stats: xr.DataArray,
    rebalance_flags: np.ndarray,
) -> dict:
    """
    整合 Quantiacs 內建統計 + 額外自計指標，回傳 dict。

    指標說明：
    - 夏普比率   : 年化超額報酬 / 年化波動率（最核心的風險調整報酬指標）
    - 年化平均報酬: 複利折算的年化報酬率
    - 年化波動率  : 日報酬標準差 * sqrt(252)
    - 最大回撤    : 歷史上從最高點到最低點的最大跌幅（衡量最差情境）
    - 卡瑪比率    : 年化報酬 / |最大回撤|（越高越能用小回撤換取報酬）
    - 索提諾比率  : 只計下行波動率的夏普（對下跌風險更敏感）
    - 平均換手率  : 每日平均買賣比例（間接反映交易成本）
    - 累計總報酬  : 整個回測期間的累計報酬
    - 再平衡次數  : 觸發再平衡的天數（越少代表持有成本越低）
    """
    df = stats.to_pandas()
    last = df.iloc[-1]

    mean_ret = float(last.get("mean_return", np.nan))
    vol      = float(last.get("volatility", np.nan))
    max_dd   = float(last.get("max_drawdown", np.nan))
    sr       = float(last.get("sharpe_ratio", np.nan))
    turnover = float(last.get("avg_turnover", np.nan))
    avg_hold = float(last.get("avg_holdingtime", np.nan))

    equity = df["equity"].dropna()
    total_return = (equity.iloc[-1] / equity.iloc[0]) - 1.0

    calmar = mean_ret / abs(max_dd) if max_dd != 0 and not np.isnan(max_dd) else np.nan

    rr = df["relative_return"].dropna()
    downside = rr[rr < 0]
    sortino_denom = downside.std() * np.sqrt(252) if len(downside) > 0 else np.nan
    sortino = mean_ret / sortino_denom if sortino_denom and sortino_denom != 0 else np.nan

    n_rebalances = int(rebalance_flags.sum())

    return {
        "夏普比率 (Sharpe Ratio)":         round(sr, 4),
        "年化平均報酬 (Mean Return)":        f"{mean_ret:.2%}",
        "年化波動率 (Volatility)":           f"{vol:.2%}",
        "最大回撤 (Max Drawdown)":           f"{max_dd:.2%}",
        "卡瑪比率 (Calmar Ratio)":           round(calmar, 4),
        "索提諾比率 (Sortino Ratio)":        round(sortino, 4),
        "平均換手率 (Avg Turnover)":         f"{turnover:.2%}",
        "平均持倉天數 (Avg Holding Days)":   round(avg_hold, 1),
        "再平衡次數 (# Rebalances)":         n_rebalances,
        "累計總報酬 (Total Return)":         f"{total_return:.2%}",
    }


# ─────────────────────────────────────────────
# 執行回測
# ─────────────────────────────────────────────
def run_backtest() -> tuple[xr.DataArray, xr.DataArray, np.ndarray]:
    """
    執行完整回測，印出指標並繪圖。
    Returns (output, stats, rebalance_flags)，供 compare.py 使用。
    """
    print("=" * 60)
    print("策略一：50/50 S&P 500 + 現金（10% 再平衡閾值）")
    print("=" * 60)

    # ── 載入資料 ─────────────────────────────
    print(f"\n[1/3] 載入 SPX500 成分股資料（{START_DATE} 起）...")
    spx_data = qndata.stocks_load_spx_data(min_date=START_DATE)
    print(f"      成分股總數：{len(spx_data.asset)}，交易日數：{len(spx_data.time)}")

    print("[2/3] 載入 SPX 指數價格...")
    spx_index = qndata.index_load_data(assets=["SPX"], min_date=START_DATE)
    print(f"      SPX 資料：{str(spx_index.time.values[0])[:10]} ~ {str(spx_index.time.values[-1])[:10]}")

    # ── 計算權重 ─────────────────────────────
    print("[3/3] 計算策略權重...")
    output, rebalance_flags = strategy(spx_data, spx_index)

    # Quantiacs 標準清理
    output = qnout.clean(output, spx_data)

    # ── 計算統計 ─────────────────────────────
    # 統計從第一年後開始，確保有足夠歷史資料
    stats_start = str(pd.Timestamp(spx_data.time.values[0]) + pd.DateOffset(years=1))[:10]
    stats = qnstats.calc_stat(
        spx_data,
        output.sel(time=slice(stats_start, None)),
    )

    # ── 顯示結果 ─────────────────────────────
    print(f"\n─── 回測統計（{stats_start} 至今）───")
    metrics = calc_comparison_metrics(stats, rebalance_flags)
    for k, v in metrics.items():
        print(f"  {k:<38}: {v}")

    # ── 繪圖 ─────────────────────────────────
    _plot(spx_data, spx_index, output, stats, rebalance_flags)

    return output, stats, rebalance_flags


def _plot(spx_data, spx_index, output, stats, rebalance_flags):
    df_stats = stats.to_pandas()
    times = spx_data.time.values

    # 每日股票部位「總權重」= 所有成分股權重加總
    total_etf_weight = output.sum(dim="asset").to_pandas()

    # SPX 指數價格（正規化到 1）
    spx_price = spx_index.sel(asset="SPX").reindex(
        time=spx_data.time, method="ffill"
    ).to_pandas()
    spx_norm = spx_price / spx_price.iloc[0]

    rebalance_dates = pd.to_datetime(times[rebalance_flags])

    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    fig.suptitle("Strategy 1: 50/50 S&P500 + Cash (10% Rebalance Threshold)", fontsize=14)

    # Equity curve
    ax1 = axes[0]
    equity = df_stats["equity"].dropna()
    ax1.plot(equity.index, equity.values, color="steelblue", linewidth=1.5, label="Strategy Equity")
    ax1.plot(spx_norm.index, spx_norm.values, color="gray", linewidth=1, alpha=0.6, linestyle="--", label="SPX Index (normalized)")
    ax1.set_ylabel("Equity (start=1)")
    ax1.set_title("Equity Curve")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # SPX + rebalance points
    ax2 = axes[1]
    ax2.plot(spx_price.index, spx_price.values, color="darkorange", linewidth=1, alpha=0.8, label="SPX Close")
    if len(rebalance_dates) > 0:
        rb_prices = spx_price.reindex(rebalance_dates, method="nearest")
        ax2.scatter(rb_prices.index, rb_prices.values,
                    color="red", s=25, zorder=5,
                    label=f"Rebalance ({len(rebalance_dates)} times)")
    ax2.set_ylabel("SPX Level")
    ax2.set_title("SPX Index & Rebalance Points")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    # Allocation
    ax3 = axes[2]
    ax3.fill_between(total_etf_weight.index, total_etf_weight.values,
                     alpha=0.55, color="steelblue", label="S&P 500 Allocation")
    ax3.fill_between(total_etf_weight.index, 1 - total_etf_weight.values,
                     total_etf_weight.values,
                     alpha=0.3, color="lightgray", label="Cash")
    ax3.axhline(0.5, color="black", linestyle="--", linewidth=0.8, label="Target 50%")
    ax3.set_ylim(0, 1)
    ax3.set_ylabel("Allocation")
    ax3.set_title("Equity / Cash Allocation")
    ax3.legend(loc="upper left")
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = "strategies/strategy_01_results.png"
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"\n圖表已儲存至 {save_path}")


if __name__ == "__main__":
    run_backtest()
