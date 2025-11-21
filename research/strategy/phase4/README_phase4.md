# Strategy Phase 4: Account-level Performance with Realistic Costs

## Overview

Phase 4 evaluates strategy performance from a **realistic account perspective**, incorporating actual transaction costs and computing practical metrics that matter for real trading.

**Key Question**: *"If I trade with account A (low cost) or account B (high cost), using V2 or V1, what does my actual performance look like?"*

---

## What's Different from Phase 3?

| Aspect | Phase 3 | Phase 4 |
|--------|---------|---------|
| **Focus** | Strategy variant comparison | Account-level realistic performance |
| **Costs** | Generic (1 bps) | Realistic (0.003% vs 0.07% per side) |
| **Metrics** | Sharpe-like, mean R | Total return, annualized return, max drawdown |
| **Output** | Variant rankings | Account equity curves, practical recommendations |
| **Perspective** | Academic/research | Practical/trading |

---

## Account Configurations

### Account A: Low Cost (Institutional)
- **Cost**: 0.003% per side (0.006% round-trip)
- **Example**: Binance VIP, institutional accounts, market makers
- **Initial Equity**: $10,000

### Account B: High Cost (Retail)
- **Cost**: 0.07% per side (0.14% round-trip)
- **Example**: Retail exchanges, smaller accounts
- **Initial Equity**: $10,000

---

## Strategy Variants (from Phase 3)

### V2_medium_plus_high_scaled (Recommended)
- **Entry**: MEDIUM regime (full size), HIGH regime (50% size)
- **Exit**: Standard EMA crossover
- **Rationale**: Best risk-adjusted returns in Phase 3

### V1_medium_only (Conservative)
- **Entry**: MEDIUM regime only
- **Exit**: Standard EMA crossover
- **Rationale**: Best tail risk control in Phase 3

---

## Experiment Scope

- **Accounts**: 2 (low_cost, high_cost)
- **Variants**: 2 (V2, V1)
- **Symbols**: 6 (BTCUSD, ETHUSD, EURUSD, USDJPY, XAGUSD, XAUUSD)
- **Timeframes**: 4 (30min, 1h, 4h, 1d)
- **Total Combinations**: 2 × 2 × 6 × 4 = **96 backtests**

---

## Key Metrics

1. **Total Return**: (Final Equity - Initial Equity) / Initial Equity
2. **Annualized Return**: Geometric return scaled to annual basis
3. **Max Drawdown**: Largest peak-to-trough decline in equity
4. **Trade Count**: Number of completed trades
5. **Net Mean R**: Average profit per trade in R-multiples (after costs)
6. **Sharpe-like**: Mean R / Std R (risk-adjusted performance)

---

## Usage

### 1. Run All Backtests
```bash
cd ~/microstructure-three-factor-regime
python3 -m research.strategy.phase4.realistic_backtest
```

### 2. Aggregate Performance
```bash
python3 -m research.strategy.phase4.equity_analysis
```

### 3. Generate Equity Curves
```bash
python3 -m research.strategy.phase4.plot_equity_curves
```

### 4. Generate Final Report
```bash
python3 -m research.strategy.phase4.report_phase4
```

---

## Output Files

### Results Directory Structure
```
results/strategy/phase4/
├── low_cost/
│   ├── V2_medium_plus_high_scaled/
│   │   ├── trades_BTCUSD_1h.csv
│   │   ├── equity_BTCUSD_1h.csv
│   │   └── summary_BTCUSD_1h.csv
│   └── V1_medium_only/
│       └── ...
├── high_cost/
│   └── ...
├── aggregate_phase4_summary.csv
├── summary_by_symbol.csv
├── summary_by_account_variant.csv
├── plots/
│   ├── equity_low_cost_V2_BTCUSD_1h.png
│   └── ...
└── STRATEGY_PHASE4_ACCOUNT_PERFORMANCE.md
```

---

## Expected Insights

1. **Cost Impact**: How much does 0.07% vs 0.003% cost affect returns?
2. **Symbol Selection**: Which symbols remain profitable under high costs?
3. **Timeframe Selection**: Do shorter timeframes become unprofitable with high costs?
4. **Variant Selection**: Does V1 (fewer trades) outperform V2 under high costs?

---

## Next Steps After Phase 4

- Select optimal account × variant × symbol × timeframe combinations
- Prepare for paper trading or live deployment
- Monitor real-world performance vs backtest expectations

