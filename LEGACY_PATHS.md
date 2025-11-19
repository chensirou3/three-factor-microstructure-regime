# Legacy Project Paths / 遗留项目路径

This document records all legacy project locations and their relationship to the new three-factor combo project.  
本文档记录所有遗留项目位置及其与新三因子组合项目的关系。

---

## Active Legacy Projects / 活跃的遗留项目

These projects contain active code and data that are being used by the new three-factor combo project.  
这些项目包含正在被新三因子组合项目使用的活跃代码和数据。

### 1. manip-ofi-joint-analysis

**Path / 路径**: `~/manip-ofi-joint-analysis/`

**Purpose / 用途**: Joint analysis of manipulation and OFI factors  
操纵和OFI因子的联合分析

**Status / 状态**: Active - Primary data source for the new project  
活跃 - 新项目的主要数据来源

**Key Data Directories / 关键数据目录**:
- `data/bars_with_ofi/` - Standard OHLCV bars with OFI features, ATR, and forward returns
  - 标准OHLCV K线数据，包含OFI特征、ATR和前向收益率
  - **Used by**: `microstructure-three-factor-regime/data/raw_bars/bars_with_ofi` (symlink)
  - **Used by**: `microstructure-three-factor-regime/data/factors/ofi/ofi_data` (symlink)

- `data/intermediate/` - VolLiqScore intermediate outputs
  - VolLiqScore中间输出
  - **Used by**: `microstructure-three-factor-regime/data/factors/vol_liq/intermediate` (symlink)

**Relationship to New Project / 与新项目的关系**:
- This project serves as the **primary data infrastructure** for the three-factor combo project
  - 该项目作为三因子组合项目的**主要数据基础设施**
- All bar data and OFI/VolLiq factor outputs are accessed via symlinks
  - 所有K线数据和OFI/VolLiq因子输出通过符号链接访问
- **DO NOT MODIFY OR DELETE** - Critical dependency
  - **不要修改或删除** - 关键依赖

---

### 2. market-manimpulation-analysis

**Path / 路径**: `~/market-manimpulation-analysis/`

**Purpose / 用途**: Market manipulation detection (Factor 1)  
市场操纵检测（因子1）

**Status / 状态**: Active - Factor 1 source  
活跃 - 因子1来源

**Key Components / 关键组件**:
- ManipScore calculation algorithms
  - ManipScore计算算法
- Price path abnormality detection
  - 价格路径异常检测
- Various analysis scripts and reports
  - 各种分析脚本和报告

**Relationship to New Project / 与新项目的关系**:
- **Symlinked to**: `microstructure-three-factor-regime/repos/market-manipulation`
  - **符号链接到**: `microstructure-three-factor-regime/repos/market-manipulation`
- Code repository is accessible for reference
  - 代码仓库可供参考
- **TODO**: Standardize ManipScore output format and create symlink to `data/factors/manip/`
  - **待办**: 标准化ManipScore输出格式并创建符号链接到 `data/factors/manip/`

---

### 3. Order-Flow-Imbalance-analysis

**Path / 路径**: `~/Order-Flow-Imbalance-analysis/`

**Purpose / 用途**: Order flow imbalance analysis (Factor 2)  
订单流失衡分析（因子2）

**Status / 状态**: Active - Factor 2 source  
活跃 - 因子2来源

**Key Components / 关键组件**:
- OFI calculation from order book data
  - 从订单簿数据计算OFI
- OFI standardization (OFI_z, OFI_abs_z)
  - OFI标准化（OFI_z, OFI_abs_z）
- Git repository with version control
  - 带版本控制的Git仓库

**Relationship to New Project / 与新项目的关系**:
- **Symlinked to**: `microstructure-three-factor-regime/repos/order-flow-imbalance`
  - **符号链接到**: `microstructure-three-factor-regime/repos/order-flow-imbalance`
- OFI data is already integrated into `manip-ofi-joint-analysis/data/bars_with_ofi/`
  - OFI数据已经整合到 `manip-ofi-joint-analysis/data/bars_with_ofi/`
- Code repository is accessible for reference
  - 代码仓库可供参考

---

## Inactive/Empty Legacy Directories / 非活跃/空的遗留目录

These directories appear to be empty or accidentally created. They can be safely removed if confirmed empty.  
这些目录似乎是空的或意外创建的。如果确认为空，可以安全删除。

### 4. Order-Flow-Imbalance-analysisconfig

**Path / 路径**: `~/Order-Flow-Imbalance-analysisconfig/`

**Status / 状态**: Empty - Possibly accidental creation  
空 - 可能是意外创建

**Recommendation / 建议**: Verify empty and consider removal  
验证为空后考虑删除

---

### 5. Order-Flow-Imbalance-analysissrctrading

**Path / 路径**: `~/Order-Flow-Imbalance-analysissrctrading/`

**Status / 状态**: Empty - Possibly accidental creation  
空 - 可能是意外创建

**Recommendation / 建议**: Verify empty and consider removal  
验证为空后考虑删除

---

## New Project Structure / 新项目结构

### microstructure-three-factor-regime

**Path / 路径**: `~/microstructure-three-factor-regime/`

**Purpose / 用途**: Umbrella project for three-factor regime research  
三因子状态研究的总控项目

**Key Directories / 关键目录**:

1. **repos/** - Code repositories (symlinks + git clone)
   - 代码仓库（符号链接 + git克隆）
   - `market-manipulation/` → symlink to `~/market-manimpulation-analysis/`
   - `order-flow-imbalance/` → symlink to `~/Order-Flow-Imbalance-analysis/`
   - `volume-liquidity-stress/` → fresh git clone from GitHub

2. **data/** - Centralized data access (symlinks)
   - 集中化数据访问（符号链接）
   - `raw_bars/bars_with_ofi/` → symlink to `~/manip-ofi-joint-analysis/data/bars_with_ofi/`
   - `factors/ofi/ofi_data/` → symlink to `~/manip-ofi-joint-analysis/data/bars_with_ofi/`
   - `factors/vol_liq/intermediate/` → symlink to `~/manip-ofi-joint-analysis/data/intermediate/`
   - `factors/manip/` → empty (placeholder for future ManipScore outputs)
   - `factors/merged_three_factor/` → empty (for future merged factor tables)

3. **research/** - Research code and notebooks
   - 研究代码和笔记本
   - `three_factor_regime/` - Three-factor regime analysis code
   - `notebooks/` - Jupyter notebooks for reports

---

## Migration Strategy / 迁移策略

**Philosophy / 理念**: "Shell project" approach - do not move or modify legacy projects  
"壳子项目"方法 - 不移动或修改遗留项目

**Key Principles / 关键原则**:
1. **Use symlinks** for all data access to avoid duplication
   - 对所有数据访问**使用符号链接**以避免重复
2. **Keep legacy projects untouched** in their original locations
   - **保持遗留项目不变**在其原始位置
3. **Centralize access** through the new project structure
   - 通过新项目结构**集中访问**
4. **Document everything** to maintain clarity
   - **记录一切**以保持清晰

---

## Cleanup Recommendations / 清理建议

After confirming the new project structure works correctly:  
在确认新项目结构正常工作后：

1. **Verify empty directories**:
   - 验证空目录：
   ```bash
   ls -la ~/Order-Flow-Imbalance-analysisconfig/
   ls -la ~/Order-Flow-Imbalance-analysissrctrading/
   ```

2. **If confirmed empty, remove**:
   - 如果确认为空，删除：
   ```bash
   rmdir ~/Order-Flow-Imbalance-analysisconfig/
   rmdir ~/Order-Flow-Imbalance-analysissrctrading/
   ```

3. **Keep all other legacy projects** as they are critical dependencies
   - **保留所有其他遗留项目**因为它们是关键依赖

---

**Last Updated / 最后更新**: 2025-11-20  
**Maintained By / 维护者**: Quant Research Team
