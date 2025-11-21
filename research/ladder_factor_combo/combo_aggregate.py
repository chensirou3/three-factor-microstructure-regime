"""
Aggregate and compare Ladder×Factor combo results.
"""

import sys
from pathlib import Path
import pandas as pd
import yaml
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def aggregate_direction_results(
    direction_dir: Path,
    direction_name: str
) -> pd.DataFrame:
    """
    Aggregate results for one direction.
    
    Args:
        direction_dir: Directory with variant subdirectories
        direction_name: Direction name (D2, D3, D4)
    
    Returns:
        Aggregated DataFrame
    """
    all_results = []
    
    for variant_dir in direction_dir.iterdir():
        if not variant_dir.is_dir():
            continue
        
        variant_id = variant_dir.name
        
        for summary_file in variant_dir.glob("summary_*.csv"):
            df = pd.read_csv(summary_file)
            
            # Extract symbol and timeframe from filename
            filename = summary_file.stem
            parts = filename.replace('summary_', '').split('_')
            
            if len(parts) >= 2:
                df['symbol'] = parts[0]
                df['timeframe'] = '_'.join(parts[1:])  # Handle multi-part timeframes
                df['variant_id'] = variant_id
                df['direction'] = direction_name
            
            all_results.append(df)
    
    if all_results:
        return pd.concat(all_results, ignore_index=True)
    else:
        return pd.DataFrame()


def compare_variants(
    agg_df: pd.DataFrame,
    output_file: Path
) -> None:
    """
    Compare variants and save comparison.
    
    Args:
        agg_df: Aggregated results
        output_file: Output file path
    """
    # Group by direction and variant
    comparison = agg_df.groupby(['direction', 'variant_id']).agg({
        'n_trades': 'sum',
        'total_return_pct': 'mean',
        'sharpe_ratio': 'mean',
        'max_drawdown_pct': 'mean',
        'win_rate_pct': 'mean',
    }).round(4)
    
    comparison.to_csv(output_file)
    logger.info(f"✓ Saved variant comparison: {output_file}")


def compare_by_symbol_timeframe(
    agg_df: pd.DataFrame,
    output_file: Path
) -> None:
    """
    Compare performance by symbol and timeframe.
    
    Args:
        agg_df: Aggregated results
        output_file: Output file path
    """
    # Group by symbol, timeframe, direction, variant
    comparison = agg_df.groupby(['symbol', 'timeframe', 'direction', 'variant_id']).agg({
        'n_trades': 'sum',
        'total_return_pct': 'mean',
        'sharpe_ratio': 'mean',
        'max_drawdown_pct': 'mean',
    }).round(4)
    
    comparison.to_csv(output_file)
    logger.info(f"✓ Saved symbol×timeframe comparison: {output_file}")


def main():
    """Main entry point."""
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    root = Path(__file__).resolve().parents[2]
    output_dir = root / config['outputs']['root']
    
    logger.info("="*80)
    logger.info("Aggregating Ladder×Factor combo results")
    logger.info("="*80)
    
    all_directions = []
    
    # Aggregate Direction 2
    d2_dir = output_dir / "direction2"
    if d2_dir.exists():
        logger.info("Aggregating Direction 2...")
        d2_agg = aggregate_direction_results(d2_dir, "D2")
        if len(d2_agg) > 0:
            d2_file = output_dir / "aggregate_D2_entry_sizing.csv"
            d2_agg.to_csv(d2_file, index=False)
            logger.info(f"  ✓ {len(d2_agg)} results → {d2_file.name}")
            all_directions.append(d2_agg)
    
    # Aggregate Direction 3
    d3_dir = output_dir / "direction3"
    if d3_dir.exists():
        logger.info("Aggregating Direction 3...")
        d3_agg = aggregate_direction_results(d3_dir, "D3")
        if len(d3_agg) > 0:
            d3_file = output_dir / "aggregate_D3_mtf_timing.csv"
            d3_agg.to_csv(d3_file, index=False)
            logger.info(f"  ✓ {len(d3_agg)} results → {d3_file.name}")
            all_directions.append(d3_agg)
    
    # Aggregate Direction 4
    d4_dir = output_dir / "direction4"
    if d4_dir.exists():
        logger.info("Aggregating Direction 4...")
        d4_agg = aggregate_direction_results(d4_dir, "D4")
        if len(d4_agg) > 0:
            d4_file = output_dir / "aggregate_D4_exit_rules.csv"
            d4_agg.to_csv(d4_file, index=False)
            logger.info(f"  ✓ {len(d4_agg)} results → {d4_file.name}")
            all_directions.append(d4_agg)
    
    # Combine all directions
    if all_directions:
        all_agg = pd.concat(all_directions, ignore_index=True)
        all_file = output_dir / "aggregate_all_directions.csv"
        all_agg.to_csv(all_file, index=False)
        logger.info(f"\n✓ Combined: {len(all_agg)} total results → {all_file.name}")
        
        # Generate comparisons
        compare_variants(all_agg, output_dir / "comparison_by_variant.csv")
        compare_by_symbol_timeframe(all_agg, output_dir / "comparison_by_symbol_timeframe.csv")
    
    logger.info("="*80)
    logger.info("✓ Aggregation complete!")
    logger.info("="*80)


if __name__ == "__main__":
    main()

