"""
Direction 4: Factor-based exit rules

Ladder controls entry, factors trigger exits or partial profit-taking.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_extreme_factor_conditions(
    row: pd.Series,
    exit_rules: Dict[str, float]
) -> bool:
    """
    Check if extreme factor conditions are met.
    
    Args:
        row: DataFrame row with factor values
        exit_rules: Exit rule thresholds
    
    Returns:
        True if extreme conditions detected
    """
    # Extract factor values
    riskscore = row.get('RiskScore', 0)
    manip_z_abs = abs(row.get('ManipScore_z', 0))
    q_vol = row.get('q_vol', 0)
    
    # Check extreme conditions (any one triggers)
    extreme_conditions = [
        riskscore > exit_rules['extreme_riskscore_quantile'],
        manip_z_abs > exit_rules['extreme_manip_z_abs'],
        q_vol > exit_rules['extreme_volliq_quantile'],
    ]
    
    return any(extreme_conditions)


def apply_factor_based_exit_rules(
    df: pd.DataFrame,
    variant_id: str,
    exit_type: str,
    exit_rules: Dict[str, float]
) -> pd.DataFrame:
    """
    Apply factor-based exit rules to Ladder strategy.
    
    Args:
        df: DataFrame with base Ladder signals (base_side, base_entry, base_exit)
        variant_id: Variant identifier
        exit_type: 'full' or 'partial'
        exit_rules: Exit rule configuration
    
    Returns:
        DataFrame with final_side, final_entry, final_exit, position_size
    """
    df = df.copy()
    
    # Start with base Ladder signals
    df['final_side'] = df['base_side'].copy()
    df['final_entry'] = df['base_entry'].copy()
    df['final_exit'] = df['base_exit'].copy()
    df['position_size'] = 1.0
    
    # Track position state
    in_position = False
    current_size = 0.0
    
    for idx in df.index:
        # Entry
        if df.loc[idx, 'base_entry']:
            in_position = True
            current_size = 1.0
            df.loc[idx, 'position_size'] = current_size
        
        # Base exit
        if df.loc[idx, 'base_exit']:
            in_position = False
            current_size = 0.0
            df.loc[idx, 'position_size'] = 0.0
        
        # Check for factor-based exit while in position
        if in_position and current_size > 0:
            if check_extreme_factor_conditions(df.loc[idx], exit_rules):
                if exit_type == 'full':
                    # Full exit
                    df.loc[idx, 'final_exit'] = True
                    df.loc[idx, 'final_side'] = 'flat'
                    df.loc[idx, 'position_size'] = 0.0
                    in_position = False
                    current_size = 0.0
                    
                elif exit_type == 'partial':
                    # Partial exit
                    partial_fraction = exit_rules['partial_exit_fraction']
                    current_size *= (1 - partial_fraction)
                    df.loc[idx, 'position_size'] = current_size
                    
                    # If size becomes too small, close completely
                    if current_size < 0.1:
                        df.loc[idx, 'final_exit'] = True
                        df.loc[idx, 'final_side'] = 'flat'
                        df.loc[idx, 'position_size'] = 0.0
                        in_position = False
                        current_size = 0.0
            else:
                # No extreme conditions, maintain current size
                df.loc[idx, 'position_size'] = current_size
        else:
            df.loc[idx, 'position_size'] = current_size
    
    return df


def generate_ladder_baseline_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate baseline Ladder signals (for Direction 4 input).
    
    Args:
        df: DataFrame with upTrend column
    
    Returns:
        DataFrame with base_side, base_entry, base_exit
    """
    df = df.copy()
    
    # Generate Ladder signals
    df['base_side'] = 'flat'
    df.loc[df['upTrend'], 'base_side'] = 'long'
    
    df['base_entry'] = False
    df['base_exit'] = False
    
    df.loc[(df['base_side'] == 'long') & (df['base_side'].shift(1).fillna('flat') == 'flat'), 'base_entry'] = True
    df.loc[(df['base_side'] == 'flat') & (df['base_side'].shift(1).fillna('flat') == 'long'), 'base_exit'] = True
    
    return df


def main():
    """Test factor-based exit rules."""
    import yaml
    
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    root = Path(__file__).resolve().parents[2]
    
    # Test on BTCUSD 4h
    symbol = "BTCUSD"
    timeframe = "4h"
    
    logger.info(f"Testing Direction 4 on {symbol} {timeframe}...")
    
    # Load Ladder data
    ladder_file = root / config['ladder_dir'] / f"ladder_{symbol}_{timeframe}.parquet"
    df = pd.read_parquet(ladder_file)
    
    # Generate baseline signals
    df = generate_ladder_baseline_signals(df)
    
    # Test each variant
    for variant_cfg in config['direction4']['variants']:
        variant_id = variant_cfg['id']
        exit_type = variant_cfg['exit_type']
        
        logger.info(f"\nTesting variant: {variant_id} (exit_type={exit_type})")
        
        df_with_exits = apply_factor_based_exit_rules(
            df,
            variant_id,
            exit_type,
            config['direction4']['exit_rules']
        )
        
        # Count exits
        base_exits = df['base_exit'].sum()
        final_exits = df_with_exits['final_exit'].sum()
        factor_exits = final_exits - base_exits
        
        logger.info(f"  Base Ladder exits: {base_exits}")
        logger.info(f"  Final exits: {final_exits}")
        logger.info(f"  Factor-triggered exits: {factor_exits}")
        
        # Analyze position sizes
        if exit_type == 'partial':
            sizes = df_with_exits[df_with_exits['final_side'] == 'long']['position_size']
            logger.info(f"  Position size stats:")
            logger.info(f"    Mean: {sizes.mean():.3f}")
            logger.info(f"    Min: {sizes.min():.3f}")
            logger.info(f"    Max: {sizes.max():.3f}")
    
    logger.info("\n✓ Direction 4 test complete!")


if __name__ == "__main__":
    main()

