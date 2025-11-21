# Ladder Trend Indicator Analysis

## 📊 Overview

The **Ladder Trend Indicator** (also known as "Blue/Yellow Ladder" or "EMA High/Low Bands") is a trend-following indicator based on dual EMA bands applied to high/low prices.

---

## 🔧 Indicator Definition

### **Ladder Bands**

**Fast Bands** (25-period EMA):
```
fastU = EMA(high, 25)  # Fast upper band
fastL = EMA(low, 25)   # Fast lower band
```

**Slow Bands** (90-period EMA):
```
slowU = EMA(high, 90)  # Slow upper band
slowL = EMA(low, 90)   # Slow lower band
```

### **Trend Conditions**

**Up Trend** (强势上涨):
```
upTrend = (close > fastU) AND (close > slowU)
```
Price is above BOTH fast and slow upper bands → strong bullish trend.

**Down Trend** (强势下跌):
```
downTrend = (close < fastL) AND (close < slowL)
```
Price is below BOTH fast and slow lower bands → strong bearish trend.

**Neutral** (震荡/弱趋势):
```
neutral = NOT upTrend AND NOT downTrend
```
Price is between bands → no clear strong trend.

### **Ladder State Encoding**

```
ladder_state:
  +1 = upTrend   (strong bullish)
  -1 = downTrend (strong bearish)
   0 = neutral   (no clear trend)
```

---

## 📁 Module Structure

```
research/ladder/
├── __init__.py                    # Module initialization
├── README_ladder.md               # This file
├── ladder_features.py             # Compute Ladder bands & states
├── ladder_stats.py                # Analyze Ladder behavior
├── ladder_baseline_strategy.py    # Ladder-only trading strategy
└── ladder_vs_ema_comparator.py    # Compare Ladder vs EMA (future)
```

---

## 🚀 Stage L1: Ladder Indicator Analysis

### **Objectives**

1. **Compute Ladder Features**: Generate Ladder bands and trend states for all symbol×timeframe
2. **Analyze Ladder Behavior**: Study trend frequency, duration, and forward return characteristics
3. **Baseline Strategy**: Test simple Ladder-only trend-following strategy

### **Workflow**

#### **Step 1: Generate Ladder Features**
```bash
cd ~/microstructure-three-factor-regime
python3 -m research.ladder.ladder_features
```

**Input**: `data/factors/merged_three_factor/merged_{symbol}_{timeframe}.parquet`  
**Output**: `data/ladder_features/ladder_{symbol}_{timeframe}.parquet`

**Added columns**:
- `fastU`, `fastL`, `slowU`, `slowL`: Ladder EMA bands
- `upTrend`, `downTrend`: Boolean trend flags
- `ladder_state`: +1 (up), -1 (down), 0 (neutral)

#### **Step 2: Analyze Ladder Statistics**
```bash
python3 -m research.ladder.ladder_stats
```

**Analyses**:
- Trend state frequency (% of bars in up/down/neutral)
- Trend duration distribution (consecutive bars in same state)
- Forward return behavior conditional on Ladder state
- Tail risk analysis (P(|ret| > 2R), P(|ret| > 3R))

**Output**: `results/ladder/ladder_state_stats_*.csv`, `ladder_durations_*.csv`

#### **Step 3: Backtest Ladder Baseline Strategy**
```bash
python3 -m research.ladder.ladder_baseline_strategy
```

**Strategy logic**:
- **Entry**: Long when `upTrend == True` (ladder_state = +1)
- **Exit**: Flat when `upTrend == False` (ladder_state != +1)
- **Position**: Long-only (no short for now)

**Output**: `results/ladder/baseline_strategy/trades_*.csv`, `equity_*.csv`, `summary_*.csv`

---

## 📈 Expected Insights from Stage L1

1. **Trend Sparsity**: How often does Ladder signal strong trends vs neutral?
2. **Trend Persistence**: Average duration of upTrend/downTrend segments
3. **Forward Returns**: Do Ladder states predict future returns?
4. **Baseline Performance**: Can simple Ladder-only strategy be profitable?

---

## 🔗 Next: Stage L2 (Ladder + Regime Integration)

See `research/strategy/ladder_phase/README_ladder_phase.md` for:
- Integrating Ladder with three-factor Regime framework
- Testing Ladder variants (L_V0/V1/V2) with Regime policies
- Comparing Ladder vs EMA under same Regime conditions

---

**Status**: Stage L1 implementation in progress  
**Last Updated**: 2025-11-21

