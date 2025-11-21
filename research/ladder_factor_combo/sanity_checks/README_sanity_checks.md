# Ladder D3 Strategy Sanity Check Suite

## 概述 / Overview

在将D3多周期择时策略投入生产之前，我们需要进行严格的完整性检查。

Before deploying the D3 multi-timeframe timing strategy to production, we need rigorous sanity checks.

---

## 四项核心检查 / Four Core Checks

### 1. **Multi-timeframe Alignment Check** (多周期对齐检查)

**目的 / Purpose**:
- 验证低周期K线使用的高周期Ladder状态没有前视偏差
- Verify that low timeframe bars use only past high timeframe Ladder states (no look-ahead)

**检查内容 / What is checked**:
- 对于每个低周期bar (t_low)，其使用的高周期状态必须来自 timestamp <= t_low 的高周期bar
- For each low TF bar at t_low, the aligned high TF state must come from a high TF bar with timestamp <= t_low

**文件 / File**: `mtf_alignment_check.py`

---

### 2. **Ladder Signal Check** (Ladder信号检查)

**目的 / Purpose**:
- 验证Ladder EMA计算的因果性（不使用未来数据）
- 确认ret_fwd_*列未用于信号生成决策
- Verify Ladder EMA computation is causal (no future data)
- Confirm ret_fwd_* columns are not used in signal generation

**检查内容 / What is checked**:
- EMA bands (fastU/slowU/fastL/slowL) 使用 ewm(..., adjust=False) 正确计算
- ret_fwd_* 仅用于事后评估，不用于入场/出场决策
- EMA bands computed correctly with ewm(..., adjust=False)
- ret_fwd_* only used for post-hoc evaluation, not for entry/exit decisions

**文件 / File**: `ladder_signal_check.py`

---

### 3. **Time-split Out-of-Sample Test** (时间分割样本外测试)

**目的 / Purpose**:
- 验证策略在样本外数据上的稳定性
- Verify strategy stability on out-of-sample data

**检查内容 / What is checked**:
- 将数据分为：
  - **In-sample (IS)**: 2010-01-01 to 2018-12-31
  - **Out-of-sample (OOS)**: 2019-01-01 to 2025-11-21
- 在两个时间段上运行相同的D3策略（无重新调参）
- Run the same D3 strategy on both periods (no retuning)
- 比较IS vs OOS的关键指标：收益、Sharpe、回撤、胜率
- Compare IS vs OOS key metrics: return, Sharpe, drawdown, win rate

**文件 / File**: `time_split_oos_check.py`

---

### 4. **Cost Sensitivity Check** (成本敏感性检查)

**目的 / Purpose**:
- 评估D3策略在不同交易成本下的表现
- Evaluate D3 strategy performance under different transaction costs

**检查内容 / What is checked**:
- 使用Phase 4的账户配置：
  - **low_cost**: ~0.003% per side (低成本账户)
  - **high_cost**: ~0.07% per side (高成本账户)
- 对比两种成本下的策略表现
- Compare strategy performance under both cost scenarios

**文件 / File**: `cost_sensitivity_check.py`

---

## 如何运行 / How to Run

### 运行所有检查 / Run all checks:

```bash
cd research/ladder_factor_combo/sanity_checks

# 1. Multi-timeframe alignment check
python mtf_alignment_check.py

# 2. Ladder signal check
python ladder_signal_check.py

# 3. Time-split OOS test
python time_split_oos_check.py

# 4. Cost sensitivity check
python cost_sensitivity_check.py

# 5. Generate summary report
python report_sanity_checks.py
```

### 查看结果 / View results:

所有结果保存在 / All results saved in:
```
results/ladder_factor_combo/sanity/
├── multitimeframe_alignment_report.csv
├── ladder_signal_check_report.md
├── d3_timesplit_BTCUSD_4h_30min.csv
├── d3_timesplit_BTCUSD_4h_1h.csv
├── d3_cost_sensitivity_BTCUSD_4h_30min.csv
├── d3_cost_sensitivity_BTCUSD_4h_1h.csv
└── LADDER_D3_SANITY_CHECK_REPORT.md  # 总结报告 / Summary report
```

---

## 成功标准 / Success Criteria

### ✅ **通过标准 / Pass criteria**:

1. **Alignment**: 无前视偏差违规 / No look-ahead violations
2. **Signal**: EMA因果性正确，ret_fwd_*未用于决策 / EMA causal, ret_fwd_* not used in decisions
3. **OOS**: 样本外表现稳定，无严重退化 / OOS performance stable, no severe degradation
4. **Cost**: 高成本下仍有合理收益 / Reasonable returns even under high cost

### ⚠️ **警告标准 / Warning criteria**:

- OOS Sharpe < 0.2 (样本外Sharpe过低)
- OOS max drawdown > 20% (样本外回撤过大)
- high_cost下收益 < 10% annualized (高成本下收益过低)

---

## 下一步 / Next Steps

只有在所有检查通过后，才能考虑：
Only after all checks pass, consider:

1. 生产代码实现 / Production code implementation
2. 实盘前评审 / Pre-live review
3. 小资金测试 / Small capital testing
4. 正式部署 / Official deployment

---

**Last Updated**: 2025-11-21

