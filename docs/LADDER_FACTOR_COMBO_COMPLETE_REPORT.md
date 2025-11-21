# 🎯 Ladder × Three-Factor Integration: Complete Report

**Four Directions Explored**: Segment analysis, Entry filtering, MTF timing, Exit rules

---

## 📊 Direction 1: Segment-Level Quality Analysis

**Goal**: Identify 'healthy' vs 'unhealthy' Ladder trends based on factor characteristics.

### Key Findings

**Top 5 Factor Bins (by mean return)**:

| Factor | Bin | Count | Mean Return % | Mean Length | % Positive |
|--------|-----|-------|---------------|-------------|------------|
| OFI_z_upTrend | (-0.5, 0.0] | 535 | 1.12 | 11.5 | 83.4 |
| OFI_z_upTrend | (0.5, 2.0] | 27699 | 0.75 | 12.7 | 80.6 |
| OFI_z_upTrend | (0.0, 0.5] | 7986 | 0.64 | 11.0 | 83.6 |
| q_vol | (-0.001, 0.3] | 11485 | 0.15 | 10.4 | 53.0 |
| risk_regime | low | 7677 | 0.14 | 10.5 | 52.7 |

**Bottom 5 Factor Bins (by mean return)**:

| Factor | Bin | Count | Mean Return % | Mean Length | % Positive |
|--------|-----|-------|---------------|-------------|------------|
| q_vol | (0.7, 0.9] | 19242 | 0.01 | 12.1 | 50.6 |
| risk_regime | high | 24997 | 0.04 | 14.4 | 50.7 |
| q_vol | (0.9, 1.0] | 20668 | 0.05 | 14.9 | 50.6 |
| manip_z_abs | (-0.001, 0.5] | 75391 | 0.07 | 12.3 | 51.5 |
| risk_regime | medium | 42698 | 0.07 | 11.4 | 51.8 |

---

## 🔬 Direction 2: Factor-Based Entry Filtering & Sizing

**Goal**: Use factors to filter Ladder entries and adjust position size.

### Performance by Variant

| Variant | Total Trades | Avg Return % | Avg Sharpe | Avg Max DD % | Avg Win Rate % |
|---------|--------------|--------------|------------|--------------|----------------|
| **D2_healthy_only** | 5916 | 17.45 | 0.0942 | -3.10 | 27.40 |
| **D2_plain_ladder** | 6261 | 18.65 | 0.0972 | -2.99 | 27.62 |
| **D2_size_by_health** | 8070 | 13.27 | 0.0881 | -2.75 | 31.97 |

### Top 10 Performers

| Symbol | Timeframe | Variant | Return % | Sharpe | Trades |
|--------|-----------|---------|----------|--------|--------|
| BTCUSD | 1d | D2_plain_ladder | 104.95 | 0.3030 | 109 |
| BTCUSD | 1d | D2_healthy_only | 93.02 | 0.2970 | 104 |
| BTCUSD | 4h | D2_plain_ladder | 83.49 | 0.1510 | 639 |
| BTCUSD | 4h | D2_healthy_only | 83.36 | 0.1540 | 607 |
| BTCUSD | 1d | D2_size_by_health | 65.78 | 0.2680 | 167 |
| BTCUSD | 4h | D2_size_by_health | 65.18 | 0.1550 | 853 |
| XAUUSD | 4h | D2_plain_ladder | 17.64 | 0.0790 | 1018 |
| XAUUSD | 4h | D2_healthy_only | 16.89 | 0.0790 | 960 |
| XAUUSD | 4h | D2_size_by_health | 15.78 | 0.0800 | 1303 |
| XAUUSD | 1d | D2_plain_ladder | 8.35 | 0.1140 | 229 |

---

## ⏰ Direction 3: Multi-Timeframe Timing

**Goal**: High-TF Ladder for direction, low-TF + factors for precise timing.

### Performance by Variant

| Variant | Total Trades | Avg Return % | Avg Sharpe | Avg Max DD % |
|---------|--------------|--------------|------------|-------------|
| **D3_ladder_high_tf_dir_and_factor_pullback** | 9609 | 107.73 | 0.4230 | -0.21 |
| **D3_ladder_high_tf_dir_only** | 10484 | 139.80 | 0.5293 | -0.18 |

---

## 🚪 Direction 4: Factor-Based Exit Rules

**Goal**: Ladder controls entry, factors trigger exits or partial profit-taking.

### Performance by Variant

| Variant | Total Trades | Avg Return % | Avg Sharpe | Avg Max DD % |
|---------|--------------|--------------|------------|-------------|
| **D4_exit_on_extreme_factors** | 6264 | 8.94 | 0.0749 | -3.19 |
| **D4_partial_takeprofit_on_extreme** | 6262 | 14.47 | 0.1024 | -2.97 |

---

## 🎯 Overall Conclusions

### Which Direction Works Best?

| Direction | Avg Sharpe | Avg Return % | Avg Max DD % |
|-----------|------------|--------------|-------------|
| **D3** | 0.4762 | 123.77 | -0.19 |
| **D2** | 0.0932 | 16.46 | -2.95 |
| **D4** | 0.0887 | 11.70 | -3.08 |

---

**Data**: See `aggregate_all_directions.csv` for complete results
