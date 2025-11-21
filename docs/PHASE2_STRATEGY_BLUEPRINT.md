# Phase 2: Strategy Integration Blueprint

**Project**: Three-Factor Microstructure Regime Analysis  
**Phase**: Strategy Implementation  
**Status**: Planning  
**Date**: 2025-11-20

---

## 🎯 Phase 2 Objectives

Transform the research framework (Phase 1) into practical trading strategies by implementing:

1. **Risk Gating**: Filter trades based on regime risk levels
2. **Position Sizing**: Dynamic sizing based on RiskScore
3. **Stop-Loss Management**: Regime-dependent stop levels
4. **Performance Monitoring**: Regime-aware backtesting and analytics

---

## 🏗️ Architecture Overview

```
Phase 1 (Research)              Phase 2 (Strategy)
┌─────────────────┐            ┌─────────────────┐
│ Three Factors   │            │  Regime Monitor │
│ - ManipScore    │───────────▶│  (Real-time)    │
│ - OFI           │            └────────┬────────┘
│ - VolLiqScore   │                     │
└─────────────────┘                     ▼
                               ┌─────────────────┐
┌─────────────────┐            │   Risk Gating   │
│ Regime Features │───────────▶│   (Filter)      │
│ - Quantiles     │            └────────┬────────┘
│ - Boxes         │                     │
│ - RiskScore     │                     ▼
└─────────────────┘            ┌─────────────────┐
                               │ Position Sizing │
                               │ (Dynamic)       │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │  Stop-Loss Mgmt │
                               │  (Regime-based) │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │   Backtesting   │
                               │   & Analytics   │
                               └─────────────────┘
```

---

## 📁 Module Structure

```
strategy/
├── __init__.py
├── regime_monitor.py          # Real-time regime detection
├── risk_gating.py             # Trade filtering based on regime
├── position_sizing.py         # Dynamic position sizing
├── dynamic_stops.py           # Regime-dependent stop-loss
├── backtest.py                # Backtesting framework
├── performance_analytics.py   # Performance attribution
└── config.py                  # Strategy configuration

examples/
├── simple_risk_gating.py      # Example: Basic risk gating
├── regime_position_sizing.py  # Example: Position sizing
└── full_strategy.py           # Example: Complete strategy

tests/
├── test_regime_monitor.py
├── test_risk_gating.py
├── test_position_sizing.py
└── test_backtest.py
```

---

## 🔧 Module Specifications

### 1. Regime Monitor (`strategy/regime_monitor.py`)

**Purpose**: Real-time regime detection and classification

**Key Functions**:
```python
class RegimeMonitor:
    def __init__(self, config: RegimeConfig):
        """Initialize with factor thresholds and windows"""
        
    def update_factors(self, timestamp, manip_score, ofi, vol_liq_score):
        """Update factor values and compute regime"""
        
    def get_current_regime(self) -> Dict:
        """Return current regime classification"""
        # Returns: {
        #   'q_manip': float,
        #   'q_ofi': float,
        #   'q_vol': float,
        #   'box': str,  # e.g., 'M_high_O_low_V_high'
        #   'risk_score': float,
        #   'risk_regime': str  # 'low', 'medium', 'high'
        # }
        
    def is_high_risk(self) -> bool:
        """Check if current regime is high-risk"""
```

**Configuration**:
- Rolling window size for quantile calculation
- High/low thresholds (default: 0.8/0.5)
- RiskScore weights (default: equal weights)

---

### 2. Risk Gating (`strategy/risk_gating.py`)

**Purpose**: Filter trades based on regime risk levels

**Key Functions**:
```python
class RiskGate:
    def __init__(self, config: RiskGateConfig):
        """Initialize with risk thresholds"""
        
    def should_trade(self, regime: Dict, signal_strength: float = 1.0) -> bool:
        """Decide whether to take a trade"""
        # Logic:
        # - Block if risk_regime == 'high'
        # - Block if RiskScore > max_risk_score
        # - Block if in specific high-risk boxes
        # - Allow with reduced size if medium risk
        
    def get_trade_approval(self, regime: Dict) -> Dict:
        """Get detailed trade approval info"""
        # Returns: {
        #   'approved': bool,
        #   'reason': str,
        #   'size_multiplier': float  # 0.0 to 1.0
        # }
```

**Configuration**:
- `max_risk_score`: Maximum RiskScore to allow trading (default: 0.7)
- `blocked_regimes`: List of regime boxes to avoid
- `medium_risk_multiplier`: Size reduction for medium risk (default: 0.5)

---

### 3. Position Sizing (`strategy/position_sizing.py`)

**Purpose**: Dynamic position sizing based on regime

**Key Functions**:
```python
class PositionSizer:
    def __init__(self, config: PositionSizeConfig):
        """Initialize with base size and limits"""
        
    def calculate_size(self, 
                      base_size: float,
                      regime: Dict,
                      volatility: float,
                      account_balance: float) -> float:
        """Calculate position size"""
        # Formula:
        # size = base_size × (1 - RiskScore) × volatility_adj × account_pct
        
    def get_regime_multiplier(self, risk_score: float) -> float:
        """Get size multiplier based on RiskScore"""
        # Linear scaling: 1.0 at RiskScore=0, 0.0 at RiskScore=1
```

**Configuration**:
- `base_position_pct`: Base position as % of capital (default: 2%)
- `max_position_pct`: Maximum position size (default: 5%)
- `min_position_pct`: Minimum position size (default: 0.5%)
- `volatility_target`: Target volatility for sizing

---

### 4. Dynamic Stops (`strategy/dynamic_stops.py`)

**Purpose**: Regime-dependent stop-loss levels

**Key Functions**:
```python
class DynamicStopLoss:
    def __init__(self, config: StopLossConfig):
        """Initialize with base stop and regime multipliers"""
        
    def calculate_stop(self,
                      entry_price: float,
                      direction: str,  # 'long' or 'short'
                      regime: Dict,
                      atr: float) -> float:
        """Calculate stop-loss price"""
        # Formula:
        # stop_distance = base_atr_mult × ATR × regime_multiplier
        # regime_multiplier: tighter in high-risk, wider in low-risk
        
    def get_regime_stop_multiplier(self, risk_regime: str) -> float:
        """Get stop multiplier for regime"""
        # 'low': 1.2 (wider stops)
        # 'medium': 1.0 (normal)
        # 'high': 0.8 (tighter stops)
```

**Configuration**:
- `base_atr_multiplier`: Base ATR multiple for stops (default: 2.0)
- `low_risk_multiplier`: Multiplier for low-risk regimes (default: 1.2)
- `high_risk_multiplier`: Multiplier for high-risk regimes (default: 0.8)

---

### 5. Backtesting (`strategy/backtest.py`)

**Purpose**: Regime-aware backtesting framework

**Key Functions**:
```python
class RegimeBacktest:
    def __init__(self, config: BacktestConfig):
        """Initialize with strategy config and data"""
        
    def run(self, 
           signals: pd.DataFrame,
           regime_data: pd.DataFrame) -> BacktestResults:
        """Run backtest with regime-based rules"""
        
    def analyze_by_regime(self) -> pd.DataFrame:
        """Performance breakdown by regime"""
        # Returns metrics for each regime:
        # - Total trades
        # - Win rate
        # - Avg return
        # - Sharpe ratio
        # - Max drawdown
```

---

## 📊 Configuration Schema

### Strategy Config (`strategy/config.py`)

```python
@dataclass
class StrategyConfig:
    # Regime Monitor
    regime_window: int = 50  # Rolling window for quantiles
    high_threshold: float = 0.8
    low_threshold: float = 0.5
    
    # Risk Gating
    max_risk_score: float = 0.7
    blocked_boxes: List[str] = field(default_factory=lambda: [
        'M_high_O_high_V_high'  # Avoid highest risk regime
    ])
    medium_risk_multiplier: float = 0.5
    
    # Position Sizing
    base_position_pct: float = 0.02  # 2% of capital
    max_position_pct: float = 0.05   # 5% max
    min_position_pct: float = 0.005  # 0.5% min
    
    # Stop Loss
    base_atr_multiplier: float = 2.0
    low_risk_stop_mult: float = 1.2
    high_risk_stop_mult: float = 0.8
    
    # Backtesting
    initial_capital: float = 100000
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005   # 0.05%
```

---

## 🎯 Implementation Roadmap

### Sprint 1: Core Infrastructure (Week 1)
- [ ] Create `strategy/` module structure
- [ ] Implement `RegimeMonitor` class
- [ ] Implement `RiskGate` class
- [ ] Write unit tests for core classes
- [ ] Create example: simple risk gating

### Sprint 2: Position & Risk Management (Week 2)
- [ ] Implement `PositionSizer` class
- [ ] Implement `DynamicStopLoss` class
- [ ] Integration testing (monitor + gating + sizing)
- [ ] Create example: regime-based position sizing

### Sprint 3: Backtesting Framework (Week 3)
- [ ] Implement `RegimeBacktest` class
- [ ] Implement `PerformanceAnalytics` class
- [ ] Run historical backtests on 6 symbols
- [ ] Generate performance reports

### Sprint 4: Validation & Documentation (Week 4)
- [ ] Out-of-sample validation
- [ ] Sensitivity analysis (parameter tuning)
- [ ] Complete documentation
- [ ] Create full strategy example

---

## 📈 Success Metrics

### Performance Targets
- **Sharpe Ratio**: > 1.5 (regime-aware vs baseline)
- **Max Drawdown**: < 15% (vs 25% baseline)
- **Win Rate**: > 55% in low-risk regimes
- **Risk-Adjusted Return**: +20% improvement vs no regime filtering

### Operational Targets
- **Regime Detection Latency**: < 1 second
- **Position Calculation**: < 100ms
- **Backtest Speed**: < 5 min for 1 year of 5min data

---

## 🔬 Research Questions to Answer

1. **Risk Gating Effectiveness**: How much does filtering high-risk regimes improve Sharpe ratio?
2. **Position Sizing Impact**: What's the optimal RiskScore-to-size mapping?
3. **Stop-Loss Optimization**: Do regime-dependent stops reduce drawdowns?
4. **Regime Persistence**: How long do regimes typically last?
5. **Cross-Asset Performance**: Do regime rules generalize across crypto/forex/metals?

---

**Next Steps**: Begin Sprint 1 implementation  
**Target Completion**: 4 weeks from start  
**Dependencies**: Phase 1 research framework (✅ Complete)

