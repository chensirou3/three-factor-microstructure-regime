# Strategy Phase 4: Account-level Performance with Realistic Costs

**Generated**: 2025-11-21 10:01:43
**Status**: ✅ Complete

---

## 📊 Executive Summary

Phase 4 evaluates strategy performance from a **realistic account perspective**,
incorporating actual transaction costs and computing practical metrics.

**Key Questions Answered:**
- How do different cost structures (0.003% vs 0.07%) impact performance?
- Which symbols/timeframes remain profitable under high costs?
- Should we use V2 (aggressive) or V1 (conservative) for each account?

---

## 💰 Account Configurations

### LOW_COST
- **Description**: Account A with ~0.003% per-side cost (institutional/low-fee exchange)
- **Cost per side**: 0.003%
- **Round-trip cost**: 0.006%
- **Initial equity**: $10,000

### HIGH_COST
- **Description**: Account B with ~0.07% per-side cost (retail/high-fee exchange)
- **Cost per side**: 0.07%
- **Round-trip cost**: 0.14%
- **Initial equity**: $10,000

---

## 🏆 Overall Performance by Account × Variant

### Summary Table

| Account | Variant | Total Trades | Ann Return | Max DD | Sharpe | Win Rate |
|---------|---------|--------------|------------|--------|--------|----------|
| low_cost | V2_medium_plus_high_scaled | 13,551 | 1.28% | -26.08% | 0.1027 | 31.3% |
| low_cost | V1_medium_only | 9,321 | 1.11% | -42.59% | 0.0988 | 30.8% |
| high_cost | V2_medium_plus_high_scaled | 13,551 | 0.91% | -28.83% | 0.0342 | 29.0% |
| high_cost | V1_medium_only | 9,321 | 0.79% | -45.11% | 0.0268 | 28.5% |

---

## ⭐ Best Performing Combinations

### LOW_COST - Top 5 by Annualized Return

| Variant | Symbol | Timeframe | Ann Return | Max DD | Trades |
|---------|--------|-----------|------------|--------|--------|
| V1_medium_only | BTCUSD | 1d | 9.21% | -7.65% | 16 |
| V2_medium_plus_high_scaled | BTCUSD | 1d | 8.93% | -7.71% | 19 |
| V2_medium_plus_high_scaled | BTCUSD | 30min | 7.87% | -17.40% | 1,045 |
| V2_medium_plus_high_scaled | BTCUSD | 1h | 7.67% | -12.43% | 496 |
| V1_medium_only | BTCUSD | 30min | 7.20% | -17.71% | 761 |

### HIGH_COST - Top 5 by Annualized Return

| Variant | Symbol | Timeframe | Ann Return | Max DD | Trades |
|---------|--------|-----------|------------|--------|--------|
| V1_medium_only | BTCUSD | 1d | 9.17% | -7.72% | 16 |
| V2_medium_plus_high_scaled | BTCUSD | 1d | 8.89% | -7.78% | 19 |
| V2_medium_plus_high_scaled | BTCUSD | 1h | 6.06% | -17.03% | 496 |
| V1_medium_only | BTCUSD | 1h | 5.69% | -17.69% | 360 |
| V2_medium_plus_high_scaled | BTCUSD | 30min | 4.31% | -26.98% | 1,045 |

---

## 📈 Performance by Symbol

### HIGH_COST × V1_medium_only

| Symbol | Ann Return | Max DD | Sharpe | Trades |
|--------|------------|--------|--------|--------|
| BTCUSD | 4.34% | -45.11% | 0.2350 | 1,230 |
| ETHUSD | 0.27% | -2.38% | 0.1947 | 1,129 |
| XAUUSD | 0.14% | -10.70% | 0.0565 | 1,682 |
| USDJPY | -0.00% | -0.01% | 0.0013 | 1,855 |
| EURUSD | -0.00% | -0.02% | -0.2303 | 1,719 |
| XAGUSD | -0.00% | -0.33% | -0.0965 | 1,706 |

### HIGH_COST × V2_medium_plus_high_scaled

| Symbol | Ann Return | Max DD | Sharpe | Trades |
|--------|------------|--------|--------|--------|
| BTCUSD | 5.11% | -28.83% | 0.2223 | 1,680 |
| ETHUSD | 0.28% | -2.57% | 0.1750 | 1,539 |
| XAUUSD | 0.06% | -13.19% | 0.0488 | 2,559 |
| USDJPY | -0.00% | -0.02% | -0.0120 | 2,603 |
| EURUSD | -0.00% | -0.02% | -0.2270 | 2,605 |
| XAGUSD | -0.00% | -0.39% | -0.0020 | 2,565 |

### LOW_COST × V1_medium_only

| Symbol | Ann Return | Max DD | Sharpe | Trades |
|--------|------------|--------|--------|--------|
| BTCUSD | 5.63% | -42.59% | 0.2477 | 1,230 |
| XAUUSD | 0.69% | -6.31% | 0.1283 | 1,682 |
| ETHUSD | 0.36% | -1.95% | 0.2080 | 1,129 |
| XAGUSD | 0.00% | -0.18% | -0.0490 | 1,706 |
| USDJPY | 0.00% | -0.00% | 0.1187 | 1,855 |
| EURUSD | -0.00% | -0.00% | -0.0612 | 1,719 |

### LOW_COST × V2_medium_plus_high_scaled

| Symbol | Ann Return | Max DD | Sharpe | Trades |
|--------|------------|--------|--------|--------|
| BTCUSD | 6.56% | -26.08% | 0.2355 | 1,680 |
| XAUUSD | 0.75% | -5.52% | 0.1172 | 2,559 |
| ETHUSD | 0.38% | -2.03% | 0.1875 | 1,539 |
| XAGUSD | 0.01% | -0.19% | 0.0400 | 2,565 |
| USDJPY | 0.00% | -0.00% | 0.1040 | 2,603 |
| EURUSD | -0.00% | -0.00% | -0.0678 | 2,605 |

---

## 💸 Cost Sensitivity Analysis

Comparing performance between low_cost and high_cost accounts:

### V2_medium_plus_high_scaled
- **Low cost return**: 1.28%
- **High cost return**: 0.91%
- **Performance drop**: 0.37% (29.2% relative)

### V1_medium_only
- **Low cost return**: 1.11%
- **High cost return**: 0.79%
- **Performance drop**: 0.32% (28.8% relative)

---

## 💡 Recommendations

### Primary Recommendation
- **Account**: low_cost
- **Strategy**: V2_medium_plus_high_scaled
- **Expected Ann Return**: 1.28%
- **Max Drawdown**: -26.08%
- **Sharpe Ratio**: 0.1027

### Recommended Symbols
- **BTCUSD**: 6.56% ann return
- **XAUUSD**: 0.75% ann return
- **ETHUSD**: 0.38% ann return

### Timeframe Recommendations
- **For low_cost account**: All timeframes (30min-1d) viable
- **For high_cost account**: Prefer longer timeframes (4h-1d) to reduce cost impact

---

**Report Generated**: Phase 4 Account-level Performance Analysis
**Next Steps**: Review equity curves and select optimal configurations for live trading