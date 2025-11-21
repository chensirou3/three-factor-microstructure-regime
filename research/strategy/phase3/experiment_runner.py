"""
Phase 3 Experiment Runner

Systematically runs backtests for all strategy variants across
symbols and timeframes, saving results for comparison.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import logging
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.baseline_strategy import generate_baseline_signals
from research.strategy.regime_wrapper import apply_regime_wrapper
from research.strategy.backtest_engine import run_backtest
from research.strategy.phase3.regime_policies import load_policies_from_config, RegimePolicy
from research.strategy.phase3.strategy_variants import apply_regime_policy_to_signals

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_merged_data(symbol: str, timeframe: str, data_dir: Path) -> pd.DataFrame:
    """Load merged three-factor data for a symbol/timeframe."""
    file_path = data_dir / f"merged_{symbol}_{timeframe}.parquet"
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    df = pd.read_parquet(file_path)
    logger.info(f"Loaded {len(df)} bars for {symbol}_{timeframe}")
    return df


def run_single_experiment(
    symbol: str,
    timeframe: str,
    policy: RegimePolicy,
    config: Dict,
    data_dir: Path,
    output_dir: Path
) -> Dict:
    """
    Run a single experiment for one variant × symbol × timeframe.
    
    Args:
        symbol: Trading symbol
        timeframe: Timeframe string
        policy: RegimePolicy to apply
        config: Full config dict
        data_dir: Path to merged data
        output_dir: Path to save results
        
    Returns:
        Dictionary with summary statistics
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Running: {policy.id} × {symbol} × {timeframe}")
    logger.info(f"{'='*80}")
    
    # Load data
    df = load_merged_data(symbol, timeframe, data_dir)
    
    # Generate baseline EMA signals
    baseline_params = config['baseline']
    df = generate_baseline_signals(
        df,
        fast_len=baseline_params['fast_len'],
        slow_len=baseline_params['slow_len']
    )
    
    # Apply base regime wrapper (with Phase 2 threshold if configured)
    exp_config = config['experiments']
    if exp_config.get('use_new_high_riskscore', False):
        high_riskscore = exp_config['high_riskscore']
    else:
        high_riskscore = 0.80  # Phase 1 default

    # Configure gating and sizing for wrapper
    gating_cfg = {
        'block_new_entries_in_high_pressure': True,  # Will use high_riskscore threshold
        'block_new_entries_in_triple_high_box': False  # Disable box-based gating
    }

    sizing_cfg = {
        'base_size': 1.0,
        'size_by_riskregime': {
            'low': 1.0,
            'medium': 0.7,
            'high': 0.3
        }
    }

    # Note: We need to add high_pressure column based on RiskScore threshold
    df['high_pressure'] = df['RiskScore'] >= high_riskscore

    df = apply_regime_wrapper(
        df,
        gating_cfg=gating_cfg,
        sizing_cfg=sizing_cfg,
        triple_high_box_name="M_high_O_high_V_high"
    )
    
    # Apply regime policy to get final signals
    df = apply_regime_policy_to_signals(df, policy)

    # Run backtest using final signals
    # Note: backtest_engine expects final_side, final_entry, final_exit columns
    backtest_results = run_backtest(
        df,
        symbol=symbol,
        timeframe=timeframe,
        initial_equity=100000.0,
        transaction_cost_pct=0.0,  # We'll apply costs separately
        slippage_pct=0.0
    )

    trades_df = backtest_results['trades']
    equity_df = backtest_results['equity']
    summary = backtest_results['summary']
    
    # Add variant metadata to trades
    if len(trades_df) > 0:
        trades_df['variant_id'] = policy.id
        trades_df['symbol'] = symbol
        trades_df['timeframe'] = timeframe
    
    # Apply transaction costs (from Phase 2C)
    cost_bps = exp_config.get('transaction_cost_bps', 1.0)
    if len(trades_df) > 0:
        cost_per_trade = cost_bps / 10000 * 2  # Both sides
        trades_df['cost_R'] = cost_per_trade / trades_df['ATR_entry']  # Approximate
        trades_df['net_R'] = trades_df['R_multiple'] - trades_df['cost_R']
    
    # Save results
    variant_dir = output_dir / policy.id
    variant_dir.mkdir(parents=True, exist_ok=True)
    
    trades_path = variant_dir / f"trades_{symbol}_{timeframe}.csv"
    equity_path = variant_dir / f"equity_{symbol}_{timeframe}.csv"
    summary_path = variant_dir / f"summary_{symbol}_{timeframe}.csv"
    
    if len(trades_df) > 0:
        trades_df.to_csv(trades_path, index=False)
        logger.info(f"Saved {len(trades_df)} trades to {trades_path}")
    
    if len(equity_df) > 0:
        equity_df.to_csv(equity_path)
        logger.info(f"Saved equity curve to {equity_path}")
    
    # Compute summary statistics
    summary_stats = compute_summary_stats(trades_df, symbol, timeframe, policy.id)
    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_csv(summary_path, index=False)
    logger.info(f"Saved summary to {summary_path}")
    
    return summary_stats


def compute_summary_stats(trades_df: pd.DataFrame, symbol: str, timeframe: str, variant_id: str) -> Dict:
    """Compute summary statistics for a backtest run."""
    if len(trades_df) == 0:
        return {
            'variant_id': variant_id,
            'symbol': symbol,
            'timeframe': timeframe,
            'total_trades': 0,
            'gross_mean_R': 0.0,
            'net_mean_R': 0.0,
            'sharpe_like': 0.0,
            'tail_R_p5': 0.0,
            'tail_R_p1': 0.0,
            'win_rate': 0.0,
            'max_drawdown': 0.0
        }

    gross_R = trades_df['R_multiple']
    net_R = trades_df['net_R'] if 'net_R' in trades_df.columns else gross_R

    # Compute Sharpe-like
    sharpe_like = net_R.mean() / net_R.std() if net_R.std() > 0 else 0.0

    # Compute max drawdown
    cumulative_R = net_R.cumsum()
    running_max = cumulative_R.expanding().max()
    drawdown = cumulative_R - running_max
    max_drawdown = drawdown.min()

    return {
        'variant_id': variant_id,
        'symbol': symbol,
        'timeframe': timeframe,
        'total_trades': len(trades_df),
        'gross_mean_R': gross_R.mean(),
        'net_mean_R': net_R.mean(),
        'gross_total_R': gross_R.sum(),
        'net_total_R': net_R.sum(),
        'sharpe_like': sharpe_like,
        'std_R': net_R.std(),
        'tail_R_p5': net_R.quantile(0.05),
        'tail_R_p1': net_R.quantile(0.01),
        'tail_R_p95': net_R.quantile(0.95),
        'tail_R_p99': net_R.quantile(0.99),
        'win_rate': (net_R > 0).mean(),
        'max_drawdown': max_drawdown
    }


def run_phase3_experiments(config_path: Path = None):
    """
    Main entrypoint for Phase 3 experiments.

    Runs all enabled variants across all symbols × timeframes.
    """
    if config_path is None:
        config_path = Path("research/strategy/phase3/config_phase3.yaml")

    logger.info(f"\n{'='*80}")
    logger.info("PHASE 3 EXPERIMENT RUNNER")
    logger.info(f"{'='*80}\n")

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Load policies
    policies = load_policies_from_config(config_path)

    # Get experiment settings
    exp_config = config['experiments']
    symbols = exp_config['symbols']
    timeframes = exp_config['timeframes']
    output_dir = Path(exp_config['output_dir'])
    data_dir = Path("data/factors/merged_three_factor")

    # Filter to enabled variants
    enabled_policies = {k: v for k, v in policies.items() if v.enabled}

    logger.info(f"Symbols: {symbols}")
    logger.info(f"Timeframes: {timeframes}")
    logger.info(f"Enabled variants: {list(enabled_policies.keys())}")
    logger.info(f"Total experiments: {len(enabled_policies) * len(symbols) * len(timeframes)}\n")

    # Run all experiments
    all_results = []

    for policy_id, policy in enabled_policies.items():
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    summary = run_single_experiment(
                        symbol=symbol,
                        timeframe=timeframe,
                        policy=policy,
                        config=config,
                        data_dir=data_dir,
                        output_dir=output_dir
                    )
                    all_results.append(summary)

                except Exception as e:
                    logger.error(f"Error in {policy_id} × {symbol} × {timeframe}: {e}")
                    import traceback
                    traceback.print_exc()

    # Save aggregated results
    if all_results:
        results_df = pd.DataFrame(all_results)
        agg_path = output_dir / "all_experiments_summary.csv"
        results_df.to_csv(agg_path, index=False)
        logger.info(f"\n{'='*80}")
        logger.info(f"Saved aggregated results to {agg_path}")
        logger.info(f"Total successful experiments: {len(results_df)}")
        logger.info(f"{'='*80}\n")

    return all_results


if __name__ == "__main__":
    run_phase3_experiments()

