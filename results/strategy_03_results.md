# Strategy 3: 50/50 Dynamic Threshold (Bull 15% / Bear 5%)

## Description

Same 50/50 allocation as Strategy 1, but the rebalance trigger adapts to the market regime detected by the 200-day moving average of SPX:
- Bull market (SPX > 200d MA): rebalance only when SPX moves ±15% (let winners run longer).
- Bear market (SPX < 200d MA): rebalance at ±5% (act more defensively to limit drawdown).

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Bull Market Threshold | ±15% (SPX > 200-day MA) |
| Bear Market Threshold | ±5%  (SPX < 200-day MA) |
| Regime Signal | SPX 200-day simple moving average |
| Stock Universe | S&P 500 constituents (equal-weight, liquid only) |

## Backtest Results (2007-01-03 to 2026-04-09)

| Metric | Value | Description |
|--------|-------|-------------|
| Sharpe Ratio | 0.4847 | Risk-adjusted return (higher is better) |
| Annual Return | 5.26% | Geometric annualized return |
| Volatility | 10.86% | Annualized std dev of daily returns |
| Max Drawdown | -35.81% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1470 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.5918 | Sharpe using downside volatility only |
| Avg Turnover | 1.12% | Average daily portfolio turnover |
| Total Return | 168.23% | Cumulative return over full period |
| # Rebalances | 116 | Number of rebalancing events |
