# Three-Factor Combo Project Status / 三因子组合项目状态

**Project Name / 项目名称**: microstructure-three-factor-regime  
**Created / 创建日期**: 2025-11-20  
**Status / 状态**: ✅ Setup Complete - Ready for Research / 设置完成 - 准备研究

---

## Executive Summary / 执行摘要

Successfully created a new "umbrella project" that centralizes access to three microstructure factor analysis projects without modifying or moving any legacy code or data.  
成功创建了一个新的"总控项目"，集中访问三个微观结构因子分析项目，而不修改或移动任何遗留代码或数据。

**Key Achievement / 关键成就**: Zero data duplication, zero risk to legacy projects, clean unified interface.  
零数据重复，零遗留项目风险，干净的统一接口。

---

## Project Structure / 项目结构

```
~/microstructure-three-factor-regime/
├── README_THREE_FACTOR_COMBO.md    # Main project documentation
├── LEGACY_PATHS.md                  # Legacy project locations and relationships
├── PROJECT_STATUS.md                # This file
│
├── repos/                           # Code repositories (symlinks + git clone)
│   ├── market-manipulation/         → symlink to ~/market-manimpulation-analysis/
│   ├── order-flow-imbalance/        → symlink to ~/Order-Flow-Imbalance-analysis/
│   └── volume-liquidity-stress/     → fresh git clone from GitHub
│
├── data/                            # Centralized data access (symlinks)
│   ├── DATA_SOURCES.md              # Data source documentation
│   ├── raw_bars/
│   │   └── bars_with_ofi/           → symlink to ~/manip-ofi-joint-analysis/data/bars_with_ofi/
│   └── factors/
│       ├── manip/                   # Empty (placeholder for Factor 1 outputs)
│       ├── ofi/
│       │   └── ofi_data/            → symlink to ~/manip-ofi-joint-analysis/data/bars_with_ofi/
│       ├── vol_liq/
│       │   └── intermediate/        → symlink to ~/manip-ofi-joint-analysis/data/intermediate/
│       └── merged_three_factor/     # Empty (for future merged factor tables)
│
└── research/                        # Research code and notebooks
    ├── three_factor_regime/
    │   ├── __init__.py
    │   ├── README_three_factor_regime.md  # Research goals and methodology
    │   └── TODO.md                        # Implementation task list
    └── notebooks/                   # Empty (for Jupyter notebooks)
```

---

## What Was Created / 创建内容

### 1. Directory Structure / 目录结构
✅ Created root directory: `~/microstructure-three-factor-regime/`  
✅ Created subdirectories: `repos/`, `data/`, `research/`  
✅ Created data subdirectories: `raw_bars/`, `factors/{manip,ofi,vol_liq,merged_three_factor}/`  
✅ Created research subdirectories: `three_factor_regime/`, `notebooks/`

### 2. Repository Links / 仓库链接
✅ Symlinked `market-manipulation` → `~/market-manimpulation-analysis/`  
✅ Symlinked `order-flow-imbalance` → `~/Order-Flow-Imbalance-analysis/`  
✅ Git cloned `volume-liquidity-stress` from GitHub

### 3. Data Symlinks / 数据符号链接
✅ `data/raw_bars/bars_with_ofi` → `~/manip-ofi-joint-analysis/data/bars_with_ofi/`  
✅ `data/factors/ofi/ofi_data` → `~/manip-ofi-joint-analysis/data/bars_with_ofi/`  
✅ `data/factors/vol_liq/intermediate` → `~/manip-ofi-joint-analysis/data/intermediate/`

**Symlink Verification / 符号链接验证**: ✅ All symlinks working, no broken links  
所有符号链接正常工作，无损坏链接

### 4. Documentation / 文档
✅ `README_THREE_FACTOR_COMBO.md` - Main project overview (bilingual)  
✅ `LEGACY_PATHS.md` - Legacy project locations and relationships  
✅ `data/DATA_SOURCES.md` - Data source documentation  
✅ `research/three_factor_regime/README_three_factor_regime.md` - Research goals  
✅ `research/three_factor_regime/TODO.md` - Implementation task list  
✅ `PROJECT_STATUS.md` - This status document

---

## Three Factors / 三个因子

### Factor 1: ManipScore / 因子1：操纵评分
- **Source Project / 来源项目**: `market-manipulation-analysis`
- **Purpose / 用途**: Market manipulation / price path abnormality detection  
  市场操纵 / 价格路径异常检测
- **Status / 状态**: ⚠️ TODO - Standardize output format and create symlink  
  待办 - 标准化输出格式并创建符号链接

### Factor 2: OFI (Order Flow Imbalance) / 因子2：订单流失衡
- **Source Project / 来源项目**: `Order-Flow-Imbalance-analysis`
- **Purpose / 用途**: Order flow imbalance from order book data  
  从订单簿数据计算订单流失衡
- **Status / 状态**: ✅ Data available via symlink  
  数据可通过符号链接访问

### Factor 3: VolLiqScore / 因子3：成交量流动性评分
- **Source Project / 来源项目**: `volume-surprise-and-liquidity-stress`
- **Purpose / 用途**: Volume surprise + liquidity stress indicators  
  成交量惊喜 + 流动性压力指标
- **Status / 状态**: ✅ Data available via symlink  
  数据可通过符号链接访问

---

## Data Sources / 数据来源

All data is accessed via symlinks from the legacy project:  
所有数据通过符号链接从遗留项目访问：

**Primary Data Source / 主要数据来源**: `~/manip-ofi-joint-analysis/`

This project contains:  
该项目包含：
- Standard OHLCV bar data with OFI features, ATR, and forward returns  
  标准OHLCV K线数据，包含OFI特征、ATR和前向收益率
- VolLiqScore intermediate outputs  
  VolLiqScore中间输出

**Critical Dependency / 关键依赖**: DO NOT modify or delete `~/manip-ofi-joint-analysis/`  
不要修改或删除 `~/manip-ofi-joint-analysis/`

---

## Research Framework / 研究框架

The `research/three_factor_regime/` directory contains the framework for three-factor regime analysis:  
`research/three_factor_regime/` 目录包含三因子状态分析框架：

### Research Goals / 研究目标

1. **Single-Factor Analysis / 单因子分析**
   - Decile vs tail risk curves  
     十分位数 vs 尾部风险曲线

2. **Two-Factor Heatmaps / 双因子热力图**
   - 2D regime analysis (Vol vs OFI, Vol vs Manip, OFI vs Manip)  
     二维状态分析（成交量 vs OFI，成交量 vs 操纵，OFI vs 操纵）

3. **Three-Factor Boxes (2×2×2) / 三因子盒子 (2×2×2)**
   - 3D regime classification  
     三维状态分类

4. **Continuous RiskScore / 连续风险评分**
   - Composite risk indicator from three factors  
     从三个因子构建综合风险指标

5. **Logistic Regression Models / 逻辑回归模型**
   - Compare baseline (Vol only) vs full (Vol + OFI + Manip)  
     比较基线（仅成交量）vs 完整（成交量 + OFI + 操纵）

See `research/three_factor_regime/README_three_factor_regime.md` for detailed methodology.  
查看 `research/three_factor_regime/README_three_factor_regime.md` 了解详细方法。

---

## Completed Work / 已完成工作

### Phase 1: Research Framework ✅
- ✅ Standardized all three factors (ManipScore, OFI, VolLiqScore)
- ✅ Merged three-factor datasets (36 files)
- ✅ Implemented regime feature engineering
- ✅ Single-factor decile analysis (ManipScore)
- ✅ Three-factor regime statistics (108 CSV files)
- ✅ GitHub synchronization

### Strategy Phase 1: Regime-aware Baseline ✅
- ✅ Implemented EMA crossover baseline strategy
- ✅ Regime-based gating and position sizing
- ✅ Event-based backtesting engine
- ✅ Regime-conditioned performance analysis
- ✅ Backtested 6 symbols on 4h timeframe
- ✅ Generated 36 result files + comparison report

## Next Steps / 下一步

### Immediate Tasks (This Week) / 即时任务（本周）

1. **Calibrate Gating Thresholds / 校准过滤阈值**
   - [ ] Analyze regime feature distributions (RiskScore, high_pressure frequency)
   - [ ] Set thresholds to block 10-20% of entries (currently 0%)
   - [ ] Re-run backtest with calibrated thresholds

2. **Investigate High-Risk Paradox / 调查高风险悖论**
   - [ ] Plot volatility vs returns by regime
   - [ ] Analyze trade duration by regime
   - [ ] Check if high-risk regimes coincide with strong trends

3. **Expand Analysis / 扩展分析**
   - [ ] Run on multiple timeframes (1h, 1d) for robustness
   - [ ] Analyze regime persistence (how long do regimes last?)
   - [ ] Cross-asset regime correlation

### Medium-term (Next 2 Weeks) / 中期（未来2周）

4. **Improve Baseline Strategy / 改进基线策略**
   - [ ] Add filters (ADX, volume confirmation)
   - [ ] Optimize EMA parameters per symbol
   - [ ] Test alternative entry/exit rules

5. **Advanced Regime Rules / 高级Regime规则**
   - [ ] Dynamic position sizing based on volatility
   - [ ] Regime-dependent stop-loss
   - [ ] Regime transition signals

6. **ML Integration / ML集成**
   - [ ] Train logistic regression for tail event prediction
   - [ ] Use ML-based RiskScore instead of simple average
   - [ ] Feature importance analysis

---

## Legacy Projects / 遗留项目

### Active Projects / 活跃项目
- `~/manip-ofi-joint-analysis/` - **DO NOT MODIFY** (critical data source)  
  **不要修改**（关键数据来源）
- `~/market-manimpulation-analysis/` - Factor 1 source  
  因子1来源
- `~/Order-Flow-Imbalance-analysis/` - Factor 2 source  
  因子2来源

### Empty Directories (Can Be Removed) / 空目录（可删除）
- `~/Order-Flow-Imbalance-analysisconfig/`
- `~/Order-Flow-Imbalance-analysissrctrading/`

See `LEGACY_PATHS.md` for detailed information.  
查看 `LEGACY_PATHS.md` 了解详细信息。

---

## Technical Details / 技术细节

### Symlink Strategy / 符号链接策略
- **Philosophy / 理念**: Avoid data duplication, maintain single source of truth  
  避免数据重复，维护单一数据源
- **Implementation / 实现**: All data accessed via `ln -s` symlinks  
  所有数据通过 `ln -s` 符号链接访问
- **Benefit / 好处**: Zero storage overhead, automatic updates when source data changes  
  零存储开销，源数据更改时自动更新

### Git Strategy / Git策略
- **Legacy repos / 遗留仓库**: Symlinked (not cloned) to preserve git history  
  符号链接（未克隆）以保留git历史
- **New repo / 新仓库**: `volume-liquidity-stress` cloned fresh from GitHub  
  `volume-liquidity-stress` 从GitHub新克隆

---

## Verification / 验证

### Symlink Health Check / 符号链接健康检查
```bash
cd ~/microstructure-three-factor-regime
find data -type l -exec ls -l {} \;
```
**Result / 结果**: ✅ All 3 symlinks working correctly  
所有3个符号链接正常工作

### Broken Link Check / 损坏链接检查
```bash
find ~/microstructure-three-factor-regime -type l ! -exec test -e {} \; -print
```
**Result / 结果**: ✅ No broken links  
无损坏链接

---

## Success Criteria / 成功标准

✅ New project structure created without modifying legacy projects  
新项目结构已创建，未修改遗留项目

✅ All data accessible via symlinks (zero duplication)  
所有数据可通过符号链接访问（零重复）

✅ All three factor repositories accessible under `repos/`  
所有三个因子仓库可在 `repos/` 下访问

✅ Research framework prepared with documentation and TODO list  
研究框架已准备，包含文档和待办列表

✅ Comprehensive documentation created (README, LEGACY_PATHS, DATA_SOURCES, PROJECT_STATUS)  
已创建全面文档（README、LEGACY_PATHS、DATA_SOURCES、PROJECT_STATUS）

---

## Conclusion / 结论

The three-factor combo project is now ready for research. The next step is to implement the data loader and begin single-factor analysis.  
三因子组合项目现已准备好进行研究。下一步是实现数据加载器并开始单因子分析。

**Philosophy / 理念**: "整理 → 画像 → 策略接入" (Organize → Characterize → Strategy Integration)  
We have completed the "整理" (Organize) phase. The "画像" (Characterize) phase begins with implementing the research framework.  
我们已完成"整理"阶段。"画像"阶段从实现研究框架开始。

---

**Last Updated / 最后更新**: 2025-11-20
**Maintained By / 维护者**: Quant Research Team
**Status / 状态**: ✅ Phase 1 Complete, Strategy Phase 1 Complete / Phase 1完成，策略Phase 1完成
