# Data Sources Documentation / 数据来源文档

This document records all data sources and symlink mappings in the three-factor combo project.
本文档记录三因子组合项目中的所有数据来源和符号链接映射。

## Raw Bar Data / 原始K线数据

### `raw_bars/bars_with_ofi/`
- **Source / 来源**: `~/manip-ofi-joint-analysis/data/bars_with_ofi/`
- **Type / 类型**: Symlink / 符号链接
- **Content / 内容**: Standard OHLCV bars with OFI features, ATR, and forward returns
  - 标准 OHLCV K线数据，包含 OFI 特征、ATR 和前向收益率
- **Legacy Project / 遗留项目**: `manip-ofi-joint-analysis`
- **Description / 描述**: This is the canonical bar data used across all three factor projects. It contains:
  - 这是所有三个因子项目使用的标准K线数据，包含：
  - OHLC (Open, High, Low, Close) / 开高低收
  - Volume / 成交量
  - ATR (Average True Range) / 平均真实波幅
  - Forward returns at multiple horizons / 多个时间跨度的前向收益率
  - OFI-related features / OFI 相关特征

---

## Factor Data / 因子数据

### Factor 1: ManipScore / 因子1：操纵评分

#### `factors/manip/`
- **Source / 来源**: Standardized from `~/market-manimpulation-analysis/results/`
  - 从 `~/market-manimpulation-analysis/results/` 标准化而来
- **Type / 类型**: Parquet files / Parquet 文件
- **Content / 内容**: Per-bar ManipScore outputs in standardized format
  - 标准化格式的每根K线 ManipScore 输出
- **Schema / 模式**:
  - `symbol`: Asset symbol (e.g., BTCUSD, ETHUSD, EURUSD) / 资产代码
  - `timeframe`: Bar timeframe (e.g., 4h) / K线时间框架
  - `timestamp`: Bar timestamp (timezone-aware) / K线时间戳（带时区）
  - `ManipScore_raw`: Raw manipulation score / 原始操纵评分
  - `ManipScore_z`: Z-score normalized within (symbol, timeframe) panel / 在（品种，时间框架）面板内的Z分数标准化
- **Files / 文件**:
  - `manip_BTCUSD_4h.parquet` (168K, 6027 rows, 2017-05-07 to 2020-12-31)
  - `manip_ETHUSD_4h.parquet` (432K, 15470 rows, 2017-12-11 to 2025-10-08)
  - `manip_EURUSD_4h.parquet` (700K, 24779 rows, 2010-01-01 to 2025-10-03)
- **Legacy Project / 遗留项目**: `market-manipulation-analysis`
- **Standardization Script / 标准化脚本**: `research/three_factor_regime/standardize_manipscore.py`
- **Status / 状态**: ✅ Complete / 完成 (2025-11-20)

---

### Factor 2: OFI (Order Flow Imbalance) / 因子2：订单流失衡

#### `factors/ofi/ofi_data/`
- **Source / 来源**: `~/manip-ofi-joint-analysis/data/bars_with_ofi/`
- **Type / 类型**: Symlink / 符号链接
- **Content / 内容**: Per-bar OFI features including:
  - 每根K线的 OFI 特征，包括：
  - `OFI_z`: Standardized OFI score / 标准化 OFI 评分
  - `OFI_abs_z`: Absolute standardized OFI / 绝对值标准化 OFI
  - Other OFI-related metrics / 其他 OFI 相关指标
- **Legacy Project / 遗留项目**: `Order-Flow-Imbalance-analysis` (via `manip-ofi-joint-analysis`)
- **Note / 注意**: OFI data is already integrated into the bar data
  - OFI 数据已经整合到K线数据中

---

### Factor 3: VolLiqScore (Volume Surprise + Liquidity Stress) / 因子3：成交量惊喜 + 流动性压力

#### `factors/vol_liq/intermediate/`
- **Source / 来源**: `~/manip-ofi-joint-analysis/data/intermediate/`
- **Type / 类型**: Symlink / 符号链接
- **Content / 内容**: Intermediate outputs from VolLiqScore calculation:
  - VolLiqScore 计算的中间输出：
  - Volume surprise metrics / 成交量惊喜指标
  - Liquidity stress indicators / 流动性压力指标
  - Combined VolLiqScore / 组合的 VolLiqScore
- **Legacy Project / 遗留项目**: `volume-surprise-and-liquidity-stress` (via `manip-ofi-joint-analysis`)
- **Note / 注意**: This project reuses the data infrastructure from the joint analysis project
  - 本项目重用联合分析项目的数据基础设施

---

## Merged Three-Factor Data / 合并的三因子数据

### `factors/merged_three_factor/`
- **Source / 来源**: N/A (will be generated) / 不适用（将生成）
- **Type / 类型**: New data folder / 新数据文件夹
- **Content / 内容**: Combined per-bar tables with all three factors:
  - 包含所有三个因子的每根K线合并表：
  - Columns: `symbol`, `timeframe`, `timestamp`, `ManipScore_z`, `OFI_abs_z`, `VolLiqScore`, `ATR`, `ret_fwd_*`, etc.
  - 列：`symbol`（品种）、`timeframe`（时间框架）、`timestamp`（时间戳）、`ManipScore_z`、`OFI_abs_z`、`VolLiqScore`、`ATR`、`ret_fwd_*` 等
- **Purpose / 目的**: Unified data source for three-factor regime research
  - 三因子状态研究的统一数据源

---

## Data Integrity / 数据完整性

### Symlink Verification / 符号链接验证

To verify all symlinks are working:
验证所有符号链接是否正常工作：

```bash
cd ~/microstructure-three-factor-regime/data
find . -type l -exec ls -l {} \;
```

To check for broken symlinks:
检查损坏的符号链接：

```bash
find . -type l ! -exec test -e {} \; -print
```

### ManipScore Data Verification / ManipScore 数据验证

To verify ManipScore parquet files:
验证 ManipScore parquet 文件：

```bash
cd ~/microstructure-three-factor-regime/data/factors/manip
ls -lh *.parquet
```

To inspect ManipScore data with Python:
使用 Python 检查 ManipScore 数据：

```python
import pandas as pd
df = pd.read_parquet('manip_BTCUSD_4h.parquet')
print(df.info())
print(df.head())
print(df.describe())
```

---

## Legacy Project Locations / 遗留项目位置

For reference, here are the original project locations:
供参考，以下是原始项目位置：

1. **manip-ofi-joint-analysis**
   - Path / 路径: `~/manip-ofi-joint-analysis/`
   - Purpose / 用途: Joint analysis of manipulation and OFI factors
   - 操纵和 OFI 因子的联合分析

2. **market-manipulation-analysis**
   - Path / 路径: `~/market-manimpulation-analysis/`
   - Purpose / 用途: Market manipulation detection (Factor 1)
   - 市场操纵检测（因子1）

3. **Order-Flow-Imbalance-analysis**
   - Path / 路径: `~/Order-Flow-Imbalance-analysis/`
   - Purpose / 用途: Order flow imbalance analysis (Factor 2)
   - 订单流失衡分析（因子2）

4. **volume-liquidity-stress** (GitHub only, cloned to repos/)
   - Path / 路径: `~/microstructure-three-factor-regime/repos/volume-liquidity-stress/`
   - Purpose / 用途: Volume surprise and liquidity stress (Factor 3)
   - 成交量惊喜和流动性压力（因子3）

---

**Last Updated / 最后更新**: 2025-11-20
**Maintained By / 维护者**: Quant Research Team
