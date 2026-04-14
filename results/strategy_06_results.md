# Strategy 6: 50/50 Threshold Rebalancing (5%)

## Description

Identical to Strategy 1 but with a tighter ±5% rebalance trigger. The portfolio rebalances back to 50/50 more frequently, keeping the allocation closer to target at the cost of more trades.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Trigger | ±5% SPX price move from last rebalance |
| Stock Universe | S&P 500 constituents (equal-weight, liquid only) |

## Backtest Results (2007-01-03 to 2026-04-09)

| Metric | Value | Description |
|--------|-------|-------------|
| Sharpe Ratio | 0.4834 | Risk-adjusted return (higher is better) |
| Annual Return | 5.21% | Geometric annualized return |
| Volatility | 10.79% | Annualized std dev of daily returns |
| Max Drawdown | -35.60% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1465 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.5885 | Sharpe using downside volatility only |
| Avg Turnover | 1.10% | Average daily portfolio turnover |
| Total Return | 165.84% | Cumulative return over full period |
| # Rebalances | 201 | Number of rebalancing events |
