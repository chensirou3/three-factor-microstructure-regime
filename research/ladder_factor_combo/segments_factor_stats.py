"""
Direction 1: Segment-level factor statistics

Attach factor features to segments and analyze performance by factor bins.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def attach_factor_features_to_segments(
    segments_df: pd.DataFrame,
    root: Path,
    merged_dir: str,
    ladder_dir: str
) -> pd.DataFrame:
    """
    Attach factor features from segment start time.
    
    Args:
        segments_df: DataFrame with segments
        root: Project root path
        merged_dir: Path to merged factor data
        ladder_dir: Path to ladder features
    
    Returns:
        segments_df with factor columns added
    """
    logger.info("Attaching factor features to segments...")
    
    segments_with_factors = []
    
    for symbol in segments_df['symbol'].unique():
        for timeframe in segments_df['timeframe'].unique():
            # Filter segments for this symbol×timeframe
            mask = (segments_df['symbol'] == symbol) & (segments_df['timeframe'] == timeframe)
            seg_subset = segments_df[mask].copy()
            
            if len(seg_subset) == 0:
                continue
            
            # Load Ladder data (has factors merged)
            ladder_file = root / ladder_dir / f"ladder_{symbol}_{timeframe}.parquet"
            
            if not ladder_file.exists():
                logger.warning(f"  Ladder file not found: {ladder_file}")
                continue
            
            df = pd.read_parquet(ladder_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # For each segment, find start bar and attach factors
            for idx, row in seg_subset.iterrows():
                start_time = pd.to_datetime(row['start_time'])
                
                # Find matching bar (exact or nearest)
                time_diff = (df['timestamp'] - start_time).abs()
                nearest_idx = time_diff.idxmin()
                
                # Attach factor values
                factor_bar = df.loc[nearest_idx]
                
                seg_subset.loc[idx, 'ManipScore_z'] = factor_bar.get('ManipScore_z', np.nan)
                seg_subset.loc[idx, 'OFI_z'] = factor_bar.get('OFI_z', np.nan)
                seg_subset.loc[idx, 'OFI_abs_z'] = factor_bar.get('OFI_abs_z', np.nan)
                seg_subset.loc[idx, 'VolLiqScore'] = factor_bar.get('VolLiqScore', np.nan)
                seg_subset.loc[idx, 'RiskScore'] = factor_bar.get('RiskScore', np.nan)
                seg_subset.loc[idx, 'q_manip'] = factor_bar.get('q_manip', np.nan)
                seg_subset.loc[idx, 'q_ofi'] = factor_bar.get('q_ofi', np.nan)
                seg_subset.loc[idx, 'q_vol'] = factor_bar.get('q_vol', np.nan)
                seg_subset.loc[idx, 'risk_regime'] = factor_bar.get('risk_regime', 'unknown')
            
            segments_with_factors.append(seg_subset)
            logger.info(f"  ✓ {symbol}_{timeframe}: {len(seg_subset)} segments")
    
    if segments_with_factors:
        result = pd.concat(segments_with_factors, ignore_index=True)
        logger.info(f"✓ Total segments with factors: {len(result)}")
        return result
    else:
        logger.warning("No segments with factors!")
        return pd.DataFrame()


def compute_segment_factor_stats(
    segments_with_factors: pd.DataFrame,
    factor_bins: dict,
    output_dir: Path
) -> pd.DataFrame:
    """
    Compute segment performance statistics by factor bins.
    
    Args:
        segments_with_factors: Segments with factor columns
        factor_bins: Bin edges for each factor
        output_dir: Output directory
    
    Returns:
        DataFrame with statistics by factor bins
    """
    logger.info("Computing segment statistics by factor bins...")
    
    stats_list = []
    
    # 1. Stats by |ManipScore_z| bins
    if 'ManipScore_z' in segments_with_factors.columns:
        segments_with_factors['manip_z_abs'] = segments_with_factors['ManipScore_z'].abs()
        segments_with_factors['manip_bin'] = pd.cut(
            segments_with_factors['manip_z_abs'],
            bins=factor_bins['manip_z_abs'],
            include_lowest=True
        )
        
        for bin_label, group in segments_with_factors.groupby('manip_bin', observed=True):
            if len(group) > 0:
                stats_list.append({
                    'factor': 'manip_z_abs',
                    'bin': str(bin_label),
                    'count': len(group),
                    'mean_return': group['segment_return'].mean(),
                    'median_return': group['segment_return'].median(),
                    'std_return': group['segment_return'].std(),
                    'mean_length': group['length_bars'].mean(),
                    'mean_max_dd': group['segment_max_drawdown'].mean(),
                    'mean_max_runup': group['segment_max_runup'].mean(),
                    'pct_positive': (group['segment_return'] > 0).mean() * 100,
                })
    
    # 2. Stats by q_vol bins
    if 'q_vol' in segments_with_factors.columns:
        segments_with_factors['volliq_bin'] = pd.cut(
            segments_with_factors['q_vol'],
            bins=factor_bins['volliq_quantile'],
            include_lowest=True
        )
        
        for bin_label, group in segments_with_factors.groupby('volliq_bin', observed=True):
            if len(group) > 0:
                stats_list.append({
                    'factor': 'q_vol',
                    'bin': str(bin_label),
                    'count': len(group),
                    'mean_return': group['segment_return'].mean(),
                    'median_return': group['segment_return'].median(),
                    'std_return': group['segment_return'].std(),
                    'mean_length': group['length_bars'].mean(),
                    'mean_max_dd': group['segment_max_drawdown'].mean(),
                    'mean_max_runup': group['segment_max_runup'].mean(),
                    'pct_positive': (group['segment_return'] > 0).mean() * 100,
                })
    
    # 3. Stats by OFI_z bins (direction-aware)
    if 'OFI_z' in segments_with_factors.columns:
        # For upTrend segments
        up_segments = segments_with_factors[segments_with_factors['direction'] == 'up'].copy()
        if len(up_segments) > 0:
            up_segments['ofi_bin'] = pd.cut(
                up_segments['OFI_z'],
                bins=factor_bins['ofi_z'],
                include_lowest=True
            )
            
            for bin_label, group in up_segments.groupby('ofi_bin', observed=True):
                if len(group) > 0:
                    stats_list.append({
                        'factor': 'OFI_z_upTrend',
                        'bin': str(bin_label),
                        'count': len(group),
                        'mean_return': group['segment_return'].mean(),
                        'median_return': group['segment_return'].median(),
                        'std_return': group['segment_return'].std(),
                        'mean_length': group['length_bars'].mean(),
                        'mean_max_dd': group['segment_max_drawdown'].mean(),
                        'mean_max_runup': group['segment_max_runup'].mean(),
                        'pct_positive': (group['segment_return'] > 0).mean() * 100,
                    })
    
    # 4. Stats by risk_regime
    if 'risk_regime' in segments_with_factors.columns:
        for regime, group in segments_with_factors.groupby('risk_regime'):
            if len(group) > 0:
                stats_list.append({
                    'factor': 'risk_regime',
                    'bin': regime,
                    'count': len(group),
                    'mean_return': group['segment_return'].mean(),
                    'median_return': group['segment_return'].median(),
                    'std_return': group['segment_return'].std(),
                    'mean_length': group['length_bars'].mean(),
                    'mean_max_dd': group['segment_max_drawdown'].mean(),
                    'mean_max_runup': group['segment_max_runup'].mean(),
                    'pct_positive': (group['segment_return'] > 0).mean() * 100,
                })
    
    stats_df = pd.DataFrame(stats_list)
    
    # Save
    output_file = output_dir / "segments_factor_stats.csv"
    stats_df.to_csv(output_file, index=False)
    logger.info(f"✓ Saved factor stats: {output_file}")
    
    return stats_df


def main():
    """Main entry point."""
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    root = Path(__file__).resolve().parents[2]
    output_dir = root / config['outputs']['root']
    
    # Load segments
    segments_file = output_dir / "segments_all.csv"
    if not segments_file.exists():
        logger.error(f"Segments file not found: {segments_file}")
        logger.error("Please run segments_extractor.py first!")
        return
    
    segments_df = pd.read_csv(segments_file)
    logger.info(f"Loaded {len(segments_df)} segments from {segments_file}")
    
    # Attach factors
    segments_with_factors = attach_factor_features_to_segments(
        segments_df,
        root,
        config['merged_dir'],
        config['ladder_dir']
    )
    
    # Save segments with factors
    segments_with_factors_file = output_dir / "segments_with_factors.csv"
    segments_with_factors.to_csv(segments_with_factors_file, index=False)
    logger.info(f"✓ Saved segments with factors: {segments_with_factors_file}")
    
    # Compute stats
    compute_segment_factor_stats(
        segments_with_factors,
        config['direction1']['factor_bins'],
        output_dir
    )
    
    logger.info("="*80)
    logger.info("✓ Direction 1 analysis complete!")
    logger.info("="*80)


if __name__ == "__main__":
    main()

