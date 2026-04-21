# Strategy 4: 50/50 Monthly Calendar Rebalancing

## Description

Hold 50% in an equal-weight S&P 500 basket and 50% in cash. Rebalance back to 50/50 on the first trading day of every calendar month, regardless of how much the market has moved. Compares fixed-calendar rebalancing against threshold-based approaches.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Schedule | First trading day of each calendar month |
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
| Sharpe Ratio | 0.5586 | Risk-adjusted return (higher is better) |
| Annual Return | 6.22% | Geometric annualized return (CAGR) |
| Volatility | 11.14% | Annualized std dev of daily returns |
| Max Drawdown | -35.81% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1738 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6955 | Sharpe using downside volatility only |
| Avg Turnover | 0.98% | Average daily portfolio turnover |
| Total Return | 221.34% | Cumulative return over full period |
| # Rebalances | 232 | Number of rebalancing / regime-switch events |
