# Strategy 4: 50/50 Monthly Calendar Rebalancing

## Description

Hold 50% in an equal-weight S&P 500 basket and 50% in cash. Rebalance back to 50/50 on the first trading day of every calendar month, regardless of how much the market has moved. Compares fixed-calendar rebalancing against threshold-based approaches.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Schedule | First trading day of each calendar month |
| Stock Universe | S&P 500 constituents (equal-weight, liquid only) |

## Backtest Results (2007-01-03 to 2026-04-09)

| Metric | Value | Description |
|--------|-------|-------------|
| Sharpe Ratio | 0.4932 | Risk-adjusted return (higher is better) |
| Annual Return | 5.21% | Geometric annualized return |
| Volatility | 10.56% | Annualized std dev of daily returns |
| Max Drawdown | -35.93% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1449 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6049 | Sharpe using downside volatility only |
| Avg Turnover | 1.09% | Average daily portfolio turnover |
| Total Return | 165.42% | Cumulative return over full period |
| # Rebalances | 244 | Number of rebalancing events |
