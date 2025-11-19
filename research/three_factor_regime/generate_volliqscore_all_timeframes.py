#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate VolLiqScore for All Timeframes

This script computes VolLiqScore from raw OHLCV bars for all symbols and timeframes.
VolLiqScore = 0.5 × z_vol + 0.5 × z_liq_stress

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def load_raw_bars(symbol: str, timeframe: str, root: Path) -> pd.DataFrame:
    """Load raw OHLCV bars from CSV."""
    # Map internal timeframe to file naming convention
    tf_map = {
        "5min": "5min",
        "15min": "15min",
        "30min": "30min",
        "1h": "1H",
        "4h": "4H",
        "1d": "1D"
    }
    file_tf = tf_map.get(timeframe, timeframe)
    
    # Construct file path
    bars_dir = root / "data" / "raw_bars" / "bars_with_ofi"
    file_path = bars_dir / f"{symbol}_{file_tf}_merged_bars_with_ofi.csv"
    
    if not file_path.exists():
        logger.error(f"  File not found: {file_path}")
        return None
    
    # Load CSV
    df = pd.read_csv(file_path)
    logger.info(f"  Loaded {len(df)} rows, date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    return df


def compute_volliqscore(bars: pd.DataFrame) -> pd.DataFrame:
    """
    Compute VolLiqScore from OHLCV bars.
    
    VolLiqScore = 0.5 × z_vol + 0.5 × z_liq_stress
    where:
    - z_vol: Z-score of log(volume) with 50-period rolling window
    - z_liq_stress: Z-score of (range/ATR) with 50-period rolling window
    - ATR: 50-period rolling mean of True Range
    """
    lookback = 50
    
    # Compute log volume
    log_vol = np.log(bars['volume'] + 1)
    
    # Z-score of log volume
    vol_mean = log_vol.rolling(window=lookback, min_periods=lookback//2).mean()
    vol_std = log_vol.rolling(window=lookback, min_periods=lookback//2).std()
    z_vol = (log_vol - vol_mean) / (vol_std + 1e-10)
    
    # Compute True Range
    high_low = bars['high'] - bars['low']
    high_close = np.abs(bars['high'] - bars['close'].shift(1))
    low_close = np.abs(bars['low'] - bars['close'].shift(1))
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Compute ATR (50-period rolling mean of True Range)
    ATR = true_range.rolling(window=lookback, min_periods=lookback//2).mean()
    
    # Compute liquidity stress: range / ATR
    bar_range = bars['high'] - bars['low']
    liq_stress = bar_range / (ATR + 1e-10)
    
    # Z-score of liquidity stress
    liq_mean = liq_stress.rolling(window=lookback, min_periods=lookback//2).mean()
    liq_std = liq_stress.rolling(window=lookback, min_periods=lookback//2).std()
    z_liq_stress = (liq_stress - liq_mean) / (liq_std + 1e-10)
    
    # Compute VolLiqScore
    VolLiqScore = 0.5 * z_vol + 0.5 * z_liq_stress
    
    # Create result DataFrame
    result = pd.DataFrame({
        'timestamp': bars['timestamp'],
        'z_vol': z_vol,
        'ATR': ATR,
        'z_liq_stress': z_liq_stress,
        'VolLiqScore': VolLiqScore
    })
    
    return result


def save_volliqscore_parquet(df: pd.DataFrame, symbol: str, timeframe: str, root: Path):
    """Save VolLiqScore to parquet file."""
    # Add metadata columns
    df.insert(0, 'symbol', symbol)
    df.insert(1, 'timeframe', timeframe)
    
    # Create output directory
    output_dir = root / "data" / "factors" / "vol_liq"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to parquet
    output_file = output_dir / f"vol_liq_{symbol}_{timeframe}.parquet"
    df.to_parquet(output_file, index=False)
    
    # Get file size
    file_size = output_file.stat().st_size
    size_str = f"{file_size / 1024:.0f}K" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f}M"
    
    # Count non-null VolLiqScore values
    valid_count = df['VolLiqScore'].notna().sum()
    total_count = len(df)
    coverage = valid_count / total_count * 100 if total_count > 0 else 0
    
    logger.info(f"  VolLiqScore computed: {valid_count} / {total_count} ({coverage:.1f}%)")
    logger.info(f"  Saved: {output_file.name} ({size_str}, {total_count} rows)")


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("VolLiqScore Generation for All Timeframes")
    logger.info("=" * 80)

    # Setup paths
    root = get_project_root()
    logger.info(f"Project root: {root}")

    # Define symbols and timeframes
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]

    # Process each combination
    success_count = 0
    fail_count = 0

    for symbol in symbols:
        for timeframe in timeframes:
            logger.info("")
            logger.info(f"Processing: {symbol} {timeframe}")

            try:
                # Load raw bars
                logger.info(f"Loading: {symbol}_{timeframe}_merged_bars_with_ofi.csv")
                bars = load_raw_bars(symbol, timeframe, root)

                if bars is None:
                    fail_count += 1
                    continue

                # Compute VolLiqScore
                logger.info(f"  Computing VolLiqScore...")
                volliq_df = compute_volliqscore(bars)

                # Save to parquet
                save_volliqscore_parquet(volliq_df, symbol, timeframe, root)

                success_count += 1
                logger.info(f"  ✓ Success")

            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1

            logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Failed: {fail_count}")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✓ VolLiqScore generation complete!")


if __name__ == "__main__":
    main()

