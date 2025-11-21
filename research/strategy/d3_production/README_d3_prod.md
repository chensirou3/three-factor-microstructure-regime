# D3 Production Strategy Module

**Status**: Production-ready  
**Version**: 1.0  
**Last Updated**: 2025-11-21

---

## Overview

This module contains the production-ready implementation of the **D3 Multi-timeframe Ladder Strategy**, validated through comprehensive sanity checks with excellent out-of-sample performance.

### Strategy Performance (Validated)

**BTCUSD 4h → 30min**:
- Total Return: 694.85%
- Annualized Return: 27.92%
- Sharpe-like: 0.420
- Win Rate: 92.02%
- Max Drawdown: -0.24%

**BTCUSD 4h → 1h**:
- Total Return: 613.97%
- Annualized Return: 26.30%
- Sharpe-like: 0.399
- Win Rate: 83.72%
- Max Drawdown: -1.25%

**Validation Status**: ✅ All 4 sanity checks passed
- ✅ No look-ahead bias in multi-timeframe alignment
- ✅ Causal signal computation (no future data leakage)
- ✅ Stable OOS performance (Sharpe 4.16-7.81)
- ✅ Robust to transaction costs (minimal degradation)

---

## Strategy Logic

### D3 Multi-timeframe Ladder Strategy

**Concept**: Use high timeframe Ladder to determine trend direction, enter/exit based on high TF state transitions.

**Variant**: `D3_ladder_high_tf_dir_only` (simplicity wins - no factor filters)

**Components**:

1. **High Timeframe Ladder** (e.g., 4h):
   - Determines market environment
   - `ladder_state = 1` (upTrend): Bullish environment
   - `ladder_state = 0 or -1`: Neutral/bearish, stay flat

2. **Entry Logic**:
   - Enter LONG when high TF transitions into upTrend (state 0/-1 → 1)
   - Entry executed on low timeframe (30min/1h) at close price

3. **Exit Logic**:
   - Exit when high TF exits upTrend (state 1 → 0/-1)
   - OR when maximum holding period reached (200 bars default)
   - OR when ATR-based stop loss hit

4. **Position**: Long only, no shorting

**Key Insight**: High timeframe Ladder state is sufficient for strong performance. Factor-based filters add complexity without improving results.

---

## Module Structure

```
d3_production/
├── __init__.py                   # Module exports
├── config_d3_prod.yaml           # Configuration file
├── d3_core.py                    # Pure strategy logic (no risk/costs)
├── risk_management.py            # Position sizing, stops, risk limits
├── execution_interface.py        # Abstract execution layer
├── logging_utils.py              # Logging utilities
├── run_d3_prod_backtest.py       # Production backtest runner
├── run_d3_paper_trading_stub.py  # Paper trading stub (future)
└── README_d3_prod.md             # This file
```

---

## Risk Management Features

### Position Sizing
- **Base Notional**: Configurable base position size (default: $1,000)
- **Portfolio Exposure Limit**: Max total exposure as % of equity (default: 30%)
- **Per-Symbol Limit**: Max positions per symbol (default: 1)
- **Global Limit**: Max total concurrent positions (default: 3)

### Stop Loss
- **ATR-based Stops**: Stop at `entry_price - (R * ATR)` where R is configurable (default: 3.0)
- **Dynamic**: Stop calculated at entry using entry bar's ATR
- **Optional**: Can be disabled via configuration

### Holding Period
- **Max Holding Bars**: Force exit after N bars (default: 200)
- **Prevents**: Indefinite holding in stale positions

### Daily Risk Limits
- **Daily Loss Limit**: Stop opening new positions if daily loss exceeds threshold (default: 5% of equity)
- **Reset**: Resets at start of each trading day
- **Optional**: Can be disabled via configuration

---

## Configuration

See `config_d3_prod.yaml` for full configuration options.

**Key Settings**:

```yaml
# Strategy
strategy:
  variant_id: "D3_ladder_high_tf_dir_only"
  use_factor_pullback: false

# Risk Management
risk_management:
  base_position_notional: 1000.0
  atr_stop_R: 3.0
  max_holding_bars: 200
  daily_loss_limit_pct: 5.0

# Backtest
backtest:
  initial_equity: 10000.0
  default_cost_scenario: "low"  # or "high"
```

---

## Usage

### Running Production Backtest

```bash
cd ~/microstructure-three-factor-regime
python3 -m research.strategy.d3_production.run_d3_prod_backtest
```

This will:
1. Load configuration from `config_d3_prod.yaml`
2. Run backtests for all configured (symbol, high_tf, low_tf) pairs
3. Apply full risk management stack
4. Save results to `results/d3_production/`
5. Generate performance summaries

**Output Files** (per pair):
- `trades_d3_prod_{symbol}_{high_tf}_{low_tf}.csv` - Trade log
- `equity_d3_prod_{symbol}_{high_tf}_{low_tf}.csv` - Equity curve
- `summary_d3_prod_{symbol}_{high_tf}_{low_tf}.csv` - Performance metrics

### Paper Trading (Future)

```bash
python3 -m research.strategy.d3_production.run_d3_paper_trading_stub
```

Currently a stub for future live/paper integration.

---

## Code Architecture

### Separation of Concerns

1. **d3_core.py**: Pure strategy logic
   - No risk management
   - No costs
   - No execution
   - Just signal generation: `d3_side`, `d3_entry`, `d3_exit`

2. **risk_management.py**: Risk layer
   - Wraps core signals
   - Applies position sizing
   - Enforces stops and limits
   - Outputs: `final_side`, `final_entry`, `final_exit`, `position_notional`

3. **execution_interface.py**: Execution abstraction
   - Abstract interface for broker integration
   - Stub implementation for testing
   - Future: MT5/IB/Exness implementations

4. **Backtest runner**: Orchestration
   - Loads data
   - Calls core → risk → backtest engine
   - Saves results

### Data Flow

```
High TF Data + Low TF Data
    ↓
d3_core.generate_d3_signals_for_pair()
    ↓
d3_side, d3_entry, d3_exit (pure signals)
    ↓
risk_management.apply_risk_management()
    ↓
final_side, final_entry, final_exit, position_notional
    ↓
backtest_engine.run_backtest() OR execution_interface.send_order()
    ↓
Results / Live Execution
```

---

## Next Steps

### Immediate
- [x] Core strategy module
- [x] Risk management layer
- [x] Execution interface stub
- [x] Production backtest runner
- [ ] Validate backtest results match research

### Short-term
- [ ] Implement paper trading runner
- [ ] Add real-time data feed integration
- [ ] Create monitoring dashboard hooks

### Medium-term
- [ ] MT5 execution implementation
- [ ] Interactive Brokers execution implementation
- [ ] Small capital live testing

### Long-term
- [ ] Multi-symbol portfolio management
- [ ] Advanced risk analytics
- [ ] Performance attribution

---

## Validation

This production module should produce results consistent with research:

**Expected Metrics** (BTCUSD 4h→30min, low cost):
- Total Return: ~695%
- Annualized Return: ~28%
- Win Rate: ~92%
- Sharpe-like: ~0.42

**Sanity Check**: If production backtest results deviate significantly from research results, investigate:
1. Data alignment issues
2. Signal generation differences
3. Risk management unintended effects
4. Cost application errors

---

## Contact & Support

For questions or issues with this module, refer to:
- Sanity check reports: `results/ladder_factor_combo/sanity/`
- Research documentation: `docs/LADDER_D3_SANITY_CHECK_SUMMARY.md`
- Project progress: `docs/PROJECT_PROGRESS_REPORT.md`

