"""
Regime-aware wrapper for baseline strategy.

Applies three-factor regime information to baseline signals:
1. Gating: Block new entries in high-risk regimes
2. Position sizing: Scale position size based on risk_regime

This allows us to analyze how regime-based risk management affects
baseline strategy performance.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def apply_regime_wrapper(
    df: pd.DataFrame,
    gating_cfg: Dict[str, Any],
    sizing_cfg: Dict[str, Any],
    triple_high_box_name: str
) -> pd.DataFrame:
    """
    Apply regime-based gating and position sizing to baseline signals.
    
    Parameters
    ----------
    df : pd.DataFrame
        Must contain:
        - Baseline signals: baseline_side, baseline_entry, baseline_exit
        - Regime features: RiskScore, risk_regime, high_pressure, three_factor_box
    gating_cfg : dict
        Gating configuration with keys:
        - block_new_entries_in_high_pressure: bool
        - block_new_entries_in_triple_high_box: bool
    sizing_cfg : dict
        Position sizing configuration with keys:
        - base_size: float
        - size_by_riskregime: dict[str, float]
    triple_high_box_name : str
        Name of the triple-high box (e.g., "M_high_O_high_V_high")
    
    Returns
    -------
    pd.DataFrame
        Input df with added columns:
        - final_side: Actual position after gating ('flat' or 'long')
        - final_entry: True if actually entering long
        - final_exit: True if actually exiting
        - position_size: Numeric size (0 for flat, scaled for long)
        - entry_blocked: True if entry was blocked by gating
        - block_reason: Reason for blocking (if applicable)
    """
    df = df.copy()
    
    # Initialize output columns
    df['final_side'] = 'flat'
    df['final_entry'] = False
    df['final_exit'] = False
    df['position_size'] = 0.0
    df['entry_blocked'] = False
    df['block_reason'] = ''
    
    # Extract config
    block_high_pressure = gating_cfg.get('block_new_entries_in_high_pressure', True)
    block_triple_high = gating_cfg.get('block_new_entries_in_triple_high_box', True)
    base_size = sizing_cfg.get('base_size', 1.0)
    size_by_regime = sizing_cfg.get('size_by_riskregime', {'low': 1.0, 'medium': 0.7, 'high': 0.3})
    
    # State tracking
    current_position = 'flat'
    current_size = 0.0
    
    # Counters for logging
    n_entries_baseline = 0
    n_entries_blocked = 0
    n_entries_allowed = 0
    
    for idx in df.index:
        baseline_side = df.loc[idx, 'baseline_side']
        baseline_entry = df.loc[idx, 'baseline_entry']
        baseline_exit = df.loc[idx, 'baseline_exit']
        
        # Get regime info
        risk_regime = df.loc[idx, 'risk_regime'] if 'risk_regime' in df.columns else 'medium'
        high_pressure = df.loc[idx, 'high_pressure'] if 'high_pressure' in df.columns else False
        three_factor_box = df.loc[idx, 'three_factor_box'] if 'three_factor_box' in df.columns else ''
        
        # Handle entry signals
        if baseline_entry:
            n_entries_baseline += 1
            
            # Check gating rules
            blocked = False
            block_reason = ''
            
            if block_high_pressure and high_pressure:
                blocked = True
                block_reason = 'high_pressure'
            elif block_triple_high and three_factor_box == triple_high_box_name:
                blocked = True
                block_reason = 'triple_high_box'
            
            if blocked:
                # Block entry, stay flat
                n_entries_blocked += 1
                df.loc[idx, 'final_side'] = 'flat'
                df.loc[idx, 'final_entry'] = False
                df.loc[idx, 'position_size'] = 0.0
                df.loc[idx, 'entry_blocked'] = True
                df.loc[idx, 'block_reason'] = block_reason
                current_position = 'flat'
                current_size = 0.0
            else:
                # Allow entry, calculate size
                n_entries_allowed += 1
                size_multiplier = size_by_regime.get(risk_regime, 0.7)
                position_size = base_size * size_multiplier
                
                df.loc[idx, 'final_side'] = 'long'
                df.loc[idx, 'final_entry'] = True
                df.loc[idx, 'position_size'] = position_size
                current_position = 'long'
                current_size = position_size
        
        # Handle exit signals
        elif baseline_exit:
            if current_position == 'long':
                # Exit to flat (always allowed)
                df.loc[idx, 'final_side'] = 'flat'
                df.loc[idx, 'final_exit'] = True
                df.loc[idx, 'position_size'] = 0.0
                current_position = 'flat'
                current_size = 0.0
            else:
                # Already flat
                df.loc[idx, 'final_side'] = 'flat'
                df.loc[idx, 'position_size'] = 0.0
        
        # No signal, maintain position
        else:
            df.loc[idx, 'final_side'] = current_position
            df.loc[idx, 'position_size'] = current_size
    
    # Log gating statistics
    if n_entries_baseline > 0:
        block_rate = n_entries_blocked / n_entries_baseline * 100
        logger.info(f"Gating stats: {n_entries_baseline} baseline entries, "
                   f"{n_entries_blocked} blocked ({block_rate:.1f}%), "
                   f"{n_entries_allowed} allowed")
    
    return df


def analyze_gating_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze the impact of regime-based gating on entry signals.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with baseline and final signals
    
    Returns
    -------
    dict
        Statistics on gating impact:
        - n_baseline_entries: Number of baseline entry signals
        - n_blocked_entries: Number of blocked entries
        - n_final_entries: Number of actual entries
        - block_rate_pct: Percentage of entries blocked
        - blocks_by_reason: Count of blocks by reason
    """
    n_baseline = df['baseline_entry'].sum()
    n_blocked = df['entry_blocked'].sum()
    n_final = df['final_entry'].sum()
    
    block_rate = (n_blocked / n_baseline * 100) if n_baseline > 0 else 0
    
    # Count blocks by reason
    blocks_by_reason = df[df['entry_blocked']]['block_reason'].value_counts().to_dict()
    
    return {
        'n_baseline_entries': int(n_baseline),
        'n_blocked_entries': int(n_blocked),
        'n_final_entries': int(n_final),
        'block_rate_pct': round(block_rate, 2),
        'blocks_by_reason': blocks_by_reason
    }

