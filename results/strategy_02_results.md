# Strategy 2: 100% S&P500 Buy & Hold (Benchmark)

## Description

Hold 100% of capital in an equal-weight S&P 500 basket at all times. No cash buffer, no market-timing, no threshold rebalancing. This represents the maximum equity exposure and acts as the benchmark against which risk-managed strategies are evaluated.

## Parameters

| Parameter | Value |
|-----------|-------|
| Target Allocation | 100% stocks / 0% cash |
| Rebalance Rule | None (stocks rebalanced to equal-weight daily within index) |
| Stock Universe | S&P 500 constituents (equal-weight, liquid only) |

## Backtest Results (2007-01-03 to 2026-04-09)

| Metric | Value | Description |
|--------|-------|-------------|
| Sharpe Ratio | 0.4395 | Risk-adjusted return (higher is better) |
| Annual Return | 9.41% | Geometric annualized return |
| Volatility | 21.42% | Annualized std dev of daily returns |
| Max Drawdown | -61.08% | Worst peak-to-trough loss |
| Calmar Ratio | 0.1541 | Annual Return / |Max Drawdown| |
| Sortino Ratio | 0.5380 | Sharpe using downside volatility only |
| Avg Turnover | 2.37% | Average daily portfolio turnover |
| Total Return | 464.25% | Cumulative return over full period |
| # Rebalances | 0 | Number of rebalancing events |
