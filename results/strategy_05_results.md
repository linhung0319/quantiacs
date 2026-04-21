# Strategy 5: MA Market Timing (200-day)

## Description

Use the SPX 200-day simple moving average as a market regime filter. When SPX is above the 200d MA (bullish trend), hold 100% in an equal-weight S&P 500 basket. When SPX is below (bearish), move entirely to cash. Signal is computed at close and executed at the next open. Unlike Strategies 1-4 there is no fixed 50/50 split — this is a binary 'risk-on / risk-off' approach.

## Parameters

| Parameter | Value |
|-----------|-------|
| Bull Allocation | 100% stocks (SPX > 200d MA) |
| Bear Allocation | 0% stocks / 100% cash (SPX < 200d MA) |
| MA Period | 200 trading days (~10 months) |
| Signal | SPX daily close vs. 200-day SMA |
| Execution | Signal at close t → trade at open t+1 |
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
| Sharpe Ratio | 0.5506 | Risk-adjusted return (higher is better) |
| Annual Return | 7.14% | Geometric annualized return (CAGR) |
| Volatility | 12.98% | Annualized std dev of daily returns |
| Max Drawdown | -26.45% | Worst peak-to-trough loss |
| Calmar Ratio | 0.2701 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.6031 | Sharpe using downside volatility only |
| Avg Turnover | 3.66% | Average daily portfolio turnover |
| Total Return | 279.64% | Cumulative return over full period |
| # Rebalances | 117 | Number of rebalancing / regime-switch events |
