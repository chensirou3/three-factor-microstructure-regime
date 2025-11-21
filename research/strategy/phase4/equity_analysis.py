"""
Equity and performance analysis for Phase 4.

Aggregates backtest results across accounts, variants, symbols, and timeframes
to provide comprehensive performance summaries.
"""

import sys
from pathlib import Path
from typing import List
import pandas as pd
import yaml
import logging

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.phase4.accounts import AccountConfig, load_accounts_from_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def aggregate_phase4_results(
    phase4_root: Path,
    accounts: List[AccountConfig],
    variants: List[str],
    symbols: List[str],
    timeframes: List[str],
) -> pd.DataFrame:
    """
    Load all summary files and aggregate into a single DataFrame.
    
    Args:
        phase4_root: Root directory for Phase 4 results
        accounts: List of account configurations
        variants: List of variant IDs
        symbols: List of symbols
        timeframes: List of timeframes
        
    Returns:
        Aggregated DataFrame with all results
    """
    logger.info("Aggregating Phase 4 results...")
    
    all_results = []
    
    for account in accounts:
        for variant_id in variants:
            for symbol in symbols:
                for timeframe in timeframes:
                    # Construct path to summary file
                    summary_file = (phase4_root / account.id / variant_id / 
                                   f"summary_{symbol}_{timeframe}.csv")
                    
                    if not summary_file.exists():
                        logger.warning(f"Missing: {summary_file}")
                        continue
                    
                    # Load summary
                    summary_df = pd.read_csv(summary_file)
                    
                    # Add identifiers
                    summary_df['account_id'] = account.id
                    summary_df['variant_id'] = variant_id
                    summary_df['symbol'] = symbol
                    summary_df['timeframe'] = timeframe
                    
                    all_results.append(summary_df)
    
    if not all_results:
        logger.error("No results found!")
        return pd.DataFrame()
    
    # Combine all results
    aggregate_df = pd.concat(all_results, ignore_index=True)
    
    logger.info(f"Aggregated {len(aggregate_df)} results")
    
    # Save aggregated results
    output_file = phase4_root / "aggregate_phase4_summary.csv"
    aggregate_df.to_csv(output_file, index=False)
    logger.info(f"Saved aggregated summary to {output_file}")
    
    return aggregate_df


def aggregate_by_symbol(aggregate_df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Aggregate results by symbol (across timeframes).
    
    Args:
        aggregate_df: Full aggregated DataFrame
        output_path: Path to save output
        
    Returns:
        DataFrame aggregated by account × variant × symbol
    """
    logger.info("Aggregating by symbol...")
    
    # Group by account, variant, symbol
    grouped = aggregate_df.groupby(['account_id', 'variant_id', 'symbol']).agg({
        'n_trades': 'sum',
        'mean_R': 'mean',
        'sharpe_ratio': 'mean',
        'total_return': 'mean',
        'annualized_return': 'mean',
        'max_drawdown': 'min',  # Most negative drawdown
    }).reset_index()
    
    # Sort by annualized return
    grouped = grouped.sort_values(['account_id', 'variant_id', 'annualized_return'], 
                                   ascending=[True, True, False])
    
    grouped.to_csv(output_path, index=False)
    logger.info(f"Saved symbol summary to {output_path}")
    
    return grouped


def aggregate_by_account_variant(aggregate_df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Aggregate results by account × variant (across all symbols and timeframes).
    
    Args:
        aggregate_df: Full aggregated DataFrame
        output_path: Path to save output
        
    Returns:
        DataFrame aggregated by account × variant
    """
    logger.info("Aggregating by account × variant...")
    
    # Group by account, variant
    grouped = aggregate_df.groupby(['account_id', 'variant_id']).agg({
        'n_trades': 'sum',
        'mean_R': 'mean',
        'sharpe_ratio': 'mean',
        'total_return': 'mean',
        'annualized_return': 'mean',
        'max_drawdown': 'min',
        'win_rate_pct': 'mean',
    }).reset_index()
    
    # Sort by annualized return
    grouped = grouped.sort_values('annualized_return', ascending=False)
    
    grouped.to_csv(output_path, index=False)
    logger.info(f"Saved account×variant summary to {output_path}")

    return grouped


def run_equity_analysis():
    """
    Run complete equity analysis for Phase 4 results.
    """
    # Load configuration
    root = Path(__file__).resolve().parents[3]
    config_path = root / "research/strategy/phase4/config_phase4.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Load accounts
    accounts = load_accounts_from_config(config_path)

    # Get experiment settings
    exp_config = config['experiments']
    symbols = exp_config['symbols']
    timeframes = exp_config['timeframes']
    output_root = root / exp_config['output_root']

    # Get strategy variants
    variants = [v['id'] for v in config['strategies']]

    logger.info("="*80)
    logger.info("Phase 4 Equity Analysis")
    logger.info("="*80)

    # 1. Aggregate all results
    aggregate_df = aggregate_phase4_results(
        phase4_root=output_root,
        accounts=accounts,
        variants=variants,
        symbols=symbols,
        timeframes=timeframes
    )

    if aggregate_df.empty:
        logger.error("No results to analyze!")
        return

    # 2. Aggregate by symbol
    symbol_summary = aggregate_by_symbol(
        aggregate_df,
        output_path=output_root / "summary_by_symbol.csv"
    )

    # 3. Aggregate by account × variant
    account_variant_summary = aggregate_by_account_variant(
        aggregate_df,
        output_path=output_root / "summary_by_account_variant.csv"
    )

    logger.info("="*80)
    logger.info("Equity analysis complete!")
    logger.info("="*80)

    # Print summary
    print("\n" + "="*80)
    print("PHASE 4 PERFORMANCE SUMMARY")
    print("="*80)
    print("\nBy Account × Variant:")
    print(account_variant_summary.to_string(index=False))
    print("\n" + "="*80)


if __name__ == "__main__":
    run_equity_analysis()

