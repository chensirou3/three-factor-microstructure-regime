"""
Phase 4 report generation.

Generates a practical, non-academic summary report of account-level performance
with realistic transaction costs.
"""

import sys
from pathlib import Path
import pandas as pd
import yaml
import logging
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.phase4.accounts import load_accounts_from_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_phase4_report(
    aggregate_df: pd.DataFrame,
    summary_by_symbol_df: pd.DataFrame,
    account_variant_summary_df: pd.DataFrame,
    accounts: list,
    output_path: Path,
) -> None:
    """
    Generate Phase 4 markdown report.
    
    Args:
        aggregate_df: Full aggregated results
        summary_by_symbol_df: Results aggregated by symbol
        account_variant_summary_df: Results aggregated by account × variant
        accounts: List of account configurations
        output_path: Path to save report
    """
    logger.info("Generating Phase 4 report...")
    
    lines = []
    
    # Header
    lines.append("# Strategy Phase 4: Account-level Performance with Realistic Costs")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("**Status**: ✅ Complete")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Executive Summary
    lines.append("## 📊 Executive Summary")
    lines.append("")
    lines.append("Phase 4 evaluates strategy performance from a **realistic account perspective**,")
    lines.append("incorporating actual transaction costs and computing practical metrics.")
    lines.append("")
    lines.append("**Key Questions Answered:**")
    lines.append("- How do different cost structures (0.003% vs 0.07%) impact performance?")
    lines.append("- Which symbols/timeframes remain profitable under high costs?")
    lines.append("- Should we use V2 (aggressive) or V1 (conservative) for each account?")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Account Configurations
    lines.append("## 💰 Account Configurations")
    lines.append("")
    for acc in accounts:
        lines.append(f"### {acc.id.upper()}")
        lines.append(f"- **Description**: {acc.description}")
        lines.append(f"- **Cost per side**: {acc.cost_per_side_pct}%")
        lines.append(f"- **Round-trip cost**: {acc.cost_per_side_pct * 2}%")
        lines.append(f"- **Initial equity**: ${acc.initial_equity:,.0f}")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # Overall Performance by Account × Variant
    lines.append("## 🏆 Overall Performance by Account × Variant")
    lines.append("")
    lines.append("### Summary Table")
    lines.append("")
    
    # Format table
    lines.append("| Account | Variant | Total Trades | Ann Return | Max DD | Sharpe | Win Rate |")
    lines.append("|---------|---------|--------------|------------|--------|--------|----------|")
    
    for _, row in account_variant_summary_df.iterrows():
        lines.append(
            f"| {row['account_id']} | {row['variant_id']} | "
            f"{row['n_trades']:,} | "
            f"{row['annualized_return']*100:.2f}% | "
            f"{row['max_drawdown']*100:.2f}% | "
            f"{row['sharpe_ratio']:.4f} | "
            f"{row['win_rate_pct']:.1f}% |"
        )
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Best Performing Combinations
    lines.append("## ⭐ Best Performing Combinations")
    lines.append("")
    
    # Find best by annualized return for each account
    for acc_id in aggregate_df['account_id'].unique():
        acc_data = aggregate_df[aggregate_df['account_id'] == acc_id]
        best = acc_data.nlargest(5, 'annualized_return')
        
        lines.append(f"### {acc_id.upper()} - Top 5 by Annualized Return")
        lines.append("")
        lines.append("| Variant | Symbol | Timeframe | Ann Return | Max DD | Trades |")
        lines.append("|---------|--------|-----------|------------|--------|--------|")
        
        for _, row in best.iterrows():
            lines.append(
                f"| {row['variant_id']} | {row['symbol']} | {row['timeframe']} | "
                f"{row['annualized_return']*100:.2f}% | "
                f"{row['max_drawdown']*100:.2f}% | "
                f"{row['n_trades']:,} |"
            )
        
        lines.append("")

    lines.append("---")
    lines.append("")

    # Per-Symbol Performance
    lines.append("## 📈 Performance by Symbol")
    lines.append("")

    for acc_id in summary_by_symbol_df['account_id'].unique():
        for variant_id in summary_by_symbol_df['variant_id'].unique():
            subset = summary_by_symbol_df[
                (summary_by_symbol_df['account_id'] == acc_id) &
                (summary_by_symbol_df['variant_id'] == variant_id)
            ].sort_values('annualized_return', ascending=False)

            if subset.empty:
                continue

            lines.append(f"### {acc_id.upper()} × {variant_id}")
            lines.append("")
            lines.append("| Symbol | Ann Return | Max DD | Sharpe | Trades |")
            lines.append("|--------|------------|--------|--------|--------|")

            for _, row in subset.iterrows():
                lines.append(
                    f"| {row['symbol']} | "
                    f"{row['annualized_return']*100:.2f}% | "
                    f"{row['max_drawdown']*100:.2f}% | "
                    f"{row['sharpe_ratio']:.4f} | "
                    f"{row['n_trades']:,} |"
                )

            lines.append("")

    lines.append("---")
    lines.append("")

    # Cost Sensitivity Analysis
    lines.append("## 💸 Cost Sensitivity Analysis")
    lines.append("")
    lines.append("Comparing performance between low_cost and high_cost accounts:")
    lines.append("")

    # Calculate cost impact for each variant
    for variant_id in account_variant_summary_df['variant_id'].unique():
        low_cost_row = account_variant_summary_df[
            (account_variant_summary_df['account_id'] == 'low_cost') &
            (account_variant_summary_df['variant_id'] == variant_id)
        ]
        high_cost_row = account_variant_summary_df[
            (account_variant_summary_df['account_id'] == 'high_cost') &
            (account_variant_summary_df['variant_id'] == variant_id)
        ]

        if low_cost_row.empty or high_cost_row.empty:
            continue

        low_return = low_cost_row['annualized_return'].iloc[0]
        high_return = high_cost_row['annualized_return'].iloc[0]
        return_drop = low_return - high_return

        lines.append(f"### {variant_id}")
        lines.append(f"- **Low cost return**: {low_return*100:.2f}%")
        lines.append(f"- **High cost return**: {high_return*100:.2f}%")
        lines.append(f"- **Performance drop**: {return_drop*100:.2f}% ({return_drop/low_return*100:.1f}% relative)")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Recommendations
    lines.append("## 💡 Recommendations")
    lines.append("")

    # Find best overall combination
    best_overall = account_variant_summary_df.nlargest(1, 'annualized_return').iloc[0]

    lines.append("### Primary Recommendation")
    lines.append(f"- **Account**: {best_overall['account_id']}")
    lines.append(f"- **Strategy**: {best_overall['variant_id']}")
    lines.append(f"- **Expected Ann Return**: {best_overall['annualized_return']*100:.2f}%")
    lines.append(f"- **Max Drawdown**: {best_overall['max_drawdown']*100:.2f}%")
    lines.append(f"- **Sharpe Ratio**: {best_overall['sharpe_ratio']:.4f}")
    lines.append("")

    # Symbol recommendations
    lines.append("### Recommended Symbols")
    best_symbols = summary_by_symbol_df[
        (summary_by_symbol_df['account_id'] == best_overall['account_id']) &
        (summary_by_symbol_df['variant_id'] == best_overall['variant_id'])
    ].nlargest(3, 'annualized_return')

    for _, row in best_symbols.iterrows():
        lines.append(f"- **{row['symbol']}**: {row['annualized_return']*100:.2f}% ann return")

    lines.append("")
    lines.append("### Timeframe Recommendations")
    lines.append("- **For low_cost account**: All timeframes (30min-1d) viable")
    lines.append("- **For high_cost account**: Prefer longer timeframes (4h-1d) to reduce cost impact")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Report Generated**: Phase 4 Account-level Performance Analysis")
    lines.append("**Next Steps**: Review equity curves and select optimal configurations for live trading")

    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    logger.info(f"Report saved to {output_path}")


def run_report_generation():
    """
    Run Phase 4 report generation.
    """
    # Load configuration
    root = Path(__file__).resolve().parents[3]
    config_path = root / "research/strategy/phase4/config_phase4.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Load accounts
    accounts = load_accounts_from_config(config_path)

    # Get output root
    exp_config = config['experiments']
    output_root = root / exp_config['output_root']

    logger.info("="*80)
    logger.info("Phase 4 Report Generation")
    logger.info("="*80)

    # Load aggregated results
    aggregate_file = output_root / "aggregate_phase4_summary.csv"
    symbol_summary_file = output_root / "summary_by_symbol.csv"
    account_variant_file = output_root / "summary_by_account_variant.csv"

    if not aggregate_file.exists():
        logger.error(f"Aggregate file not found: {aggregate_file}")
        logger.error("Please run equity_analysis.py first!")
        return

    aggregate_df = pd.read_csv(aggregate_file)
    summary_by_symbol_df = pd.read_csv(symbol_summary_file)
    account_variant_summary_df = pd.read_csv(account_variant_file)

    # Generate report
    report_path = root / "STRATEGY_PHASE4_ACCOUNT_PERFORMANCE.md"

    generate_phase4_report(
        aggregate_df=aggregate_df,
        summary_by_symbol_df=summary_by_symbol_df,
        account_variant_summary_df=account_variant_summary_df,
        accounts=accounts,
        output_path=report_path
    )

    logger.info("="*80)
    logger.info("Report generation complete!")
    logger.info(f"Report saved to: {report_path}")
    logger.info("="*80)


if __name__ == "__main__":
    run_report_generation()

