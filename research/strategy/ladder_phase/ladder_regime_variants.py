"""
Ladder + Regime Strategy Variants

Applies regime policies to Ladder signals.
Reuses RegimePolicy from Phase 3.
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.phase3.regime_policies import RegimePolicy, load_policies_from_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_regime_policy_to_ladder_signals(df: pd.DataFrame,
                                          policy: RegimePolicy) -> pd.DataFrame:
    """
    Apply regime policy to Ladder signals.
    
    This is the Ladder equivalent of apply_regime_policy_to_signals() from Phase 3.
    
    Args:
        df: DataFrame with Ladder signals and regime features
        policy: RegimePolicy object
    
    Returns:
        DataFrame with final signals after applying regime policy
    """
    df = df.copy()
    
    # Start with Ladder signals
    df['final_side'] = df['signal_side'].copy()
    df['final_entry'] = df['entry_signal'].copy()
    df['final_exit'] = df['exit_signal'].copy()
    df['position_size'] = 1.0
    
    if not policy.use_regime_policy:
        # No regime policy, use signals as-is
        return df
    
    # Apply regime-based entry filtering and position sizing
    for idx in df.index:
        regime = df.loc[idx, 'risk_regime']
        
        if regime not in policy.actions:
            continue
        
        action = policy.actions[regime]
        
        # Block entry if not allowed in this regime
        if not action.allow_entry and df.loc[idx, 'entry_signal']:
            df.loc[idx, 'final_entry'] = False
            df.loc[idx, 'final_side'] = 'flat'
        
        # Apply position size multiplier
        if df.loc[idx, 'final_side'] == 'long':
            df.loc[idx, 'position_size'] = action.size_multiplier
    
    # Apply dynamic exit rules if enabled
    if policy.dynamic_exit.enabled:
        high_count = 0
        in_position = False
        
        for idx in df.index:
            # Track if we're in a position
            if df.loc[idx, 'final_entry']:
                in_position = True
                high_count = 0
            
            if df.loc[idx, 'final_exit']:
                in_position = False
                high_count = 0
            
            # Count consecutive HIGH regime bars while in position
            if in_position and df.loc[idx, 'risk_regime'] == 'high':
                high_count += 1
                
                # Force exit if HIGH persists too long
                if high_count >= policy.dynamic_exit.high_persistence_bars:
                    df.loc[idx, 'final_exit'] = True
                    df.loc[idx, 'final_side'] = 'flat'
                    in_position = False
                    high_count = 0
            else:
                high_count = 0
    
    return df


def load_ladder_policies_from_config(cfg_path: Path) -> dict:
    """
    Load Ladder regime policies from config_ladder_phase.yaml.
    
    Args:
        cfg_path: Path to config_ladder_phase.yaml
    
    Returns:
        Dictionary mapping policy_id to RegimePolicy object
    """
    # Reuse the same loader from Phase 3
    return load_policies_from_config(cfg_path)


if __name__ == "__main__":
    # Test loading policies
    root = Path(__file__).resolve().parents[3]
    cfg_path = root / "research/strategy/ladder_phase/config_ladder_phase.yaml"
    
    policies = load_ladder_policies_from_config(cfg_path)
    
    logger.info(f"Loaded {len(policies)} Ladder policies:")
    for policy_id, policy in policies.items():
        logger.info(f"  - {policy_id}: {policy.description}")

