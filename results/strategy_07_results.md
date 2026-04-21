# Strategy 7: 50/50 Threshold Rebalancing (20%)

## Description

Identical to Strategy 1 but with a wider ±20% rebalance trigger. The portfolio is rebalanced back to 50/50 less frequently, allowing larger allocation drifts while minimising transaction costs.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Trigger | ±20% SPX price move from last rebalance |
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
| Sharpe Ratio | 0.5578 | Risk-adjusted return (higher is better) |
| Annual Return | 6.30% | Geometric annualized return (CAGR) |
| Volatility | 11.29% | Annualized std dev of daily returns |
| Max Drawdown | -35.59% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1770 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6968 | Sharpe using downside volatility only |
| Avg Turnover | 0.99% | Average daily portfolio turnover |
| Total Return | 225.67% | Cumulative return over full period |
| # Rebalances | 17 | Number of rebalancing / regime-switch events |
