"""
Run backtests for all Ladder×Factor combo variants.

Executes Direction 2, 3, and 4 backtests and saves results.
"""

import sys
from pathlib import Path
import pandas as pd
import yaml
import logging
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research.strategy.backtest_engine import run_backtest
from research.ladder_factor_combo.entry_filter_and_sizing import (
    generate_entry_filter_and_sizing_signals,
    load_ladder_data_with_factors
)
from research.ladder_factor_combo.exit_rules import (
    apply_factor_based_exit_rules,
    generate_ladder_baseline_signals
)
from research.ladder_factor_combo.mtf_timing import (
    generate_mtf_timing_signals,
    load_and_align_mtf_data
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_direction2_backtests(
    config: Dict,
    root: Path,
    output_dir: Path
) -> None:
    """
    Run Direction 2 backtests: Entry filtering and sizing.
    
    Args:
        config: Configuration dictionary
        root: Project root path
        output_dir: Output directory
    """
    logger.info("="*80)
    logger.info("Running Direction 2 backtests: Entry filtering & sizing")
    logger.info("="*80)
    
    symbols = config['symbols']
    timeframes = config['high_timeframes']  # Focus on 4h/1d for Ladder
    variants = config['direction2']['variants']
    
    d2_output = output_dir / "direction2"
    d2_output.mkdir(parents=True, exist_ok=True)
    
    total = len(symbols) * len(timeframes) * len(variants)
    completed = 0
    
    for variant_cfg in variants:
        variant_id = variant_cfg['id']
        variant_dir = d2_output / variant_id
        variant_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"\nVariant: {variant_id}")
        logger.info(f"  {variant_cfg['description']}")
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # Load data
                    df = load_ladder_data_with_factors(
                        symbol, timeframe, root, config['ladder_dir']
                    )
                    
                    # Generate signals
                    df_signals = generate_entry_filter_and_sizing_signals(
                        df,
                        variant_id,
                        variant_cfg,
                        config['direction2']['healthy_thresholds'],
                        config['direction2']['sizing']
                    )
                    
                    # Run backtest
                    results = run_backtest(
                        df=df_signals,
                        symbol=symbol,
                        timeframe=timeframe,
                        initial_equity=config['backtest']['initial_equity'],
                        transaction_cost_pct=config['backtest']['transaction_cost_bps'] / 10000.0,
                        slippage_pct=config['backtest']['slippage_pct']
                    )
                    
                    # Save results
                    trades_file = variant_dir / f"trades_{symbol}_{timeframe}.csv"
                    results['trades'].to_csv(trades_file, index=False)
                    
                    equity_file = variant_dir / f"equity_{symbol}_{timeframe}.csv"
                    results['equity'].to_csv(equity_file, index=False)
                    
                    summary_file = variant_dir / f"summary_{symbol}_{timeframe}.csv"
                    results['summary'].to_csv(summary_file, index=False)
                    
                    completed += 1
                    logger.info(f"  ✓ {symbol}_{timeframe}: {results['summary']['n_trades'].iloc[0]:.0f} trades, "
                               f"Return {results['summary']['total_return_pct'].iloc[0]:.2f}%")
                    
                except Exception as e:
                    logger.error(f"  ✗ {symbol}_{timeframe}: {e}")
    
    logger.info(f"\nDirection 2 complete: {completed}/{total} backtests")


def run_direction4_backtests(
    config: Dict,
    root: Path,
    output_dir: Path
) -> None:
    """
    Run Direction 4 backtests: Factor-based exits.
    
    Args:
        config: Configuration dictionary
        root: Project root path
        output_dir: Output directory
    """
    logger.info("="*80)
    logger.info("Running Direction 4 backtests: Factor-based exits")
    logger.info("="*80)
    
    symbols = config['symbols']
    timeframes = config['high_timeframes']
    variants = config['direction4']['variants']
    
    d4_output = output_dir / "direction4"
    d4_output.mkdir(parents=True, exist_ok=True)
    
    total = len(symbols) * len(timeframes) * len(variants)
    completed = 0
    
    for variant_cfg in variants:
        variant_id = variant_cfg['id']
        exit_type = variant_cfg['exit_type']
        variant_dir = d4_output / variant_id
        variant_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"\nVariant: {variant_id} (exit_type={exit_type})")
        logger.info(f"  {variant_cfg['description']}")
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # Load data
                    df = load_ladder_data_with_factors(
                        symbol, timeframe, root, config['ladder_dir']
                    )
                    
                    # Generate baseline Ladder signals
                    df = generate_ladder_baseline_signals(df)
                    
                    # Apply factor-based exits
                    df_signals = apply_factor_based_exit_rules(
                        df,
                        variant_id,
                        exit_type,
                        config['direction4']['exit_rules']
                    )
                    
                    # Run backtest
                    results = run_backtest(
                        df=df_signals,
                        symbol=symbol,
                        timeframe=timeframe,
                        initial_equity=config['backtest']['initial_equity'],
                        transaction_cost_pct=config['backtest']['transaction_cost_bps'] / 10000.0,
                        slippage_pct=config['backtest']['slippage_pct']
                    )
                    
                    # Save results
                    trades_file = variant_dir / f"trades_{symbol}_{timeframe}.csv"
                    results['trades'].to_csv(trades_file, index=False)
                    
                    equity_file = variant_dir / f"equity_{symbol}_{timeframe}.csv"
                    results['equity'].to_csv(equity_file, index=False)
                    
                    summary_file = variant_dir / f"summary_{symbol}_{timeframe}.csv"
                    results['summary'].to_csv(summary_file, index=False)
                    
                    completed += 1
                    logger.info(f"  ✓ {symbol}_{timeframe}: {results['summary']['n_trades'].iloc[0]:.0f} trades, "
                               f"Return {results['summary']['total_return_pct'].iloc[0]:.2f}%")
                    
                except Exception as e:
                    logger.error(f"  ✗ {symbol}_{timeframe}: {e}")
    
    logger.info(f"\nDirection 4 complete: {completed}/{total} backtests")


def run_direction3_backtests(
    config: Dict,
    root: Path,
    output_dir: Path
) -> None:
    """
    Run Direction 3 backtests: Multi-timeframe timing.

    Args:
        config: Configuration dictionary
        root: Project root path
        output_dir: Output directory
    """
    logger.info("="*80)
    logger.info("Running Direction 3 backtests: Multi-timeframe timing")
    logger.info("="*80)

    symbols = config['symbols']
    variants = config['direction3']['variants']
    high_tf_mapping = config['direction3']['high_tf_for_each']

    d3_output = output_dir / "direction3"
    d3_output.mkdir(parents=True, exist_ok=True)

    total = len(symbols) * len(high_tf_mapping) * len(variants)
    completed = 0

    for variant_cfg in variants:
        variant_id = variant_cfg['id']
        use_factor_pullback = variant_cfg['use_factor_pullback']
        variant_dir = d3_output / variant_id
        variant_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"\nVariant: {variant_id}")
        logger.info(f"  {variant_cfg['description']}")

        for symbol in symbols:
            for low_tf, high_tf in high_tf_mapping.items():
                try:
                    # Load and align MTF data
                    high_tf_df, low_tf_aligned = load_and_align_mtf_data(
                        symbol, high_tf, low_tf, root, config['ladder_dir']
                    )

                    # Generate MTF signals
                    df_signals = generate_mtf_timing_signals(
                        low_tf_aligned,
                        variant_id,
                        use_factor_pullback,
                        config['direction3']['pullback_conditions']
                    )

                    # Run backtest
                    results = run_backtest(
                        df=df_signals,
                        symbol=symbol,
                        timeframe=f"{high_tf}_{low_tf}",  # Combined label
                        initial_equity=config['backtest']['initial_equity'],
                        transaction_cost_pct=config['backtest']['transaction_cost_bps'] / 10000.0,
                        slippage_pct=config['backtest']['slippage_pct']
                    )

                    # Save results
                    combo_label = f"{symbol}_{high_tf}_{low_tf}"
                    trades_file = variant_dir / f"trades_{combo_label}.csv"
                    results['trades'].to_csv(trades_file, index=False)

                    equity_file = variant_dir / f"equity_{combo_label}.csv"
                    results['equity'].to_csv(equity_file, index=False)

                    summary_file = variant_dir / f"summary_{combo_label}.csv"
                    results['summary'].to_csv(summary_file, index=False)

                    completed += 1
                    logger.info(f"  ✓ {combo_label}: {results['summary']['n_trades'].iloc[0]:.0f} trades, "
                               f"Return {results['summary']['total_return_pct'].iloc[0]:.2f}%")

                except Exception as e:
                    logger.error(f"  ✗ {symbol}_{high_tf}_{low_tf}: {e}")

    logger.info(f"\nDirection 3 complete: {completed}/{total} backtests")


def main():
    """Main entry point."""
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    root = Path(__file__).resolve().parents[2]
    output_dir = root / config['outputs']['root']
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run Direction 2
    run_direction2_backtests(config, root, output_dir)

    # Run Direction 4
    run_direction4_backtests(config, root, output_dir)

    # Run Direction 3
    run_direction3_backtests(config, root, output_dir)

    logger.info("="*80)
    logger.info("✓ All combo backtests complete!")
    logger.info("="*80)


if __name__ == "__main__":
    main()

