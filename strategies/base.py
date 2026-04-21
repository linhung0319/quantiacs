"""
strategies/base.py
------------------
所有 S&P 500 回測策略共用的工具函式。

【資料來源】
  spx_data  : S&P 500 成分股的每日 OHLCV 資料（約 500～800 支股票，視年份而定）
              由 qndata.stocks_load_spx_data() 載入
  spx_index : SPX 指數的每日收盤價（這就是 S&P 500 指數本身，非個股）
              由 qndata.index_load_data(assets=["SPX"]) 載入
              → SPX 是根據成分股市值加權計算出來的指數數值，我們用它作為
                「市場走勢訊號」（例如觸發再平衡、計算移動平均線）

【股票權重的計算方式】
  真實的市值權重（每家公司市值 / 全部市值加總）在 Quantiacs 無法直接取得，
  因此我們用「63 日滾動平均美元成交量」作為市值的代理指標：
      dollar_volume_i = close_i × vol_i
      cap_weight_i    = rolling_mean(dollar_volume_i, 63d)
                        / sum_j( rolling_mean(dollar_volume_j, 63d) )
  這個近似是合理的：市值越大的公司，日均成交金額也越大。

【calc_stat 參數（所有策略固定不變，以確保比較的公平性）】
  slippage_factor=0.05  每筆交易的滑價成本（ATR 的 5%）
  min_periods=1         最少 1 天即開始計算統計值
  max_periods=None      使用全部歷史資料計算滾動統計
  per_asset=False       以整體組合計算，而非個別股票
  points_per_year=251   一年約有 251 個交易日
"""

import os
from dotenv import load_dotenv
load_dotenv()   # 從 .env 讀取 API_KEY

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("Agg")   # 無顯示器環境下輸出 PNG（不開視窗）
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import qnt.data as qndata
import qnt.stats as qnstats
import qnt.output as qnout

START_DATE  = "2007-01-03"
RESULTS_DIR = "results"

# 所有策略共用同一組 calc_stat 參數，確保跨策略比較的公平性
CALC_STAT_KWARGS = dict(
    slippage_factor = 0.05,   # 滑價成本係數（相對於 ATR）
    min_periods     = 1,      # 統計計算的最小資料天數
    max_periods     = None,   # 不限制滾動視窗上限
    per_asset       = False,  # 以組合整體計算，非個別股票
    points_per_year = 251,    # 年化係數（251 個交易日）
)

CAP_WEIGHT_WINDOW = 63   # 計算市值代理權重時的滾動天數（約 1 季）


# ─────────────────────────────────────────────────────────────
# 資料載入
# ─────────────────────────────────────────────────────────────

def load_market_data(start_date: str = START_DATE):
    """
    載入兩種資料：
    1. spx_data  : S&P 500 成分股的個股 OHLCV（open/high/low/close/vol）
                   + is_liquid 欄位（Quantiacs 標記該股當日是否流動性足夠）
    2. spx_index : SPX 指數每日收盤價（S&P 500 指數，市值加權）
                   → 這裡只有「價格」，沒有個股資料
    Returns (spx_data, spx_index)
    """
    print(f"  Loading SPX500 stocks ({start_date} onwards)...")
    spx_data = qndata.stocks_load_spx_data(min_date=start_date, forward_order=True)
    print(f"  Loaded {len(spx_data.asset)} stocks, {len(spx_data.time)} trading days")

    print("  Loading SPX index price...")
    spx_index = qndata.index_load_data(assets=["SPX"], min_date=start_date, forward_order=True)
    print(f"  SPX: {str(spx_index.time.values[0])[:10]} ~ {str(spx_index.time.values[-1])[:10]}")

    return spx_data, spx_index


# ─────────────────────────────────────────────────────────────
# 市值代理權重計算
# ─────────────────────────────────────────────────────────────

def calc_cap_weights(spx_data: xr.DataArray) -> xr.DataArray:
    """
    用 63 日滾動平均美元成交量作為市值的代理指標，計算每支股票的權重。

    步驟：
    1. 計算每日美元成交量：dollar_vol = close × vol
       （只計算 is_liquid==1 的股票，過濾掉流動性不足的標的）
    2. 做 63 日滾動平均，平滑每日波動
    3. 每天對所有股票的平滑值加總，除以總和 → 各股票佔比（加總為 1）

    為何這是市值的代理？
    → 市值大的公司日均成交金額也大，所以美元成交量與市值高度正相關。
      這是在 Quantiacs 資料集中，市值加權的最佳可用近似方式。
    """
    close     = spx_data.sel(field="close")
    vol       = spx_data.sel(field="vol")
    is_liquid = spx_data.sel(field="is_liquid")

    # 只保留流動性足夠的股票，其餘設為 NaN
    dollar_vol = (close * vol).where(is_liquid == 1)

    # 63 日滾動平均，減少單日大量交易造成的雜訊
    dollar_vol_smooth = dollar_vol.rolling(
        time=CAP_WEIGHT_WINDOW, min_periods=1
    ).mean()

    # 每日對所有股票加總，再各自除以總和 → 得到比例（加總為 1）
    total = dollar_vol_smooth.sum(dim="asset")
    cap_weights = dollar_vol_smooth / total

    return cap_weights.fillna(0.0)   # NaN（非流動股）填 0


# ─────────────────────────────────────────────────────────────
# 組合輸出建構
# ─────────────────────────────────────────────────────────────

def build_output(
    spx_data: xr.DataArray,
    total_weights: np.ndarray,
    cap_weights: xr.DataArray,
) -> xr.DataArray:
    """
    建立 Quantiacs 格式的組合權重 DataArray。

    最終輸出的邏輯是兩層乘法：
      output[t, i] = total_weights[t] × cap_weights[t, i]

    第一層：total_weights[t]
      → 這一天整體有多少比例投入股票（例如 0.5 = 50%）
      → 每個策略各自計算自己的 total_weights
    第二層：cap_weights[t, i]
      → 投入股票的那部分，如何分配到各個成分股（按市值代理比例）
      → 所有股票的 cap_weights 加總為 1

    組合的剩餘部分（1 - total_weights[t]）視為持有現金，不出現在輸出中。
    """
    close = spx_data.sel(field="close")
    cap_np = cap_weights.values          # shape: (time, asset)
    tw = total_weights[:, np.newaxis]    # shape: (time, 1)，便於廣播
    output_np = tw * cap_np              # shape: (time, asset)

    return xr.DataArray(output_np, dims=close.dims, coords=close.coords)


def run_stats(
    spx_data: xr.DataArray,
    output: xr.DataArray,
    stats_start: str | None = None,
) -> tuple[xr.DataArray, str]:
    """
    清理組合輸出並計算績效統計。

    步驟：
    1. qnout.clean()：Quantiacs 內建清理，處理流動性過濾、缺漏日期等
    2. qnstats.calc_stat()：計算 Sharpe、Max Drawdown、equity 曲線等
       → 使用固定的 CALC_STAT_KWARGS，確保跨策略比較公平
    stats_start 預設為資料起始日（2007-01-03）
    """
    output = qnout.clean(output, spx_data)
    if stats_start is None:
        stats_start = str(spx_data.time.values[0])[:10]
    stats = qnstats.calc_stat(
        spx_data,
        output.sel(time=slice(stats_start, None)),
        **CALC_STAT_KWARGS,
    )
    return stats, stats_start


# ─────────────────────────────────────────────────────────────
# 績效指標計算
# ─────────────────────────────────────────────────────────────

def calc_metrics(
    stats: xr.DataArray,
    rebalance_flags: np.ndarray | None = None,
) -> dict:
    """
    從 calc_stat 的輸出中萃取並計算各項比較指標。

    指標說明：
    - Sharpe Ratio    : 年化超額報酬 / 年化波動度（越高越好，主要比較指標）
    - Annual Return   : 年化幾何平均報酬（CAGR）
    - Volatility      : 每日報酬率的年化標準差
    - Max Drawdown    : 最大由高峰到谷底的跌幅
    - Calmar Ratio    : 年化報酬 / |最大回撤|
    - Sortino Ratio   : 只用下行波動計算的 Sharpe（對虧損更敏感）
    - Avg Turnover    : 平均每日換手率（反映交易成本）
    - Total Return    : 整段期間的累積報酬
    - # Rebalances    : 觸發再平衡或切換操作的次數（交易成本的代理）
    """
    df = stats.to_pandas()
    last = df.iloc[-1]   # calc_stat 是累積計算，最後一列即為全期結果

    mean_ret = float(last.get("mean_return", np.nan))
    vol      = float(last.get("volatility", np.nan))
    max_dd   = float(last.get("max_drawdown", np.nan))
    sr       = float(last.get("sharpe_ratio", np.nan))
    turnover = float(last.get("avg_turnover", np.nan))

    equity = df["equity"].dropna()
    total_return = float((equity.iloc[-1] / equity.iloc[0]) - 1.0)

    calmar = mean_ret / abs(max_dd) if max_dd and not np.isnan(max_dd) and max_dd != 0 else np.nan

    # Sortino 分母：只用負報酬日的標準差年化
    rr   = df["relative_return"].dropna()
    down = rr[rr < 0]
    sortino_denom = down.std() * np.sqrt(CALC_STAT_KWARGS["points_per_year"]) if len(down) > 0 else np.nan
    sortino = mean_ret / sortino_denom if sortino_denom and sortino_denom != 0 else np.nan

    n_rebalances = int(rebalance_flags.sum()) if rebalance_flags is not None else 0

    return {
        "sharpe_ratio":  sr,
        "mean_return":   mean_ret,
        "volatility":    vol,
        "max_drawdown":  max_dd,
        "calmar_ratio":  calmar,
        "sortino_ratio": sortino,
        "avg_turnover":  turnover,
        "total_return":  total_return,
        "n_rebalances":  n_rebalances,
    }


def print_metrics(metrics: dict, period: str = ""):
    rows = [
        ("Sharpe Ratio",    f"{metrics['sharpe_ratio']:.4f}"),
        ("Annual Return",   f"{metrics['mean_return']:.2%}"),
        ("Volatility",      f"{metrics['volatility']:.2%}"),
        ("Max Drawdown",    f"{metrics['max_drawdown']:.2%}"),
        ("Calmar Ratio",    f"{metrics['calmar_ratio']:.4f}"),
        ("Sortino Ratio",   f"{metrics['sortino_ratio']:.4f}"),
        ("Avg Turnover",    f"{metrics['avg_turnover']:.2%}"),
        ("Total Return",    f"{metrics['total_return']:.2%}"),
        ("# Rebalances",    str(metrics['n_rebalances'])),
    ]
    if period:
        print(f"\n--- Results ({period}) ---")
    for label, val in rows:
        print(f"  {label:<28}: {val}")


# ─────────────────────────────────────────────────────────────
# Markdown 輸出
# ─────────────────────────────────────────────────────────────

def save_md(
    strategy_name: str,
    description: str,
    params: dict,
    metrics: dict,
    period: str,
    save_path: str,
):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    lines = [
        f"# {strategy_name}",
        "",
        "## Description",
        "",
        description,
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
    ]
    for k, v in params.items():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Backtest Settings",
        "",
        "| Setting | Value |",
        "|---------|-------|",
        f"| Start Date | {period.split(' to ')[0]} |",
        f"| Slippage Factor | {CALC_STAT_KWARGS['slippage_factor']} |",
        f"| Points per Year | {CALC_STAT_KWARGS['points_per_year']} |",
        f"| Stock Weighting | Market-cap proxy (63d rolling dollar volume) |",
        "",
        f"## Backtest Results ({period})",
        "",
        "| Metric | Value | Description |",
        "|--------|-------|-------------|",
        f"| Sharpe Ratio | {metrics['sharpe_ratio']:.4f} | Risk-adjusted return (higher is better) |",
        f"| Annual Return | {metrics['mean_return']:.2%} | Geometric annualized return (CAGR) |",
        f"| Volatility | {metrics['volatility']:.2%} | Annualized std dev of daily returns |",
        f"| Max Drawdown | {metrics['max_drawdown']:.2%} | Worst peak-to-trough loss |",
        f"| Calmar Ratio | {metrics['calmar_ratio']:.4f} | Annual Return / |Max Drawdown| |",
        f"| Sortino Ratio | {metrics['sortino_ratio']:.4f} | Sharpe using downside volatility only |",
        f"| Avg Turnover | {metrics['avg_turnover']:.2%} | Average daily portfolio turnover |",
        f"| Total Return | {metrics['total_return']:.2%} | Cumulative return over full period |",
        f"| # Rebalances | {metrics['n_rebalances']} | Number of rebalancing / regime-switch events |",
        "",
    ]

    with open(save_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Results saved to {save_path}")


# ─────────────────────────────────────────────────────────────
# 圖表繪製
# ─────────────────────────────────────────────────────────────

def plot_strategy(
    strategy_title: str,
    spx_data: xr.DataArray,
    spx_index: xr.DataArray,
    output: xr.DataArray,
    stats: xr.DataArray,
    rebalance_flags: np.ndarray | None,
    save_path: str,
):
    """
    產生三格面板圖表：
    Panel 1 - Equity Curve   : 策略淨值曲線 vs SPX 指數（標準化）
    Panel 2 - SPX + Rebalance: SPX 收盤價 + 再平衡觸發點（紅點）
    Panel 3 - Allocation     : 每日股票配置比例 vs 現金比例
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    df_stats = stats.to_pandas()
    times    = spx_data.time.values

    # 每日股票總配置（所有個股權重加總 = 投入股票的比例）
    total_etf_weight = output.sum(dim="asset").to_pandas()

    # 取 SPX 收盤價，對齊到 spx_data 的時間軸（前向填充缺漏日）
    spx_price = (
        spx_index.sel(asset="SPX")
        .reindex(time=spx_data.time, method="ffill")
        .to_pandas()
    )
    spx_norm = spx_price / spx_price.iloc[0]   # 標準化為起始值 = 1

    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    fig.suptitle(strategy_title, fontsize=13)

    # Panel 1: 淨值曲線
    ax1 = axes[0]
    equity = df_stats["equity"].dropna()
    ax1.plot(equity.index, equity.values,
             color="#1f77b4", linewidth=1.8, label="Strategy Equity")
    ax1.plot(spx_norm.index, spx_norm.values,
             color="#ff7f0e", linewidth=1.2, linestyle="--",
             alpha=0.85, label="SPX (normalized)")
    ax1.set_ylabel("Equity (start=1)")
    ax1.set_title("Panel 1 — Equity Curve")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Panel 2: SPX 走勢 + 再平衡觸發點
    ax2 = axes[1]
    ax2.plot(spx_price.index, spx_price.values,
             color="#1f77b4", linewidth=1.2, label="SPX Close")
    if rebalance_flags is not None and rebalance_flags.sum() > 0:
        rb_dates  = pd.to_datetime(times[rebalance_flags])
        rb_prices = spx_price.reindex(rb_dates, method="nearest")
        ax2.scatter(rb_prices.index, rb_prices.values,
                    color="#d62728", s=28, zorder=5,
                    label=f"Rebalance / Switch ({int(rebalance_flags.sum())} times)")
    ax2.set_ylabel("SPX Level")
    ax2.set_title("Panel 2 — SPX Index & Rebalance Points")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    # Panel 3: 配置比例（股票 vs 現金）
    ax3 = axes[2]
    cash = (1 - total_etf_weight).clip(lower=0)   # 現金 = 1 - 股票比例
    ax3.plot(total_etf_weight.index, total_etf_weight.values,
             color="#1f77b4", linewidth=1.6, label="S&P 500 allocation")
    ax3.plot(cash.index, cash.values,
             color="#d62728", linewidth=1.6, linestyle="--", label="Cash allocation")
    ax3.axhline(0.5, color="black", linestyle=":", linewidth=0.9, alpha=0.5)
    ax3.set_ylim(-0.03, 1.08)
    ax3.set_ylabel("Allocation (fraction)")
    ax3.set_title("Panel 3 — S&P 500 vs Cash Allocation Over Time")
    ax3.legend(loc="upper left")
    ax3.grid(True, alpha=0.3)

    # X 軸：每年一個刻度
    for ax in axes:
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(axes[-1].get_xticklabels(), rotation=45, ha="right", fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Chart saved to {save_path}")
