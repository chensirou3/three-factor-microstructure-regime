"""
Direction 3: Multi-timeframe timing

High timeframe Ladder for direction, low timeframe + factors for precise timing.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def align_high_low_tf_ladder(
    high_tf_df: pd.DataFrame,
    low_tf_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Align high timeframe Ladder state to low timeframe bars.
    
    Args:
        high_tf_df: High timeframe DataFrame with ladder_state
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
    
    # Merge_asof to get most recent high TF state for each low TF bar
    merged = pd.merge_asof(
        low_tf_df,
        high_tf_df[['timestamp', 'ladder_state']].rename(columns={'ladder_state': 'high_tf_ladder_state'}),
        on='timestamp',
        direction='backward'
    )
    
    return merged


def check_factor_pullback_conditions(
    row: pd.Series,
    pullback_conditions: Dict[str, any]
) -> bool:
    """
    Check if factor pullback conditions are met.
    
    Args:
        row: DataFrame row with factor values
        pullback_conditions: Pullback condition thresholds
    
    Returns:
        True if pullback conditions met
    """
    q_vol = row.get('q_vol', 0.5)
    ofi_z = row.get('OFI_z', 0)
    riskscore = row.get('RiskScore', 0.5)
    
    # Pullback conditions
    volliq_range = pullback_conditions['volliq_range']
    ofi_z_min = pullback_conditions['ofi_z_min']
    riskscore_max = pullback_conditions['riskscore_max']
    
    conditions = [
        volliq_range[0] <= q_vol <= volliq_range[1],  # q_vol in neutral range
        ofi_z >= ofi_z_min,                            # OFI turning positive
        riskscore < riskscore_max,                     # RiskScore not too high
    ]
    
    return all(conditions)


def generate_mtf_timing_signals(
    low_df: pd.DataFrame,
    variant_id: str,
    use_factor_pullback: bool,
    pullback_conditions: Dict[str, any]
) -> pd.DataFrame:
    """
    Generate multi-timeframe timing signals.
    
    Args:
        low_df: Low timeframe DataFrame with high_tf_ladder_state attached
        variant_id: Variant identifier
        use_factor_pullback: Whether to use factor pullback conditions
        pullback_conditions: Pullback condition configuration
    
    Returns:
        DataFrame with final_side, final_entry, final_exit, position_size
    """
    df = low_df.copy()
    
    # Initialize signals
    df['final_side'] = 'flat'
    df['final_entry'] = False
    df['final_exit'] = False
    df['position_size'] = 1.0
    
    # Track position state
    in_position = False
    
    for idx in df.index:
        high_tf_state = df.loc[idx, 'high_tf_ladder_state']
        
        # Only consider long when high TF is in upTrend
        if high_tf_state == 1:
            if not in_position:
                # Check entry conditions
                if use_factor_pullback:
                    # D3_ladder_high_tf_dir_and_factor_pullback
                    if check_factor_pullback_conditions(df.loc[idx], pullback_conditions):
                        df.loc[idx, 'final_entry'] = True
                        df.loc[idx, 'final_side'] = 'long'
                        in_position = True
                else:
                    # D3_ladder_high_tf_dir_only: Simple entry when high TF upTrend starts
                    # Enter on first bar of high TF upTrend
                    if idx > 0 and df.loc[idx-1, 'high_tf_ladder_state'] != 1:
                        df.loc[idx, 'final_entry'] = True
                        df.loc[idx, 'final_side'] = 'long'
                        in_position = True
            else:
                # Already in position, maintain
                df.loc[idx, 'final_side'] = 'long'
        else:
            # High TF not in upTrend
            if in_position:
                # Exit position
                df.loc[idx, 'final_exit'] = True
                df.loc[idx, 'final_side'] = 'flat'
                in_position = False
            else:
                df.loc[idx, 'final_side'] = 'flat'
    
    return df


def load_and_align_mtf_data(
    symbol: str,
    high_tf: str,
    low_tf: str,
    root: Path,
    ladder_dir: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and align high and low timeframe data.
    
    Args:
        symbol: Symbol name
        high_tf: High timeframe
        low_tf: Low timeframe
        root: Project root
        ladder_dir: Ladder features directory
    
    Returns:
        Tuple of (high_tf_df, low_tf_df_aligned)
    """
    # Load high TF
    high_tf_file = root / ladder_dir / f"ladder_{symbol}_{high_tf}.parquet"
    if not high_tf_file.exists():
        raise FileNotFoundError(f"High TF file not found: {high_tf_file}")
    
    high_tf_df = pd.read_parquet(high_tf_file)
    
    # Load low TF
    low_tf_file = root / ladder_dir / f"ladder_{symbol}_{low_tf}.parquet"
    if not low_tf_file.exists():
        raise FileNotFoundError(f"Low TF file not found: {low_tf_file}")
    
    low_tf_df = pd.read_parquet(low_tf_file)
    
    # Align
    low_tf_aligned = align_high_low_tf_ladder(high_tf_df, low_tf_df)
    
    return high_tf_df, low_tf_aligned


def main():
    """Test multi-timeframe timing."""
    import yaml
    
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    root = Path(__file__).resolve().parents[2]
    
    # Test on BTCUSD: 4h high, 1h low
    symbol = "BTCUSD"
    high_tf = "4h"
    low_tf = "1h"
    
    logger.info(f"Testing Direction 3 on {symbol}: {high_tf} (high) + {low_tf} (low)...")
    
    # Load and align data
    high_tf_df, low_tf_aligned = load_and_align_mtf_data(
        symbol, high_tf, low_tf, root, config['ladder_dir']
    )
    
    logger.info(f"  High TF bars: {len(high_tf_df)}")
    logger.info(f"  Low TF bars: {len(low_tf_aligned)}")
    
    # Test each variant
    for variant_cfg in config['direction3']['variants']:
        variant_id = variant_cfg['id']
        use_factor_pullback = variant_cfg['use_factor_pullback']
        
        logger.info(f"\nTesting variant: {variant_id}")
        
        df_signals = generate_mtf_timing_signals(
            low_tf_aligned,
            variant_id,
            use_factor_pullback,
            config['direction3']['pullback_conditions']
        )
        
        # Count signals
        n_entries = df_signals['final_entry'].sum()
        n_exits = df_signals['final_exit'].sum()
        
        logger.info(f"  Entries: {n_entries}")
        logger.info(f"  Exits: {n_exits}")
        
        # High TF state distribution
        high_tf_dist = low_tf_aligned['high_tf_ladder_state'].value_counts()
        logger.info(f"  High TF state distribution:\n{high_tf_dist}")
    
    logger.info("\n✓ Direction 3 test complete!")


if __name__ == "__main__":
    main()

