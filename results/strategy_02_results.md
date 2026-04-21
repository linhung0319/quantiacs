# Strategy 2: 100% S&P500 Buy & Hold (Benchmark)

## Description

Hold 100% of capital in an equal-weight S&P 500 basket at all times. No cash buffer, no market-timing, no threshold rebalancing. This represents the maximum equity exposure and acts as the benchmark against which risk-managed strategies are evaluated.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 100% stocks / 0% cash |
| Rebalance Rule | None (stocks rebalanced to equal-weight daily within index) |
| Stock Universe | S&P 500 constituents (market-cap proxy weight, liquid only) |

## Backtest Settings

| Setting | Value |
|---------|-------|
| Start Date | 2007-01-03 |
| Slippage Factor | 0.05 |
| Points per Year | 251 |
| Stock Weighting | Market-cap proxy (63d rolling dollar volume) |

## Backtest Results (2007-01-03 to 2026-04-16)

| Metric | Value | Description |
|--------|-------|-------------|
| Sharpe Ratio | 0.5039 | Risk-adjusted return (higher is better) |
| Annual Return | 11.36% | Geometric annualized return (CAGR) |
| Volatility | 22.55% | Annualized std dev of daily returns |
| Max Drawdown | -61.04% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1862 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6263 | Sharpe using downside volatility only |
| Avg Turnover | 2.15% | Average daily portfolio turnover |
| Total Return | 700.99% | Cumulative return over full period |
| # Rebalances | 0 | Number of rebalancing / regime-switch events |
