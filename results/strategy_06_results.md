# Strategy 6: 50/50 Threshold Rebalancing (5%)

## Description

Identical to Strategy 1 but with a tighter ±5% rebalance trigger. The portfolio rebalances back to 50/50 more frequently, keeping the allocation closer to target at the cost of more trades.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Trigger | ±5% SPX price move from last rebalance |
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
| Sharpe Ratio | 0.5534 | Risk-adjusted return (higher is better) |
| Annual Return | 6.29% | Geometric annualized return (CAGR) |
| Volatility | 11.37% | Annualized std dev of daily returns |
| Max Drawdown | -35.30% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1783 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6857 | Sharpe using downside volatility only |
| Avg Turnover | 1.00% | Average daily portfolio turnover |
| Total Return | 225.37% | Cumulative return over full period |
| # Rebalances | 200 | Number of rebalancing / regime-switch events |
