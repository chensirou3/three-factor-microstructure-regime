# 🎯 Ladder vs EMA: Final Comparison Report

**Stage L2 Complete**: Comprehensive comparison of Ladder and EMA trend engines under three-factor regime framework

---

## 📊 Overall Performance

| Trend Engine | Avg Return % | Avg Sharpe | Avg Max DD % | Total Trades | Avg Win Rate % |
|--------------|--------------|------------|--------------|--------------|----------------|
| **EMA** | nan | nan | nan | 0 | nan |
| **Ladder** | -5.34 | -0.0126 | -13.92 | 1118783 | 22.69 |

## 🔬 Performance by Variant

| Variant | Engine | Avg Return % | Avg Sharpe | Total Trades |
|---------|--------|--------------|------------|-------------|
| V0_baseline | **EMA** | nan | nan | 0 |
| V0_baseline | **Ladder** | -4.56 | -0.0110 | 450992 |
| V1_medium_only | **EMA** | nan | nan | 0 |
| V1_medium_only | **Ladder** | -6.37 | -0.0205 | 277585 |
| V2_medium_plus_high_scaled | **EMA** | nan | nan | 0 |
| V2_medium_plus_high_scaled | **Ladder** | -5.09 | -0.0062 | 390206 |
| V3_medium_with_high_escape | **EMA** | nan | nan | 0 |

## 🏆 Top 10 Ladder Performers (by Return)

| Rank | Symbol | Timeframe | Variant | Return % | Sharpe | Trades |
|------|--------|-----------|---------|----------|--------|--------|
| 1 | BTCUSD | 1d | V0_baseline | 104.95 | 0.3030 | 109 |
| 2 | BTCUSD | 4h | V0_baseline | 83.49 | 0.1510 | 639 |
| 3 | BTCUSD | 4h | V2_medium_plus_high_scaled | 70.32 | 0.1600 | 543 |
| 4 | BTCUSD | 1d | V2_medium_plus_high_scaled | 66.36 | 0.3080 | 92 |
| 5 | BTCUSD | 4h | V1_medium_only | 56.67 | 0.1610 | 402 |
| 6 | BTCUSD | 1h | V0_baseline | 44.74 | 0.0740 | 2815 |
| 7 | BTCUSD | 1d | V1_medium_only | 36.35 | 0.2320 | 73 |
| 8 | BTCUSD | 1h | V2_medium_plus_high_scaled | 29.67 | 0.0760 | 2365 |
| 9 | BTCUSD | 1h | V1_medium_only | 24.49 | 0.0800 | 1758 |
| 10 | BTCUSD | 30min | V0_baseline | 18.01 | 0.0450 | 5893 |

## ⚠️ Bottom 10 Ladder Performers (by Return)

| Rank | Symbol | Timeframe | Variant | Return % | Sharpe | Trades |
|------|--------|-----------|---------|----------|--------|--------|
| 1 | BTCUSD | 5min | V0_baseline | -185.66 | -0.0110 | 36576 |
| 2 | XAUUSD | 5min | V0_baseline | -178.81 | -0.1700 | 52799 |
| 3 | BTCUSD | 5min | V2_medium_plus_high_scaled | -141.01 | -0.0070 | 31286 |
| 4 | XAUUSD | 5min | V2_medium_plus_high_scaled | -133.32 | -0.1660 | 45898 |
| 5 | BTCUSD | 5min | V1_medium_only | -129.21 | -0.0140 | 24123 |
| 6 | XAUUSD | 5min | V1_medium_only | -113.39 | -0.1960 | 32678 |
| 7 | BTCUSD | 15min | V1_medium_only | -55.72 | 0.0170 | 7724 |
| 8 | BTCUSD | 15min | V2_medium_plus_high_scaled | -48.42 | 0.0220 | 10236 |
| 9 | XAUUSD | 15min | V0_baseline | -45.90 | -0.0700 | 16901 |
| 10 | BTCUSD | 15min | V0_baseline | -32.76 | 0.0220 | 12192 |

## 📈 Performance by Symbol (Ladder)

| Symbol | Avg Return % | Avg Sharpe | Total Trades |
|--------|--------------|------------|-------------|
| **ETHUSD** | 1.36 | 0.0823 | 136720 |
| **USDJPY** | -0.02 | -0.0547 | 218766 |
| **EURUSD** | -0.03 | -0.1504 | 207542 |
| **XAGUSD** | -0.81 | -0.0322 | 204710 |
| **BTCUSD** | -5.58 | 0.0936 | 145593 |
| **XAUUSD** | -26.94 | -0.0141 | 205452 |

## ⏰ Performance by Timeframe (Ladder)

| Timeframe | Avg Return % | Avg Sharpe | Total Trades |
|-----------|--------------|------------|-------------|
| **1d** | 13.33 | 0.1273 | 2702 |
| **4h** | 14.44 | 0.0677 | 12957 |
| **1h** | 5.95 | 0.0023 | 53146 |
| **30min** | -2.15 | -0.0328 | 109684 |
| **15min** | -13.56 | -0.0715 | 226057 |
| **5min** | -50.02 | -0.1685 | 714237 |

---

**Data**: See `ladder_vs_ema_full_comparison.csv` for complete results
