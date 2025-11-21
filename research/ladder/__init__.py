"""
Ladder Trend Indicator Analysis Module

This module implements the "Blue/Yellow Ladder" EMA-based trend indicator
and provides comprehensive analysis tools.

Ladder Indicator Definition:
---------------------------
Fast bands:
  - fastU = EMA(high, 25)
  - fastL = EMA(low, 25)

Slow bands:
  - slowU = EMA(high, 90)
  - slowL = EMA(low, 90)

Trend conditions:
  - upTrend   = (close > fastU) AND (close > slowU)
  - downTrend = (close < fastL) AND (close < slowL)
  - neutral   = neither upTrend nor downTrend

Ladder State:
  - +1: upTrend (strong bullish)
  - -1: downTrend (strong bearish)
  -  0: neutral (no clear trend)

Modules:
--------
- ladder_features.py: Compute Ladder bands and trend states
- ladder_stats.py: Analyze Ladder behavior (frequency, duration, returns)
- ladder_baseline_strategy.py: Simple Ladder-only trading strategy
- ladder_vs_ema_comparator.py: Compare Ladder vs EMA performance

Stage L1: Ladder Indicator Analysis (no factors)
  1. Compute Ladder features for all symbol×timeframe
  2. Analyze trend state statistics and durations
  3. Backtest simple Ladder-only baseline strategy

Stage L2: Ladder + Three-Factor Regime Integration
  (Implemented in research/strategy/ladder_phase/)
  1. Integrate Ladder signals with Regime framework
  2. Test Ladder variants (L_V0/V1/V2) with Regime policies
  3. Compare Ladder vs EMA under same Regime conditions
"""

__version__ = "1.0.0"
__author__ = "Quant Research Team"

from pathlib import Path

# Module root
MODULE_ROOT = Path(__file__).parent

# Default Ladder parameters
DEFAULT_FAST_LEN = 25
DEFAULT_SLOW_LEN = 90

# Default paths
DEFAULT_MERGED_DIR = "data/factors/merged_three_factor"
DEFAULT_OUTPUT_DIR = "data/ladder_features"
DEFAULT_RESULTS_DIR = "results/ladder"

