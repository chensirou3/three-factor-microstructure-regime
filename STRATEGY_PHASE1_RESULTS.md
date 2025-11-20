# Strategy Phase 1 Results: Regime-aware Baseline Strategy

**Date**: 2025-11-20  
**Status**: ✅ **COMPLETE**  
**Strategy**: EMA Crossover (20/50) with Three-Factor Regime Gating & Sizing

---

## 🎯 Executive Summary

Successfully implemented and backtested a regime-aware baseline strategy across 6 symbols on 4h timeframe. The diagnostic framework reveals **how strategy performance varies across different regime states**, providing critical insights for Phase 2 optimization.

### Key Findings

1. **Gating Impact**: Current gating rules (high_pressure, triple_high_box) blocked **0% of entries** across all symbols
   - This suggests our high-risk thresholds may be too conservative
   - Need to analyze actual regime distributions to calibrate gating rules

2. **Performance by Risk Regime** (BTCUSD 4h example):
   - **High risk**: 27 trades, 37% win rate, mean R = 5.16 ✅ **Best performance**
   - **Low risk**: 23 trades, 30% win rate, mean R = 3.10
   - **Medium risk**: 93 trades, 28% win rate, mean R = 2.64

3. **Surprising Result**: High-risk regimes showed **better** mean R-multiples
   - This is counter-intuitive and warrants deeper investigation
   - Possible explanations:
     - High volatility → larger moves when trend is correct
     - Position sizing may be over-conservative in high-risk regimes
     - Sample size effects (only 27 trades in high-risk)

4. **Baseline vs Regime Comparison**:
   - Regime-aware strategy had **similar or slightly worse** performance
   - This is expected since gating blocked 0% of trades
   - Position sizing differences had minimal impact

---

## 📊 Performance Summary by Symbol

| Symbol | Timeframe | Trades | Return % | Sharpe | Max DD % | Win Rate % |
|--------|-----------|--------|----------|--------|----------|------------|
| BTCUSD | 4h | 144 | 5.78% | 0.246 | -1.81% | 30.56% |
| ETHUSD | 4h | 140 | 0.33% | 0.210 | -0.18% | 30.00% |
| EURUSD | 4h | 253 | -0.00% | -0.042 | -0.00% | 27.67% |
| USDJPY | 4h | 263 | 0.00% | 0.061 | -0.00% | 27.76% |
| XAGUSD | 4h | 241 | 0.03% | 0.099 | -0.01% | 29.88% |
| XAUUSD | 4h | 240 | 0.72% | 0.126 | -0.21% | 30.00% |

**Observations**:
- BTCUSD shows strongest performance (5.78% return)
- Crypto (BTC, ETH) outperforms FX and metals
- Overall win rates ~28-31% (typical for trend-following)
- Low Sharpe ratios suggest high volatility relative to returns

---

## 🔬 Regime-Conditioned Performance Analysis

### BTCUSD 4h - Performance by Risk Regime

| Risk Regime | Trades | Win Rate % | Mean R | Median R | Tail R (p5) | Tail R (p95) | Total PnL |
|-------------|--------|------------|--------|----------|-------------|--------------|-----------|
| **High** | 27 | 37.04% | **5.16** | -0.83 | -3.67 | 43.88 | $1,425 |
| **Low** | 23 | 30.43% | 3.10 | -1.12 | -3.00 | 12.52 | $4,844 |
| **Medium** | 93 | 27.96% | 2.64 | -1.57 | -4.23 | 30.35 | -$533 |

**Key Insights**:
- High-risk regime has **highest mean R** (5.16) but also highest tail risk (p95 = 43.88)
- Medium-risk regime has **most trades** (93) but **negative total PnL**
- Low-risk regime has **highest total PnL** ($4,844) despite lower mean R

### BTCUSD 4h - Performance by Three-Factor Box

| Box | Trades | Win Rate % | Mean R | Total PnL |
|-----|--------|------------|--------|-----------|
| M_low_O_high_V_high | 21 | 33.33% | **6.10** | $1,022 |
| M_low_O_high_V_low | 6 | 66.67% | 3.68 | $886 |
| M_low_O_low_V_low | 101 | 27.72% | 2.67 | $4,623 |
| M_low_O_low_V_high | 16 | 31.25% | 2.45 | -$748 |

**Key Insights**:
- **M_low_O_high_V_high**: Best mean R (6.10) - high OFI + high VolLiq favorable
- **M_low_O_high_V_low**: Highest win rate (66.67%) but small sample (6 trades)
- **M_low_O_low_V_low**: Most common regime (101 trades), positive PnL
- **M_low_O_low_V_high**: Negative PnL - high VolLiq alone may be unfavorable

### Performance by High Pressure

| High Pressure | Trades | Win Rate % | Mean R | Total PnL |
|---------------|--------|------------|--------|-----------|
| False | 144 | 30.56% | 3.19 | $5,783 |
| True | 0 | - | - | - |

**Observation**: No trades occurred during high_pressure = True states
- This explains why gating had 0% block rate
- Need to investigate: Are high_pressure states rare, or is threshold too strict?

---

## 🚨 Critical Observations

### 1. Gating Rules Not Triggered

**Problem**: 0% of entries were blocked by gating rules across all symbols

**Possible Causes**:
- `high_pressure` threshold too strict (never True)
- `triple_high_box` ("M_high_O_high_V_high") extremely rare
- Regime features may not be properly computed

**Action Items**:
- [ ] Check regime feature distributions (histogram of RiskScore, high_pressure frequency)
- [ ] Analyze three_factor_box distribution (how many trades in each box?)
- [ ] Calibrate thresholds based on actual data distribution

### 2. High-Risk Regimes Outperform

**Observation**: High-risk regimes show better mean R than low-risk regimes

**Possible Explanations**:
1. **Volatility Effect**: High-risk = high volatility → larger moves when trend is correct
2. **Position Sizing**: Current sizing (30% in high-risk) may be too conservative
3. **Sample Size**: Only 27 trades in high-risk vs 93 in medium-risk
4. **Regime Definition**: Our "risk" may actually capture "opportunity" not "danger"

**Action Items**:
- [ ] Analyze volatility vs returns in each regime
- [ ] Test different position sizing rules
- [ ] Increase sample size (run on more timeframes)
- [ ] Redefine risk metrics (use tail loss instead of RiskScore?)

### 3. Baseline Strategy Performance

**Observation**: Simple EMA crossover shows mixed results (5.78% on BTC, ~0% on FX)

**Implications**:
- Baseline is working as intended (simple, transparent)
- Crypto shows stronger trends than FX/metals
- Low Sharpe ratios suggest need for better risk management

**Action Items**:
- [ ] This is expected for diagnostic phase
- [ ] Phase 2 should focus on improving baseline alpha, not just regime gating

---

## 📁 Generated Files

### Per-Symbol Results (6 symbols × 6 file types = 36 files)

For each symbol (BTCUSD, ETHUSD, EURUSD, USDJPY, XAGUSD, XAUUSD):

1. **`trades_{symbol}_4h.csv`**: Per-trade log with regime info
   - Columns: entry_time, exit_time, entry_price, exit_price, net_pnl, R_multiple, RiskScore_entry, risk_regime_entry, high_pressure_entry, three_factor_box_entry

2. **`equity_{symbol}_4h.csv`**: Equity curve (timestamp, equity, in_trade)

3. **`summary_{symbol}_4h.csv`**: Overall metrics
   - n_trades, total_return_pct, win_rate_pct, mean_R, median_R, sharpe_ratio, max_drawdown_pct

4. **`perf_by_risk_regime_{symbol}_4h.csv`**: Performance by risk_regime
   - Grouped by: low, medium, high

5. **`perf_by_pressure_{symbol}_4h.csv`**: Performance by high_pressure
   - Grouped by: True, False

6. **`perf_by_box_{symbol}_4h.csv`**: Performance by three_factor_box
   - Grouped by: 8 possible boxes (only shows boxes with ≥5 trades)

### Comparison File

**`compare_baseline_vs_regime.csv`**: Side-by-side comparison
- Columns: symbol, timeframe, baseline_return_pct, regime_return_pct, baseline_sharpe, regime_sharpe, etc.

---

## 🎯 Next Steps for Phase 2

### Immediate Actions (This Week)

1. **Calibrate Gating Thresholds**
   - [ ] Analyze regime feature distributions
   - [ ] Set thresholds to block 10-20% of entries (not 0%)
   - [ ] Re-run backtest with calibrated thresholds

2. **Investigate High-Risk Paradox**
   - [ ] Plot volatility vs returns by regime
   - [ ] Analyze trade duration by regime
   - [ ] Check if high-risk regimes coincide with strong trends

3. **Expand Analysis**
   - [ ] Run on multiple timeframes (1h, 1d) for robustness
   - [ ] Analyze regime persistence (how long do regimes last?)
   - [ ] Cross-asset regime correlation

### Medium-term (Next 2 Weeks)

4. **Improve Baseline Strategy**
   - [ ] Add filters (ADX, volume confirmation)
   - [ ] Optimize EMA parameters per symbol
   - [ ] Test alternative entry/exit rules

5. **Advanced Regime Rules**
   - [ ] Dynamic position sizing based on volatility
   - [ ] Regime-dependent stop-loss
   - [ ] Regime transition signals

6. **ML Integration**
   - [ ] Train logistic regression for tail event prediction
   - [ ] Use ML-based RiskScore instead of simple average
   - [ ] Feature importance analysis

---

## 📝 Technical Notes

### Assumptions
- Execution: Entry/exit at bar close
- Costs: 0% transaction costs, 0% slippage
- Position: Long-only, single-asset
- Sizing: Base size = 1.0, scaled by risk_regime

### Data Coverage
- Timeframe: 4h bars
- Date Range: 2010-2025 (varies by symbol)
- Total Bars: 15,470 (ETHUSD) to 25,404 (USDJPY)

### Code Quality
- ✅ Modular design (baseline, wrapper, backtest separate)
- ✅ Config-driven (easy to modify parameters)
- ✅ Comprehensive logging
- ✅ Regime-conditioned performance analysis

---

**Status**: Phase 1 Complete ✅  
**Next**: Calibrate thresholds and investigate high-risk paradox  
**Timeline**: Phase 2 Sprint 1 starts this week

