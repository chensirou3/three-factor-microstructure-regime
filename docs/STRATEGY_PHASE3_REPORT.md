# Strategy Phase 3: Regime-aware Variants - Experiment Report

**Generated**: Auto-generated from Phase 3 experiments
**Status**: ✅ Complete

---

## 📊 Executive Summary

Phase 3 implements and tests multiple regime-aware strategy variants:

- **V0_baseline**: Original EMA + RiskScore gating (0.70) - for comparison
- **V1_medium_only**: Entries only in MEDIUM regime
- **V2_medium_plus_high_scaled**: Entries in MEDIUM and HIGH, scaled sizing
- **V3_medium_with_high_escape**: MEDIUM entries + dynamic exit on HIGH persistence

**Total Experiments**: 144
**Symbols**: 6
**Timeframes**: 6

---

## 🏆 Variant Rankings

### Overall Performance (by Sharpe-like)

| Rank | Variant | Avg Sharpe | Avg Net R | Tail p5 | Win Rate | Total Trades |
|------|---------|------------|-----------|---------|----------|--------------|
| 1 | V2_medium_plus_high_scaled | 0.0695 | 1.061 | -5.102 | 30.1% | 83801 |
| 2 | V0_baseline | 0.0685 | 0.995 | -5.007 | 29.7% | 96427 |
| 3 | V1_medium_only | 0.0662 | 1.181 | -4.531 | 29.2% | 57584 |
| 4 | V3_medium_with_high_escape | 0.0159 | 0.142 | -3.534 | 42.0% | 57595 |

---

## ⭐ Best Performing Variant

**V2_medium_plus_high_scaled**

- **Sharpe-like**: 0.0695
- **Average Net R**: 1.061
- **Tail Risk (p5)**: -5.102
- **Win Rate**: 30.1%
- **Total Trades**: 83801

---

## 📈 Improvement vs Baseline (V0)

### Average Improvements Across All Symbol×Timeframe Combinations

| Variant | Sharpe Δ | Mean R Δ | Tail p5 Δ |
|---------|----------|----------|-----------|
| V1_medium_only | -0.0023 | +0.186 | +0.476 |
| V2_medium_plus_high_scaled | +0.0010 | +0.067 | -0.095 |
| V3_medium_with_high_escape | -0.0526 | -0.852 | +1.472 |

---

## 🎯 Trade Distribution by Regime

### Percentage of Trades in Each Regime

| Variant | LOW % | MEDIUM % | HIGH % |
|---------|-------|----------|--------|
| V0_baseline | 13.0% | 59.7% | 27.2% |
| V1_medium_only | 0.0% | 100.0% | 0.0% |
| V2_medium_plus_high_scaled | 0.0% | 68.7% | 31.3% |
| V3_medium_with_high_escape | 0.0% | 100.0% | 0.0% |

---

## 📊 Performance by Symbol

### Best Variant for Each Symbol (by Sharpe-like)

| Symbol | Best Variant | Sharpe | Net Mean R |
|--------|--------------|--------|------------|
| BTCUSD | V1_medium_only | 0.4659 | 14.341 |
| ETHUSD | V1_medium_only | 0.3481 | 8.292 |
| EURUSD | V3_medium_with_high_escape | 0.0527 | 0.140 |
| USDJPY | V1_medium_only | 0.2917 | 4.575 |
| XAGUSD | V0_baseline | 0.0986 | 0.603 |
| XAUUSD | V3_medium_with_high_escape | 0.2545 | 0.841 |

---

## 💡 Recommendations

1. **Primary Strategy**: Use **V2_medium_plus_high_scaled** for best risk-adjusted returns
2. **Regime Focus**: Results confirm Phase 2 findings - MEDIUM regime is optimal
3. **Dynamic Management**: Consider V3's dynamic exit approach for tail risk control

---

**Report Generated**: Phase 3 Experiment Framework
**Next Steps**: Review detailed results and select optimal variant for live trading