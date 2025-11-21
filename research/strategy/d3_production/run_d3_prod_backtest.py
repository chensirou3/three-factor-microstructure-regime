"""
D3 Production Backtest Runner.

Runs production-style backtests for D3 strategy using the full production stack:
- D3 core signal generation
- Risk management layer
- Proper backtest engine with costs

This should produce results consistent with research validation.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import logging
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from research.strategy.d3_production.d3_core import D3Config, generate_d3_signals_for_pair
from research.strategy.d3_production.risk_management import RiskConfig, apply_risk_management
from research.strategy.d3_production.logging_utils import setup_logger, log_performance_summary
from research.strategy.backtest_engine import run_backtest as core_run_backtest


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_ladder_data(
    symbol: str,
    timeframe: str,
    ladder_dir: Path
) -> pd.DataFrame:
    """
    Load Ladder features for a symbol and timeframe.
    
    Args:
        symbol: Symbol name (e.g., 'BTCUSD')
        timeframe: Timeframe (e.g., '4h', '30min', '1h')
        ladder_dir: Directory containing Ladder feature files
    
    Returns:
        DataFrame with Ladder features
    """
    file_path = ladder_dir / f"ladder_{symbol}_{timeframe}.parquet"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Ladder data not found: {file_path}")
    
    df = pd.read_parquet(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df


def run_d3_backtest_for_pair(
    symbol: str,
    high_tf: str,
    low_tf: str,
    config: dict,
    logger: logging.Logger
) -> Dict[str, pd.DataFrame]:
    """
    Run D3 production backtest for a single (symbol, high_tf, low_tf) pair.
    
    Args:
        symbol: Trading symbol
        high_tf: High timeframe
        low_tf: Low timeframe
        config: Configuration dictionary
        logger: Logger instance
    
    Returns:
        Dictionary with 'trades', 'equity', 'summary' DataFrames
    """
    logger.info("=" * 80)
    logger.info(f"Running D3 backtest: {symbol} {high_tf} → {low_tf}")
    logger.info("=" * 80)
    
    # Paths
    root = Path(__file__).resolve().parents[3]
    ladder_dir = root / config['data']['ladder_dir']
    
    # Load data
    logger.info(f"Loading data from {ladder_dir}")
    high_tf_df = load_ladder_data(symbol, high_tf, ladder_dir)
    low_tf_df = load_ladder_data(symbol, low_tf, ladder_dir)
    
    logger.info(f"  High TF ({high_tf}): {len(high_tf_df)} bars")
    logger.info(f"  Low TF ({low_tf}): {len(low_tf_df)} bars")
    
    # Step 1: Generate D3 core signals
    logger.info("Step 1: Generating D3 core signals...")
    d3_config = D3Config(
        fast_len=config['ladder_params']['fast_len'],
        slow_len=config['ladder_params']['slow_len'],
        max_holding_bars=config['risk_management']['max_holding_bars'],
        variant_id=config['strategy']['variant_id']
    )
    
    df_with_signals = generate_d3_signals_for_pair(high_tf_df, low_tf_df, d3_config)
    
    n_entries = df_with_signals['d3_entry'].sum()
    n_exits = df_with_signals['d3_exit'].sum()
    logger.info(f"  D3 core signals: {n_entries} entries, {n_exits} exits")
    
    # Step 2: Apply risk management
    logger.info("Step 2: Applying risk management...")
    risk_config = RiskConfig(
        base_notional=config['risk_management']['base_position_notional'],
        max_positions_per_symbol=config['risk_management']['max_positions_per_symbol'],
        max_total_positions=config['risk_management']['max_total_positions'],
        atr_stop_R=config['risk_management']['atr_stop_R'],
        use_atr_stop=config['risk_management']['use_atr_stop'],
        max_holding_bars=config['risk_management']['max_holding_bars'],
        daily_loss_limit_pct=config['risk_management']['daily_loss_limit_pct'],
        use_daily_limit=config['risk_management']['use_daily_limit'],
        max_portfolio_exposure_pct=config['risk_management']['max_portfolio_exposure_pct']
    )
    
    initial_equity = config['backtest']['initial_equity']
    
    df_risk_managed = apply_risk_management(
        df_with_signals,
        risk_config,
        initial_equity,
        atr_col=risk_config.atr_stop_R if 'ATR' in df_with_signals.columns else 'ATR',
        symbol=symbol
    )
    
    n_final_entries = df_risk_managed['final_entry'].sum()
    n_final_exits = df_risk_managed['final_exit'].sum()
    n_stops = df_risk_managed['stop_hit'].sum()
    logger.info(f"  Risk-managed signals: {n_final_entries} entries, {n_final_exits} exits, {n_stops} stops")
    
    # Step 3: Run backtest with costs
    logger.info("Step 3: Running backtest with transaction costs...")
    
    # Determine cost scenario
    cost_scenario = config['backtest'].get('default_cost_scenario', 'low')
    if cost_scenario == 'low':
        cost_pct = config['backtest']['cost_per_side_pct_low']
    else:
        cost_pct = config['backtest']['cost_per_side_pct_high']
    
    logger.info(f"  Using {cost_scenario} cost scenario: {cost_pct}% per side")

    # Prepare DataFrame for backtest engine
    # The backtest engine expects: final_side, final_entry, final_exit, position_size
    df_for_backtest = df_risk_managed.copy()
    df_for_backtest['position_size'] = 1.0  # Uniform size (notional handled in risk mgmt)

    # Run backtest
    backtest_results = core_run_backtest(
        df_for_backtest,
        symbol=symbol,
        timeframe=f"{high_tf}→{low_tf}",
        initial_equity=initial_equity,
        transaction_cost_pct=cost_pct / 100.0,  # Convert to decimal
        slippage_pct=0.0
    )

    # Extract results
    trades_df = backtest_results['trades']
    equity_df = backtest_results['equity']
    summary_df = backtest_results['summary']

    logger.info(f"  Backtest complete: {len(trades_df)} trades")

    # Log summary
    if len(summary_df) > 0:
        summary_dict = summary_df.iloc[0].to_dict()
        log_performance_summary(logger, summary_dict)

    return {
        'trades': trades_df,
        'equity': equity_df,
        'summary': summary_df
    }


def save_results(
    results: Dict[str, pd.DataFrame],
    symbol: str,
    high_tf: str,
    low_tf: str,
    output_dir: Path
) -> None:
    """
    Save backtest results to CSV files.

    Args:
        results: Dictionary with 'trades', 'equity', 'summary' DataFrames
        symbol: Trading symbol
        high_tf: High timeframe
        low_tf: Low timeframe
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"d3_prod_{symbol}_{high_tf}_{low_tf}"

    # Save trades
    trades_file = output_dir / f"trades_{base_name}.csv"
    results['trades'].to_csv(trades_file, index=False)

    # Save equity curve
    equity_file = output_dir / f"equity_{base_name}.csv"
    results['equity'].to_csv(equity_file, index=False)

    # Save summary
    summary_file = output_dir / f"summary_{base_name}.csv"
    results['summary'].to_csv(summary_file, index=False)

    print(f"✓ Results saved to {output_dir}")
    print(f"  - {trades_file.name}")
    print(f"  - {equity_file.name}")
    print(f"  - {summary_file.name}")


def main():
    """Main execution function."""
    # Load configuration
    config_path = Path(__file__).parent / "config_d3_prod.yaml"
    config = load_config(config_path)

    # Setup logging
    root = Path(__file__).resolve().parents[3]
    log_dir = root / config['data']['log_dir']
    logger = setup_logger(
        "d3_prod_backtest",
        log_dir,
        level=config['logging']['level'],
        console=config['logging']['console_output']
    )

    logger.info("=" * 80)
    logger.info("D3 PRODUCTION BACKTEST RUNNER")
    logger.info("=" * 80)
    logger.info(f"Configuration: {config_path}")
    logger.info(f"Log directory: {log_dir}")

    # Results directory
    results_dir = root / config['data']['results_root']
    results_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Results directory: {results_dir}")

    # Run backtests for all configured pairs
    all_results = []

    for pair_config in config['d3_pairs']:
        symbol = pair_config['symbol']
        high_tf = pair_config['high_tf']
        low_tf = pair_config['low_tf']

        try:
            # Run backtest
            results = run_d3_backtest_for_pair(
                symbol, high_tf, low_tf, config, logger
            )

            # Save results
            save_results(results, symbol, high_tf, low_tf, results_dir)

            # Collect summary
            if len(results['summary']) > 0:
                summary_row = results['summary'].iloc[0].copy()
                summary_row['symbol'] = symbol
                summary_row['high_tf'] = high_tf
                summary_row['low_tf'] = low_tf
                all_results.append(summary_row)

        except Exception as e:
            logger.error(f"Error processing {symbol} {high_tf}→{low_tf}: {e}", exc_info=True)
            continue

    # Create aggregate summary
    if all_results:
        aggregate_df = pd.DataFrame(all_results)
        aggregate_file = results_dir / "d3_prod_aggregate_summary.csv"
        aggregate_df.to_csv(aggregate_file, index=False)

        logger.info("=" * 80)
        logger.info("AGGREGATE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"\n{aggregate_df.to_string(index=False)}")
        logger.info(f"\nAggregate summary saved to: {aggregate_file}")

    logger.info("=" * 80)
    logger.info("D3 PRODUCTION BACKTEST COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

