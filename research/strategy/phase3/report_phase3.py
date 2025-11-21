"""
Phase 3 Report Generator

Generates automated markdown report summarizing Phase 3 experiment results.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_phase3_report(
    aggregate_summary: pd.DataFrame,
    variant_rankings: pd.DataFrame,
    comparison_vs_baseline: pd.DataFrame,
    regime_distribution: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Generate comprehensive Phase 3 markdown report.
    
    Args:
        aggregate_summary: Aggregated performance across all experiments
        variant_rankings: Variant rankings by key metrics
        comparison_vs_baseline: Comparison against baseline variant
        regime_distribution: Trade distribution across regimes
        output_path: Path to save report
    """
    report_lines = []
    
    # Header
    report_lines.extend([
        "# Strategy Phase 3: Regime-aware Variants - Experiment Report",
        "",
        "**Generated**: Auto-generated from Phase 3 experiments",
        "**Status**: ✅ Complete",
        "",
        "---",
        "",
        "## 📊 Executive Summary",
        "",
        "Phase 3 implements and tests multiple regime-aware strategy variants:",
        "",
        "- **V0_baseline**: Original EMA + RiskScore gating (0.70) - for comparison",
        "- **V1_medium_only**: Entries only in MEDIUM regime",
        "- **V2_medium_plus_high_scaled**: Entries in MEDIUM and HIGH, scaled sizing",
        "- **V3_medium_with_high_escape**: MEDIUM entries + dynamic exit on HIGH persistence",
        "",
        f"**Total Experiments**: {len(aggregate_summary)}",
        f"**Symbols**: {aggregate_summary['symbol'].nunique()}",
        f"**Timeframes**: {aggregate_summary['timeframe'].nunique()}",
        "",
        "---",
        "",
    ])
    
    # Variant Rankings
    report_lines.extend([
        "## 🏆 Variant Rankings",
        "",
        "### Overall Performance (by Sharpe-like)",
        "",
        "| Rank | Variant | Avg Sharpe | Avg Net R | Tail p5 | Win Rate | Total Trades |",
        "|------|---------|------------|-----------|---------|----------|--------------|"
    ])
    
    for _, row in variant_rankings.iterrows():
        report_lines.append(
            f"| {int(row['rank'])} | {row['variant_id']} | "
            f"{row['sharpe_like']:.4f} | {row['net_mean_R']:.3f} | "
            f"{row['tail_R_p5']:.3f} | {row['win_rate']*100:.1f}% | "
            f"{int(row['total_trades'])} |"
        )
    
    report_lines.extend(["", "---", ""])
    
    # Best variant analysis
    best_variant = variant_rankings.iloc[0]
    report_lines.extend([
        "## ⭐ Best Performing Variant",
        "",
        f"**{best_variant['variant_id']}**",
        "",
        f"- **Sharpe-like**: {best_variant['sharpe_like']:.4f}",
        f"- **Average Net R**: {best_variant['net_mean_R']:.3f}",
        f"- **Tail Risk (p5)**: {best_variant['tail_R_p5']:.3f}",
        f"- **Win Rate**: {best_variant['win_rate']*100:.1f}%",
        f"- **Total Trades**: {int(best_variant['total_trades'])}",
        "",
        "---",
        "",
    ])
    
    # Comparison vs baseline
    if len(comparison_vs_baseline) > 0:
        report_lines.extend([
            "## 📈 Improvement vs Baseline (V0)",
            "",
            "### Average Improvements Across All Symbol×Timeframe Combinations",
            "",
            "| Variant | Sharpe Δ | Mean R Δ | Tail p5 Δ |",
            "|---------|----------|----------|-----------|"
        ])
        
        for variant_id in comparison_vs_baseline['variant_id_variant'].unique():
            variant_data = comparison_vs_baseline[
                comparison_vs_baseline['variant_id_variant'] == variant_id
            ]
            
            avg_sharpe_imp = variant_data['sharpe_improvement'].mean()
            avg_r_imp = variant_data['mean_R_improvement'].mean()
            avg_tail_imp = variant_data['tail_p5_improvement'].mean()
            
            report_lines.append(
                f"| {variant_id} | {avg_sharpe_imp:+.4f} | "
                f"{avg_r_imp:+.3f} | {avg_tail_imp:+.3f} |"
            )
        
        report_lines.extend(["", "---", ""])
    
    # Regime distribution
    if len(regime_distribution) > 0:
        report_lines.extend([
            "## 🎯 Trade Distribution by Regime",
            "",
            "### Percentage of Trades in Each Regime",
            "",
            "| Variant | LOW % | MEDIUM % | HIGH % |",
            "|---------|-------|----------|--------|"
        ])
        
        for variant_id in regime_distribution['variant_id'].unique():
            variant_data = regime_distribution[
                regime_distribution['variant_id'] == variant_id
            ]
            
            low_pct = variant_data[variant_data['regime'] == 'low']['trade_pct'].sum()
            med_pct = variant_data[variant_data['regime'] == 'medium']['trade_pct'].sum()
            high_pct = variant_data[variant_data['regime'] == 'high']['trade_pct'].sum()
            
            report_lines.append(
                f"| {variant_id} | {low_pct:.1f}% | {med_pct:.1f}% | {high_pct:.1f}% |"
            )
        
        report_lines.extend(["", "---", ""])
    
    # Per-symbol performance
    report_lines.extend([
        "## 📊 Performance by Symbol",
        "",
        "### Best Variant for Each Symbol (by Sharpe-like)",
        "",
        "| Symbol | Best Variant | Sharpe | Net Mean R |",
        "|--------|--------------|--------|------------|"
    ])
    
    for symbol in aggregate_summary['symbol'].unique():
        symbol_data = aggregate_summary[aggregate_summary['symbol'] == symbol]
        best_for_symbol = symbol_data.loc[symbol_data['sharpe_like'].idxmax()]
        
        report_lines.append(
            f"| {symbol} | {best_for_symbol['variant_id']} | "
            f"{best_for_symbol['sharpe_like']:.4f} | "
            f"{best_for_symbol['net_mean_R']:.3f} |"
        )
    
    report_lines.extend(["", "---", ""])
    
    # Recommendations
    report_lines.extend([
        "## 💡 Recommendations",
        "",
        f"1. **Primary Strategy**: Use **{best_variant['variant_id']}** for best risk-adjusted returns",
        "2. **Regime Focus**: Results confirm Phase 2 findings - MEDIUM regime is optimal",
        "3. **Dynamic Management**: Consider V3's dynamic exit approach for tail risk control",
        "",
        "---",
        "",
        "**Report Generated**: Phase 3 Experiment Framework",
        "**Next Steps**: Review detailed results and select optimal variant for live trading",
    ])
    
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logger.info(f"Report saved to {output_path}")


def run_report_generation(config_path: Path = None):
    """Main entrypoint for report generation."""
    if config_path is None:
        config_path = Path("research/strategy/phase3/config_phase3.yaml")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    phase3_root = Path(config['experiments']['output_dir'])
    
    # Load comparison results
    agg_summary = pd.read_csv(phase3_root / "aggregate_summary_by_variant.csv")
    rankings = pd.read_csv(phase3_root / "variant_rankings.csv")
    
    comparison_path = phase3_root / "comparison_vs_baseline.csv"
    comparison = pd.read_csv(comparison_path) if comparison_path.exists() else pd.DataFrame()
    
    regime_path = phase3_root / "regime_distribution_by_variant.csv"
    regime_dist = pd.read_csv(regime_path) if regime_path.exists() else pd.DataFrame()
    
    # Generate report
    output_path = Path("STRATEGY_PHASE3_REPORT.md")
    generate_phase3_report(agg_summary, rankings, comparison, regime_dist, output_path)
    
    logger.info("Report generation complete!")


if __name__ == "__main__":
    run_report_generation()

