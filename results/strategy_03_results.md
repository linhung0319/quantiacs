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
| Sharpe Ratio | 0.5561 | Risk-adjusted return (higher is better) |
| Annual Return | 6.37% | Geometric annualized return (CAGR) |
| Volatility | 11.45% | Annualized std dev of daily returns |
| Max Drawdown | -35.30% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1803 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6909 | Sharpe using downside volatility only |
| Avg Turnover | 1.01% | Average daily portfolio turnover |
| Total Return | 229.66% | Cumulative return over full period |
| # Rebalances | 122 | Number of rebalancing / regime-switch events |
