"""
Strategy Variants - Apply Regime Policies to Baseline Signals

This module takes baseline EMA signals and applies regime-based policies
to control entry, sizing, and dynamic exits.
"""

import pandas as pd
import numpy as np
from typing import Optional
import logging

from .regime_policies import RegimePolicy, get_regime_action

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_regime_policy_to_signals(
    df: pd.DataFrame,
    policy: RegimePolicy
) -> pd.DataFrame:
    """
    Apply regime policy to baseline signals.
    
    Input df must contain:
        - baseline_side: 1 (long), 0 (flat), -1 (short)
        - baseline_entry: True when new position should open
        - baseline_exit: True when position should close
        - risk_regime: 'low', 'medium', 'high'
        - RiskScore: float [0, 1]
        
    Output df will have:
        - final_side: Adjusted side after policy
        - final_entry: Adjusted entry signal
        - final_exit: Adjusted exit signal
        - position_size: Size multiplier for position
        - exit_reason: String describing why exit occurred
        
    Args:
        df: DataFrame with baseline signals and regime features
        policy: RegimePolicy to apply
        
    Returns:
        DataFrame with final signals and position sizing
    """
    df = df.copy()
    
    # Initialize output columns
    df['final_side'] = 0
    df['final_entry'] = False
    df['final_exit'] = False
    df['position_size'] = 0.0
    df['exit_reason'] = ''
    df['entry_regime'] = ''  # Track regime at entry
    
    # If not using regime policy, just copy baseline
    if not policy.use_regime_policy:
        df['final_side'] = df['baseline_side']
        df['final_entry'] = df['baseline_entry']
        df['final_exit'] = df['baseline_exit']
        df['position_size'] = 1.0
        df.loc[df['final_exit'], 'exit_reason'] = 'baseline_exit'
        return df
    
    # Track state
    in_position = False
    entry_regime = None
    high_regime_count = 0  # Consecutive bars in HIGH regime while in position
    
    for i in range(len(df)):
        current_regime = df.loc[df.index[i], 'risk_regime']
        baseline_entry = df.loc[df.index[i], 'baseline_entry']
        baseline_exit = df.loc[df.index[i], 'baseline_exit']
        baseline_side = df.loc[df.index[i], 'baseline_side']
        
        # Get regime action
        action = get_regime_action(policy, current_regime)
        
        # Handle entry signals
        if baseline_entry and not in_position:
            if action.allow_entry:
                # Allow entry
                df.loc[df.index[i], 'final_entry'] = True
                df.loc[df.index[i], 'final_side'] = baseline_side
                df.loc[df.index[i], 'position_size'] = action.size_multiplier
                df.loc[df.index[i], 'entry_regime'] = current_regime
                in_position = True
                entry_regime = current_regime
                high_regime_count = 0
                logger.debug(f"Entry at {df.index[i]}: regime={current_regime}, size={action.size_multiplier}")
            else:
                # Block entry due to regime policy
                df.loc[df.index[i], 'final_side'] = 0
                df.loc[df.index[i], 'position_size'] = 0.0
                logger.debug(f"Entry blocked at {df.index[i]}: regime={current_regime}")
        
        # Handle holding period
        elif in_position:
            # Check for baseline exit
            if baseline_exit:
                df.loc[df.index[i], 'final_exit'] = True
                df.loc[df.index[i], 'final_side'] = 0
                df.loc[df.index[i], 'position_size'] = 0.0
                df.loc[df.index[i], 'exit_reason'] = 'baseline_exit'
                in_position = False
                entry_regime = None
                high_regime_count = 0
                logger.debug(f"Baseline exit at {df.index[i]}")
                continue
            
            # Check for dynamic exit (if enabled)
            if policy.dynamic_exit.enabled:
                if current_regime == 'high':
                    high_regime_count += 1
                else:
                    high_regime_count = 0
                
                if high_regime_count >= policy.dynamic_exit.high_persistence_bars:
                    # Trigger dynamic exit
                    df.loc[df.index[i], 'final_exit'] = True
                    df.loc[df.index[i], 'final_side'] = 0
                    df.loc[df.index[i], 'position_size'] = 0.0
                    df.loc[df.index[i], 'exit_reason'] = f'high_persistence_{high_regime_count}bars'
                    in_position = False
                    entry_regime = None
                    high_regime_count = 0
                    logger.debug(f"Dynamic exit at {df.index[i]}: HIGH for {high_regime_count} bars")
                    continue
            
            # Continue holding
            df.loc[df.index[i], 'final_side'] = baseline_side
            # Keep entry regime size (could also dynamically adjust based on current regime)
            entry_action = get_regime_action(policy, entry_regime)
            df.loc[df.index[i], 'position_size'] = entry_action.size_multiplier
            df.loc[df.index[i], 'entry_regime'] = entry_regime
    
    return df


if __name__ == "__main__":
    # Test with sample data
    from pathlib import Path
    from .regime_policies import load_policies_from_config
    
    config_path = Path("research/strategy/phase3/config_phase3.yaml")
    policies = load_policies_from_config(config_path)
    
    # Create sample data
    sample_df = pd.DataFrame({
        'baseline_side': [1, 1, 1, 0, 1, 1, 0],
        'baseline_entry': [True, False, False, False, True, False, False],
        'baseline_exit': [False, False, True, False, False, False, True],
        'risk_regime': ['medium', 'medium', 'high', 'low', 'medium', 'high', 'high'],
        'RiskScore': [0.6, 0.65, 0.75, 0.4, 0.6, 0.72, 0.75]
    })
    
    print("\nTesting V1_medium_only policy:")
    result = apply_regime_policy_to_signals(sample_df, policies['V1_medium_only'])
    print(result[['risk_regime', 'baseline_entry', 'final_entry', 'final_exit', 'position_size', 'exit_reason']])

