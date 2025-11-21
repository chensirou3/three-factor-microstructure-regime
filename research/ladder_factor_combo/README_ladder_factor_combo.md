# Ladder × Three-Factor Integration

## 📋 Overview

This module explores **four directions** for integrating the Ladder trend indicator with three microstructure factors, **without changing Ladder parameters (25/90)**.

### Background

- **Ladder Indicator**: EMA bands on high/low prices
  - Fast bands: `fastU = EMA(high, 25)`, `fastL = EMA(low, 25)`
  - Slow bands: `slowU = EMA(high, 90)`, `slowL = EMA(low, 90)`
  - Trend states: `upTrend`, `downTrend`, `neutral`

- **Three Factors**:
  - `ManipScore_z`: Manipulation detection
  - `OFI_z` / `OFI_abs_z`: Order flow imbalance
  - `VolLiqScore`: Volume/liquidity stress

- **Previous Results**:
  - Stage L1 (Ladder-only): Avg +15.75%, Sharpe 0.0469
  - Stage L2 (Ladder + EMA-style Regime): Avg -5.34%, Sharpe -0.0126
  - **Conclusion**: Direct application of EMA Regime policies hurt Ladder performance

---

## 🎯 Four Directions

### Direction 1: Segment-level Quality Analysis (段级别"体检")

**Goal**: Identify which Ladder trends are "healthy" vs "unhealthy" based on factor characteristics.

**Approach**:
1. Extract all Ladder trend segments (continuous upTrend/downTrend periods)
2. Record factor values at segment start
3. Analyze segment performance by factor bins
4. Define "healthy trend" criteria

**Output**:
- `segments_all.csv`: All extracted Ladder segments
- `segments_factor_stats.csv`: Performance statistics by factor bins
- Criteria for "healthy" vs "unhealthy" trends

---

### Direction 2: Entry Filtering & Position Sizing (因子决定"做/不做、做多大")

**Goal**: Use factors to filter Ladder entries and adjust position size.

**Approach**:
- Ladder determines direction (upTrend → long)
- Factors determine:
  - **Filter**: Should we enter this Ladder signal?
  - **Size**: How much position size?

**Variants**:
1. **D2_plain_ladder**: Baseline (no factor filtering)
2. **D2_healthy_only**: Only enter on "healthy" Ladder trends
3. **D2_size_by_health**: Scale position by health (healthy=1.0, suspicious=0.5, unhealthy=0.0)

**"Healthy" Criteria** (from Direction 1 analysis):
- `|ManipScore_z| < 1.0`
- `q_vol < 0.85`
- `OFI_z >= -0.5` (for upTrend)

---

### Direction 3: Multi-Timeframe Timing (高周期定方向，低周期择时)

**Goal**: High timeframe Ladder for direction, low timeframe + factors for precise timing.

**Approach**:
- High TF (4h/1d): Ladder determines trend direction
- Low TF (30min/1h): Factor-based entry timing
  - Only enter when high-TF Ladder is in upTrend
  - Use low-TF factor conditions for precise entry

**Variants**:
1. **D3_ladder_high_tf_dir_only**: Simple high-TF direction filter
2. **D3_ladder_high_tf_dir_and_factor_pullback**: High-TF direction + low-TF factor pullback timing

**Pullback Conditions**:
- `q_vol` in neutral range [0.3, 0.7]
- `OFI_z` turning positive (>= -0.5)
- `RiskScore` not too high (< 0.7)

---

### Direction 4: Factor-Based Exit Rules (因子管退出/止盈)

**Goal**: Ladder controls entry, factors trigger exits or partial profit-taking.

**Approach**:
- Entry: Pure Ladder (unchanged)
- Exit: Monitor factors during position
  - Trigger on extreme factor conditions

**Variants**:
1. **D4_exit_on_extreme_factors**: Full exit when extreme factors detected
2. **D4_partial_takeprofit_on_extreme**: Partial exit (50%) when extreme factors detected

**Extreme Conditions**:
- `RiskScore > 0.90`
- `|ManipScore_z| > 2.0`
- `q_vol > 0.95`

---

## 📂 Module Structure

```
ladder_factor_combo/
├── __init__.py
├── config_ladder_factor.yaml           # Configuration for all 4 directions
├── README_ladder_factor_combo.md       # This file
│
├── segments_extractor.py               # D1: Extract Ladder trend segments
├── segments_factor_stats.py            # D1: Factor-based segment analysis
│
├── entry_filter_and_sizing.py          # D2: Factor-based entry filters & sizing
├── mtf_timing.py                       # D3: Multi-timeframe integration
├── exit_rules.py                       # D4: Factor-based exit management
│
├── combo_backtests.py                  # Run backtests for all variants
├── combo_aggregate.py                  # Aggregate & compare results
└── combo_report.py                     # Generate final report
```

---

## 🚀 Execution Order

1. **Direction 1** (Segment Analysis):
   ```bash
   python research/ladder_factor_combo/segments_extractor.py
   python research/ladder_factor_combo/segments_factor_stats.py
   ```
   → Generates `segments_factor_stats.csv` for "healthy" criteria

2. **Direction 2** (Entry Filtering):
   ```bash
   # Implemented in combo_backtests.py
   ```
   → Test on BTCUSD 4h/1d first

3. **Direction 4** (Exit Rules):
   ```bash
   # Implemented in combo_backtests.py
   ```
   → Apply to Ladder-only baseline

4. **Direction 3** (MTF Timing):
   ```bash
   # Implemented in combo_backtests.py
   ```
   → Test BTCUSD (4h high, 30min/1h low)

5. **Aggregate & Report**:
   ```bash
   python research/ladder_factor_combo/combo_aggregate.py
   python research/ladder_factor_combo/combo_report.py
   ```

---

## 📊 Expected Outputs

- `results/ladder_factor_combo/segments_all.csv`
- `results/ladder_factor_combo/segments_factor_stats.csv`
- `results/ladder_factor_combo/direction2/D2_*/` (backtest results)
- `results/ladder_factor_combo/direction3/D3_*/` (backtest results)
- `results/ladder_factor_combo/direction4/D4_*/` (backtest results)
- `results/ladder_factor_combo/aggregate_*.csv`
- `LADDER_FACTOR_COMBO_COMPLETE_REPORT.md`

---

## 🎯 Key Questions to Answer

1. **Direction 1**: What factor characteristics define "healthy" Ladder trends?
2. **Direction 2**: Does filtering Ladder entries by factor health improve performance?
3. **Direction 3**: Does MTF timing (high-TF direction + low-TF factors) add value?
4. **Direction 4**: Do factor-based exits reduce tail risk without sacrificing returns?

---

**Note**: This module is **non-destructive** and coexists with existing EMA/Ladder/Regime pipelines.

