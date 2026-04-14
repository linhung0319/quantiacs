# Strategy 7: 50/50 Threshold Rebalancing (20%)

## Description

Identical to Strategy 1 but with a wider ±20% rebalance trigger. The portfolio is rebalanced back to 50/50 less frequently, allowing larger allocation drifts while minimising transaction costs.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Trigger | ±20% SPX price move from last rebalance |
| Stock Universe | S&P 500 constituents (equal-weight, liquid only) |

## Backtest Results (2007-01-03 to 2026-04-09)

| Metric | Value | Description |
|--------|-------|-------------|
| Sharpe Ratio | 0.4942 | Risk-adjusted return (higher is better) |
| Annual Return | 5.30% | Geometric annualized return |
| Volatility | 10.73% | Annualized std dev of daily returns |
| Max Drawdown | -35.31% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1502 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6062 | Sharpe using downside volatility only |
| Avg Turnover | 1.10% | Average daily portfolio turnover |
| Total Return | 170.23% | Cumulative return over full period |
| # Rebalances | 18 | Number of rebalancing events |
