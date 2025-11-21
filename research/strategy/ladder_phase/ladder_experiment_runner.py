"""
Ladder + Regime Experiment Runner

Runs all Ladder + Regime experiments for Stage L2.
"""

import sys
from pathlib import Path
from typing import List
import pandas as pd
import yaml
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.ladder_phase.ladder_strategy_signals import load_ladder_data_and_generate_signals
from research.strategy.ladder_phase.ladder_regime_variants import (
    load_ladder_policies_from_config,
    apply_regime_policy_to_ladder_signals
)
from research.strategy.backtest_engine import run_backtest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_single_ladder_experiment(symbol: str,
                                 timeframe: str,
                                 variant_id: str,
                                 policy,
                                 ladder_dir: Path,
                                 output_dir: Path,
                                 transaction_cost_bps: float = 1.0) -> dict:
    """
    Run a single Ladder + Regime experiment.
    
    Args:
        symbol: Symbol name
        timeframe: Timeframe
        variant_id: Variant ID (e.g., 'L_V0_baseline')
        policy: RegimePolicy object
        ladder_dir: Directory with Ladder features
        output_dir: Output directory
        transaction_cost_bps: Transaction cost in basis points
    
    Returns:
        Dictionary with experiment results
    """
    try:
        # Load Ladder data and generate signals
        df = load_ladder_data_and_generate_signals(symbol, timeframe, ladder_dir)
        
        # Apply regime policy
        df = apply_regime_policy_to_ladder_signals(df, policy)
        
        # Run backtest
        results = run_backtest(
            df=df,
            symbol=symbol,
            timeframe=timeframe,
            initial_equity=10000.0,
            transaction_cost_pct=transaction_cost_bps / 10000.0,  # Convert bps to percentage
            slippage_pct=0.0
        )
        
        # Save results
        variant_dir = output_dir / variant_id
        variant_dir.mkdir(parents=True, exist_ok=True)
        
        trades_file = variant_dir / f"trades_{symbol}_{timeframe}.csv"
        results['trades'].to_csv(trades_file, index=False)
        
        equity_file = variant_dir / f"equity_{symbol}_{timeframe}.csv"
        results['equity'].to_csv(equity_file, index=False)
        
        summary_file = variant_dir / f"summary_{symbol}_{timeframe}.csv"
        results['summary'].to_csv(summary_file, index=False)
        
        logger.info(f"✓ {variant_id} × {symbol}_{timeframe}: "
                   f"{results['summary']['n_trades'].iloc[0]:.0f} trades, "
                   f"Return {results['summary']['total_return_pct'].iloc[0]:.2f}%")
        
        return {
            'success': True,
            'variant_id': variant_id,
            'symbol': symbol,
            'timeframe': timeframe,
            'n_trades': results['summary']['n_trades'].iloc[0]
        }
        
    except Exception as e:
        logger.error(f"✗ {variant_id} × {symbol}_{timeframe}: {e}")
        return {
            'success': False,
            'variant_id': variant_id,
            'symbol': symbol,
            'timeframe': timeframe,
            'error': str(e)
        }


def run_all_ladder_experiments(config_path: Path,
                               ladder_dir: Path,
                               output_dir: Path) -> None:
    """
    Run all Ladder + Regime experiments.
    
    Args:
        config_path: Path to config_ladder_phase.yaml
        ladder_dir: Directory with Ladder features
        output_dir: Output directory
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    symbols = config['experiments']['symbols']
    timeframes = config['experiments']['timeframes']
    transaction_cost_bps = config['experiments']['transaction_cost_bps']
    
    # Load policies
    policies = load_ladder_policies_from_config(config_path)
    
    # Filter enabled variants
    enabled_variants = [v for v in config['variants'] if v['enabled']]
    
    total = len(symbols) * len(timeframes) * len(enabled_variants)
    completed = 0
    failed = 0
    
    logger.info("="*80)
    logger.info(f"Running Ladder + Regime experiments")
    logger.info(f"  Symbols: {len(symbols)}")
    logger.info(f"  Timeframes: {len(timeframes)}")
    logger.info(f"  Variants: {len(enabled_variants)}")
    logger.info(f"  Total experiments: {total}")
    logger.info("="*80)
    
    for variant_cfg in enabled_variants:
        variant_id = variant_cfg['id']
        policy = policies[variant_id]
        
        logger.info(f"\nRunning variant: {variant_id}")
        logger.info(f"  {policy.description}")
        
        for symbol in symbols:
            for timeframe in timeframes:
                result = run_single_ladder_experiment(
                    symbol=symbol,
                    timeframe=timeframe,
                    variant_id=variant_id,
                    policy=policy,
                    ladder_dir=ladder_dir,
                    output_dir=output_dir,
                    transaction_cost_bps=transaction_cost_bps
                )
                
                if result['success']:
                    completed += 1
                else:
                    failed += 1
    
    logger.info("="*80)
    logger.info("Ladder + Regime experiments complete!")
    logger.info(f"  Completed: {completed}/{total}")
    logger.info(f"  Failed: {failed}")
    logger.info("="*80)


if __name__ == "__main__":
    # Project root
    root = Path(__file__).resolve().parents[3]

    # Paths
    config_path = root / "research/strategy/ladder_phase/config_ladder_phase.yaml"
    ladder_dir = root / "data/ladder_features"
    output_dir = root / "results/strategy/ladder_phase"

    # Run all experiments
    run_all_ladder_experiments(config_path, ladder_dir, output_dir)

