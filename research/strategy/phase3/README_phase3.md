# Strategy Phase 3: Regime-aware Strategy Variants

## 🎯 Goals / 目标

**English:**
Build a comprehensive experiment framework to test multiple regime-aware trading strategy variants systematically. Phase 3 goes beyond simple threshold tuning to implement declarative regime policies that control entry, sizing, and dynamic exits.

**中文:**
构建完整的实验框架，系统性测试多种regime感知的交易策略变体。Phase 3超越简单的阈值调优，实现了声明式的regime策略，控制入场、仓位和动态退出。

---

## 📦 Modules / 模块

### 1. `regime_policies.py`
**English:** Defines regime policy dataclasses and config loader. Policies specify per-regime actions (entry permissions, size multipliers) and dynamic exit rules.

**中文:** 定义regime策略数据类和配置加载器。策略指定每个regime的行为（入场权限、仓位倍数）和动态退出规则。

### 2. `strategy_variants.py`
**English:** Applies regime policies to baseline EMA signals. Handles entry gating, position sizing, and dynamic exits based on regime transitions.

**中文:** 将regime策略应用到基准EMA信号。根据regime转换处理入场过滤、仓位调整和动态退出。

### 3. `experiment_runner.py`
**English:** Orchestrates systematic experiments across variants × symbols × timeframes. Uses Phase 2 recommended threshold (0.70).

**中文:** 编排系统性实验（变体 × 标的 × 周期）。使用Phase 2推荐阈值（0.70）。

### 4. `performance_comparator.py`
**English:** Aggregates results, ranks variants, compares against baseline, analyzes regime distribution.

**中文:** 汇总结果、排名变体、对比基准、分析regime分布。

### 5. `report_phase3.py`
**English:** Generates automated markdown report with rankings, improvements, and recommendations.

**中文:** 生成自动化markdown报告，包含排名、改进和建议。

---

## 🔬 Strategy Variants / 策略变体

### V0: Baseline (基准)
- **English:** Original EMA + RiskScore gating (0.70), no extra regime logic
- **中文:** 原始EMA + RiskScore过滤（0.70），无额外regime逻辑
- **Purpose / 目的:** Comparison reference / 对比参考

### V1: Medium-only (仅MEDIUM)
- **English:** Entries only allowed in MEDIUM regime
- **中文:** 仅在MEDIUM regime允许入场
- **Rationale / 理由:** Phase 2 showed MEDIUM has best Sharpe-like (0.034) and stability (3.82 bars)

### V2: Medium + High Scaled (MEDIUM+HIGH缩量)
- **English:** Entries in MEDIUM (100% size) and HIGH (50% size)
- **中文:** MEDIUM入场（100%仓位）和HIGH入场（50%仓位）
- **Rationale / 理由:** Capture HIGH's higher mean_R (0.263) while managing tail risk

### V3: Medium with High Escape (MEDIUM+HIGH逃逸)
- **English:** Enter in MEDIUM only, exit early if HIGH persists for 2+ bars
- **中文:** 仅MEDIUM入场，若HIGH持续2+根K线则提前退出
- **Rationale / 理由:** Proactive tail risk management based on regime deterioration

---

## 🚀 Usage / 使用方法

### Run Full Experiments / 运行完整实验
```bash
cd ~/microstructure-three-factor-regime
python3 research/strategy/phase3/experiment_runner.py
```

### Run Performance Comparison / 运行性能对比
```bash
python3 research/strategy/phase3/performance_comparator.py
```

### Generate Report / 生成报告
```bash
python3 research/strategy/phase3/report_phase3.py
```

### Test Single Variant / 测试单个变体
```python
from pathlib import Path
from research.strategy.phase3.regime_policies import load_policies_from_config
from research.strategy.phase3.strategy_variants import apply_regime_policy_to_signals

config_path = Path("research/strategy/phase3/config_phase3.yaml")
policies = load_policies_from_config(config_path)

# Apply V1 policy to your signals DataFrame
df_with_signals = apply_regime_policy_to_signals(df, policies['V1_medium_only'])
```

---

## 📊 Expected Outputs / 预期输出

```
results/strategy/phase3/
├── V0_baseline/
│   ├── trades_{symbol}_{timeframe}.csv
│   ├── equity_{symbol}_{timeframe}.csv
│   └── summary_{symbol}_{timeframe}.csv
├── V1_medium_only/
│   └── [same structure]
├── V2_medium_plus_high_scaled/
│   └── [same structure]
├── V3_medium_with_high_escape/
│   └── [same structure]
├── all_experiments_summary.csv
├── aggregate_summary_by_variant.csv
├── variant_rankings.csv
├── comparison_vs_baseline.csv
└── regime_distribution_by_variant.csv
```

**Root-level report:**
- `STRATEGY_PHASE3_REPORT.md` - Comprehensive summary with rankings and recommendations

---

## 🔑 Key Differences from Phase 1/2 / 与Phase 1/2的关键区别

**Phase 1:**
- Single strategy with basic regime gating
- Threshold = 0.80 (never triggered)
- No regime-specific logic

**Phase 2:**
- Analysis-only (no new strategies)
- Calibrated threshold to 0.70
- Identified MEDIUM as optimal regime

**Phase 3:**
- **Multiple strategy variants** with declarative policies
- **Systematic experimentation** framework
- **Dynamic regime management** (V3)
- **Automated comparison** and reporting

---

## 📈 Success Criteria / 成功标准

1. ✅ All 4 variants run successfully on selected symbols × timeframes
2. ✅ Clear ranking of variants by Sharpe-like ratio
3. ✅ Measurable improvement vs Phase 1 baseline
4. ✅ Regime distribution analysis confirms policy behavior
5. ✅ Automated report generation

---

## 🔮 Future Extensions (Phase 4+) / 未来扩展

- **Adaptive regime thresholds** based on market conditions
- **Multi-regime portfolios** (allocate across regimes)
- **Regime transition prediction** for proactive management
- **Real-time regime monitoring** infrastructure

---

**Status:** ✅ Framework Complete  
**Next:** Run validation experiment (BTCUSD 4h) → Full experiments → Report

