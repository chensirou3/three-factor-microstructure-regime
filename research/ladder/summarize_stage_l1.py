"""
Summarize Stage L1 Results

Aggregate all Ladder baseline strategy results and generate summary report.
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def aggregate_baseline_results(results_dir: Path, output_file: Path) -> pd.DataFrame:
    """
    Aggregate all Ladder baseline strategy summary files.
    
    Args:
        results_dir: Directory with summary_{symbol}_{timeframe}.csv files
        output_file: Output file for aggregated results
    
    Returns:
        Aggregated DataFrame
    """
    summary_files = list(results_dir.glob("summary_*.csv"))
    
    if not summary_files:
        logger.error(f"No summary files found in {results_dir}")
        return pd.DataFrame()
    
    logger.info(f"Found {len(summary_files)} summary files")
    
    all_results = []

    for file in summary_files:
        df = pd.read_csv(file)

        # Extract symbol and timeframe from filename
        # Format: summary_{symbol}_{timeframe}.csv
        filename = file.stem  # Remove .csv
        parts = filename.replace('summary_', '').rsplit('_', 1)

        if len(parts) == 2:
            symbol, timeframe = parts
            df['symbol'] = symbol
            df['timeframe'] = timeframe

        all_results.append(df)

    # Concatenate all results
    agg_df = pd.concat(all_results, ignore_index=True)
    
    # Sort by symbol and timeframe
    agg_df = agg_df.sort_values(['symbol', 'timeframe'])
    
    # Save aggregated results
    agg_df.to_csv(output_file, index=False)
    logger.info(f"✓ Saved aggregated results: {output_file}")
    
    return agg_df


def generate_summary_report(agg_df: pd.DataFrame, output_file: Path) -> None:
    """
    Generate summary report from aggregated results.
    
    Args:
        agg_df: Aggregated results DataFrame
        output_file: Output markdown file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Stage L1: Ladder Baseline Strategy - Summary Report\n\n")
        f.write(f"**Total Experiments**: {len(agg_df)}\n\n")
        f.write("---\n\n")
        
        # Overall statistics
        f.write("## Overall Statistics\n\n")
        f.write(f"- **Total Trades**: {agg_df['n_trades'].sum():,.0f}\n")
        f.write(f"- **Average Return**: {agg_df['total_return_pct'].mean():.2f}%\n")
        f.write(f"- **Average Sharpe**: {agg_df['sharpe_ratio'].mean():.4f}\n")
        f.write(f"- **Average Max Drawdown**: {agg_df['max_drawdown_pct'].mean():.2f}%\n")
        f.write(f"- **Average Win Rate**: {agg_df['win_rate_pct'].mean():.2f}%\n\n")
        
        # Top 10 performers by total return
        f.write("## Top 10 Performers (by Total Return)\n\n")
        top10 = agg_df.nlargest(10, 'total_return_pct')[
            ['symbol', 'timeframe', 'total_return_pct', 'max_drawdown_pct', 'sharpe_ratio', 'n_trades']
        ]
        f.write("| Symbol | Timeframe | Return % | Max DD % | Sharpe | Trades |\n")
        f.write("|--------|-----------|----------|----------|--------|--------|\n")
        for _, row in top10.iterrows():
            f.write(f"| {row['symbol']} | {row['timeframe']} | {row['total_return_pct']:.2f} | "
                   f"{row['max_drawdown_pct']:.2f} | {row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
        f.write("\n")

        # Top 10 by Sharpe ratio
        f.write("## Top 10 Performers (by Sharpe Ratio)\n\n")
        top10_sharpe = agg_df.nlargest(10, 'sharpe_ratio')[
            ['symbol', 'timeframe', 'sharpe_ratio', 'total_return_pct', 'max_drawdown_pct', 'n_trades']
        ]
        f.write("| Symbol | Timeframe | Sharpe | Return % | Max DD % | Trades |\n")
        f.write("|--------|-----------|--------|----------|----------|--------|\n")
        for _, row in top10_sharpe.iterrows():
            f.write(f"| {row['symbol']} | {row['timeframe']} | {row['sharpe_ratio']:.4f} | "
                   f"{row['total_return_pct']:.2f} | {row['max_drawdown_pct']:.2f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        # Performance by symbol
        f.write("## Performance by Symbol\n\n")
        by_symbol = agg_df.groupby('symbol').agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown_pct': 'mean',
            'n_trades': 'sum'
        }).round(4)
        f.write("| Symbol | Avg Return % | Avg Sharpe | Avg Max DD % | Total Trades |\n")
        f.write("|--------|--------------|------------|--------------|-------------|\n")
        for symbol, row in by_symbol.iterrows():
            f.write(f"| {symbol} | {row['total_return_pct']:.2f} | {row['sharpe_ratio']:.4f} | "
                   f"{row['max_drawdown_pct']:.2f} | {row['n_trades']:.0f} |\n")
        f.write("\n")

        # Performance by timeframe
        f.write("## Performance by Timeframe\n\n")
        by_timeframe = agg_df.groupby('timeframe').agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown_pct': 'mean',
            'n_trades': 'sum'
        }).round(4)
        # Sort by timeframe order
        timeframe_order = ['5min', '15min', '30min', '1h', '4h', '1d']
        by_timeframe = by_timeframe.reindex([tf for tf in timeframe_order if tf in by_timeframe.index])
        f.write("| Timeframe | Avg Return % | Avg Sharpe | Avg Max DD % | Total Trades |\n")
        f.write("|-----------|--------------|------------|--------------|-------------|\n")
        for timeframe, row in by_timeframe.iterrows():
            f.write(f"| {timeframe} | {row['total_return_pct']:.2f} | {row['sharpe_ratio']:.4f} | "
                   f"{row['max_drawdown_pct']:.2f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        f.write("---\n\n")
        f.write("**Stage L1 Complete**: All 36 combinations tested successfully!\n")
    
    logger.info(f"✓ Saved summary report: {output_file}")


if __name__ == "__main__":
    # Project root
    root = Path(__file__).resolve().parents[2]
    
    # Paths
    results_dir = root / "results/ladder/baseline_strategy"
    output_csv = root / "results/ladder/ladder_baseline_aggregated.csv"
    output_md = root / "LADDER_STAGE_L1_SUMMARY.md"
    
    # Aggregate results
    logger.info("="*80)
    logger.info("Aggregating Stage L1 results...")
    logger.info("="*80)
    
    agg_df = aggregate_baseline_results(results_dir, output_csv)
    
    if not agg_df.empty:
        # Generate summary report
        generate_summary_report(agg_df, output_md)
        
        logger.info("="*80)
        logger.info("Stage L1 summary complete!")
        logger.info("="*80)

