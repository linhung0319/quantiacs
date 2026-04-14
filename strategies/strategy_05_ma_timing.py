"""
Strategy 5: MA Market Timing (200-day Moving Average)
------------------------------------------------------
Allocation : 100% S&P 500 when bullish, 100% Cash when bearish
Signal     : SPX 200-day simple moving average
Rule       : If SPX close > 200d MA  →  hold 100% equal-weight S&P 500
             If SPX close < 200d MA  →  hold 100% cash
             Switch happens at the open of the next trading day.
"""

import numpy as np
import xarray as xr

from strategies.base import (
    load_market_data, build_output, run_stats,
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
    "Stock Universe":     "S&P 500 constituents (equal-weight, liquid only)",
}

MA_PERIOD = 200


# ─────────────────────────────────────────────
# Core logic
# ─────────────────────────────────────────────

def compute_total_etf_weight(
    spx_prices: np.ndarray,
    ma_period: int = MA_PERIOD,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Binary allocation: 1.0 (bull) or 0.0 (bear) based on MA crossover.
    rebalance_flags marks every regime-change day.
    """
    n = len(spx_prices)
    weights = np.zeros(n)
    flags   = np.zeros(n, dtype=bool)
    prev_regime = None                  # track regime changes

    for i in range(n):
        p = spx_prices[i]
        if np.isnan(p) or p <= 0:
            weights[i] = weights[i - 1] if i > 0 else 0.0
            continue

        if i < ma_period - 1:
            # Not enough history: stay in cash conservatively
            weights[i] = 0.0
            regime = "bear"
        else:
            ma = float(np.nanmean(spx_prices[i - ma_period + 1 : i + 1]))
            regime = "bull" if p > ma else "bear"
            weights[i] = 1.0 if regime == "bull" else 0.0

        if prev_regime is not None and regime != prev_regime:
            flags[i] = True             # regime switch
        prev_regime = regime

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
            f"{RESULTS_DIR}/strategy_05_results.md")
    plot_strategy(NAME, spx_data, spx_index, output, stats, flags,
                  f"{RESULTS_DIR}/strategy_05_chart.png")

    return output, stats, metrics, flags


def run_backtest():
    print("=" * 60)
    print(NAME)
    print("=" * 60)
    spx_data, spx_index = load_market_data(START_DATE)
    return run(spx_data, spx_index)


if __name__ == "__main__":
    run_backtest()
