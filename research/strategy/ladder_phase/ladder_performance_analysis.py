"""
Ladder + Regime Performance Analysis

Aggregates Ladder + Regime results and compares with EMA-based Phase 3 results.
"""

import sys
from pathlib import Path
import pandas as pd
import yaml
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def aggregate_ladder_results(results_dir: Path) -> pd.DataFrame:
    """
    Aggregate all Ladder + Regime experiment results.
    
    Args:
        results_dir: Directory with variant subdirectories
    
    Returns:
        Aggregated DataFrame
    """
    all_results = []
    
    for variant_dir in results_dir.iterdir():
        if not variant_dir.is_dir():
            continue
        
        variant_id = variant_dir.name
        
        for summary_file in variant_dir.glob("summary_*.csv"):
            df = pd.read_csv(summary_file)
            
            # Extract symbol and timeframe from filename
            filename = summary_file.stem
            parts = filename.replace('summary_', '').rsplit('_', 1)
            
            if len(parts) == 2:
                symbol, timeframe = parts
                df['symbol'] = symbol
                df['timeframe'] = timeframe
                df['variant_id'] = variant_id
                df['trend_engine'] = 'Ladder'
            
            all_results.append(df)
    
    if not all_results:
        logger.warning("No Ladder results found")
        return pd.DataFrame()
    
    agg_df = pd.concat(all_results, ignore_index=True)
    return agg_df


def load_ema_results(ema_results_dir: Path) -> pd.DataFrame:
    """
    Load EMA-based Phase 3 results for comparison.
    
    Args:
        ema_results_dir: Directory with Phase 3 results
    
    Returns:
        Aggregated DataFrame with EMA results
    """
    all_results = []
    
    for variant_dir in ema_results_dir.iterdir():
        if not variant_dir.is_dir():
            continue
        
        variant_id = variant_dir.name
        
        for summary_file in variant_dir.glob("summary_*.csv"):
            df = pd.read_csv(summary_file)
            
            # Extract symbol and timeframe from filename
            filename = summary_file.stem
            parts = filename.replace('summary_', '').rsplit('_', 1)
            
            if len(parts) == 2:
                symbol, timeframe = parts
                df['symbol'] = symbol
                df['timeframe'] = timeframe
                df['variant_id'] = variant_id
                df['trend_engine'] = 'EMA'
            
            all_results.append(df)
    
    if not all_results:
        logger.warning("No EMA results found")
        return pd.DataFrame()
    
    agg_df = pd.concat(all_results, ignore_index=True)
    return agg_df


def compare_ladder_vs_ema(ladder_df: pd.DataFrame,
                         ema_df: pd.DataFrame,
                         output_file: Path) -> pd.DataFrame:
    """
    Compare Ladder vs EMA performance.
    
    Args:
        ladder_df: Ladder results
        ema_df: EMA results
        output_file: Output CSV file
    
    Returns:
        Comparison DataFrame
    """
    # Combine both datasets
    combined = pd.concat([ladder_df, ema_df], ignore_index=True)
    
    # Map variant IDs (L_V0 -> V0, etc.)
    combined['base_variant'] = combined['variant_id'].str.replace('L_', '')
    
    # Save combined results
    combined.to_csv(output_file, index=False)
    logger.info(f"✓ Saved combined results: {output_file}")
    
    return combined


def generate_comparison_report(combined_df: pd.DataFrame,
                               output_file: Path) -> None:
    """
    Generate Ladder vs EMA comparison report.
    
    Args:
        combined_df: Combined Ladder + EMA results
        output_file: Output markdown file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Ladder vs EMA: Performance Comparison\n\n")
        f.write("**Stage L2 Complete**: Ladder + Regime vs EMA + Regime\n\n")
        f.write("---\n\n")
        
        # Overall comparison
        f.write("## Overall Performance\n\n")
        by_engine = combined_df.groupby('trend_engine').agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown_pct': 'mean',
            'n_trades': 'sum',
            'win_rate_pct': 'mean'
        }).round(4)
        
        f.write("| Trend Engine | Avg Return % | Avg Sharpe | Avg Max DD % | Total Trades | Avg Win Rate % |\n")
        f.write("|--------------|--------------|------------|--------------|--------------|----------------|\n")
        for engine, row in by_engine.iterrows():
            f.write(f"| {engine} | {row['total_return_pct']:.2f} | {row['sharpe_ratio']:.4f} | "
                   f"{row['max_drawdown_pct']:.2f} | {row['n_trades']:.0f} | {row['win_rate_pct']:.2f} |\n")
        f.write("\n")
        
        # By variant comparison
        f.write("## Performance by Variant\n\n")
        by_variant = combined_df.groupby(['base_variant', 'trend_engine']).agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'n_trades': 'sum'
        }).round(4)
        
        f.write("| Variant | Engine | Avg Return % | Avg Sharpe | Total Trades |\n")
        f.write("|---------|--------|--------------|------------|-------------|\n")
        for (variant, engine), row in by_variant.iterrows():
            f.write(f"| {variant} | {engine} | {row['total_return_pct']:.2f} | "
                   f"{row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        f.write("---\n\n")
        f.write("**Conclusion**: See detailed analysis in ladder_vs_ema_summary.csv\n")
    
    logger.info(f"✓ Saved comparison report: {output_file}")


if __name__ == "__main__":
    # Project root
    root = Path(__file__).resolve().parents[3]

    # Paths
    ladder_results_dir = root / "results/strategy/ladder_phase"
    ema_results_dir = root / "results/strategy/phase3"
    output_csv = root / "results/strategy/ladder_phase/ladder_vs_ema_summary.csv"
    output_md = root / "LADDER_VS_EMA_COMPARISON.md"

    logger.info("="*80)
    logger.info("Analyzing Ladder + Regime performance...")
    logger.info("="*80)

    # Aggregate Ladder results
    ladder_df = aggregate_ladder_results(ladder_results_dir)
    logger.info(f"Loaded {len(ladder_df)} Ladder experiments")

    # Load EMA results
    ema_df = load_ema_results(ema_results_dir)
    logger.info(f"Loaded {len(ema_df)} EMA experiments")

    # Compare
    combined_df = compare_ladder_vs_ema(ladder_df, ema_df, output_csv)

    # Generate report
    generate_comparison_report(combined_df, output_md)

    logger.info("="*80)
    logger.info("Ladder vs EMA analysis complete!")
    logger.info("="*80)

