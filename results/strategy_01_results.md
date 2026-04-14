# Strategy 1: 50/50 Threshold Rebalancing (10%)

## Description

Hold 50% in an equal-weight S&P 500 basket and 50% in cash. Rebalance back to 50/50 whenever the SPX index moves ±10% from the price at the last rebalance. Between rebalance events the portfolio drifts freely — no daily trading.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Trigger | ±10% SPX price move from last rebalance |
| Stock Universe | S&P 500 constituents (equal-weight, liquid only) |
| Benchmark Signal | SPX index (daily close) |

## Backtest Results (2007-01-03 to 2026-04-09)

| Metric | Value | Description |
|--------|-------|-------------|
| Sharpe Ratio | 0.4803 | Risk-adjusted return (higher is better) |
| Annual Return | 5.17% | Geometric annualized return |
| Volatility | 10.75% | Annualized std dev of daily returns |
| Max Drawdown | -35.73% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1445 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.5855 | Sharpe using downside volatility only |
| Avg Turnover | 1.09% | Average daily portfolio turnover |
| Total Return | 163.45% | Cumulative return over full period |
| # Rebalances | 52 | Number of rebalancing events |
