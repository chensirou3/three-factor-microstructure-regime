"""
Generate comprehensive Ladder×Factor combo report.
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


def generate_report(
    all_agg: pd.DataFrame,
    segments_stats: pd.DataFrame,
    output_file: Path
) -> None:
    """
    Generate comprehensive report.
    
    Args:
        all_agg: Aggregated results from all directions
        segments_stats: Segment factor statistics from Direction 1
        output_file: Output markdown file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🎯 Ladder × Three-Factor Integration: Complete Report\n\n")
        f.write("**Four Directions Explored**: Segment analysis, Entry filtering, MTF timing, Exit rules\n\n")
        f.write("---\n\n")
        
        # Direction 1: Segment Analysis
        f.write("## 📊 Direction 1: Segment-Level Quality Analysis\n\n")
        f.write("**Goal**: Identify 'healthy' vs 'unhealthy' Ladder trends based on factor characteristics.\n\n")
        
        if len(segments_stats) > 0:
            f.write("### Key Findings\n\n")
            
            # Best factor bins by mean return
            top_bins = segments_stats.nlargest(5, 'mean_return')[
                ['factor', 'bin', 'count', 'mean_return', 'mean_length', 'pct_positive']
            ]
            
            f.write("**Top 5 Factor Bins (by mean return)**:\n\n")
            f.write("| Factor | Bin | Count | Mean Return % | Mean Length | % Positive |\n")
            f.write("|--------|-----|-------|---------------|-------------|------------|\n")
            for _, row in top_bins.iterrows():
                f.write(f"| {row['factor']} | {row['bin']} | {row['count']:.0f} | "
                       f"{row['mean_return']:.2f} | {row['mean_length']:.1f} | {row['pct_positive']:.1f} |\n")
            f.write("\n")
            
            # Worst factor bins
            bottom_bins = segments_stats.nsmallest(5, 'mean_return')[
                ['factor', 'bin', 'count', 'mean_return', 'mean_length', 'pct_positive']
            ]
            
            f.write("**Bottom 5 Factor Bins (by mean return)**:\n\n")
            f.write("| Factor | Bin | Count | Mean Return % | Mean Length | % Positive |\n")
            f.write("|--------|-----|-------|---------------|-------------|------------|\n")
            for _, row in bottom_bins.iterrows():
                f.write(f"| {row['factor']} | {row['bin']} | {row['count']:.0f} | "
                       f"{row['mean_return']:.2f} | {row['mean_length']:.1f} | {row['pct_positive']:.1f} |\n")
            f.write("\n")
        else:
            f.write("*No segment statistics available*\n\n")
        
        f.write("---\n\n")
        
        # Direction 2: Entry Filtering
        f.write("## 🔬 Direction 2: Factor-Based Entry Filtering & Sizing\n\n")
        f.write("**Goal**: Use factors to filter Ladder entries and adjust position size.\n\n")
        
        d2_results = all_agg[all_agg['direction'] == 'D2']
        if len(d2_results) > 0:
            d2_summary = d2_results.groupby('variant_id').agg({
                'n_trades': 'sum',
                'total_return_pct': 'mean',
                'sharpe_ratio': 'mean',
                'max_drawdown_pct': 'mean',
                'win_rate_pct': 'mean',
            }).round(4)
            
            f.write("### Performance by Variant\n\n")
            f.write("| Variant | Total Trades | Avg Return % | Avg Sharpe | Avg Max DD % | Avg Win Rate % |\n")
            f.write("|---------|--------------|--------------|------------|--------------|----------------|\n")
            for variant, row in d2_summary.iterrows():
                f.write(f"| **{variant}** | {row['n_trades']:.0f} | {row['total_return_pct']:.2f} | "
                       f"{row['sharpe_ratio']:.4f} | {row['max_drawdown_pct']:.2f} | {row['win_rate_pct']:.2f} |\n")
            f.write("\n")
            
            # Top performers
            top_d2 = d2_results.nlargest(10, 'total_return_pct')[
                ['symbol', 'timeframe', 'variant_id', 'total_return_pct', 'sharpe_ratio', 'n_trades']
            ]
            
            f.write("### Top 10 Performers\n\n")
            f.write("| Symbol | Timeframe | Variant | Return % | Sharpe | Trades |\n")
            f.write("|--------|-----------|---------|----------|--------|--------|\n")
            for _, row in top_d2.iterrows():
                f.write(f"| {row['symbol']} | {row['timeframe']} | {row['variant_id']} | "
                       f"{row['total_return_pct']:.2f} | {row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
            f.write("\n")
        else:
            f.write("*No Direction 2 results available*\n\n")
        
        f.write("---\n\n")
        
        # Direction 3: MTF Timing
        f.write("## ⏰ Direction 3: Multi-Timeframe Timing\n\n")
        f.write("**Goal**: High-TF Ladder for direction, low-TF + factors for precise timing.\n\n")
        
        d3_results = all_agg[all_agg['direction'] == 'D3']
        if len(d3_results) > 0:
            d3_summary = d3_results.groupby('variant_id').agg({
                'n_trades': 'sum',
                'total_return_pct': 'mean',
                'sharpe_ratio': 'mean',
                'max_drawdown_pct': 'mean',
            }).round(4)
            
            f.write("### Performance by Variant\n\n")
            f.write("| Variant | Total Trades | Avg Return % | Avg Sharpe | Avg Max DD % |\n")
            f.write("|---------|--------------|--------------|------------|-------------|\n")
            for variant, row in d3_summary.iterrows():
                f.write(f"| **{variant}** | {row['n_trades']:.0f} | {row['total_return_pct']:.2f} | "
                       f"{row['sharpe_ratio']:.4f} | {row['max_drawdown_pct']:.2f} |\n")
            f.write("\n")
        else:
            f.write("*No Direction 3 results available*\n\n")
        
        f.write("---\n\n")
        
        # Direction 4: Exit Rules
        f.write("## 🚪 Direction 4: Factor-Based Exit Rules\n\n")
        f.write("**Goal**: Ladder controls entry, factors trigger exits or partial profit-taking.\n\n")
        
        d4_results = all_agg[all_agg['direction'] == 'D4']
        if len(d4_results) > 0:
            d4_summary = d4_results.groupby('variant_id').agg({
                'n_trades': 'sum',
                'total_return_pct': 'mean',
                'sharpe_ratio': 'mean',
                'max_drawdown_pct': 'mean',
            }).round(4)
            
            f.write("### Performance by Variant\n\n")
            f.write("| Variant | Total Trades | Avg Return % | Avg Sharpe | Avg Max DD % |\n")
            f.write("|---------|--------------|--------------|------------|-------------|\n")
            for variant, row in d4_summary.iterrows():
                f.write(f"| **{variant}** | {row['n_trades']:.0f} | {row['total_return_pct']:.2f} | "
                       f"{row['sharpe_ratio']:.4f} | {row['max_drawdown_pct']:.2f} |\n")
            f.write("\n")
        else:
            f.write("*No Direction 4 results available*\n\n")
        
        f.write("---\n\n")
        
        # Overall Conclusions
        f.write("## 🎯 Overall Conclusions\n\n")
        f.write("### Which Direction Works Best?\n\n")
        
        # Compare average Sharpe by direction
        dir_comparison = all_agg.groupby('direction').agg({
            'sharpe_ratio': 'mean',
            'total_return_pct': 'mean',
            'max_drawdown_pct': 'mean',
        }).round(4).sort_values('sharpe_ratio', ascending=False)
        
        f.write("| Direction | Avg Sharpe | Avg Return % | Avg Max DD % |\n")
        f.write("|-----------|------------|--------------|-------------|\n")
        for direction, row in dir_comparison.iterrows():
            f.write(f"| **{direction}** | {row['sharpe_ratio']:.4f} | "
                   f"{row['total_return_pct']:.2f} | {row['max_drawdown_pct']:.2f} |\n")
        f.write("\n")
        
        f.write("---\n\n")
        f.write("**Data**: See `aggregate_all_directions.csv` for complete results\n")
    
    logger.info(f"✓ Saved report: {output_file}")


def main():
    """Main entry point."""
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    root = Path(__file__).resolve().parents[2]
    output_dir = root / config['outputs']['root']
    
    logger.info("="*80)
    logger.info("Generating Ladder×Factor combo report")
    logger.info("="*80)
    
    # Load aggregated results
    all_agg_file = output_dir / "aggregate_all_directions.csv"
    if not all_agg_file.exists():
        logger.error(f"Aggregated results not found: {all_agg_file}")
        logger.error("Please run combo_aggregate.py first!")
        return
    
    all_agg = pd.read_csv(all_agg_file)
    logger.info(f"Loaded {len(all_agg)} aggregated results")
    
    # Load segment stats
    segments_stats_file = output_dir / "segments_factor_stats.csv"
    if segments_stats_file.exists():
        segments_stats = pd.read_csv(segments_stats_file)
        logger.info(f"Loaded {len(segments_stats)} segment statistics")
    else:
        logger.warning("Segment statistics not found, skipping Direction 1 analysis")
        segments_stats = pd.DataFrame()
    
    # Generate report
    report_file = root / "LADDER_FACTOR_COMBO_COMPLETE_REPORT.md"
    generate_report(all_agg, segments_stats, report_file)
    
    logger.info("="*80)
    logger.info("✓ Report generation complete!")
    logger.info("="*80)


if __name__ == "__main__":
    main()

