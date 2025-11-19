# Three-Factor Microstructure Regime Analysis

A comprehensive research framework for analyzing market microstructure using three key factors to identify risk regimes.

## 🎯 Project Overview

This project implements a **risk-focused, three-factor regime analysis framework** for microstructure research, combining:

1. **ManipScore** - Price-path abnormality / manipulation intensity detection
2. **OFI (Order Flow Imbalance)** - Buy vs sell pressure measurement
3. **VolLiqScore** - Volume surprise + liquidity stress composite

The framework classifies market states into distinct regimes and computes risk metrics for each regime.

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

## 📁 Project Structure

```
three-factor-microstructure-regime/
├── research/
│   └── three_factor_regime/
│       ├── data_loader.py                    # Core data loading & merging
│       ├── three_factor_regime_features.py   # Regime feature engineering
│       ├── single_factor_decile_analysis.py  # Single-factor analysis
│       ├── three_factor_regime_stats.py      # Regime statistics
│       ├── standardize_ofi.py                # OFI standardization
│       ├── standardize_manipscore.py         # ManipScore standardization
│       └── standardize_volliqscore.py        # VolLiqScore standardization
│
├── data/
│   ├── factors/
│   │   ├── manip/                 # ManipScore factor files
│   │   ├── ofi/                   # OFI factor files
│   │   ├── vol_liq/               # VolLiqScore factor files
│   │   └── merged_three_factor/   # Merged datasets
│   └── DATA_SOURCES.md            # Data schema documentation
│
├── results/
│   └── three_factor_regime/
│       ├── single_factor_deciles/ # Single-factor decile analysis
│       └── regime_stats/          # Regime-level statistics
│
├── run_complete_pipeline.py       # Complete analysis pipeline
├── FINAL_COMPLETION_REPORT.md     # Project completion report
├── PROGRESS_REPORT_THREE_FACTOR_REGIME.md  # Progress tracking
└── PROJECT_STATUS.md              # Current project status
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pandas
- numpy
- pyarrow (for parquet support)

### Installation

```bash
git clone git@github.com:chensirou3/three-factor-microstructure-regime.git
cd three-factor-microstructure-regime
pip install -r requirements.txt  # (to be created)
```

### Usage

1. **Prepare Data**: Place your tick data in `data/tick_data/`

2. **Run Complete Pipeline**:
```bash
python run_complete_pipeline.py
```

This will:
- Load and merge three factors
- Add regime features to merged datasets
- Run single-factor decile analysis
- Compute regime-level statistics

## 📊 Data Coverage

- **Symbols**: BTCUSD, ETHUSD, EURUSD, USDJPY, XAGUSD, XAUUSD (6 total)
- **Timeframes**: 5min, 15min, 30min, 1h, 4h, 1d (6 total)
- **Total Combinations**: 36 (6 symbols × 6 timeframes)

## 📈 Output Files

### Merged Factor Datasets
- Location: `data/factors/merged_three_factor/`
- Format: Parquet files with OHLCV + 3 factors + regime features
- Count: 36 files (one per symbol×timeframe)

### Analysis Results
- **Single-Factor Deciles**: `results/three_factor_regime/single_factor_deciles/` (36 CSV files)
- **Regime Statistics**: `results/three_factor_regime/regime_stats/` (108 CSV files)
  - High vs Low Pressure (36 files)
  - 2×2×2 Box Statistics (36 files)
  - RiskScore Deciles (36 files)

## 🎯 Key Metrics

For each regime and forward horizon H ∈ {2, 5, 10}:

- **count**: Sample size
- **share**: Percentage of total bars
- **mean_abs_ret**: E(|ret|) - risk magnitude
- **tail_prob_2R**: P(|ret| > 2 × ATR)
- **tail_prob_3R**: P(|ret| > 3 × ATR)
- **mean_ret**: E(ret) - directional bias
- **Distribution stats**: median, p10, p25, p75, p90

## 📚 Documentation

- [FINAL_COMPLETION_REPORT.md](FINAL_COMPLETION_REPORT.md) - Complete project summary
- [PROGRESS_REPORT_THREE_FACTOR_REGIME.md](PROGRESS_REPORT_THREE_FACTOR_REGIME.md) - Progress tracking
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status
- [data/DATA_SOURCES.md](data/DATA_SOURCES.md) - Data schema documentation

## 🔧 Module Details

### Core Modules

1. **data_loader.py**: Unified interface for loading and merging factors
2. **three_factor_regime_features.py**: Compute quantile scores, boxes, RiskScore
3. **single_factor_decile_analysis.py**: Risk-focused decile analysis
4. **three_factor_regime_stats.py**: Regime-level risk statistics

### Standardization Modules

- **standardize_ofi.py**: Extract and standardize OFI from raw bars
- **standardize_manipscore.py**: Standardize ManipScore factor
- **standardize_volliqscore.py**: Standardize VolLiqScore factor

## 🎓 Research Principles

✅ **Risk-Focused** (not alpha): Focus on |ret| and tail probabilities  
✅ **Time-Series** (not cross-sectional): Within symbol×timeframe analysis  
✅ **Modular**: Config-driven, easy to extend  
✅ **Idempotent**: All scripts can be re-run safely  

## 🚀 Future Extensions

- [ ] Extend single-factor analysis to OFI and VolLiqScore
- [ ] ML-based RiskScore (logistic regression for tail events)
- [ ] Cross-factor correlation analysis
- [ ] Interactive visualization dashboard
- [ ] Strategy integration (risk gating, position sizing)

## 📝 License

MIT License (or specify your license)

## 👥 Contributors

- Your Name

## 📧 Contact

For questions or collaboration: your.email@example.com

---

**Status**: ✅ Research Framework Complete  
**Last Updated**: 2025-11-20

