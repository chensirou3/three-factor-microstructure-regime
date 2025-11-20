# Strategy Phase 1: Regime-aware Baseline Strategy

## Overview

This module implements a **diagnostic strategy framework** to understand how three-factor regime information affects trading performance. The goal is not to build the final alpha, but to analyze how a simple baseline strategy performs across different regime states.

## Architecture

```
Baseline Strategy (Regime-agnostic)
         ↓
   EMA Crossover Signals
         ↓
Regime Wrapper (Three-factor gating & sizing)
         ↓
   Final Trading Decisions
         ↓
Event-based Backtest
         ↓
Regime-conditioned Performance Analysis
```

## Components

### 1. Baseline Strategy (`baseline_strategy.py`)

**Simple EMA crossover trend-following strategy:**
- **Entry**: Fast EMA (20) crosses above Slow EMA (50) → Enter long
- **Exit**: Fast EMA crosses below Slow EMA → Exit to flat
- **Position**: Long/flat only (no short positions in v1)

**Why this baseline?**
- Transparent and interpretable
- Regime-agnostic (only uses price)
- Easy to replace with custom strategy later
- Isolates the effect of regime-based risk management

### 2. Regime Wrapper (`regime_wrapper.py`)

**Applies three-factor regime rules to baseline signals:**

**Gating (block new entries in high-risk states):**
- Block if `high_pressure == True` (configurable)
- Block if `three_factor_box == "M_high_O_high_V_high"` (configurable)
- Always allow exits (risk reduction)

**Position Sizing (scale by risk regime):**
- Low risk: 100% of base size
- Medium risk: 70% of base size
- High risk: 30% of base size

### 3. Backtest Engine (`backtest_engine.py`)

**Simple event-based backtester:**
- Entry/exit at bar close
- Position sizing based on regime
- Per-trade logging with regime information
- Equity curve tracking

**Outputs:**
- `trades_{symbol}_{timeframe}.csv`: Per-trade log with regime info
- `equity_{symbol}_{timeframe}.csv`: Equity curve
- `summary_{symbol}_{timeframe}.csv`: Overall performance metrics
- `perf_by_risk_regime_{symbol}_{timeframe}.csv`: Performance by risk regime
- `perf_by_pressure_{symbol}_{timeframe}.csv`: Performance by high_pressure
- `perf_by_box_{symbol}_{timeframe}.csv`: Performance by three_factor_box

### 4. Orchestrator (`run_regime_strategy.py`)

**Main script that:**
1. Loads merged three-factor data
2. Generates baseline signals
3. Applies regime wrapper
4. Runs backtest
5. Saves results
6. Compares baseline vs regime-aware performance

## Configuration

Edit `config_strategy.yaml` to customize:

```yaml
# Symbols and timeframes
symbols: ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
timeframes: ["4h"]

# Baseline strategy parameters
baseline:
  fast_len: 20
  slow_len: 50

# Position sizing by risk regime
position_sizing:
  base_size: 1.0
  size_by_riskregime:
    low: 1.0
    medium: 0.7
    high: 0.3

# Gating rules
gating:
  block_new_entries_in_high_pressure: true
  block_new_entries_in_triple_high_box: true
```

## Usage

### Run backtest for all configured symbols×timeframes:

```bash
cd ~/microstructure-three-factor-regime
python research/strategy/run_regime_strategy.py
```

### Check results:

```bash
ls -lh results/strategy/
```

### Analyze regime-conditioned performance:

```bash
# Performance by risk regime
cat results/strategy/perf_by_risk_regime_BTCUSD_4h.csv

# Performance by high_pressure
cat results/strategy/perf_by_pressure_BTCUSD_4h.csv

# Performance by three_factor_box
cat results/strategy/perf_by_box_BTCUSD_4h.csv

# Baseline vs regime comparison
cat results/strategy/compare_baseline_vs_regime.csv
```

## Key Metrics

### Overall Performance
- `total_return_pct`: Total return percentage
- `sharpe_ratio`: Risk-adjusted return
- `max_drawdown_pct`: Maximum drawdown
- `win_rate_pct`: Percentage of winning trades

### Per-trade Metrics
- `R_multiple`: PnL / (ATR × position_size)
- `net_pnl`: Net profit/loss after costs
- `return_pct`: Percentage return on trade

### Regime-conditioned Metrics
- `mean_R`: Average R-multiple by regime
- `median_R`: Median R-multiple by regime
- `tail_R_p5`: 5th percentile R (tail loss)
- `tail_R_p95`: 95th percentile R (tail gain)

## Assumptions (v1)

- **Execution**: Entry/exit at bar close
- **Costs**: 0% transaction costs (configurable)
- **Slippage**: 0% slippage (configurable)
- **Position**: Long-only, single-asset
- **Sizing**: Fixed base size, scaled by regime

## Next Steps (Phase 2)

### TODO: Future Enhancements

1. **Replace baseline strategy** with custom alpha logic
2. **Add transaction costs & slippage** for realistic simulation
3. **Extend to short positions** for long/short strategies
4. **Multi-asset portfolio** backtesting
5. **ML-based RiskScore** integration
6. **Dynamic stop-loss** based on regime
7. **Regime transition analysis** (how long do regimes last?)
8. **Out-of-sample validation** (walk-forward testing)

## Diagnostic Questions to Answer

After running the backtest, analyze:

1. **Which regimes are profitable?**
   - Check `perf_by_risk_regime`: Is mean_R higher in low-risk regimes?
   
2. **Does gating improve performance?**
   - Compare `compare_baseline_vs_regime.csv`: Does blocking high-risk entries improve Sharpe?
   
3. **Which boxes to avoid?**
   - Check `perf_by_box`: Which three_factor_boxes have negative mean_R?
   
4. **Is position sizing effective?**
   - Do smaller positions in high-risk regimes reduce tail losses?

5. **Trade-off analysis:**
   - How many trades are blocked? (`gating_stats`)
   - Is the reduction in trades worth the improvement in metrics?

## File Structure

```
research/strategy/
├── __init__.py
├── config_strategy.yaml          # Configuration
├── baseline_strategy.py          # EMA crossover logic
├── regime_wrapper.py             # Gating & sizing
├── backtest_engine.py            # Backtester
├── run_regime_strategy.py        # Orchestrator
└── README_strategy.md            # This file

results/strategy/
├── trades_{symbol}_{timeframe}.csv
├── equity_{symbol}_{timeframe}.csv
├── summary_{symbol}_{timeframe}.csv
├── perf_by_risk_regime_{symbol}_{timeframe}.csv
├── perf_by_pressure_{symbol}_{timeframe}.csv
├── perf_by_box_{symbol}_{timeframe}.csv
└── compare_baseline_vs_regime.csv
```

---

**Status**: Ready to run  
**Next**: Execute backtest and analyze regime-conditioned performance

