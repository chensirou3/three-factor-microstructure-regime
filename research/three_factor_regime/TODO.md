# Three-Factor Regime Research TODO / 待办事项

## Phase 1: Data Preparation / 第一阶段：数据准备

### 1.1 Design Unified Schema / 设计统一模式
- [ ] Define standard column names for merged three-factor data
  - 定义合并三因子数据的标准列名
- [ ] Specify data types and formats
  - 指定数据类型和格式
- [ ] Document expected data ranges and units
  - 记录预期的数据范围和单位

### 1.2 Implement Data Loader / 实现数据加载器
- [ ] Create `data_loader.py` module
  - 创建 `data_loader.py` 模块
- [ ] Implement function to load raw bar data from `data/raw_bars/`
  - 实现从 `data/raw_bars/` 加载原始K线数据的函数
- [ ] Implement function to load OFI data from `data/factors/ofi/`
  - 实现从 `data/factors/ofi/` 加载OFI数据的函数
- [ ] Implement function to load VolLiq data from `data/factors/vol_liq/`
  - 实现从 `data/factors/vol_liq/` 加载VolLiq数据的函数
- [ ] Implement function to merge all three factors into unified DataFrame
  - 实现将所有三个因子合并到统一DataFrame的函数
- [ ] Add data validation and quality checks
  - 添加数据验证和质量检查

### 1.3 Handle ManipScore Data / 处理ManipScore数据
- [x] Investigate current ManipScore output format in `market-manipulation` project
  - ✅ 调查 `market-manipulation` 项目中当前的ManipScore输出格式
  - **Status**: Found CSV files in `repos/market-manipulation/results/` with format: `timestamp, open, high, low, close, volume, ManipScore, ManipScore_z`
- [x] Standardize ManipScore output to per-bar format
  - ✅ 将ManipScore输出标准化为每根K线格式
  - **Status**: Created `standardize_manipscore.py` script with canonical schema: `symbol, timeframe, timestamp, ManipScore_raw, ManipScore_z`
- [x] Create symlink or copy standardized outputs to `data/factors/manip/`
  - ✅ 创建符号链接或复制标准化输出到 `data/factors/manip/`
  - **Status**: Generated 3 parquet files:
    - `manip_BTCUSD_4h.parquet` (168K, 6027 rows, 2017-05-07 to 2020-12-31)
    - `manip_ETHUSD_4h.parquet` (432K, 15470 rows, 2017-12-11 to 2025-10-08)
    - `manip_EURUSD_4h.parquet` (700K, 24779 rows, 2010-01-01 to 2025-10-03)

---

## Phase 2: Feature Engineering / 第二阶段：特征工程

### 2.1 Implement Feature Engineering Module / 实现特征工程模块
- [ ] Create `feature_engineering.py` module
  - 创建 `feature_engineering.py` 模块
- [ ] Implement decile calculation for each factor
  - 实现每个因子的十分位数计算
- [ ] Implement 2×2×2 box classification
  - 实现2×2×2盒子分类
- [ ] Implement continuous RiskScore calculation
  - 实现连续风险评分计算
- [ ] Add forward-looking metrics (volatility, tail events)
  - 添加前瞻性指标（波动率、尾部事件）

---

## Phase 3: Single-Factor Analysis / 第三阶段：单因子分析

### 3.1 Implement Decile Analysis / 实现十分位数分析
- [ ] Create `single_factor_analysis.py` module
  - 创建 `single_factor_analysis.py` 模块
- [ ] Implement decile vs tail risk curve generation
  - 实现十分位数 vs 尾部风险曲线生成
- [ ] Generate CSV outputs for each factor
  - 为每个因子生成CSV输出
- [ ] Create visualization plots
  - 创建可视化图表

---

## Phase 4: Two-Factor Analysis / 第四阶段：双因子分析

### 4.1 Implement Heatmap Analysis / 实现热力图分析
- [ ] Create `two_factor_heatmaps.py` module
  - 创建 `two_factor_heatmaps.py` 模块
- [ ] Implement 2D grid generation for factor pairs
  - 实现因子对的二维网格生成
- [ ] Compute metrics for each grid cell
  - 计算每个网格单元的指标
- [ ] Generate CSV outputs
  - 生成CSV输出
- [ ] Create heatmap visualizations
  - 创建热力图可视化

---

## Phase 5: Three-Factor Analysis / 第五阶段：三因子分析

### 5.1 Implement Box Analysis / 实现盒子分析
- [ ] Create `three_factor_boxes.py` module
  - 创建 `three_factor_boxes.py` 模块
- [ ] Implement 2×2×2 box classification logic
  - 实现2×2×2盒子分类逻辑
- [ ] Compute statistics for each box
  - 计算每个盒子的统计数据
- [ ] Generate CSV outputs
  - 生成CSV输出
- [ ] Create bar chart visualizations
  - 创建柱状图可视化

---

## Phase 6: RiskScore Analysis / 第六阶段：风险评分分析

### 6.1 Implement RiskScore Module / 实现风险评分模块
- [ ] Create `riskscore_analysis.py` module
  - 创建 `riskscore_analysis.py` 模块
- [ ] Implement RiskScore calculation with configurable weights
  - 实现可配置权重的风险评分计算
- [ ] Analyze RiskScore vs future volatility
  - 分析风险评分 vs 未来波动率
- [ ] Analyze RiskScore vs tail event probability
  - 分析风险评分 vs 尾部事件概率
- [ ] Generate CSV outputs
  - 生成CSV输出
- [ ] Create scatter plots and correlation analysis
  - 创建散点图和相关性分析

---

## Phase 7: Logistic Regression Models / 第七阶段：逻辑回归模型

### 7.1 Implement Model Comparison / 实现模型比较
- [ ] Create `logistic_models.py` module
  - 创建 `logistic_models.py` 模块
- [ ] Implement baseline model (Vol only)
  - 实现基线模型（仅成交量）
- [ ] Implement two-factor model (Vol + OFI)
  - 实现双因子模型（成交量 + OFI）
- [ ] Implement full model (Vol + OFI + Manip)
  - 实现完整模型（成交量 + OFI + 操纵）
- [ ] Compute evaluation metrics (AUC-ROC, Precision, Recall, F1)
  - 计算评估指标（AUC-ROC、精确率、召回率、F1）
- [ ] Generate comparison CSV
  - 生成比较CSV
- [ ] Create ROC curve plots
  - 创建ROC曲线图

---

## Phase 8: Documentation and Reporting / 第八阶段：文档和报告

### 8.1 Create Jupyter Notebooks / 创建Jupyter Notebooks
- [ ] Create notebook for single-factor analysis
  - 创建单因子分析notebook
- [ ] Create notebook for two-factor heatmaps
  - 创建双因子热力图notebook
- [ ] Create notebook for three-factor boxes
  - 创建三因子盒子notebook
- [ ] Create notebook for RiskScore analysis
  - 创建风险评分分析notebook
- [ ] Create notebook for logistic model comparison
  - 创建逻辑模型比较notebook

### 8.2 Write Summary Report / 编写总结报告
- [ ] Summarize key findings from all analyses
  - 总结所有分析的关键发现
- [ ] Compare predictive power of different factor combinations
  - 比较不同因子组合的预测能力
- [ ] Provide recommendations for strategy integration
  - 提供策略整合建议

---

## Notes / 注意事项

- **Priority**: Focus on Phase 1-3 first to establish data pipeline and basic analysis
  - **优先级**：首先关注第1-3阶段，建立数据管道和基础分析
- **Modularity**: Keep each module independent and reusable
  - **模块化**：保持每个模块独立且可重用
- **Testing**: Add unit tests for data loading and feature engineering
  - **测试**：为数据加载和特征工程添加单元测试
- **Performance**: Consider using Dask or Polars for large datasets
  - **性能**：考虑对大数据集使用Dask或Polars

---

**Last Updated**: 2025-11-20
**Status**: Phase 1.3 Complete - ManipScore Standardization Done / 第1.3阶段完成 - ManipScore标准化完成
