"""
多策略比較工具
--------------
用法：

    from strategies.compare import StrategyComparison
    from strategies.strategy_01_rebalance_10pct import run_backtest as s1

    comp = StrategyComparison()
    comp.add("策略一：50/50 10%再平衡", *s1())
    # comp.add("策略二：...", *s2())

    comp.summary()      # 印出對比表格
    comp.plot()         # 繪製資產曲線對比圖
"""

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from tabulate import tabulate

import qnt.stats as qnstats


class StrategyComparison:
    """收集多個策略的回測結果，進行橫向比較。"""

    # 比較指標設定：(欄位名, 顯示名, 是否「越大越好」)
    METRICS = [
        ("sharpe_ratio",      "夏普比率 (Sharpe)",    True),
        ("mean_return",       "年化報酬",              True),
        ("volatility",        "年化波動率",            False),
        ("max_drawdown",      "最大回撤",              False),
        ("calmar_ratio",      "卡瑪比率 (Calmar)",     True),
        ("sortino_ratio",     "索提諾比率 (Sortino)",  True),
        ("avg_turnover",      "平均換手率",            False),
        ("total_return",      "累計總報酬",            True),
        ("n_rebalances",      "再平衡次數",            False),
    ]

    def __init__(self):
        self._entries: list[dict] = []

    def add(self, name: str, output: xr.DataArray, stats: xr.DataArray,
            rebalance_flags: np.ndarray = None):
        """
        新增一個策略結果。

        Parameters
        ----------
        name             : 策略名稱
        output           : Quantiacs 輸出權重（xr.DataArray）
        stats            : qnstats.calc_stat 的結果
        rebalance_flags  : bool 陣列，True 表示當天執行再平衡（可選）
        """
        if rebalance_flags is None:
            rebalance_flags = np.array([], dtype=bool)

        raw = self._extract(stats, rebalance_flags)
        self._entries.append({"name": name, "output": output, "stats": stats,
                               "metrics": raw, "rebalance_flags": rebalance_flags})
        print(f"[compare] 已新增策略：{name}")

    # ─────────────────────────────────────────
    def summary(self, markdown: bool = False):
        """印出所有策略的指標對比表格。"""
        if not self._entries:
            print("尚未新增任何策略。")
            return

        headers = ["指標"] + [e["name"] for e in self._entries]
        rows = []

        for key, label, higher_is_better in self.METRICS:
            row = [label]
            values = [e["metrics"].get(key, np.nan) for e in self._entries]

            # 標記最佳值
            valid = [v for v in values if not np.isnan(v)]
            if valid:
                best = max(valid) if higher_is_better else min(valid)
            else:
                best = None

            for v in values:
                if np.isnan(v):
                    row.append("N/A")
                elif key in ("mean_return", "volatility", "max_drawdown",
                              "avg_turnover", "total_return"):
                    cell = f"{v:.2%}"
                elif key == "n_rebalances":
                    cell = str(int(v))
                else:
                    cell = f"{v:.4f}"
                if best is not None and abs(v - best) < 1e-9:
                    cell = f"★ {cell}"
                row.append(cell)
            rows.append(row)

        fmt = "pipe" if markdown else "rounded_outline"
        print("\n" + "=" * 60)
        print("策略比較摘要")
        print("=" * 60)
        print(tabulate(rows, headers=headers, tablefmt=fmt))
        print("（★ 表示該指標最佳值）\n")

    def plot(self, save_path: str = "strategies/comparison.png"):
        """繪製所有策略的資產曲線對比圖。"""
        if not self._entries:
            print("尚未新增任何策略。")
            return

        fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        colors = plt.cm.tab10.colors

        ax1, ax2 = axes
        ax1.set_title("資產曲線比較（Equity Curves）")
        ax2.set_title("最大回撤比較（Drawdown）")

        for i, entry in enumerate(self._entries):
            c = colors[i % len(colors)]
            df = entry["stats"].to_pandas()
            equity = df["equity"].dropna()
            underwater = df["underwater"].dropna()

            ax1.plot(equity.index, equity.values, label=entry["name"],
                     color=c, linewidth=1.5)
            ax2.fill_between(underwater.index, underwater.values, 0,
                              alpha=0.4, color=c, label=entry["name"])

        ax1.set_ylabel("資產（初始=1）")
        ax1.legend(loc="upper left")
        ax1.grid(True, alpha=0.3)

        ax2.set_ylabel("回撤幅度")
        ax2.legend(loc="lower left")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.show()
        print(f"\n比較圖已儲存至 {save_path}")

    # ─────────────────────────────────────────
    def _extract(self, stats: xr.DataArray, rebalance_flags: np.ndarray) -> dict:
        df = stats.to_pandas()
        last = df.iloc[-1]

        mean_ret = float(last.get("mean_return", np.nan))
        vol      = float(last.get("volatility", np.nan))
        max_dd   = float(last.get("max_drawdown", np.nan))
        sr       = float(last.get("sharpe_ratio", np.nan))
        turnover = float(last.get("avg_turnover", np.nan))

        equity = df["equity"].dropna()
        total_return = (equity.iloc[-1] / equity.iloc[0]) - 1.0

        calmar = mean_ret / abs(max_dd) if max_dd != 0 and not np.isnan(max_dd) else np.nan

        rr = df["relative_return"].dropna()
        downside = rr[rr < 0]
        points_per_year = 252
        sortino_denom = downside.std() * np.sqrt(points_per_year) if len(downside) > 0 else np.nan
        sortino = mean_ret / sortino_denom if sortino_denom and sortino_denom != 0 else np.nan

        return {
            "sharpe_ratio":  sr,
            "mean_return":   mean_ret,
            "volatility":    vol,
            "max_drawdown":  max_dd,
            "calmar_ratio":  calmar,
            "sortino_ratio": sortino,
            "avg_turnover":  turnover,
            "total_return":  total_return,
            "n_rebalances":  float(rebalance_flags.sum()) if len(rebalance_flags) > 0 else 0.0,
        }
