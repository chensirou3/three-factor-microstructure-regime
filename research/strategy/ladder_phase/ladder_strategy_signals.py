"""
Ladder Strategy Signal Generator

Generates trading signals based on Ladder trend indicator.
Similar to baseline_strategy.py but uses Ladder instead of EMA crossover.
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_ladder_signals(df: pd.DataFrame,
                            fast_len: int = 25,
                            slow_len: int = 90) -> pd.DataFrame:
    """
    Generate Ladder-based trading signals.
    
    This is the Ladder equivalent of generate_baseline_signals() from baseline_strategy.py.
    
    Strategy logic:
      - Long when upTrend == True (close > fastU AND close > slowU)
      - Flat otherwise
      - No short positions (long-only)
    
    Args:
        df: DataFrame with OHLCV data
        fast_len: Fast EMA band length (default: 25)
        slow_len: Slow EMA band length (default: 90)
    
    Returns:
        DataFrame with added columns:
          - fastU, fastL: Fast EMA bands
          - slowU, slowL: Slow EMA bands
          - upTrend, downTrend: Boolean trend flags
          - ladder_state: +1 (up), -1 (down), 0 (neutral)
          - signal_side: 'long' or 'flat'
          - entry_signal: bool (entry signal)
          - exit_signal: bool (exit signal)
    """
    df = df.copy()
    
    # Compute Ladder bands
    df['fastU'] = df['high'].ewm(span=fast_len, adjust=False).mean()
    df['fastL'] = df['low'].ewm(span=fast_len, adjust=False).mean()
    df['slowU'] = df['high'].ewm(span=slow_len, adjust=False).mean()
    df['slowL'] = df['low'].ewm(span=slow_len, adjust=False).mean()
    
    # Compute trend conditions
    df['upTrend'] = (df['close'] > df['fastU']) & (df['close'] > df['slowU'])
    df['downTrend'] = (df['close'] < df['fastL']) & (df['close'] < df['slowL'])
    
    # Encode ladder state
    df['ladder_state'] = 0
    df.loc[df['upTrend'], 'ladder_state'] = 1
    df.loc[df['downTrend'], 'ladder_state'] = -1
    
    # Generate trading signals (long-only)
    df['signal_side'] = 'flat'
    df.loc[df['upTrend'], 'signal_side'] = 'long'
    
    # Detect entry/exit signals
    df['entry_signal'] = False
    df['exit_signal'] = False
    
    # Entry: transition from flat to long
    df.loc[(df['signal_side'] == 'long') & (df['signal_side'].shift(1) == 'flat'), 'entry_signal'] = True
    
    # Exit: transition from long to flat
    df.loc[(df['signal_side'] == 'flat') & (df['signal_side'].shift(1) == 'long'), 'exit_signal'] = True
    
    return df


def load_ladder_data_and_generate_signals(symbol: str,
                                          timeframe: str,
                                          ladder_dir: Path,
                                          fast_len: int = 25,
                                          slow_len: int = 90) -> pd.DataFrame:
    """
    Load Ladder-enriched data and generate trading signals.
    
    Args:
        symbol: Symbol name
        timeframe: Timeframe
        ladder_dir: Directory with ladder_{symbol}_{timeframe}.parquet files
        fast_len: Fast EMA band length
        slow_len: Slow EMA band length
    
    Returns:
        DataFrame with Ladder features and trading signals
    """
    # Load Ladder data
    ladder_file = ladder_dir / f"ladder_{symbol}_{timeframe}.parquet"
    
    if not ladder_file.exists():
        raise FileNotFoundError(f"Ladder file not found: {ladder_file}")
    
    df = pd.read_parquet(ladder_file)
    
    # Generate signals (Ladder features already exist, just add signal columns)
    df['signal_side'] = 'flat'
    df.loc[df['upTrend'], 'signal_side'] = 'long'
    
    df['entry_signal'] = False
    df['exit_signal'] = False
    
    df.loc[(df['signal_side'] == 'long') & (df['signal_side'].shift(1) == 'flat'), 'entry_signal'] = True
    df.loc[(df['signal_side'] == 'flat') & (df['signal_side'].shift(1) == 'long'), 'exit_signal'] = True
    
    return df


if __name__ == "__main__":
    # Test on BTCUSD 4h
    root = Path(__file__).resolve().parents[3]
    ladder_dir = root / "data/ladder_features"
    
    df = load_ladder_data_and_generate_signals('BTCUSD', '4h', ladder_dir)
    
    logger.info(f"Loaded {len(df)} bars")
    logger.info(f"Columns: {df.columns.tolist()}")
    logger.info(f"Entry signals: {df['entry_signal'].sum()}")
    logger.info(f"Exit signals: {df['exit_signal'].sum()}")
    logger.info(f"upTrend bars: {df['upTrend'].sum()} ({df['upTrend'].sum()/len(df)*100:.1f}%)")

