"""
Direction 2: Factor-based entry filtering and position sizing

Ladder determines direction, factors determine: do we enter? how much size?
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


def classify_ladder_entry_health(
    row: pd.Series,
    thresholds: Dict[str, float]
) -> str:
    """
    Classify Ladder entry as 'healthy', 'suspicious', or 'unhealthy'.
    
    Args:
        row: DataFrame row with factor values
        thresholds: Health thresholds from config
    
    Returns:
        'healthy', 'suspicious', or 'unhealthy'
    """
    # Extract factor values
    manip_z_abs = abs(row.get('ManipScore_z', 0))
    q_vol = row.get('q_vol', 0.5)
    ofi_z = row.get('OFI_z', 0)
    ladder_state = row.get('ladder_state', 0)
    
    # Healthy criteria
    healthy_conditions = []
    
    # 1. Low manipulation
    healthy_conditions.append(manip_z_abs < thresholds['max_manip_z_abs'])
    
    # 2. Low volume/liquidity stress
    healthy_conditions.append(q_vol < thresholds['max_volliq_quantile'])
    
    # 3. OFI aligned with direction (for upTrend)
    if ladder_state == 1:  # upTrend
        healthy_conditions.append(ofi_z >= thresholds['min_ofi_same_dir_z'])
    elif ladder_state == -1:  # downTrend
        healthy_conditions.append(ofi_z <= -thresholds['min_ofi_same_dir_z'])
    
    # Classify
    if all(healthy_conditions):
        return 'healthy'
    elif sum(healthy_conditions) >= len(healthy_conditions) - 1:
        return 'suspicious'
    else:
        return 'unhealthy'


def generate_entry_filter_and_sizing_signals(
    df: pd.DataFrame,
    variant_id: str,
    variant_config: Dict,
    thresholds: Dict[str, float],
    sizing: Dict[str, float]
) -> pd.DataFrame:
    """
    Generate entry signals with factor-based filtering and sizing.
    
    Args:
        df: DataFrame with Ladder signals and factor columns
        variant_id: Variant identifier (D2_plain_ladder, D2_healthy_only, etc.)
        variant_config: Variant configuration
        thresholds: Health thresholds
        sizing: Position sizing by health
    
    Returns:
        DataFrame with final_side, final_entry, final_exit, position_size
    """
    df = df.copy()
    
    # Ensure required columns exist
    if 'upTrend' not in df.columns:
        logger.error("Missing upTrend column!")
        return df
    
    # Generate base Ladder signals
    df['base_side'] = 'flat'
    df.loc[df['upTrend'], 'base_side'] = 'long'
    
    df['base_entry'] = False
    df['base_exit'] = False
    
    df.loc[(df['base_side'] == 'long') & (df['base_side'].shift(1) == 'flat'), 'base_entry'] = True
    df.loc[(df['base_side'] == 'flat') & (df['base_side'].shift(1) == 'long'), 'base_exit'] = True
    
    # Classify health at each bar
    df['entry_health'] = df.apply(
        lambda row: classify_ladder_entry_health(row, thresholds),
        axis=1
    )
    
    # Apply variant logic
    use_health_filter = variant_config.get('use_health_filter', False)
    use_health_sizing = variant_config.get('use_health_sizing', False)
    
    df['final_side'] = df['base_side'].copy()
    df['final_entry'] = df['base_entry'].copy()
    df['final_exit'] = df['base_exit'].copy()
    df['position_size'] = 1.0
    
    if use_health_filter:
        # D2_healthy_only: Only allow entries on 'healthy' signals
        for idx in df.index:
            if df.loc[idx, 'base_entry']:
                if df.loc[idx, 'entry_health'] != 'healthy':
                    # Block this entry
                    df.loc[idx, 'final_entry'] = False
                    df.loc[idx, 'final_side'] = 'flat'
    
    if use_health_sizing:
        # D2_size_by_health: Scale position by health
        for idx in df.index:
            if df.loc[idx, 'final_side'] == 'long':
                health = df.loc[idx, 'entry_health']
                df.loc[idx, 'position_size'] = sizing.get(health, 0.0)
                
                # If size is 0, treat as flat
                if df.loc[idx, 'position_size'] == 0:
                    df.loc[idx, 'final_side'] = 'flat'
                    if df.loc[idx, 'final_entry']:
                        df.loc[idx, 'final_entry'] = False
    
    # Recalculate entry/exit signals based on final_side
    df['final_entry'] = False
    df['final_exit'] = False
    
    df.loc[(df['final_side'] == 'long') & (df['final_side'].shift(1).fillna('flat') == 'flat'), 'final_entry'] = True
    df.loc[(df['final_side'] == 'flat') & (df['final_side'].shift(1).fillna('flat') == 'long'), 'final_exit'] = True
    
    return df


def load_ladder_data_with_factors(
    symbol: str,
    timeframe: str,
    root: Path,
    ladder_dir: str
) -> pd.DataFrame:
    """
    Load Ladder data with factor features.
    
    Args:
        symbol: Symbol name
        timeframe: Timeframe
        root: Project root
        ladder_dir: Ladder features directory
    
    Returns:
        DataFrame with Ladder and factor columns
    """
    ladder_file = root / ladder_dir / f"ladder_{symbol}_{timeframe}.parquet"
    
    if not ladder_file.exists():
        raise FileNotFoundError(f"Ladder file not found: {ladder_file}")
    
    df = pd.read_parquet(ladder_file)
    
    # Ensure required columns
    required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'upTrend', 'ladder_state']
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return df


def main():
    """Test entry filtering and sizing."""
    import yaml
    
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    root = Path(__file__).resolve().parents[2]
    
    # Test on BTCUSD 4h
    symbol = "BTCUSD"
    timeframe = "4h"
    
    logger.info(f"Testing Direction 2 on {symbol} {timeframe}...")
    
    # Load data
    df = load_ladder_data_with_factors(symbol, timeframe, root, config['ladder_dir'])
    
    # Test each variant
    for variant_cfg in config['direction2']['variants']:
        variant_id = variant_cfg['id']
        logger.info(f"\nTesting variant: {variant_id}")
        
        df_signals = generate_entry_filter_and_sizing_signals(
            df,
            variant_id,
            variant_cfg,
            config['direction2']['healthy_thresholds'],
            config['direction2']['sizing']
        )
        
        # Count signals
        n_entries = df_signals['final_entry'].sum()
        n_exits = df_signals['final_exit'].sum()
        avg_size = df_signals[df_signals['final_side'] == 'long']['position_size'].mean()
        
        logger.info(f"  Entries: {n_entries}")
        logger.info(f"  Exits: {n_exits}")
        logger.info(f"  Avg position size: {avg_size:.2f}")
        
        # Health distribution
        health_dist = df_signals[df_signals['base_entry']]['entry_health'].value_counts()
        logger.info(f"  Entry health distribution:\n{health_dist}")
    
    logger.info("\n✓ Direction 2 test complete!")


if __name__ == "__main__":
    main()

