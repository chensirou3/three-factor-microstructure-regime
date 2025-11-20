"""
Baseline trend-following strategy (regime-agnostic).

Implements a simple EMA crossover strategy:
- Fast EMA (default 20) crosses above Slow EMA (default 50) → Enter long
- Fast EMA crosses below Slow EMA → Exit to flat
- Long/flat only (no short positions in v1)

This baseline is intentionally simple and transparent to isolate the effect
of regime-based gating and position sizing.
"""

import pandas as pd
import numpy as np
from typing import Literal

Side = Literal["flat", "long"]


def generate_baseline_signals(
    df: pd.DataFrame,
    fast_len: int = 20,
    slow_len: int = 50
) -> pd.DataFrame:
    """
    Generate baseline EMA crossover signals for a single symbol×timeframe.
    
    Parameters
    ----------
    df : pd.DataFrame
        Merged data for single symbol×timeframe, sorted by timestamp.
        Must contain 'close' column.
    fast_len : int
        Fast EMA period (default 20)
    slow_len : int
        Slow EMA period (default 50)
    
    Returns
    -------
    pd.DataFrame
        Input df with added columns:
        - fast_ma: Fast EMA
        - slow_ma: Slow EMA
        - baseline_side: 'flat' or 'long'
        - baseline_entry: True on bars where long is opened
        - baseline_exit: True on bars where long is closed
    
    Notes
    -----
    - No look-ahead bias: uses only information available up to current bar
    - Position is either 0 (flat) or +1 (long)
    - First slow_len bars will have NaN for slow_ma
    """
    df = df.copy()
    
    # Compute EMAs using pandas ewm
    df['fast_ma'] = df['close'].ewm(span=fast_len, adjust=False).mean()
    df['slow_ma'] = df['close'].ewm(span=slow_len, adjust=False).mean()
    
    # Initialize signal columns
    df['baseline_side'] = 'flat'
    df['baseline_entry'] = False
    df['baseline_exit'] = False
    
    # Detect crossovers
    # Cross above: fast_ma[t] > slow_ma[t] and fast_ma[t-1] <= slow_ma[t-1]
    # Cross below: fast_ma[t] < slow_ma[t] and fast_ma[t-1] >= slow_ma[t-1]

    # Use fillna(False) to handle NaN values properly
    fast_above_slow = (df['fast_ma'] > df['slow_ma']).fillna(False)
    fast_above_slow_prev = fast_above_slow.shift(1).fillna(False)

    cross_above = fast_above_slow & ~fast_above_slow_prev
    cross_below = ~fast_above_slow & fast_above_slow_prev
    
    # State machine: track position bar by bar
    position = 'flat'
    
    for idx in df.index:
        # Skip if we don't have both MAs yet
        if pd.isna(df.loc[idx, 'fast_ma']) or pd.isna(df.loc[idx, 'slow_ma']):
            df.loc[idx, 'baseline_side'] = 'flat'
            continue
        
        # Check for signals
        if cross_above.loc[idx]:
            # Enter long
            if position == 'flat':
                df.loc[idx, 'baseline_entry'] = True
                df.loc[idx, 'baseline_side'] = 'long'
                position = 'long'
            else:
                # Already long, stay long
                df.loc[idx, 'baseline_side'] = 'long'
        
        elif cross_below.loc[idx]:
            # Exit to flat
            if position == 'long':
                df.loc[idx, 'baseline_exit'] = True
                df.loc[idx, 'baseline_side'] = 'flat'
                position = 'flat'
            else:
                # Already flat, stay flat
                df.loc[idx, 'baseline_side'] = 'flat'
        
        else:
            # No crossover, maintain position
            df.loc[idx, 'baseline_side'] = position
    
    return df


def validate_baseline_signals(df: pd.DataFrame) -> dict:
    """
    Validate baseline signals and return summary statistics.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with baseline signals
    
    Returns
    -------
    dict
        Summary statistics:
        - n_entries: Number of long entries
        - n_exits: Number of exits
        - pct_long: Percentage of bars in long position
        - avg_hold_bars: Average holding period in bars
    """
    n_entries = df['baseline_entry'].sum()
    n_exits = df['baseline_exit'].sum()
    n_long = (df['baseline_side'] == 'long').sum()
    pct_long = n_long / len(df) * 100 if len(df) > 0 else 0
    
    # Calculate average holding period
    if n_entries > 0:
        # Find holding periods
        in_trade = False
        hold_start = None
        hold_periods = []
        
        for idx in df.index:
            if df.loc[idx, 'baseline_entry']:
                in_trade = True
                hold_start = idx
            elif df.loc[idx, 'baseline_exit'] and in_trade:
                in_trade = False
                if hold_start is not None:
                    hold_periods.append(df.index.get_loc(idx) - df.index.get_loc(hold_start))
        
        avg_hold_bars = np.mean(hold_periods) if hold_periods else 0
    else:
        avg_hold_bars = 0
    
    return {
        'n_entries': int(n_entries),
        'n_exits': int(n_exits),
        'pct_long': round(pct_long, 2),
        'avg_hold_bars': round(avg_hold_bars, 2)
    }

