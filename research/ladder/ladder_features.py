"""
Ladder Trend Indicator - Feature Computation

Computes Ladder EMA bands and trend states for all symbol×timeframe combinations.

Ladder Bands:
  - fastU = EMA(high, 25), fastL = EMA(low, 25)
  - slowU = EMA(high, 90), slowL = EMA(low, 90)

Trend States:
  - upTrend   = (close > fastU) & (close > slowU)
  - downTrend = (close < fastL) & (close < slowL)
  - ladder_state: +1 (up), -1 (down), 0 (neutral)
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List
import pandas as pd
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class LadderConfig:
    """Configuration for Ladder feature generation."""
    root: Path
    symbols: List[str]
    timeframes: List[str]
    fast_len: int = 25
    slow_len: int = 90
    merged_dir: str = "data/factors/merged_three_factor"
    output_dir: str = "data/ladder_features"


def compute_ladder_bands(df: pd.DataFrame,
                         fast_len: int = 25,
                         slow_len: int = 90) -> pd.DataFrame:
    """
    Compute Ladder EMA bands and trend states.
    
    Args:
        df: DataFrame with columns: high, low, close, timestamp
        fast_len: Fast EMA period (default: 25)
        slow_len: Slow EMA period (default: 90)
    
    Returns:
        DataFrame with added columns:
          - fastU, fastL: Fast EMA bands
          - slowU, slowL: Slow EMA bands
          - upTrend, downTrend: Boolean trend flags
          - ladder_state: +1 (up), -1 (down), 0 (neutral)
    """
    df = df.copy()
    
    # Compute fast bands (25-period EMA on high/low)
    df['fastU'] = df['high'].ewm(span=fast_len, adjust=False).mean()
    df['fastL'] = df['low'].ewm(span=fast_len, adjust=False).mean()
    
    # Compute slow bands (90-period EMA on high/low)
    df['slowU'] = df['high'].ewm(span=slow_len, adjust=False).mean()
    df['slowL'] = df['low'].ewm(span=slow_len, adjust=False).mean()
    
    # Compute trend conditions
    df['upTrend'] = (df['close'] > df['fastU']) & (df['close'] > df['slowU'])
    df['downTrend'] = (df['close'] < df['fastL']) & (df['close'] < df['slowL'])
    
    # Encode ladder state: +1 (up), -1 (down), 0 (neutral)
    df['ladder_state'] = 0
    df.loc[df['upTrend'], 'ladder_state'] = 1
    df.loc[df['downTrend'], 'ladder_state'] = -1
    
    return df


def generate_ladder_features_for_all(cfg: LadderConfig) -> None:
    """
    Generate Ladder features for all symbol×timeframe combinations.
    
    For each (symbol, timeframe):
      1. Load merged_{symbol}_{timeframe}.parquet
      2. Compute Ladder bands and states
      3. Save to output_dir/ladder_{symbol}_{timeframe}.parquet
    
    Args:
        cfg: LadderConfig with paths and parameters
    """
    merged_dir = cfg.root / cfg.merged_dir
    output_dir = cfg.root / cfg.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total = len(cfg.symbols) * len(cfg.timeframes)
    completed = 0
    failed = 0
    
    logger.info("="*80)
    logger.info(f"Generating Ladder features for {total} combinations")
    logger.info(f"  Symbols: {cfg.symbols}")
    logger.info(f"  Timeframes: {cfg.timeframes}")
    logger.info(f"  Fast length: {cfg.fast_len}")
    logger.info(f"  Slow length: {cfg.slow_len}")
    logger.info("="*80)
    
    for symbol in cfg.symbols:
        for timeframe in cfg.timeframes:
            try:
                # Load merged data
                merged_file = merged_dir / f"merged_{symbol}_{timeframe}.parquet"
                if not merged_file.exists():
                    logger.warning(f"Merged file not found: {merged_file}")
                    failed += 1
                    continue
                
                df = pd.read_parquet(merged_file)
                logger.info(f"Processing {symbol}_{timeframe}: {len(df)} bars")
                
                # Compute Ladder features
                df = compute_ladder_bands(df, cfg.fast_len, cfg.slow_len)
                
                # Save to output
                output_file = output_dir / f"ladder_{symbol}_{timeframe}.parquet"
                df.to_parquet(output_file, index=False)
                
                completed += 1
                logger.info(f"  ✓ Saved: {output_file.name}")
                logger.info(f"  Progress: {completed}/{total} ({completed/total*100:.1f}%)")
                
            except Exception as e:
                logger.error(f"Failed: {symbol}_{timeframe}")
                logger.error(f"  Error: {e}")
                failed += 1
    
    logger.info("="*80)
    logger.info("Ladder feature generation complete!")
    logger.info(f"  Completed: {completed}/{total}")
    logger.info(f"  Failed: {failed}")
    logger.info("="*80)


if __name__ == "__main__":
    # Project root
    root = Path(__file__).resolve().parents[2]

    # Configuration - ALL symbols × ALL timeframes
    cfg = LadderConfig(
        root=root,
        symbols=['BTCUSD', 'ETHUSD', 'EURUSD', 'USDJPY', 'XAGUSD', 'XAUUSD'],
        timeframes=['5min', '15min', '30min', '1h', '4h', '1d'],
        fast_len=25,
        slow_len=90
    )

    # Generate Ladder features
    generate_ladder_features_for_all(cfg)

