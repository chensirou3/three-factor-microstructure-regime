# Strategy Phase 2: Optimization & Deep Analysis

**策略第二阶段：优化与深度分析**

---

## 📋 Overview / 概述

**English:**
Phase 2 builds on Phase 1's diagnostic baseline strategy to create a more effective regime-aware trading system. We address the key findings from Phase 1:
- Gating rules never triggered (0% block rate)
- "High risk" regime paradoxically showed better performance than "low risk"
- Need for tail-risk analysis beyond mean returns
- Opportunity for per-symbol parameter optimization

**中文:**
第二阶段在第一阶段诊断性基线策略的基础上，构建更有效的regime感知交易系统。我们解决第一阶段的关键发现：
- Gating规则从未触发（0%阻挡率）
- "高风险"regime矛盾地表现优于"低风险"
- 需要超越平均收益的尾部风险分析
- 针对不同标的优化参数的机会

---

## 🎯 Phase 2 Sub-Phases / 子阶段

### **Phase 2A: Threshold Calibration / 阈值校准**

**Goal / 目标:**
Make gating rules actually work by calibrating RiskScore thresholds based on empirical distribution.

**Module:** `threshold_calibration.py`

**Key Functions:**
- `load_all_trades()` - Load all Phase 1 trade logs
- `analyze_riskscore_distribution()` - Compute RiskScore quantiles
- `evaluate_candidate_thresholds()` - Test different threshold values
- `update_high_riskscore_in_config()` - Update config with new threshold
- `compare_baseline_vs_phase2()` - Compare before/after metrics

**Outputs:**
- `riskscore_distribution.csv` - RiskScore distribution statistics
- `threshold_blockable_rates.csv` - Block rates for each candidate threshold
- `compare_baseline_vs_phase2.csv` - Performance comparison

---

### **Phase 2B: Regime Tail-Risk Analysis / Regime尾部风险分析**

**Goal / 目标:**
Characterize regimes by tail risk (not just mean returns) to resolve the "high risk = high return" paradox.

**Module:** `regime_tailrisk_analysis.py`

**Key Functions:**
- `compute_tail_stats_by_risk_regime()` - Tail statistics by risk regime
- `compute_tail_stats_by_pressure()` - Tail statistics by high_pressure
- `compute_tail_stats_by_box()` - Tail statistics by three_factor_box
- `aggregate_tail_stats()` - Aggregate across all symbol×timeframe

**Metrics Computed:**
- `mean_R`, `median_R` - Central tendency
- `std_R` - Volatility
- `p1_R`, `p5_R` - Left tail (worst outcomes)
- `p95_R`, `p99_R` - Right tail (best outcomes)
- `win_rate` - Percentage of winning trades

**Outputs:**
- `tailrisk_by_risk_regime_{symbol}_{timeframe}.csv`
- `tailrisk_by_pressure_{symbol}_{timeframe}.csv`
- `tailrisk_by_box_{symbol}_{timeframe}.csv`
- `tailrisk_aggregated.csv` - Global statistics

---

### **Phase 2C: Strategy Tuning & Cost Model / 策略调优与成本模型**

**Goal / 目标:**
Improve strategy performance through per-symbol parameter optimization and realistic cost modeling.

**Module:** `strategy_tuning.py`

**Key Features:**
1. **Per-Symbol EMA Parameters** - Different fast/slow lengths for different symbols
2. **Transaction Cost Model** - Fees + slippage (configurable basis points)
3. **Grid Search** (optional) - Systematic parameter optimization
4. **Focus on Best Timeframes** - 30min-1d range for efficiency

**Key Functions:**
- `get_strategy_params()` - Retrieve per-symbol/timeframe parameters
- `apply_transaction_costs()` - Deduct costs from PnL
- `run_grid_search()` - Systematic parameter search
- `compare_gross_vs_net()` - Compare before/after cost metrics

**Outputs:**
- `tuning_{symbol}_{timeframe}.csv` - Grid search results
- `cost_impact_analysis.csv` - Cost impact on performance
- `optimal_params.yaml` - Recommended parameters

---

### **Phase 2D: Regime Persistence & Transition Analysis / Regime持续性与转换分析**

**Goal / 目标:**
Understand regime dynamics to inform future strategy rules (e.g., "exit if regime deteriorates during holding").

**Module:** `regime_persistence_analysis.py`

**Key Functions:**
- `compute_regime_durations()` - Duration distribution of each regime
- `build_transition_matrix()` - Regime transition probabilities
- `analyze_entry_vs_holding_regime()` - Compare entry vs holding regime patterns
- `identify_regime_switches()` - Detect regime changes during trades

**Analyses:**
1. **Duration Analysis** - How long does each regime last?
2. **Transition Matrix** - Probability of regime changes
3. **Entry vs Holding** - Does regime change during trade affect performance?

**Outputs:**
- `regime_durations_{symbol}_{timeframe}.csv`
- `regime_transition_matrix_{symbol}_{timeframe}.csv`
- `entry_vs_holding_regime_{symbol}_{timeframe}.csv`
- `regime_persistence_summary.csv`

---

## 📂 Directory Structure / 目录结构

```
research/strategy/phase2/
├── __init__.py
├── config_phase2.yaml                    # Phase 2 configuration
├── README_phase2.md                      # This file
├── threshold_calibration.py              # Phase 2A
├── regime_tailrisk_analysis.py           # Phase 2B
├── strategy_tuning.py                    # Phase 2C
└── regime_persistence_analysis.py        # Phase 2D

results/strategy/phase2/
├── threshold_calibration/                # Phase 2A outputs
├── tailrisk_analysis/                    # Phase 2B outputs
├── strategy_tuning/                      # Phase 2C outputs
└── regime_persistence/                   # Phase 2D outputs
```

---

## 🚀 Usage / 使用方法

### **Run Phase 2A (Threshold Calibration)**
```bash
python research/strategy/phase2/threshold_calibration.py
```

### **Run Phase 2B (Tail-Risk Analysis)**
```bash
python research/strategy/phase2/regime_tailrisk_analysis.py
```

### **Run Phase 2C (Strategy Tuning)**
```bash
python research/strategy/phase2/strategy_tuning.py
```

### **Run Phase 2D (Regime Persistence)**
```bash
python research/strategy/phase2/regime_persistence_analysis.py
```

---

## 🔗 Building on Phase 1 / 基于第一阶段

Phase 2 **does not break** Phase 1 functionality. Instead:

✅ Uses Phase 1 trade logs as input  
✅ Produces new analysis outputs in separate directories  
✅ Provides recommendations for config updates  
✅ Enables iterative improvement without losing baseline results

**Phase 1 outputs used:**
- `results/strategy/trades_{symbol}_{timeframe}.csv`
- `results/strategy/summary_{symbol}_{timeframe}.csv`
- `results/strategy/perf_by_risk_regime_{symbol}_{timeframe}.csv`
- `data/factors/merged_three_factor/merged_{symbol}_{timeframe}.parquet`

---

## 📊 Expected Outcomes / 预期成果

After completing Phase 2, we will have:

1. ✅ **Calibrated thresholds** that make gating actually work (10-30% block rate)
2. ✅ **Tail-risk profiles** for each regime (resolve high-risk paradox)
3. ✅ **Optimized parameters** per symbol/timeframe
4. ✅ **Realistic cost model** showing net performance
5. ✅ **Regime dynamics** understanding for future strategy rules

---

**Status:** 🚧 In Development  
**Version:** 2.0.0  
**Last Updated:** 2025-11-20

