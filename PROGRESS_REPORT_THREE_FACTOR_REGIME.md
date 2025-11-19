# Three-Factor Regime Research - Progress Report

**Date**: 2025-11-20  
**Project**: microstructure-three-factor-regime  
**Phase**: Data Preparation & Research Pipeline Implementation

---

## 📊 Executive Summary

We are implementing a comprehensive three-factor regime analysis framework combining:
- **Factor 1**: ManipScore (price-path abnormality / manipulation intensity)
- **Factor 2**: OFI (Order Flow Imbalance - buy vs sell pressure)
- **Factor 3**: VolLiqScore (volume surprise + liquidity stress)

**Current Status**: ✅ **Data Preparation Complete (100%)**  
**Next Phase**: Research Pipeline Implementation (In Progress)

---

## ✅ Completed Work

### Phase 0: Data Generation & Standardization

#### 1. Raw Data Collection ✅
- **Tick Data**: 6 symbols × 6 timeframes = 36 datasets
  - Symbols: BTCUSD, ETHUSD, EURUSD, USDJPY, XAGUSD, XAUUSD
  - Timeframes: 5min, 15min, 30min, 1h, 4h, 1d
  - Total: ~14,000 parquet files uploaded to server
  - Location: `data/tick_data/symbol={SYMBOL}/date={DATE}/`

#### 2. Raw Bars Generation ✅
- **OHLCV Bars with OFI**: 36 CSV files
  - Processed from tick data using memory-efficient file-by-file approach
  - Includes: OHLCV, volume, OFI metrics, forward returns
  - Location: `data/raw_bars/bars_with_ofi/{SYMBOL}_{TIMEFRAME}_merged_bars_with_ofi.csv`
  - Schema: `timestamp, open, high, low, close, volume, OFI_buy_vol, OFI_sell_vol, OFI_tot_vol, OFI_raw, OFI_mean, OFI_std, OFI_z, fut_ret_2, fut_ret_5, fut_ret_10`

#### 3. Factor 1 - ManipScore ✅
- **Status**: 36/36 files generated
- **Location**: `data/factors/manip/manip_{symbol}_{timeframe}.parquet`
- **Schema**: 
  - `symbol: str`
  - `timeframe: str`
  - `timestamp: datetime64[ns, UTC]`
  - `ManipScore_raw: float`
  - `ManipScore_z: float` (z-score within symbol×timeframe)
- **Sample Stats** (BTCUSD 5min):
  - Rows: 772,411
  - Date range: 2017-05-07 to 2025-10-08
  - File size: 5.5M

#### 4. Factor 2 - OFI (Order Flow Imbalance) ✅
- **Status**: 36/36 files standardized (2025-11-20 07:12)
- **Location**: `data/factors/ofi/ofi_{symbol}_{timeframe}.parquet`
- **Schema**:
  - `symbol: str`
  - `timeframe: str`
  - `timestamp: datetime64[ns, UTC]`
  - `OFI_raw: float` (buy_vol - sell_vol)
  - `OFI_z: float` (z-score within symbol×timeframe)
  - `OFI_abs_z: float` (|OFI_z| for pressure strength)
- **Sample Stats** (BTCUSD 5min):
  - Rows: 772,411
  - Date range: 2017-05-07 to 2025-10-08
  - File size: 26.5M
- **Script**: `research/three_factor_regime/standardize_ofi.py`

#### 5. Factor 3 - VolLiqScore ✅
- **Status**: 36/36 files generated
- **Location**: `data/factors/vol_liq/vol_liq_{symbol}_{timeframe}.parquet`
- **Schema**:
  - `symbol: str`
  - `timeframe: str`
  - `timestamp: datetime64[ns, UTC]`
  - `z_vol: float` (z-score of log(volume))
  - `ATR: float` (Average True Range)
  - `z_liq_stress: float` (z-score of range/ATR)
  - `VolLiqScore: float` (0.5 × z_vol + 0.5 × z_liq_stress)
- **Sample Stats** (BTCUSD 5min):
  - Rows: 772,411
  - Date range: 2017-05-07 to 2025-10-08
  - File size: 27.4M

---

## 📈 Data Completeness Summary

| Factor | Files | Status | Total Size | Coverage |
|--------|-------|--------|------------|----------|
| **Raw Bars (with OFI)** | 36/36 | ✅ 100% | ~2.5 GB | All symbols × timeframes |
| **Factor 1 (ManipScore)** | 36/36 | ✅ 100% | ~150 MB | All symbols × timeframes |
| **Factor 2 (OFI)** | 36/36 | ✅ 100% | ~450 MB | All symbols × timeframes |
| **Factor 3 (VolLiqScore)** | 36/36 | ✅ 100% | ~450 MB | All symbols × timeframes |
| **TOTAL** | **108/108** | ✅ **100%** | **~3.5 GB** | **Complete** |

---

## 🔄 Current Work (In Progress)

### Phase 1: Research Pipeline Implementation

Following the research blueprint, we are implementing:

#### Step 2: Core Data Loader (In Progress)
- **File**: `research/three_factor_regime/data_loader.py`
- **Purpose**: Unified interface to load and merge raw bars + 3 factors
- **Status**: Creating module
- **Key Functions**:
  - `load_raw_bars()` - Load OHLCV + forward returns
  - `load_factor_manip()` - Load ManipScore
  - `load_factor_ofi()` - Load OFI
  - `load_factor_vol_liq()` - Load VolLiqScore
  - `merge_factors_for_symbol_timeframe()` - Merge all data
  - `save_merged_three_factors()` - Generate merged parquet files

#### Step 3: Single-Factor Decile Analysis (Pending)
- **File**: `research/three_factor_regime/single_factor_decile_analysis.py`
- **Purpose**: Risk-focused decile statistics for each factor
- **Metrics**:
  - Quantile scores (q_manip, q_ofi, q_vol)
  - Decile-level statistics: count, share, mean_abs_ret, tail_prob_2R, tail_prob_3R
  - Focus on risk & tail, not alpha

#### Step 4: Three-Factor Regime Features (Pending)
- **File**: `research/three_factor_regime/three_factor_regime_features.py`
- **Purpose**: Construct regime classification features
- **Features**:
  - Quantile scores for all 3 factors
  - High/low pressure flags
  - 2×2×2 box labels (8 regimes)
  - RiskScore (unified risk intensity)

#### Step 5: Three-Factor Regime Statistics (Pending)
- **File**: `research/three_factor_regime/three_factor_regime_stats.py`
- **Purpose**: Compute regime-level risk statistics
- **Outputs**:
  - High vs low pressure stats
  - 2×2×2 box stats (8 boxes)
  - RiskScore decile stats

---

## 📁 Project Structure

```
~/microstructure-three-factor-regime/
├── data/
│   ├── tick_data/                    # Raw tick data (14K+ files)
│   ├── raw_bars/
│   │   └── bars_with_ofi/            # 36 CSV files ✅
│   └── factors/
│       ├── manip/                    # 36 parquet files ✅
│       ├── ofi/                      # 36 parquet files ✅
│       ├── vol_liq/                  # 36 parquet files ✅
│       └── merged_three_factor/      # To be generated
├── research/
│   └── three_factor_regime/
│       ├── standardize_ofi.py        # ✅ Complete
│       ├── data_loader.py            # 🔄 In progress
│       ├── single_factor_decile_analysis.py  # ⏳ Pending
│       ├── three_factor_regime_features.py   # ⏳ Pending
│       └── three_factor_regime_stats.py      # ⏳ Pending
└── results/
    └── three_factor_regime/          # Analysis outputs (to be generated)
```

---

## ⏱️ Timeline

| Phase | Task | Status | Completion Date |
|-------|------|--------|-----------------|
| **Phase 0** | Tick data upload | ✅ | 2025-11-20 05:00 |
| **Phase 0** | Raw bars generation | ✅ | 2025-11-20 06:00 |
| **Phase 0** | ManipScore generation | ✅ | 2025-11-20 06:55 |
| **Phase 0** | VolLiqScore generation | ✅ | 2025-11-20 06:49 |
| **Phase 0** | OFI standardization | ✅ | 2025-11-20 07:12 |
| **Phase 1** | Data loader | 🔄 | In progress |
| **Phase 1** | Single-factor analysis | ⏳ | Pending |
| **Phase 1** | Regime features | ⏳ | Pending |
| **Phase 1** | Regime statistics | ⏳ | Pending |

---

## 🎯 Next Steps

1. ✅ **Complete data_loader.py** - Merge all factors into unified datasets
2. ⏳ **Run data merger** - Generate 36 merged parquet files
3. ⏳ **Implement single-factor analysis** - Decile statistics for each factor
4. ⏳ **Implement regime features** - 2×2×2 classification + RiskScore
5. ⏳ **Implement regime statistics** - Risk-focused regime analysis
6. ⏳ **Generate analysis reports** - CSV outputs and visualizations
7. ⏳ **Update documentation** - DATA_SOURCES.md, TODO.md, PROJECT_STATUS.md

---

## 📝 Notes

- **Design Philosophy**: Risk-focused (not alpha-focused), time-series within symbol×timeframe (not cross-sectional)
- **No Trading Logic**: This phase is pure research - no backtests or strategies
- **Modular & Upgradeable**: Config-driven, easy to extend
- **Idempotent**: All scripts can be re-run safely

---

**Report Generated**: 2025-11-20 07:15 UTC  
**Next Update**: After data loader completion

