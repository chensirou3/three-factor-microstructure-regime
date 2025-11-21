"""
Ladder Baseline Strategy - Simple Trend Following

Simple Ladder-only trading strategy (no Regime, no factors):
  - Entry: Long when upTrend == True (ladder_state = +1)
  - Exit: Flat when upTrend == False (ladder_state != +1)
  - Position: Long-only (no short for now)

This provides a baseline to compare against Ladder + Regime strategies.
"""

import sys
from pathlib import Path
from typing import List
import pandas as pd
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research.strategy.backtest_engine import run_backtest

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_ladder_baseline_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Ladder baseline trading signals.
    
    Strategy logic:
      - Long when upTrend == True (ladder_state = +1)
      - Flat otherwise
    
    Args:
        df: Ladder-enriched DataFrame with 'upTrend' and 'ladder_state' columns
    
    Returns:
        DataFrame with added columns:
          - ladder_side: 'flat' or 'long'
          - ladder_entry: bool (entry signal)
          - ladder_exit: bool (exit signal)
    """
    df = df.copy()
    
    # Determine position side based on upTrend
    df['ladder_side'] = 'flat'
    df.loc[df['upTrend'], 'ladder_side'] = 'long'
    
    # Detect entry/exit signals
    df['ladder_entry'] = False
    df['ladder_exit'] = False
    
    # Entry: transition from flat to long
    df.loc[(df['ladder_side'] == 'long') & (df['ladder_side'].shift(1) == 'flat'), 'ladder_entry'] = True
    
    # Exit: transition from long to flat
    df.loc[(df['ladder_side'] == 'flat') & (df['ladder_side'].shift(1) == 'long'), 'ladder_exit'] = True
    
    return df


def run_ladder_baseline_backtest(symbol: str,
                                 timeframe: str,
                                 ladder_file: Path,
                                 output_dir: Path,
                                 initial_equity: float = 10000.0,
                                 transaction_cost_pct: float = 0.0,
                                 slippage_pct: float = 0.0) -> None:
    """
    Run Ladder baseline strategy backtest for one symbol×timeframe.
    
    Args:
        symbol: Symbol name
        timeframe: Timeframe
        ladder_file: Path to ladder_{symbol}_{timeframe}.parquet
        output_dir: Output directory for results
        initial_equity: Initial account equity
        transaction_cost_pct: Transaction cost (%)
        slippage_pct: Slippage (%)
    """
    # Load Ladder data
    df = pd.read_parquet(ladder_file)
    logger.info(f"Running Ladder baseline backtest: {symbol}_{timeframe} ({len(df)} bars)")
    
    # Generate Ladder baseline signals
    df = generate_ladder_baseline_signals(df)

    # Prepare for backtest engine
    # Map ladder signals to final signal columns (expected by backtest_engine)
    df['final_side'] = df['ladder_side']
    df['final_entry'] = df['ladder_entry']
    df['final_exit'] = df['ladder_exit']

    # Add position_size (default to 1.0 for baseline)
    df['position_size'] = 1.0
    
    # Run backtest using existing engine
    results = run_backtest(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
        initial_equity=initial_equity,
        transaction_cost_pct=transaction_cost_pct,
        slippage_pct=slippage_pct
    )
    
    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    
    trades_file = output_dir / f"trades_{symbol}_{timeframe}.csv"
    results['trades'].to_csv(trades_file, index=False)
    logger.info(f"  ✓ Saved trades: {trades_file.name}")
    
    equity_file = output_dir / f"equity_{symbol}_{timeframe}.csv"
    results['equity'].to_csv(equity_file, index=False)
    logger.info(f"  ✓ Saved equity: {equity_file.name}")
    
    summary_file = output_dir / f"summary_{symbol}_{timeframe}.csv"
    results['summary'].to_csv(summary_file, index=False)
    logger.info(f"  ✓ Saved summary: {summary_file.name}")
    
    # Log key metrics
    summary = results['summary'].iloc[0]
    logger.info(f"  Total Return: {summary['total_return_pct']:.2f}%")
    logger.info(f"  Max Drawdown: {summary['max_drawdown_pct']:.2f}%")
    logger.info(f"  Sharpe Ratio: {summary['sharpe_ratio']:.4f}")
    logger.info(f"  Trades: {summary['n_trades']}")


def run_all_ladder_baseline_backtests(symbols: List[str],
                                      timeframes: List[str],
                                      ladder_dir: Path,
                                      output_dir: Path) -> None:
    """
    Run Ladder baseline backtests for all symbol×timeframe combinations.
    
    Args:
        symbols: List of symbols
        timeframes: List of timeframes
        ladder_dir: Directory with ladder_{symbol}_{timeframe}.parquet files
        output_dir: Output directory for results
    """
    total = len(symbols) * len(timeframes)
    completed = 0
    failed = 0
    
    logger.info("="*80)
    logger.info(f"Running Ladder baseline backtests for {total} combinations")
    logger.info("="*80)
    
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                ladder_file = ladder_dir / f"ladder_{symbol}_{timeframe}.parquet"
                if not ladder_file.exists():
                    logger.warning(f"Ladder file not found: {ladder_file}")
                    failed += 1
                    continue
                
                run_ladder_baseline_backtest(symbol, timeframe, ladder_file, output_dir)
                completed += 1
                logger.info(f"Progress: {completed}/{total} ({completed/total*100:.1f}%)")
                
            except Exception as e:
                logger.error(f"Failed: {symbol}_{timeframe}")
                logger.error(f"  Error: {e}")
                failed += 1
    
    logger.info("="*80)
    logger.info("Ladder baseline backtests complete!")
    logger.info(f"  Completed: {completed}/{total}")
    logger.info(f"  Failed: {failed}")
    logger.info("="*80)


if __name__ == "__main__":
    # Project root
    root = Path(__file__).resolve().parents[2]

    # Paths
    ladder_dir = root / "data/ladder_features"
    output_dir = root / "results/ladder/baseline_strategy"

    # Configuration - ALL symbols × ALL timeframes
    symbols = ['BTCUSD', 'ETHUSD', 'EURUSD', 'USDJPY', 'XAGUSD', 'XAUUSD']
    timeframes = ['5min', '15min', '30min', '1h', '4h', '1d']

    # Run backtests
    run_all_ladder_baseline_backtests(symbols, timeframes, ladder_dir, output_dir)

