# Current Method vs SPY: Key Differences

## The Three Things Being Compared

### 1. S&P 500 Index

A **number**, not something you can directly buy.

- Calculated daily by S&P Global, tracking the 500 largest US-listed companies
- **Market-cap weighted**: larger companies have more influence (Apple, Microsoft, NVIDIA each ~6–7%)
- You cannot invest in the index directly — you need a financial product that tracks it

---

### 2. SPY (S&P 500 ETF)

An exchange-traded fund issued by State Street Corporation.

- Trades on the stock exchange just like a regular stock
- Holds the actual 500 constituent stocks in market-cap-weighted proportions
- Goal: replicate the S&P 500 index return as closely as possible
- Annual management fee: 0.0945% (negligible)
- **In practice, SPY ≈ S&P 500 index** — daily return differences are typically less than 0.01%

---

### 3. Our Backtest Method (Equal-Weight SPX500 Basket)

An approximation built around the constraints of the Quantiacs data format.

Instead of a single SPY position, we:

1. Load all S&P 500 constituent stocks with full OHLCV data
2. Spread the equity allocation equally across all liquid constituent stocks each day
3. Use the SPX index price series as the rebalancing signal

---

## Comparison Table

| Dimension | SPY | Our Method |
|-----------|-----|------------|
| **Weighting** | Market-cap weighted (Apple ~7%) | **Equal-weight** (~0.2% per stock) |
| **Constituent updates** | Tracks official index in real time | Approximated via Quantiacs `is_liquid` field |
| **Internal rebalancing** | Handled inside the fund, near-zero cost | Equal-weight reset applied daily → generates turnover |
| **Management fee** | 0.09% / year (already in price) | None (slippage model applied instead) |
| **Dividends** | Reinvested, reflected in adjusted price | Calculated via `divs` field in Quantiacs |
| **Available history** | 1993 (SPY inception) to present | ~2000 to present (Quantiacs data) |

---

## The Biggest Difference: Equal-Weight vs Market-Cap Weight

**SPY (market-cap weighted)**
- Companies that grow larger automatically receive a higher weight
- Over the past 20 years, mega-cap tech stocks (Apple, Microsoft, NVIDIA) dramatically outperformed
- This tailwind is captured by market-cap weighting

**Our method (equal-weight)**
- All 500 companies receive the same weight regardless of size
- Smaller companies have proportionally more influence
- Long-term returns tend to be **slightly lower** than cap-weighted because it misses the mega-cap tech boom

**Practical implication**: our backtest likely **understates** the returns an investor would have achieved by simply holding SPY over the same period.

---

## Why Our Method Calculates Slippage — and Why SPY Would Not

### What is slippage?

When you place an order, the actual execution price is typically slightly worse than the quoted price:

- You intend to buy at $100 → you actually pay $100.05
- You intend to sell at $100 → you actually receive $99.95

The gap comes from two sources:
1. **Bid-ask spread** — the difference between the best buy and sell quotes in the market
2. **Market impact** — a large order moves the price against you

### Why our basket method incurs meaningful slippage

Every rebalance involves trading **~500 individual stocks**:

- Each stock has its own liquidity profile — smaller companies have wider spreads
- Every rebalancing event, every index constituent change (additions/removals) generates trades
- Even a modest 1.09% daily turnover compounds to ~274% annual turnover across all positions
- Quantiacs estimates slippage per stock using ATR (Average True Range), which reflects each stock's typical intraday price movement

### Why SPY would have negligible slippage

| | 500-stock basket | SPY |
|--|--|--|
| Trades per rebalance | ~500 | **1** |
| Liquidity | Varies (some small-caps are illiquid) | Extremely high |
| Daily traded volume | — | ~$80 billion USD |
| Bid-ask spread | Can be 0.1%+ for small caps | **< 0.01%** |
| Market impact | Exists | Near zero for typical investor sizes |

SPY is one of the most liquid financial instruments in the world. For any normal investment size, the slippage cost of buying or selling SPY is effectively zero.

---

## Summary

| Question | Answer |
|----------|--------|
| Are SPY and the S&P 500 index the same? | Practically yes — differences are < 0.01%/day |
| Is our basket the same as SPY? | No — it is equal-weight, not cap-weighted |
| Does our method over- or understate costs? | Slippage is likely **overstated** (500 stocks traded vs 1) |
| Does our method over- or understate returns? | Returns are likely **understated** (misses mega-cap tech outperformance) |
| Would a SPY-based backtest need slippage? | No — it can be safely ignored for typical investment sizes |

The results produced by this backtest framework are best used for **comparing strategies against each other** (relative performance). The absolute return figures should be treated as conservative estimates relative to what an investor would actually achieve by holding SPY.
