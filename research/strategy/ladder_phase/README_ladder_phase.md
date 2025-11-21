# Stage L2: Ladder + Three-Factor Regime Integration

## Overview

Stage L2 integrates the **Ladder trend indicator** with the **three-factor regime framework**, creating a parallel pipeline to the EMA-based Phase 3 strategy.

**Goal**: Compare Ladder vs EMA as trend engines under the same regime framework.

---

## Ladder Indicator

### Definition

- **Fast Bands** (25-period): `fastU = EMA(high, 25)`, `fastL = EMA(low, 25)`
- **Slow Bands** (90-period): `slowU = EMA(high, 90)`, `slowL = EMA(low, 90)`

### Trend States

- **upTrend**: `close > fastU AND close > slowU` (strong bullish)
- **downTrend**: `close < fastL AND close < slowL` (strong bearish)
- **neutral**: Neither upTrend nor downTrend

### Trading Logic

- **Long**: Enter when `upTrend == True`
- **Flat**: Exit when `upTrend == False`
- **No short positions** (long-only)

---

## Regime Policies

Reuses the same regime policies from Phase 3:

### L_V0_baseline
- Ladder + RiskScore gating (0.70)
- No extra regime logic
- Baseline for comparison

### L_V1_medium_only
- Entries only in MEDIUM regime
- Conservative approach
- Avoids HIGH and LOW risk states

### L_V2_medium_plus_high_scaled
- Entries in MEDIUM (full size) and HIGH (50% size)
- Balanced risk/reward
- **Expected best performer** (based on Phase 3 results)

---

## Workflow

### 1. Generate Ladder Features
```bash
python3 research/ladder/ladder_features.py
```
- Input: `data/factors/merged_three_factor/merged_{symbol}_{timeframe}.parquet`
- Output: `data/ladder_features/ladder_{symbol}_{timeframe}.parquet`

### 2. Run Ladder + Regime Experiments
```bash
python3 research/strategy/ladder_phase/ladder_experiment_runner.py
```
- Runs 3 variants × 6 symbols × 6 timeframes = **108 experiments**
- Output: `results/strategy/ladder_phase/{variant_id}/`

### 3. Analyze Performance
```bash
python3 research/strategy/ladder_phase/ladder_performance_analysis.py
```
- Aggregates Ladder results
- Loads EMA Phase 3 results
- Generates `ladder_vs_ema_summary.csv`
- Creates comparison report

---

## Expected Outputs

### Results Directory Structure
```
results/strategy/ladder_phase/
├── L_V0_baseline/
│   ├── trades_{symbol}_{timeframe}.csv
│   ├── equity_{symbol}_{timeframe}.csv
│   └── summary_{symbol}_{timeframe}.csv
├── L_V1_medium_only/
│   └── ...
├── L_V2_medium_plus_high_scaled/
│   └── ...
└── ladder_vs_ema_summary.csv
```

### Comparison Report
- `LADDER_VS_EMA_COMPARISON.md`: High-level comparison
- `ladder_vs_ema_summary.csv`: Detailed results for all experiments

---

## Key Questions to Answer

1. **Which trend engine is better overall?**
   - Ladder vs EMA average performance

2. **Which symbols favor Ladder?**
   - Symbol-specific performance comparison

3. **Which timeframes favor Ladder?**
   - Timeframe-specific performance comparison

4. **Does Ladder + V2 beat EMA + V2?**
   - Best variant comparison

5. **Under what conditions is Ladder superior?**
   - Regime-specific, volatility-specific analysis

---

## Module Structure

```
research/strategy/ladder_phase/
├── __init__.py
├── README_ladder_phase.md
├── config_ladder_phase.yaml
├── ladder_strategy_signals.py       # Ladder signal generator
├── ladder_regime_variants.py        # Apply regime policies to Ladder
├── ladder_experiment_runner.py      # Run all experiments
└── ladder_performance_analysis.py   # Compare Ladder vs EMA
```

---

## Dependencies

- **Stage L1**: Ladder features must be generated first
- **Phase 3**: EMA results for comparison
- **Regime framework**: Three-factor regime features in merged data

---

## Next Steps

After Stage L2 completion:
1. Review `ladder_vs_ema_summary.csv`
2. Identify which trend engine is superior
3. Make final recommendation for production deployment

