# Strategy Comparison

**Backtest period:** 2008-01-03 to 2026-04-16

## Performance Summary

| Metric | S1: 50/50 Threshold 10% | S2: Buy & Hold 100% | S3: Dynamic 15%/5% | S4: Monthly Rebalance | S5: MA Timing 200d | S6: 50/50 Threshold 5% | S7: 50/50 Threshold 20% |
|--------| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Sharpe Ratio | 0.5487 | 0.5039 | 0.5561 | **0.5586** ★ | 0.5506 | 0.5534 | 0.5578 |
| Annual Return | 6.22% | **11.36%** ★ | 6.37% | 6.22% | 7.14% | 6.29% | 6.30% |
| Volatility | 11.33% | 22.55% | 11.45% | **11.14%** ★ | 12.98% | 11.37% | 11.29% |
| Max Drawdown | -35.54% | **-61.04%** ★ | -35.30% | -35.81% | -26.45% | -35.30% | -35.59% |
| Calmar Ratio | 0.1749 | 0.1862 | 0.1803 | 0.1738 | **0.2701** ★ | 0.1783 | 0.1770 |
| Sortino Ratio | 0.6810 | 0.6263 | 0.6909 | 0.6955 | 0.6031 | 0.6857 | **0.6968** ★ |
| Avg Turnover | 0.98% | 2.15% | 1.01% | **0.98%** ★ | 3.66% | 1.00% | 0.99% |
| Total Return | 220.86% | **700.99%** ★ | 229.66% | 221.34% | 279.64% | 225.37% | 225.67% |
| # Rebalances / Switches | 51 | **0** ★ | 122 | 232 | 117 | 200 | 17 |

## Strategy Descriptions

### Strategy 1: 50/50 Threshold Rebalancing (10%)

Hold 50% in a market-cap-weighted S&P 500 basket and 50% in cash. Rebalance back to 50/50 whenever the SPX index moves ±10% from the price at the last rebalance. Between rebalance events the portfolio drifts freely — no daily trading.

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

### Strategy 6: 50/50 Threshold Rebalancing (5%)

Identical to Strategy 1 but with a tighter ±5% rebalance trigger. The portfolio rebalances back to 50/50 more frequently, keeping the allocation closer to target at the cost of more trades.

### Strategy 7: 50/50 Threshold Rebalancing (20%)

Identical to Strategy 1 but with a wider ±20% rebalance trigger. The portfolio is rebalanced back to 50/50 less frequently, allowing larger allocation drifts while minimising transaction costs.
