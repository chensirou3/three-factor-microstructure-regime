"""
Orchestrator script for Strategy Phase 1: Regime-aware baseline strategy.

This script:
1. Loads merged three-factor data for each symbol×timeframe
2. Generates baseline EMA crossover signals
3. Applies regime-based gating and position sizing
4. Runs backtest with regime-conditioned performance analysis
5. Saves results to results/strategy/

Usage:
    cd ~/microstructure-three-factor-regime
    python research/strategy/run_regime_strategy.py
"""

import sys
from pathlib import Path
import pandas as pd
import yaml
import logging
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from research.strategy.baseline_strategy import generate_baseline_signals, validate_baseline_signals
from research.strategy.regime_wrapper import apply_regime_wrapper, analyze_gating_impact
from research.strategy.backtest_engine import run_backtest


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(project_root / 'strategy_backtest.log')
        ]
    )


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load strategy configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def load_merged_data(symbol: str, timeframe: str, data_dir: Path) -> pd.DataFrame:
    """Load merged three-factor data for a symbol×timeframe."""
    file_path = data_dir / f"merged_{symbol}_{timeframe}.parquet"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Merged data not found: {file_path}")
    
    df = pd.read_parquet(file_path)
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df


def save_results(results: Dict[str, pd.DataFrame], symbol: str, timeframe: str, output_dir: Path):
    """Save backtest results to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save each result DataFrame
    for key, df in results.items():
        if df is not None and len(df) > 0:
            filename = f"{key}_{symbol}_{timeframe}.csv"
            output_path = output_dir / filename
            df.to_csv(output_path, index=False)
            logging.info(f"Saved {key} to {output_path}")


def run_baseline_only_backtest(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    initial_equity: float
) -> Dict[str, Any]:
    """Run baseline-only backtest (no regime gating) for comparison."""
    # Create a simple wrapper that doesn't block any entries
    df_baseline = df.copy()
    df_baseline['final_side'] = df_baseline['baseline_side']
    df_baseline['final_entry'] = df_baseline['baseline_entry']
    df_baseline['final_exit'] = df_baseline['baseline_exit']
    df_baseline['position_size'] = 1.0  # Fixed size
    df_baseline.loc[df_baseline['final_side'] == 'flat', 'position_size'] = 0.0
    
    results = run_backtest(df_baseline, symbol, timeframe, initial_equity)
    
    return results['summary'].iloc[0].to_dict() if len(results['summary']) > 0 else {}


def main():
    """Main orchestrator function."""
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config_path = project_root / "research" / "strategy" / "config_strategy.yaml"
    config = load_config(config_path)
    
    # Setup logging
    setup_logging(config.get('logging', {}).get('level', 'INFO'))
    
    logger.info("=" * 80)
    logger.info("Strategy Phase 1: Regime-aware Baseline Strategy Backtest")
    logger.info("=" * 80)
    
    # Setup paths
    data_dir = project_root / "data" / "factors" / "merged_three_factor"
    output_dir = project_root / config['output']['results_dir']
    
    # Extract config
    symbols = config['symbols']
    timeframes = config['timeframes']
    baseline_cfg = config['baseline']
    gating_cfg = config['gating']
    sizing_cfg = config['position_sizing']
    backtest_cfg = config['backtest']
    triple_high_box = config['triple_high_box_name']
    
    # Comparison results
    comparison_results = []
    
    # Process each symbol×timeframe
    for symbol in symbols:
        for timeframe in timeframes:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing {symbol} {timeframe}")
            logger.info(f"{'='*60}")
            
            try:
                # Load data
                df = load_merged_data(symbol, timeframe, data_dir)
                logger.info(f"Loaded {len(df)} bars from {df['timestamp'].min()} to {df['timestamp'].max()}")
                
                # Generate baseline signals
                df = generate_baseline_signals(df, **baseline_cfg)
                baseline_stats = validate_baseline_signals(df)
                logger.info(f"Baseline signals: {baseline_stats}")
                
                # Apply regime wrapper
                df = apply_regime_wrapper(df, gating_cfg, sizing_cfg, triple_high_box)
                gating_stats = analyze_gating_impact(df)
                logger.info(f"Gating impact: {gating_stats}")
                
                # Run regime-aware backtest
                logger.info("Running regime-aware backtest...")
                results = run_backtest(
                    df, symbol, timeframe,
                    initial_equity=backtest_cfg['initial_equity'],
                    transaction_cost_pct=backtest_cfg['transaction_cost_pct'],
                    slippage_pct=backtest_cfg['slippage_pct']
                )
                
                # Run baseline-only backtest for comparison
                logger.info("Running baseline-only backtest for comparison...")
                baseline_results = run_baseline_only_backtest(
                    df, symbol, timeframe, backtest_cfg['initial_equity']
                )
                
                # Save results
                save_results(results, symbol, timeframe, output_dir)
                
                # Store comparison
                regime_summary = results['summary'].iloc[0].to_dict() if len(results['summary']) > 0 else {}
                comparison_results.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'baseline_return_pct': baseline_results.get('total_return_pct', 0),
                    'regime_return_pct': regime_summary.get('total_return_pct', 0),
                    'baseline_sharpe': baseline_results.get('sharpe_ratio', 0),
                    'regime_sharpe': regime_summary.get('sharpe_ratio', 0),
                    'baseline_max_dd_pct': baseline_results.get('max_drawdown_pct', 0),
                    'regime_max_dd_pct': regime_summary.get('max_drawdown_pct', 0),
                    'baseline_n_trades': baseline_results.get('n_trades', 0),
                    'regime_n_trades': regime_summary.get('n_trades', 0)
                })
                
                logger.info(f"✅ Completed {symbol} {timeframe}")
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol} {timeframe}: {e}", exc_info=True)
                continue
    
    # Save comparison results
    if comparison_results:
        comparison_df = pd.DataFrame(comparison_results)
        comparison_path = output_dir / "compare_baseline_vs_regime.csv"
        comparison_df.to_csv(comparison_path, index=False)
        logger.info(f"\n{'='*60}")
        logger.info(f"Saved comparison results to {comparison_path}")
        logger.info(f"{'='*60}\n")
        logger.info(comparison_df.to_string(index=False))
    
    logger.info("\n" + "="*80)
    logger.info("Strategy Phase 1 backtest complete!")
    logger.info("="*80)


if __name__ == "__main__":
    main()

