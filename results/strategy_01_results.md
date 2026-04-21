# Strategy 1: 50/50 Threshold Rebalancing (10%)

## Description

Hold 50% in a market-cap-weighted S&P 500 basket and 50% in cash. Rebalance back to 50/50 whenever the SPX index moves ±10% from the price at the last rebalance. Between rebalance events the portfolio drifts freely — no daily trading.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 50% stocks / 50% cash |
| Rebalance Trigger | ±10% SPX price move from last rebalance |
| Stock Universe | S&P 500 constituents (market-cap proxy weight, liquid only) |
| Benchmark Signal | SPX index (daily close) |

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
| Sharpe Ratio | 0.5487 | Risk-adjusted return (higher is better) |
| Annual Return | 6.22% | Geometric annualized return (CAGR) |
| Volatility | 11.33% | Annualized std dev of daily returns |
| Max Drawdown | -35.54% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1749 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6810 | Sharpe using downside volatility only |
| Avg Turnover | 0.98% | Average daily portfolio turnover |
| Total Return | 220.86% | Cumulative return over full period |
| # Rebalances | 51 | Number of rebalancing / regime-switch events |
