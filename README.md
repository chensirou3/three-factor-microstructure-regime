# Three-Factor Microstructure Regime Analysis

**最后更新**: 2025-11-21
**项目状态**: ✅ **生产就绪 - D3 Ladder复利策略完成**

A comprehensive quantitative research framework for market microstructure analysis and algorithmic trading strategy development.

---

## 🎯 项目概览

本项目实现了一个**完整的量化交易研究流程**，从市场微观结构分析到生产就绪的交易策略：

### **三因子Regime框架**
1. **ManipScore** - 价格路径异常/操纵强度检测
2. **OFI (Order Flow Imbalance)** - 买卖压力测量
3. **VolLiqScore** - 成交量异常 + 流动性压力综合

### **交易策略开发**
- **EMA策略** + Regime感知增强
- **Ladder指标** 趋势识别
- **多周期择时** 精准入场/出场

---

## 🏆 核心成果

### **🚀 Stage L4: D3 Ladder生产版本** ⭐ **最新**

**独立项目**: `d3-ladder-mtf-strategy/` (已迁移，可独立使用)

**最佳配置**: D3 Ladder 复利10% (BTCUSD 4h→30min)

| 指标 | 数值 |
|------|------|
| **总收益 (8.4年)** | **571.33%** |
| **年化收益** | **25.42%** |
| **最终资金** | **$67,133** (从$10,000) |
| **胜率** | **91.71%** |
| **盈亏比** | **61.28** |
| **最大回撤** | **-0.75%** |
| **Sharpe比率** | **0.609** |

**近期表现 (2021-2025)**:
- 年化收益: 24.97%
- 胜率: 94.59%
- 最大回撤: -0.15%

**状态**: ✅ **生产就绪，可实盘交易**

---

### **Stage L3: Ladder × Three-Factor Integration**
- **最佳策略**: 多周期择时 (D3_ladder_high_tf_dir_only)
- **表现**: 691%收益 (研究版), 91.71%胜率, Sharpe 0.419
- **配置**: BTCUSD 4h→30min, Ladder(25/90)
- **关键发现**: 多周期 > 因子过滤

### **之前的里程碑**
- ✅ 三因子regime框架 (Phase 0-4)
- ✅ EMA策略变体 + Regime策略
- ✅ Ladder纯策略基准 (Stage L1)
- ✅ 完整的回测基础设施
- ✅ 生产级代码重构 (Stage L4)

## 📊 Key Features

- **Risk-Focused Analysis**: Uses absolute values (|ManipScore_z|, OFI_abs_z) to measure risk strength
- **Time-Series Approach**: Quantile ranking within symbol×timeframe pairs (not cross-sectional)
- **Modular Design**: Config-driven, easy to extend and upgrade
- **Comprehensive Metrics**: E(|ret|), tail probabilities, distribution statistics

## 🔬 Research Methodology

### Three-Factor Framework

```
Factor 1: ManipScore
├── Meaning: Price-path abnormality detection
├── Use: |ManipScore_z| for risk strength
└── Output: q_manip ∈ [0, 1]

Factor 2: OFI (Order Flow Imbalance)
├── Meaning: Buy vs sell pressure
├── Use: OFI_abs_z for pressure strength
└── Output: q_ofi ∈ [0, 1]

Factor 3: VolLiqScore
├── Meaning: Volume + liquidity stress
├── Formula: 0.5 × z_vol + 0.5 × z_liq_stress
└── Output: q_vol ∈ [0, 1]
```

### Regime Classification

- **2×2×2 Boxes**: 8 distinct regimes based on high/low thresholds for each factor
- **RiskScore**: Unified risk intensity = (q_manip + q_ofi + q_vol) / 3
- **Risk Regime**: 3-level classification (low/medium/high)

## 📁 项目结构

```
three-factor-microstructure-regime/
├── research/
│   ├── three_factor_regime/           # Phase 0-4: 三因子框架
│   │   ├── data_loader.py
│   │   ├── three_factor_regime_features.py
│   │   └── ...
│   │
│   ├── strategy/
│   │   ├── phase3/                    # EMA策略变体
│   │   ├── phase4/                    # 账户级回测
│   │   ├── ladder_phase/              # Ladder策略研究
│   │   └── d3_production/             # ⭐ D3生产版本 (已迁移)
│   │
│   ├── ladder/                        # Ladder指标实现
│   │   └── ladder_indicator.py
│   │
│   └── ladder_factor_combo/           # ⭐ Stage L3: 最佳策略
│       ├── config_ladder_factor.yaml
│       ├── segments_extractor.py      # Direction 1: 段分析
│       ├── segments_factor_stats.py
│       ├── entry_filter_and_sizing.py # Direction 2: 入场过滤
│       ├── mtf_timing.py              # Direction 3: 多周期择时 ⭐
│       ├── exit_rules.py              # Direction 4: 退出规则
│       ├── combo_backtests.py         # 统一回测
│       ├── combo_aggregate.py         # 结果聚合
│       └── combo_report.py            # 报告生成
│
├── data/
│   ├── factors/
│   │   ├── merged_three_factor/       # 三因子合并数据
│   │   └── ladder_features/           # Ladder指标特征
│   └── DATA_SOURCES.md
│
├── results/
│   ├── three_factor_regime/           # 因子分析结果
│   ├── strategy/                      # 策略回测结果
│   ├── d3_production/                 # D3生产版本结果
│   └── ladder_factor_combo/           # ⭐ Stage L3结果 (84个实验)
│       ├── direction2/                # 入场过滤结果
│       ├── direction3/                # 多周期结果 ⭐
│       ├── direction4/                # 退出规则结果
│       └── aggregate_*.csv            # 聚合对比
│
├── docs/                              # ⭐ 完整文档
│   ├── PROJECT_PROGRESS_REPORT.md     # 项目进度报告 (已更新)
│   ├── PROJECT_HISTORY.md             # 完整项目历史 (新增)
│   ├── STAGE_L3_EXECUTIVE_SUMMARY.md  # Stage L3总结
│   ├── D3_PRODUCTION_VALIDATION.md    # D3生产验证
│   └── LADDER_FACTOR_COMBO_*.md       # 详细分析文档
│
└── README.md                          # 本文件
```

## 🚀 快速开始

### **推荐: 使用生产就绪的D3 Ladder策略**

**独立项目**: `d3-ladder-mtf-strategy/` (已从本仓库迁移)

```bash
# 1. 进入独立项目目录
cd d3-ladder-mtf-strategy

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行复利版本回测
python scripts/backtest_compound.py

# 4. 运行2021-2025近期回测
python scripts/backtest_2021_2025.py
```

**预期结果**:
- BTCUSD 4h→30min: 571%收益 (8.4年), 25.4%年化
- 胜率: 91.71%, 最大回撤: -0.75%
- 详细报告: `results/COMPOUND_PERFORMANCE_REPORT.md`

**配置文件**:
```yaml
# config/config_d3_compound.yaml
risk:
  use_compounding: true
  compound_pct: 10.0  # 10% of equity per trade
```

---

### **研究版本: 探索完整项目**

#### **前置要求**

- Python 3.10+
- pandas, numpy, pyarrow
- yaml, logging

#### **安装**

```bash
git clone https://github.com/chensirou3/three-factor-microstructure-regime.git
cd three-factor-microstructure-regime
pip install pandas numpy pyarrow pyyaml matplotlib
```

#### **选项1: 运行最佳策略 (Stage L3 - 多周期择时)**

```bash
# 运行Direction 3回测 (推荐)
cd research/ladder_factor_combo
python combo_backtests.py

# 聚合结果
python combo_aggregate.py

# 生成报告
python combo_report.py
```

**预期输出**:
- BTCUSD 4h→30min: 691%收益 (研究版), 91.71%胜率
- 完整分析: `LADDER_FACTOR_COMBO_COMPLETE_REPORT.md`

#### **选项2: 运行完整因子分析流程**

```bash
python run_complete_pipeline.py
```

这将:
- 加载并合并三因子
- 添加regime特征到合并数据集
- 运行单因子十分位分析
- 计算regime级别统计

#### **选项3: 探索各个阶段**

```bash
# Stage L1: Ladder纯策略
python research/strategy/ladder_phase/ladder_baseline_backtest.py

# Stage L2: Ladder + EMA regime
python research/strategy/ladder_phase/ladder_ema_regime_backtest.py

# Stage L3: Ladder × Factor整合 (4个方向)
python research/ladder_factor_combo/combo_backtests.py

# Stage L4: D3生产版本 (已迁移到独立项目)
cd ../d3-ladder-mtf-strategy
python scripts/backtest_compound.py
```

## 📊 Data Coverage

- **Symbols**: BTCUSD, ETHUSD, EURUSD, USDJPY, XAGUSD, XAUUSD (6 total)
- **Timeframes**: 5min, 15min, 30min, 1h, 4h, 1d (6 total)
- **Total Combinations**: 36 (6 symbols × 6 timeframes)
- **Data Period**: Multi-year historical data (varies by symbol)

## 🏆 Best Strategy Performance (Stage L3)

### **D3_ladder_high_tf_dir_only: Multi-Timeframe Timing**

**Top 3 Configurations**:

| Rank | Symbol | Timeframes | Return | Sharpe | Win Rate | Max DD |
|------|--------|------------|--------|--------|----------|--------|
| 🥇 | BTCUSD | 4h→30min | **691.18%** | 0.419 | **91.71%** | -0.24% |
| 🥈 | BTCUSD | 4h→1h | **610.29%** | 0.398 | 82.94% | -1.25% |
| 🥉 | XAUUSD | 4h→30min | **156.37%** | 0.586 | **92.04%** | -0.08% |

**Strategy Logic**:
```
1. High timeframe (4h) Ladder determines trend direction
2. Low timeframe (30min) Ladder waits for aligned signal
3. No additional factor filters (simplicity wins!)
```

**Why It Works**:
- High-TF trend filtering eliminates low-quality trades
- Low-TF execution provides precise entry timing
- Trend consistency ensures high win rate (86%+)
- Minimal drawdown (<1%) with exceptional returns

## 📈 Research Results Summary

### **Stage L3: Ladder × Three-Factor Integration** (Latest)
- **Total Experiments**: 84 backtests + 75,428 segment analysis
- **Four Directions Tested**:
  1. Segment-level quality analysis
  2. Entry filtering & position sizing
  3. **Multi-timeframe timing** ⭐ **Winner**
  4. Factor-based exit rules

**Key Finding**: Multi-timeframe approach (Direction 3) achieved:
- **5.1× better Sharpe** than factor filtering
- **7.5× higher returns** than single-timeframe strategies
- **86.59% average win rate** across all symbols

### **Stage L1-L2: Ladder Strategy Evolution**
- **L1 (Pure Ladder)**: +15.75% avg return, Sharpe 0.047
- **L2 (Ladder + EMA Regime)**: -5.34% avg return (failed)
- **L3 (Ladder × Factor MTF)**: +123.77% avg return, Sharpe 0.476 ⭐

### **Phase 0-4: Three-Factor Regime Framework**
- Comprehensive regime classification system
- Risk-focused analysis (|ret|, tail probabilities)
- Foundation for strategy development

## 📁 关键输出文件

### **🚀 Stage L4: 生产版本** (最新)
- `d3-ladder-mtf-strategy/` - **独立生产项目** (已迁移)
- `d3-ladder-mtf-strategy/results/COMPOUND_PERFORMANCE_REPORT.md` - 复利版本报告
- `docs/D3_PRODUCTION_VALIDATION.md` - 生产版本验证
- `docs/PROJECT_HISTORY.md` - **完整项目历史** (新增)

### **Stage L3 Results** (研究版本)
- `LADDER_FACTOR_COMBO_COMPLETE_REPORT.md` - 官方结果
- `LADDER_FACTOR_COMBO_ANALYSIS.md` - 深度分析
- `STAGE_L3_EXECUTIVE_SUMMARY.md` - 执行摘要
- `results/ladder_factor_combo/aggregate_all_directions.csv` - 84个实验

### **项目文档**
- `PROJECT_PROGRESS_REPORT.md` - 项目进度报告 (已更新)
- `PROJECT_HISTORY.md` - **完整项目历史** (新增)
- `LADDER_FACTOR_COMBO_TECHNICAL_DETAILS.md` - 实现细节

### **因子分析结果**
- `results/three_factor_regime/` - Regime统计 (108个CSV)
- `data/factors/merged_three_factor/` - 合并数据集 (36个parquet)

---

## 📚 文档导航

### **⭐ 推荐阅读顺序**

1. **快速了解**: `README.md` (本文件)
2. **项目历史**: `docs/PROJECT_HISTORY.md` ⭐ **新增**
   - 完整的项目演进过程
   - 每个模块的作用和设计思路
   - 为什么这样做，基于什么想法
3. **进度报告**: `docs/PROJECT_PROGRESS_REPORT.md`
   - 各阶段完成情况
   - 关键指标和结果
4. **生产版本**: `d3-ladder-mtf-strategy/docs/COMPOUND_PERFORMANCE_REPORT.md`
   - 复利版本详细报告
   - 实盘建议

### **Stage L4 文档** (生产版本)
- [PROJECT_HISTORY.md](docs/PROJECT_HISTORY.md) - **完整项目历史** ⭐
- [D3_PRODUCTION_VALIDATION.md](docs/D3_PRODUCTION_VALIDATION.md) - 生产验证
- [d3-ladder-mtf-strategy/docs/](../d3-ladder-mtf-strategy/docs/) - 独立项目文档

### **Stage L3 文档** (研究版本)
- [LADDER_FACTOR_COMBO_COMPLETE_REPORT.md](docs/LADDER_FACTOR_COMBO_COMPLETE_REPORT.md) - 官方结果
- [LADDER_FACTOR_COMBO_ANALYSIS.md](docs/LADDER_FACTOR_COMBO_ANALYSIS.md) - 深度分析
- [STAGE_L3_EXECUTIVE_SUMMARY.md](docs/STAGE_L3_EXECUTIVE_SUMMARY.md) - 执行摘要
- [LADDER_FACTOR_COMBO_TECHNICAL_DETAILS.md](docs/LADDER_FACTOR_COMBO_TECHNICAL_DETAILS.md) - 技术细节

### **之前阶段**
- [LADDER_STAGE_L1_SUMMARY.md](docs/LADDER_STAGE_L1_SUMMARY.md) - Ladder纯策略
- [STAGE_L2_COMPLETE_SUMMARY.md](docs/STAGE_L2_COMPLETE_SUMMARY.md) - Ladder + EMA regime
- [STRATEGY_PHASE3_REPORT.md](docs/STRATEGY_PHASE3_REPORT.md) - EMA策略变体
- [STRATEGY_PHASE4_ACCOUNT_PERFORMANCE.md](docs/STRATEGY_PHASE4_ACCOUNT_PERFORMANCE.md) - 账户级测试

### **基础框架**
- [FINAL_COMPLETION_REPORT.md](docs/FINAL_COMPLETION_REPORT.md) - 三因子框架完成
- [data/DATA_SOURCES.md](data/DATA_SOURCES.md) - 数据模式

## 🔧 Technical Architecture

### **Stage L3: Ladder × Factor Integration** (Production-Ready)

**Core Modules**:
1. **mtf_timing.py** ⭐ - Multi-timeframe timing (best strategy)
2. **entry_filter_and_sizing.py** - Factor-based entry filtering
3. **exit_rules.py** - Factor-based exit rules
4. **segments_extractor.py** - Trend segment analysis
5. **combo_backtests.py** - Unified backtesting engine

**Configuration**: `config_ladder_factor.yaml`
- Ladder parameters: fast=25, slow=90 (fixed)
- Timeframe pairs: 4h→30min, 4h→1h
- Symbols: 6 (BTCUSD, ETHUSD, EURUSD, USDJPY, XAGUSD, XAUUSD)

### **Ladder Indicator**

```python
# Ladder trend states
fastU = EMA(high, 25)
fastL = EMA(low, 25)
slowU = EMA(high, 90)
slowL = EMA(low, 90)

upTrend = (close > fastU) AND (close > slowU)
downTrend = (close < fastL) AND (close < slowL)
neutral = otherwise
```

### **Three-Factor Framework**

```python
# Factor 1: ManipScore (manipulation detection)
ManipScore_z = standardized manipulation score
q_manip = quantile rank within symbol×timeframe

# Factor 2: OFI (order flow imbalance)
OFI_z = standardized order flow imbalance
q_ofi = quantile rank of |OFI_z|

# Factor 3: VolLiqScore (volume/liquidity stress)
VolLiqScore = 0.5 × z_vol + 0.5 × z_liq_stress
q_vol = quantile rank

# Derived features
RiskScore = (q_manip + q_ofi + q_vol) / 3
risk_regime = low/medium/high based on RiskScore
```

## 🎓 Research Principles

✅ **Simplicity Over Complexity**: Simple multi-timeframe beats complex factor filters
✅ **Trend Consistency**: High-TF direction + Low-TF execution = High win rate
✅ **Risk-Focused**: Minimize drawdown while maximizing returns
✅ **Data-Driven**: 84 experiments, 75,428 segments analyzed
✅ **Production-Ready**: Complete backtesting with realistic costs

## 🎯 Key Insights

### **What Works**
✅ Multi-timeframe Ladder timing (Direction 3)
✅ High timeframe (4h) for trend direction
✅ Low timeframe (30min) for execution
✅ Simple strategies without over-optimization
✅ Crypto assets (BTCUSD, ETHUSD) for high returns

### **What Doesn't Work**
❌ Single-timeframe factor filtering (Direction 2)
❌ Factor-based exit rules (Direction 4)
❌ EMA regime policies on Ladder (Stage L2)
❌ High-frequency timeframes (5min, 15min)
❌ Over-complex factor conditions

## 🚀 下一步计划

### **短期 (1-2个月)** - 实盘验证
1. ✅ 代码审查和优化 (已完成)
2. ✅ 风险管理模块 (已完成)
3. ✅ 生产代码重构 (已完成)
4. ✅ 复利版本实现 (已完成)
5. 🔄 纸上交易验证 (1-2周)
6. 🔄 券商API集成 (MT5/IB/Exness)
7. 🔄 小资金实盘测试 ($500-1000)

### **中期 (3-6个月)** - 扩展优化
- [ ] 实盘性能跟踪 vs 回测
- [ ] 扩展到更多标的 (XAUUSD, ETHUSD)
- [ ] 优化复利比例 (5%-15%)
- [ ] 测试其他周期组合 (1d→4h, 1d→1h)
- [ ] 执行优化 (滑点、延迟)

### **长期 (6-12个月)** - 高级功能
- [ ] 多策略组合
- [ ] 机器学习增强
- [ ] 自适应参数调整
- [ ] 扩展到其他市场 (股票、期货)
- [ ] 投资组合优化

---

## 📊 项目统计

### **研究规模**
- **总实验数**: 350+ 回测
- **总交易数**: 1,500,000+
- **趋势段数**: 75,428
- **代码行数**: 12,000+ (研究 + 生产)
- **文档页数**: 30+
- **研究周期**: 约1年 (2024-11 至 2025-11)

### **最佳表现**
- **研究版ROI**: 691% (BTCUSD 4h→30min, 8.4年)
- **生产版ROI**: 571% (复利10%, 8.4年)
- **年化收益**: 25.4%
- **胜率**: 91.71%
- **最大回撤**: -0.75%

### **项目成果**
- ✅ 完整的三因子框架
- ✅ Ladder策略系统
- ✅ 多周期择时发现
- ✅ 生产就绪代码
- ✅ 独立项目迁移

## 📝 Citation

If you use this research framework, please cite:

```bibtex
@software{three_factor_microstructure_regime,
  title = {Three-Factor Microstructure Regime Analysis},
  author = {Chen, Sirou},
  year = {2025},
  url = {https://github.com/chensirou3/three-factor-microstructure-regime}
}
```

## 📧 Contact

For questions, collaboration, or access to data:
- GitHub: [@chensirou3](https://github.com/chensirou3)
- Repository: [three-factor-microstructure-regime](https://github.com/chensirou3/three-factor-microstructure-regime)

---

**Project Status**: ✅ **Stage L3 Complete - Production Ready**
**Best Strategy**: D3_ladder_high_tf_dir_only (BTCUSD 4h→30min)
**Performance**: 691% return, 91.71% win rate, Sharpe 0.419
**Last Updated**: 2025-11-21

