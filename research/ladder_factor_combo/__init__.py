"""
Ladder × Three-Factor Integration Module

This module explores four directions for combining Ladder trend indicator (25/90 EMA bands)
with three microstructure factors (ManipScore, OFI, VolLiqScore):

Direction 1: Segment-level quality analysis
    - Extract Ladder trend segments (upTrend/downTrend periods)
    - Analyze factor characteristics at segment start
    - Identify "healthy" vs "unhealthy" Ladder trends

Direction 2: Factor-based entry filtering & position sizing
    - Ladder determines direction (upTrend/downTrend)
    - Factors determine: do we enter? how much size?
    - Variants: plain Ladder, healthy-only, size-by-health

Direction 3: Multi-timeframe timing
    - High timeframe (4h/1d) Ladder determines trend direction
    - Low timeframe (30min/1h) + factors for precise entry timing
    - Variants: simple direction-only, factor pullback timing

Direction 4: Factor-based exit rules
    - Ladder controls entry (unchanged)
    - Factors trigger exits or partial profit-taking
    - Variants: full exit on extreme factors, partial exit

Key principle: Ladder parameters (25/90) are FIXED. We only explore how to combine
Ladder with factors, not how to optimize Ladder itself.

Dependencies:
    - Merged three-factor data: data/factors/merged_three_factor/
    - Ladder features: data/ladder_features/
    - Existing backtest engine: research/strategy/backtest_engine.py
"""

__version__ = "1.0.0"
__author__ = "Quant Research Team"

# Module components
__all__ = [
    "segments_extractor",
    "segments_factor_stats",
    "entry_filter_and_sizing",
    "mtf_timing",
    "exit_rules",
    "combo_backtests",
    "combo_aggregate",
    "combo_report",
]

