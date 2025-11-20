"""
Phase 2C: Strategy Tuning & Cost Model

Implement per-symbol parameter optimization and transaction cost modeling.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import yaml
import logging
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from baseline_strategy import generate_baseline_signals
from regime_wrapper import apply_regime_gating_and_sizing
from backtest_engine import run_backtest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_strategy_params(
    symbol: str,
    timeframe: str,
    config: Dict
) -> Dict[str, int]:
    """
    Get EMA parameters for a specific symbol×timeframe, with fallback to defaults.
    
    Args:
        symbol: Symbol name
        timeframe: Timeframe string
        config: Strategy params config dict
    
    Returns:
        Dict with fast_len and slow_len
    """
    # Check for symbol-specific override
    per_symbol = config.get('per_symbol_timeframe', {})
    if symbol in per_symbol and timeframe in per_symbol[symbol]:
        params = per_symbol[symbol][timeframe]
        logger.debug(f"Using custom params for {symbol}_{timeframe}: {params}")
        return params
    
    # Fall back to defaults
    default = config.get('default', {'fast_len': 20, 'slow_len': 50})
    logger.debug(f"Using default params for {symbol}_{timeframe}: {default}")
    return default


def apply_transaction_costs(
    trades_df: pd.DataFrame,
    per_trade_bps: float = 1.0,
    apply_to_entry: bool = True,
    apply_to_exit: bool = True
) -> pd.DataFrame:
    """
    Apply transaction costs to trades and compute net PnL.
    
    Args:
        trades_df: DataFrame with trade data
        per_trade_bps: Cost in basis points per side
        apply_to_entry: Whether to apply cost to entry
        apply_to_exit: Whether to apply cost to exit
    
    Returns:
        DataFrame with net PnL columns added
    """
    df = trades_df.copy()
    
    # Calculate number of sides charged
    num_sides = int(apply_to_entry) + int(apply_to_exit)
    
    # Assume position_size = 1 for simplicity (can be extended)
    # Cost = notional * bps * 1e-4 * num_sides
    # For R-multiple based system, we can approximate cost as:
    # cost_R = (per_trade_bps * 1e-4 * num_sides) / ATR_pct
    
    # Simple approximation: deduct fixed cost in R terms
    # Typical ATR is ~1-3% of price, so 1bp cost ≈ 0.01-0.03 R
    cost_R_per_trade = (per_trade_bps * 1e-4 * num_sides) * 100  # Rough approximation
    
    df['cost_R'] = cost_R_per_trade
    df['gross_R'] = df['R_multiple']
    df['net_R'] = df['gross_R'] - df['cost_R']
    
    # Recalculate PnL if available
    if 'pnl' in df.columns:
        df['gross_pnl'] = df['pnl']
        # Approximate cost in dollar terms (would need actual notional for precision)
        df['net_pnl'] = df['gross_pnl'] - (df['gross_pnl'].abs() * per_trade_bps * 1e-4 * num_sides)
    
    return df


def compute_net_summary_stats(trades_df: pd.DataFrame) -> Dict:
    """
    Compute summary statistics for net (post-cost) performance.
    
    Args:
        trades_df: DataFrame with net_R column
    
    Returns:
        Dict with summary statistics
    """
    if 'net_R' not in trades_df.columns:
        raise ValueError("net_R column not found. Apply transaction costs first.")
    
    net_r = trades_df['net_R']
    
    stats = {
        'n_trades': len(net_r),
        'mean_net_R': net_r.mean(),
        'median_net_R': net_r.median(),
        'std_net_R': net_r.std(),
        'total_net_R': net_r.sum(),
        'win_rate_pct': (net_r > 0).mean() * 100,
        'sharpe_like': net_r.mean() / net_r.std() if net_r.std() > 0 else 0,
        'p5_net_R': net_r.quantile(0.05),
        'p95_net_R': net_r.quantile(0.95)
    }
    
    return stats


def compare_gross_vs_net(
    trades_dir: Path,
    symbols: List[str],
    timeframes: List[str],
    per_trade_bps: float = 1.0
) -> pd.DataFrame:
    """
    Compare gross vs net performance across all combinations.
    
    Args:
        trades_dir: Directory with trade CSV files
        symbols: List of symbols
        timeframes: List of timeframes
        per_trade_bps: Transaction cost in basis points
    
    Returns:
        DataFrame with comparison
    """
    comparisons = []
    
    for symbol in symbols:
        for timeframe in timeframes:
            file_path = trades_dir / f"trades_{symbol}_{timeframe}.csv"
            
            if not file_path.exists():
                continue
            
            try:
                trades_df = pd.read_csv(file_path)
                
                # Apply costs
                trades_with_costs = apply_transaction_costs(
                    trades_df,
                    per_trade_bps=per_trade_bps
                )
                
                # Compute stats
                gross_stats = {
                    'mean_R': trades_df['R_multiple'].mean(),
                    'total_R': trades_df['R_multiple'].sum(),
                    'sharpe_like': trades_df['R_multiple'].mean() / trades_df['R_multiple'].std()
                }
                
                net_stats = compute_net_summary_stats(trades_with_costs)
                
                comparisons.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'n_trades': len(trades_df),
                    'gross_mean_R': gross_stats['mean_R'],
                    'net_mean_R': net_stats['mean_net_R'],
                    'cost_impact_R': gross_stats['mean_R'] - net_stats['mean_net_R'],
                    'gross_total_R': gross_stats['total_R'],
                    'net_total_R': net_stats['total_net_R'],
                    'gross_sharpe': gross_stats['sharpe_like'],
                    'net_sharpe': net_stats['sharpe_like']
                })
                
            except Exception as e:
                logger.error(f"Error processing {symbol}_{timeframe}: {e}")
    
    return pd.DataFrame(comparisons)


def run_grid_search(
    symbol: str,
    timeframe: str,
    data_df: pd.DataFrame,
    fast_len_candidates: List[int],
    slow_len_candidates: List[int],
    regime_config: Dict,
    per_trade_bps: float = 1.0
) -> pd.DataFrame:
    """
    Run grid search over EMA parameters for a symbol×timeframe.

    Args:
        symbol: Symbol name
        timeframe: Timeframe string
        data_df: Merged data DataFrame
        fast_len_candidates: List of fast EMA lengths to test
        slow_len_candidates: List of slow EMA lengths to test
        regime_config: Regime gating config
        per_trade_bps: Transaction cost in basis points

    Returns:
        DataFrame with grid search results
    """
    results = []

    for fast_len in fast_len_candidates:
        for slow_len in slow_len_candidates:
            if fast_len >= slow_len:
                continue  # Skip invalid combinations

            try:
                # Generate signals
                df_signals = generate_baseline_signals(
                    data_df.copy(),
                    fast_len=fast_len,
                    slow_len=slow_len
                )

                # Apply regime wrapper
                df_regime = apply_regime_gating_and_sizing(
                    df_signals,
                    regime_config
                )

                # Run backtest
                trades, equity, summary = run_backtest(
                    df_regime,
                    symbol=symbol,
                    timeframe=timeframe
                )

                if len(trades) == 0:
                    continue

                # Apply costs
                trades_with_costs = apply_transaction_costs(
                    trades,
                    per_trade_bps=per_trade_bps
                )

                net_stats = compute_net_summary_stats(trades_with_costs)

                results.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'fast_len': fast_len,
                    'slow_len': slow_len,
                    'n_trades': net_stats['n_trades'],
                    'net_mean_R': net_stats['mean_net_R'],
                    'net_total_R': net_stats['total_net_R'],
                    'net_sharpe': net_stats['sharpe_like'],
                    'win_rate_pct': net_stats['win_rate_pct']
                })

                logger.info(f"  {fast_len}/{slow_len}: net_mean_R={net_stats['mean_net_R']:.3f}, "
                          f"net_sharpe={net_stats['sharpe_like']:.3f}")

            except Exception as e:
                logger.error(f"Error with {fast_len}/{slow_len}: {e}")

    return pd.DataFrame(results)


def run_phase2c_analysis(config_path: Path = Path("research/strategy/phase2/config_phase2.yaml")) -> None:
    """
    Main function to run Phase 2C strategy tuning analysis.

    Args:
        config_path: Path to Phase 2 config file
    """
    logger.info("="*80)
    logger.info("Phase 2C: Strategy Tuning & Cost Model")
    logger.info("="*80)

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    phase2c_config = config['phase2C']
    global_config = config['global']

    # Setup paths
    trades_dir = Path(global_config['phase1_results_dir'])
    output_dir = Path(phase2c_config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Gross vs Net comparison
    logger.info("\n" + "="*80)
    logger.info("Step 1: Comparing Gross vs Net Performance")
    logger.info("="*80)

    per_trade_bps = phase2c_config['costs']['per_trade_bps']

    comparison = compare_gross_vs_net(
        trades_dir,
        global_config['symbols'],
        global_config['timeframes'],
        per_trade_bps
    )

    comparison.to_csv(output_dir / "gross_vs_net_comparison.csv", index=False)
    logger.info(f"✅ Saved: {output_dir / 'gross_vs_net_comparison.csv'}")

    # Show summary
    logger.info("\nCost Impact Summary:")
    logger.info(f"Average cost impact: {comparison['cost_impact_R'].mean():.4f} R per trade")
    logger.info(f"Total cost impact: {comparison['cost_impact_R'].sum():.2f} R across all combinations")

    # Step 2: Grid search (if enabled)
    if phase2c_config['grid_search']['enabled']:
        logger.info("\n" + "="*80)
        logger.info("Step 2: Running Grid Search")
        logger.info("="*80)

        data_dir = Path(global_config['data_dir'])
        focus_timeframes = phase2c_config['grid_search']['focus_timeframes']
        fast_candidates = phase2c_config['grid_search']['fast_len_candidates']
        slow_candidates = phase2c_config['grid_search']['slow_len_candidates']

        # Load regime config from Phase 1
        with open(Path(global_config['phase1_results_dir']).parent / 'config_strategy.yaml', 'r') as f:
            regime_config = yaml.safe_load(f)

        all_grid_results = []

        for symbol in global_config['symbols']:
            for timeframe in focus_timeframes:
                data_file = data_dir / f"merged_{symbol}_{timeframe}.parquet"

                if not data_file.exists():
                    logger.warning(f"Data file not found: {data_file}")
                    continue

                logger.info(f"\nRunning grid search for {symbol}_{timeframe}...")

                try:
                    data_df = pd.read_parquet(data_file)

                    grid_results = run_grid_search(
                        symbol,
                        timeframe,
                        data_df,
                        fast_candidates,
                        slow_candidates,
                        regime_config,
                        per_trade_bps
                    )

                    if len(grid_results) > 0:
                        # Save per-combination results
                        grid_results.to_csv(
                            output_dir / f"grid_search_{symbol}_{timeframe}.csv",
                            index=False
                        )
                        all_grid_results.append(grid_results)

                        # Show best result
                        best = grid_results.loc[grid_results['net_sharpe'].idxmax()]
                        logger.info(f"✅ Best params: fast={best['fast_len']}, slow={best['slow_len']}, "
                                  f"net_sharpe={best['net_sharpe']:.3f}")

                except Exception as e:
                    logger.error(f"Error in grid search for {symbol}_{timeframe}: {e}")

        # Combine all grid results
        if all_grid_results:
            combined_grid = pd.concat(all_grid_results, ignore_index=True)
            combined_grid.to_csv(output_dir / "grid_search_all_results.csv", index=False)
            logger.info(f"\n✅ Saved combined grid search results")

    else:
        logger.info("\n⏭️  Grid search disabled in config")

    logger.info("\n" + "="*80)
    logger.info("Phase 2C Analysis Complete!")
    logger.info("="*80)
    logger.info(f"\nOutputs saved to: {output_dir}")
    logger.info(f"\n📋 Key findings:")
    logger.info(f"   - Transaction costs impact: ~{comparison['cost_impact_R'].mean():.4f} R per trade")
    logger.info(f"   - Review gross_vs_net_comparison.csv for detailed impact")
    if phase2c_config['grid_search']['enabled']:
        logger.info(f"   - Check grid search results for optimal parameters")


if __name__ == "__main__":
    run_phase2c_analysis()


