"""
D3 Strategy Core - Pure signal generation logic.

Direction 3 (D3): Multi-timeframe Ladder strategy
- High timeframe Ladder determines trend direction
- Low timeframe Ladder for entry/exit timing
- No factor filters (D3_ladder_high_tf_dir_only variant)

This module contains ONLY the core strategy logic with no risk management,
no costs, no execution. Pure signal generation.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class D3Config:
    """Configuration for D3 strategy core."""
    fast_len: int = 25
    slow_len: int = 90
    max_holding_bars: int = 200
    variant_id: str = "D3_ladder_high_tf_dir_only"


@dataclass
class D3Signal:
    """D3 strategy signal at a single point in time."""
    side: str         # 'flat' or 'long'
    entry: bool       # True when opening a new position
    exit: bool        # True when closing a position
    bars_held: int    # Number of bars position has been held


def align_high_low_tf_ladder(
    high_tf_df: pd.DataFrame,
    low_tf_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Align high timeframe Ladder state to low timeframe bars.
    
    Uses merge_asof with direction='backward' to ensure no look-ahead bias.
    Each low TF bar gets the most recent high TF Ladder state.
    
    Args:
        high_tf_df: High timeframe DataFrame with ladder_state column
        low_tf_df: Low timeframe DataFrame
    
    Returns:
        low_tf_df with 'high_tf_ladder_state' column added
    """
    low_tf_df = low_tf_df.copy()
    high_tf_df = high_tf_df.copy()
    
    # Ensure timestamps are datetime
    low_tf_df['timestamp'] = pd.to_datetime(low_tf_df['timestamp'])
    high_tf_df['timestamp'] = pd.to_datetime(high_tf_df['timestamp'])
    
    # Sort by timestamp
    low_tf_df = low_tf_df.sort_values('timestamp').reset_index(drop=True)
    high_tf_df = high_tf_df.sort_values('timestamp').reset_index(drop=True)
    
    # Merge_asof: get most recent high TF state for each low TF bar
    # direction='backward' ensures we only use past high TF states
    merged = pd.merge_asof(
        low_tf_df,
        high_tf_df[['timestamp', 'ladder_state']].rename(
            columns={'ladder_state': 'high_tf_ladder_state'}
        ),
        on='timestamp',
        direction='backward'
    )
    
    return merged


def generate_d3_signals_for_pair(
    high_tf_df: pd.DataFrame,
    low_tf_df: pd.DataFrame,
    cfg: D3Config
) -> pd.DataFrame:
    """
    Generate D3 strategy signals for a single (symbol, high_tf, low_tf) pair.
    
    Strategy logic (D3_ladder_high_tf_dir_only):
    1. High TF Ladder determines environment:
       - high_tf_ladder_state == 1 (upTrend): bullish environment
       - Otherwise: neutral/bearish, stay flat
    
    2. Entry: When high TF transitions to upTrend (state 0 or -1 → 1)
    
    3. Exit: When high TF exits upTrend (state 1 → 0 or -1)
       OR when max_holding_bars is reached
    
    4. Position: Long only, no shorting
    
    Args:
        high_tf_df: High timeframe DataFrame with ladder_state
        low_tf_df: Low timeframe DataFrame
        cfg: D3Config with strategy parameters
    
    Returns:
        low_tf_df with added columns:
        - d3_side: 'flat' or 'long'
        - d3_entry: True when opening new position
        - d3_exit: True when closing position
        - d3_bars_held: Number of bars position has been held
    """
    # Align high TF state to low TF
    df = align_high_low_tf_ladder(high_tf_df, low_tf_df)
    
    # Initialize signal columns
    df['d3_side'] = 'flat'
    df['d3_entry'] = False
    df['d3_exit'] = False
    df['d3_bars_held'] = 0
    
    # Track position state
    in_position = False
    bars_held = 0
    
    for idx in df.index:
        high_tf_state = df.loc[idx, 'high_tf_ladder_state']
        
        # Check if high TF is in upTrend
        if high_tf_state == 1:
            if not in_position:
                # Entry condition: high TF just entered upTrend
                if idx > 0 and df.loc[idx-1, 'high_tf_ladder_state'] != 1:
                    df.loc[idx, 'd3_entry'] = True
                    df.loc[idx, 'd3_side'] = 'long'
                    in_position = True
                    bars_held = 1
                else:
                    # Already in upTrend but we're not in position (shouldn't happen normally)
                    df.loc[idx, 'd3_side'] = 'flat'
            else:
                # Continue holding position
                bars_held += 1
                df.loc[idx, 'd3_side'] = 'long'
                df.loc[idx, 'd3_bars_held'] = bars_held
                
                # Check max holding period
                if bars_held >= cfg.max_holding_bars:
                    df.loc[idx, 'd3_exit'] = True
                    df.loc[idx, 'd3_side'] = 'flat'
                    in_position = False
                    bars_held = 0
        else:
            # High TF not in upTrend
            if in_position:
                # Exit condition: high TF exited upTrend
                df.loc[idx, 'd3_exit'] = True
                df.loc[idx, 'd3_side'] = 'flat'
                in_position = False
                bars_held = 0
            else:
                df.loc[idx, 'd3_side'] = 'flat'
    
    return df

