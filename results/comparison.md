# Strategy Comparison

**Backtest period:** 2007-01-03 to 2026-04-09

## Performance Summary

| Metric | S1: 50/50 Threshold 10% | S2: Buy & Hold 100% | S3: Dynamic 15%/5% | S4: Monthly Rebalance | S5: MA Timing 200d |
|--------| :---: | :---: | :---: | :---: | :---: |
| Sharpe Ratio | 0.4803 | 0.4395 | 0.4847 | **0.4932** ★ | 0.4733 |
| Annual Return | 5.17% | **9.41%** ★ | 5.26% | 5.21% | 5.84% |
| Volatility | 10.75% | 21.42% | 10.86% | **10.56%** ★ | 12.33% |
| Max Drawdown | -35.73% | **-61.08%** ★ | -35.81% | -35.93% | -24.36% |
| Calmar Ratio | 0.1445 | 0.1541 | 0.1470 | 0.1449 | **0.2396** ★ |
| Sortino Ratio | 0.5855 | 0.5380 | 0.5918 | **0.6049** ★ | 0.5428 |
| Avg Turnover | 1.09% | 2.37% | 1.12% | **1.09%** ★ | 4.09% |
| Total Return | 163.45% | **464.25%** ★ | 168.23% | 165.42% | 197.76% |
| # Rebalances / Switches | 52 | **0** ★ | 116 | 244 | 127 |

## Strategy Descriptions

### Strategy 1: 50/50 Threshold Rebalancing (10%)

Hold 50% in an equal-weight S&P 500 basket and 50% in cash. Rebalance back to 50/50 whenever the SPX index moves ±10% from the price at the last rebalance. Between rebalance events the portfolio drifts freely — no daily trading.

### Strategy 2: 100% S&P500 Buy & Hold (Benchmark)

Hold 100% of capital in an equal-weight S&P 500 basket at all times. No cash buffer, no market-timing, no threshold rebalancing. This represents the maximum equity exposure and acts as the benchmark against which risk-managed strategies are evaluated.

### Strategy 3: 50/50 Dynamic Threshold (Bull 15% / Bear 5%)

Same 50/50 allocation as Strategy 1, but the rebalance trigger adapts to the market regime detected by the 200-day moving average of SPX:
- Bull market (SPX > 200d MA): rebalance only when SPX moves ±15% (let winners run longer).
- Bear market (SPX < 200d MA): rebalance at ±5% (act more defensively to limit drawdown).

### Strategy 4: 50/50 Monthly Calendar Rebalancing

Hold 50% in an equal-weight S&P 500 basket and 50% in cash. Rebalance back to 50/50 on the first trading day of every calendar month, regardless of how much the market has moved. Compares fixed-calendar rebalancing against threshold-based approaches.

### Strategy 5: MA Market Timing (200-day)

Use the SPX 200-day simple moving average as a market regime filter. When SPX is above the 200d MA (bullish trend), hold 100% in an equal-weight S&P 500 basket. When SPX is below (bearish), move entirely to cash. Signal is computed at close and executed at the next open. Unlike Strategies 1-4 there is no fixed 50/50 split — this is a binary 'risk-on / risk-off' approach.
