# Three-Factor Combo Project / 三因子组合项目

## Overview / 概述

This is the **three-factor combo project** for microstructure-based quantitative research.  
这是基于微观结构的**三因子组合项目**。

### Three Factors / 三个因子

1. **Factor 1: ManipScore** (Market Manipulation / Price-Path Abnormality)  
   **因子1：ManipScore**（市场操纵 / 价格路径异常）
   - Detects abnormal price movements and manipulation patterns
   - 检测异常价格波动和操纵模式

2. **Factor 2: OFI** (Order Flow Imbalance)  
   **因子2：OFI**（订单流失衡）
   - Measures imbalance in order flow at different price levels
   - 衡量不同价格水平的订单流失衡

3. **Factor 3: VolLiqScore** (Volume Surprise + Liquidity Stress)  
   **因子3：VolLiqScore**（成交量惊喜 + 流动性压力）
   - Combines volume anomalies with liquidity stress indicators
   - 结合成交量异常与流动性压力指标

## Project Structure / 项目结构

```
microstructure-three-factor-regime/
├── README_THREE_FACTOR_COMBO.md    # This file / 本文件
├── repos/                          # Code repositories / 代码仓库
│   ├── market-manipulation/        # Factor 1 project
│   ├── order-flow-imbalance/       # Factor 2 project
│   └── volume-liquidity-stress/    # Factor 3 project
├── data/                           # Centralized data access / 集中数据访问
│   ├── raw_bars/                   # Standard OHLCV + ATR + forward returns
│   └── factors/                    # Factor outputs / 因子输出
│       ├── manip/                  # ManipScore per-bar outputs
│       ├── ofi/                    # OFI per-bar outputs
│       ├── vol_liq/                # VolLiqScore per-bar outputs
│       └── merged_three_factor/    # Combined three-factor tables
└── research/                       # Research code / 研究代码
    ├── three_factor_regime/        # Three-factor regime analysis
    └── notebooks/                  # Jupyter notebooks for reports
```

## Data Philosophy / 数据理念

**All shared data lives under `data/`**, accessed via **symlinks** to avoid duplicating large files.  
**所有共享数据都在 `data/` 下**，通过**符号链接**访问以避免复制大文件。

- `data/raw_bars/` → Links to canonical bar data (OHLCV, ATR, forward returns)
- `data/factors/` → Links to per-bar factor outputs from the three projects
- `data/factors/merged_three_factor/` → New combined tables for three-factor research

## Research Goals / 研究目标

All new **three-factor regime research** will live under `research/three_factor_regime/`:

1. **Single-factor analysis**: Decile vs tail risk curves  
   **单因子分析**：十分位数 vs 尾部风险曲线

2. **Two-factor heatmaps**: e.g., Vol vs OFI  
   **双因子热力图**：例如，成交量 vs OFI

3. **Three-factor boxes**: 2×2×2 regime analysis  
   **三因子盒子**：2×2×2 状态分析

4. **Continuous RiskScore**: Relation to future volatility / tail events  
   **连续风险评分**：与未来波动率/尾部事件的关系

5. **Logistic models**: Compare baseline (Vol only) vs full (Vol + Manip + OFI)  
   **逻辑回归模型**：比较基线（仅成交量）vs 完整（成交量 + 操纵 + OFI）

## Legacy Projects / 遗留项目

**Old projects remain unchanged** and continue to exist in their original locations.  
**旧项目保持不变**，继续存在于原始位置。

This project is just a clean "umbrella" that:
- Provides unified data access
- Hosts new three-factor research
- Does NOT modify or delete old work

这个项目只是一个干净的"总控"，它：
- 提供统一的数据访问
- 承载新的三因子研究
- 不修改或删除旧工作

See `LEGACY_PATHS.md` for details on legacy project locations.  
查看 `LEGACY_PATHS.md` 了解遗留项目位置的详细信息。

## Next Steps / 下一步

1. ✅ Create project structure
2. ⏳ Clone/link the three GitHub repos under `repos/`
3. ⏳ Set up data symlinks under `data/`
4. ⏳ Prepare research framework under `research/three_factor_regime/`
5. ⏳ Begin three-factor regime analysis

---

**Created**: 2025-11-20  
**Author**: Quant Research Team
