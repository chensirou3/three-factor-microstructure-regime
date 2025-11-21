"""
Performance Comparator for Phase 3

Aggregates and compares performance across strategy variants,
symbols, and timeframes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def aggregate_variant_performance(
    phase3_root: Path,
    variants: List[str],
    symbols: List[str],
    timeframes: List[str]
) -> pd.DataFrame:
    """
    Aggregate performance across all variants.
    
    Args:
        phase3_root: Root directory for Phase 3 results
        variants: List of variant IDs
        symbols: List of symbols
        timeframes: List of timeframes
        
    Returns:
        DataFrame with aggregated performance metrics
    """
    all_summaries = []
    
    for variant_id in variants:
        variant_dir = phase3_root / variant_id
        
        for symbol in symbols:
            for timeframe in timeframes:
                summary_path = variant_dir / f"summary_{symbol}_{timeframe}.csv"
                
                if summary_path.exists():
                    df = pd.read_csv(summary_path)
                    all_summaries.append(df)
                else:
                    logger.warning(f"Missing: {summary_path}")
    
    if not all_summaries:
        logger.error("No summary files found!")
        return pd.DataFrame()
    
    # Combine all summaries
    combined = pd.concat(all_summaries, ignore_index=True)
    
    logger.info(f"Aggregated {len(combined)} experiment results")
    return combined


def compute_variant_rankings(agg_df: pd.DataFrame, rank_by: str = 'sharpe_like') -> pd.DataFrame:
    """
    Rank variants by a specific metric.
    
    Args:
        agg_df: Aggregated performance DataFrame
        rank_by: Metric to rank by
        
    Returns:
        DataFrame with variant rankings
    """
    # Group by variant and compute mean metrics
    variant_stats = agg_df.groupby('variant_id').agg({
        'total_trades': 'sum',
        'gross_mean_R': 'mean',
        'net_mean_R': 'mean',
        'sharpe_like': 'mean',
        'tail_R_p5': 'mean',
        'tail_R_p1': 'mean',
        'win_rate': 'mean',
        'max_drawdown': 'mean'
    }).reset_index()
    
    # Sort by ranking metric
    variant_stats = variant_stats.sort_values(rank_by, ascending=False)
    variant_stats['rank'] = range(1, len(variant_stats) + 1)
    
    return variant_stats


def compare_vs_baseline(
    agg_df: pd.DataFrame,
    baseline_id: str = 'V0_baseline'
) -> pd.DataFrame:
    """
    Compare each variant against baseline.
    
    Args:
        agg_df: Aggregated performance DataFrame
        baseline_id: ID of baseline variant
        
    Returns:
        DataFrame with comparison metrics
    """
    # Get baseline performance
    baseline_df = agg_df[agg_df['variant_id'] == baseline_id].copy()
    
    if len(baseline_df) == 0:
        logger.warning(f"Baseline {baseline_id} not found!")
        return pd.DataFrame()
    
    # Merge with other variants
    comparisons = []
    
    for variant_id in agg_df['variant_id'].unique():
        if variant_id == baseline_id:
            continue
        
        variant_df = agg_df[agg_df['variant_id'] == variant_id].copy()
        
        # Merge on symbol × timeframe
        merged = pd.merge(
            variant_df,
            baseline_df,
            on=['symbol', 'timeframe'],
            suffixes=('_variant', '_baseline')
        )
        
        # Compute improvements
        merged['sharpe_improvement'] = merged['sharpe_like_variant'] - merged['sharpe_like_baseline']
        merged['mean_R_improvement'] = merged['net_mean_R_variant'] - merged['net_mean_R_baseline']
        merged['tail_p5_improvement'] = merged['tail_R_p5_variant'] - merged['tail_R_p5_baseline']
        
        comparisons.append(merged)
    
    if not comparisons:
        return pd.DataFrame()
    
    comparison_df = pd.concat(comparisons, ignore_index=True)
    
    return comparison_df


def analyze_regime_distribution(phase3_root: Path, variants: List[str]) -> pd.DataFrame:
    """
    Analyze how trades are distributed across regimes for each variant.
    
    Args:
        phase3_root: Root directory for Phase 3 results
        variants: List of variant IDs
        
    Returns:
        DataFrame with regime distribution statistics
    """
    regime_stats = []
    
    for variant_id in variants:
        variant_dir = phase3_root / variant_id
        
        # Load all trades for this variant
        all_trades = []
        for trades_file in variant_dir.glob("trades_*.csv"):
            df = pd.read_csv(trades_file)
            if len(df) > 0:
                all_trades.append(df)
        
        if not all_trades:
            continue
        
        trades_df = pd.concat(all_trades, ignore_index=True)
        
        # Analyze regime distribution
        if 'risk_regime_entry' in trades_df.columns:
            regime_counts = trades_df['risk_regime_entry'].value_counts()
            regime_mean_R = trades_df.groupby('risk_regime_entry')['net_R'].mean()
            
            for regime in ['low', 'medium', 'high']:
                regime_stats.append({
                    'variant_id': variant_id,
                    'regime': regime,
                    'trade_count': regime_counts.get(regime, 0),
                    'trade_pct': regime_counts.get(regime, 0) / len(trades_df) * 100,
                    'mean_net_R': regime_mean_R.get(regime, 0.0)
                })
    
    return pd.DataFrame(regime_stats)


def run_performance_comparison(config_path: Path = None):
    """
    Main entrypoint for performance comparison.
    """
    if config_path is None:
        config_path = Path("research/strategy/phase3/config_phase3.yaml")
    
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    exp_config = config['experiments']
    phase3_root = Path(exp_config['output_dir'])
    
    # Get variant IDs
    variants = [v['id'] for v in config['variants'] if v.get('enabled', True)]
    symbols = exp_config['symbols']
    timeframes = exp_config['timeframes']
    
    logger.info("Aggregating variant performance...")
    agg_df = aggregate_variant_performance(phase3_root, variants, symbols, timeframes)
    
    if len(agg_df) == 0:
        logger.error("No data to compare!")
        return
    
    # Save aggregated summary
    agg_path = phase3_root / "aggregate_summary_by_variant.csv"
    agg_df.to_csv(agg_path, index=False)
    logger.info(f"Saved aggregated summary to {agg_path}")
    
    # Compute rankings
    rank_by = config.get('reporting', {}).get('rank_by', 'sharpe_like')
    rankings = compute_variant_rankings(agg_df, rank_by=rank_by)
    rankings_path = phase3_root / "variant_rankings.csv"
    rankings.to_csv(rankings_path, index=False)
    logger.info(f"Saved variant rankings to {rankings_path}")
    
    # Compare vs baseline
    baseline_id = config.get('reporting', {}).get('comparison_baseline', 'V0_baseline')
    comparison = compare_vs_baseline(agg_df, baseline_id=baseline_id)
    if len(comparison) > 0:
        comparison_path = phase3_root / "comparison_vs_baseline.csv"
        comparison.to_csv(comparison_path, index=False)
        logger.info(f"Saved baseline comparison to {comparison_path}")
    
    # Analyze regime distribution
    regime_dist = analyze_regime_distribution(phase3_root, variants)
    if len(regime_dist) > 0:
        regime_path = phase3_root / "regime_distribution_by_variant.csv"
        regime_dist.to_csv(regime_path, index=False)
        logger.info(f"Saved regime distribution to {regime_path}")
    
    logger.info("\nPerformance comparison complete!")
    return agg_df, rankings, comparison, regime_dist


if __name__ == "__main__":
    run_performance_comparison()

