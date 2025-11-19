# Three-Factor Regime Research / 三因子状态研究

## Overview / 概述

This module contains the research code for analyzing market regimes based on three microstructure factors.  
本模块包含基于三个微观结构因子分析市场状态的研究代码。

## Research Goals / 研究目标

### 1. Single-Factor Analysis / 单因子分析

**Decile vs Tail Risk Curves / 十分位数 vs 尾部风险曲线**

- Divide each factor into 10 deciles / 将每个因子分为10个十分位数
- For each decile, compute tail risk metrics: / 对每个十分位数，计算尾部风险指标：
  - Future volatility (e.g., std of next H bars) / 未来波动率（例如，未来H根K线的标准差）
  - Tail event probability (e.g., |ret| > 2σ) / 尾部事件概率（例如，|ret| > 2σ）
  - Maximum drawdown / 最大回撤
- Plot decile number vs tail risk / 绘制十分位数 vs 尾部风险

**Expected Output / 预期输出:**
- CSV tables: `decile_analysis_{factor}_{symbol}_{timeframe}.csv`
- Plots: Decile curves for each factor / 每个因子的十分位数曲线图

---

### 2. Two-Factor Heatmaps / 双因子热力图

**2D Regime Analysis / 二维状态分析**

- Create 2D grids for factor pairs: / 为因子对创建二维网格：
  - Vol vs OFI / 成交量 vs OFI
  - Vol vs Manip / 成交量 vs 操纵
  - OFI vs Manip / OFI vs 操纵
- For each cell in the grid, compute: / 对网格中的每个单元格，计算：
  - Average future return / 平均未来收益
  - Future volatility / 未来波动率
  - Sharpe ratio / 夏普比率
  - Tail event frequency / 尾部事件频率

**Expected Output / 预期输出:**
- CSV tables: `heatmap_{factor1}_vs_{factor2}_{symbol}_{timeframe}.csv`
- Heatmap plots / 热力图

---

### 3. Three-Factor Boxes (2×2×2) / 三因子盒子 (2×2×2)

**3D Regime Classification / 三维状态分类**

- Classify each bar into one of 8 boxes based on: / 根据以下条件将每根K线分类到8个盒子之一：
  - High/Low ManipScore / 高/低操纵评分
  - High/Low OFI / 高/低OFI
  - High/Low VolLiqScore / 高/低成交量流动性评分
- For each box, compute: / 对每个盒子，计算：
  - Sample count / 样本数量
  - Average future return / 平均未来收益
  - Future volatility / 未来波动率
  - Tail risk metrics / 尾部风险指标
  - Sharpe ratio / 夏普比率

**Expected Output / 预期输出:**
- CSV table: `three_factor_boxes_{symbol}_{timeframe}.csv`
- Bar charts comparing boxes / 比较盒子的柱状图

---

### 4. Continuous RiskScore / 连续风险评分

**Composite Risk Indicator / 综合风险指标**

- Construct a continuous RiskScore from the three factors: / 从三个因子构建连续的风险评分：
  ```
  RiskScore = w1 * ManipScore_z + w2 * OFI_abs_z + w3 * VolLiqScore_z
  ```
- Analyze relationship between RiskScore and: / 分析风险评分与以下指标的关系：
  - Future volatility / 未来波动率
  - Tail event probability / 尾部事件概率
  - Future returns / 未来收益
- Plot RiskScore distribution and its predictive power / 绘制风险评分分布及其预测能力

**Expected Output / 预期输出:**
- CSV table: `riskscore_analysis_{symbol}_{timeframe}.csv`
- Scatter plots and correlation analysis / 散点图和相关性分析

---

### 5. Logistic Regression Models / 逻辑回归模型

**Tail Event Prediction / 尾部事件预测**

Compare different models for predicting tail events (e.g., |ret_fwd_H| > 2σ):  
比较不同模型预测尾部事件的能力（例如，|ret_fwd_H| > 2σ）：

1. **Baseline**: Vol only / 仅成交量
   ```
   P(tail_event) = f(VolLiqScore)
   ```

2. **Two-Factor**: Vol + OFI / 成交量 + OFI
   ```
   P(tail_event) = f(VolLiqScore, OFI_abs_z)
   ```

3. **Full Model**: Vol + OFI + Manip / 成交量 + OFI + 操纵
   ```
   P(tail_event) = f(VolLiqScore, OFI_abs_z, ManipScore_z)
   ```

**Evaluation Metrics / 评估指标:**
- AUC-ROC
- Precision / Recall / 精确率 / 召回率
- F1 Score / F1分数
- Confusion matrix / 混淆矩阵

**Expected Output / 预期输出:**
- CSV table: `logistic_model_comparison_{symbol}_{timeframe}.csv`
- ROC curves / ROC曲线图

---

## Code Structure / 代码结构

```
three_factor_regime/
├── __init__.py
├── README_three_factor_regime.md  # This file
├── TODO.md                         # Task tracking
├── data_loader.py                  # Load and merge three-factor data
├── feature_engineering.py          # Compute regime features (deciles, boxes, RiskScore)
├── single_factor_analysis.py       # Decile analysis
├── two_factor_heatmaps.py          # 2D heatmap analysis
├── three_factor_boxes.py           # 2×2×2 box analysis
├── riskscore_analysis.py           # Continuous RiskScore analysis
└── logistic_models.py              # Logistic regression models
```

---

## Data Schema / 数据模式

### Input Data / 输入数据

Expected columns in merged three-factor data:  
合并的三因子数据中的预期列：

- `symbol`: Asset symbol / 资产代码
- `timeframe`: Bar timeframe (e.g., '30min', '1H') / K线时间框架
- `timestamp`: Bar timestamp / K线时间戳
- `ManipScore_z`: Standardized manipulation score / 标准化操纵评分
- `OFI_abs_z`: Absolute standardized OFI / 绝对值标准化OFI
- `VolLiqScore`: Volume-liquidity composite score / 成交量-流动性综合评分
- `ATR`: Average True Range / 平均真实波幅
- `ret_fwd_H`: Forward return at horizon H / 时间跨度H的前向收益率
- `vol_fwd_H`: Forward volatility at horizon H / 时间跨度H的前向波动率

---

## Next Steps / 下一步

See `TODO.md` for detailed implementation tasks.  
查看 `TODO.md` 了解详细的实现任务。

---

**Created**: 2025-11-20  
**Author**: Quant Research Team
