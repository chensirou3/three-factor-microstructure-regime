#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Tick Data and Generate All Factors

This script:
1. Converts tick data to OHLCV bars for all timeframes
2. Computes OFI (Order Flow Imbalance)
3. Generates ManipScore (Factor 1)
4. Generates VolLiqScore (Factor 3)

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_tick_files(symbol: str, root: Path) -> list:
    """Get list of tick data files for a symbol."""
    tick_dir = root / "data" / "tick_data" / f"symbol={symbol}"

    if not tick_dir.exists():
        logger.error(f"Tick data directory not found: {tick_dir}")
        return []

    # Find all parquet files
    parquet_files = sorted(list(tick_dir.glob("**/*.parquet")))

    if not parquet_files:
        logger.error(f"No parquet files found in {tick_dir}")
        return []

    logger.info(f"Found {len(parquet_files)} parquet files for {symbol}")

    return parquet_files


def resample_files_to_bars(tick_files: list, timeframe: str) -> pd.DataFrame:
    """Resample tick data files to OHLCV bars (memory efficient)."""
    # Define resampling rule
    resample_rules = {
        '5min': '5T',
        '15min': '15T',
        '30min': '30T',
        '1h': '1H',
        '4h': '4H',
        '1d': '1D'
    }

    rule = resample_rules.get(timeframe)
    if rule is None:
        raise ValueError(f"Unknown timeframe: {timeframe}")

    all_bars = []

    # Process files in batches to save memory
    for file in tick_files:
        try:
            # Load one file at a time
            ticks = pd.read_parquet(file)

            # Find timestamp column (could be 'timestamp', 'time', 'datetime', 'ts', etc.)
            timestamp_col = None
            for col in ['timestamp', 'time', 'datetime', 'ts', 'date']:
                if col in ticks.columns:
                    timestamp_col = col
                    break

            if timestamp_col is None:
                logger.warning(f"Failed to process {file.name}: No timestamp column found. Columns: {ticks.columns.tolist()}")
                continue

            # Rename to 'timestamp' if needed
            if timestamp_col != 'timestamp':
                ticks = ticks.rename(columns={timestamp_col: 'timestamp'})

            if not pd.api.types.is_datetime64_any_dtype(ticks['timestamp']):
                ticks['timestamp'] = pd.to_datetime(ticks['timestamp'])

            # Set timestamp as index
            ticks = ticks.set_index('timestamp')

            # Determine price column
            if 'price' in ticks.columns:
                price_col = 'price'
            elif 'close' in ticks.columns:
                price_col = 'close'
            elif 'last' in ticks.columns:
                price_col = 'last'
            elif 'bid' in ticks.columns and 'ask' in ticks.columns:
                # Use mid price if we have bid/ask
                ticks['price'] = (ticks['bid'] + ticks['ask']) / 2
                price_col = 'price'
            else:
                logger.warning(f"Failed to process {file.name}: No price column found. Columns: {ticks.columns.tolist()}")
                continue

            # Resample this file
            bars = pd.DataFrame()
            bars['open'] = ticks[price_col].resample(rule).first()
            bars['high'] = ticks[price_col].resample(rule).max()
            bars['low'] = ticks[price_col].resample(rule).min()
            bars['close'] = ticks[price_col].resample(rule).last()

            # Volume
            if 'volume' in ticks.columns:
                bars['volume'] = ticks['volume'].resample(rule).sum()
            elif 'size' in ticks.columns:
                bars['volume'] = ticks['size'].resample(rule).sum()
            elif 'bid_size' in ticks.columns and 'ask_size' in ticks.columns:
                # Use average of bid/ask size as proxy for volume
                ticks['volume'] = (ticks['bid_size'] + ticks['ask_size']) / 2
                bars['volume'] = ticks['volume'].resample(rule).sum()
            else:
                # Use tick count as proxy for volume
                bars['volume'] = ticks.resample(rule).size()

            # Reset index
            bars = bars.reset_index()

            # Remove rows with NaN
            bars = bars.dropna()

            if len(bars) > 0:
                all_bars.append(bars)

        except Exception as e:
            logger.warning(f"Failed to process {file.name}: {e}")

    if not all_bars:
        logger.error("No bars generated")
        return None

    # Concatenate all bars
    final_bars = pd.concat(all_bars, ignore_index=True)

    # Sort by timestamp
    final_bars = final_bars.sort_values('timestamp').reset_index(drop=True)

    # Remove duplicates (keep first)
    final_bars = final_bars.drop_duplicates(subset=['timestamp'], keep='first')

    logger.info(f"  Resampled to {len(final_bars):,} bars ({timeframe})")

    return final_bars


def compute_ofi(bars: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Order Flow Imbalance (OFI).
    Simplified version - assumes buy/sell volumes are proportional to price changes.
    """
    # Simple OFI approximation based on price changes
    price_change = bars['close'].diff()
    
    # Estimate buy/sell volumes
    bars['OFI_buy_vol'] = bars['volume'] * (price_change > 0).astype(float)
    bars['OFI_sell_vol'] = bars['volume'] * (price_change < 0).astype(float)
    bars['OFI_tot_vol'] = bars['volume']
    
    # Raw OFI
    bars['OFI_raw'] = bars['OFI_buy_vol'] - bars['OFI_sell_vol']
    
    # Standardize OFI
    lookback = 50
    bars['OFI_mean'] = bars['OFI_raw'].rolling(window=lookback, min_periods=lookback//2).mean()
    bars['OFI_std'] = bars['OFI_raw'].rolling(window=lookback, min_periods=lookback//2).std()
    bars['OFI_z'] = (bars['OFI_raw'] - bars['OFI_mean']) / (bars['OFI_std'] + 1e-10)
    
    # Compute forward returns
    for horizon in [2, 5, 10]:
        bars[f'fut_ret_{horizon}'] = bars['close'].pct_change(horizon).shift(-horizon)

    return bars


def save_bars_with_ofi(bars: pd.DataFrame, symbol: str, timeframe: str, root: Path):
    """Save OHLCV bars with OFI to CSV."""
    # Map timeframe to file naming convention
    tf_map = {
        "5min": "5min",
        "15min": "15min",
        "30min": "30min",
        "1h": "1H",
        "4h": "4H",
        "1d": "1D"
    }
    file_tf = tf_map.get(timeframe, timeframe)

    # Create output directory
    output_dir = root / "data" / "raw_bars" / "bars_with_ofi"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save to CSV
    output_file = output_dir / f"{symbol}_{file_tf}_merged_bars_with_ofi.csv"
    bars.to_csv(output_file, index=False)

    file_size = output_file.stat().st_size
    size_str = f"{file_size / 1024:.0f}K" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f}M"

    logger.info(f"  Saved: {output_file.name} ({size_str}, {len(bars)} rows)")


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("Process Tick Data and Generate All Factors")
    logger.info("=" * 80)
    logger.info("")

    # Setup paths
    root = get_project_root()
    logger.info(f"Project root: {root}")
    logger.info("")

    # Define symbols and timeframes
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]

    # Process each symbol
    for symbol in symbols:
        logger.info("=" * 80)
        logger.info(f"Processing {symbol}")
        logger.info("=" * 80)
        logger.info("")

        # Get tick files
        tick_files = get_tick_files(symbol, root)

        if not tick_files:
            logger.error(f"No tick files found for {symbol}, skipping...")
            logger.info("")
            continue

        # Process each timeframe
        for timeframe in timeframes:
            logger.info(f"Processing {symbol} {timeframe}...")

            try:
                # Resample to bars (memory efficient)
                bars = resample_files_to_bars(tick_files, timeframe)

                if bars is None:
                    logger.error(f"  ✗ Failed to generate bars")
                    continue

                # Compute OFI
                bars = compute_ofi(bars)

                # Save bars with OFI
                save_bars_with_ofi(bars, symbol, timeframe, root)

                logger.info(f"  ✓ {symbol} {timeframe} complete")
                logger.info("")

            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
                logger.info("")

    logger.info("=" * 80)
    logger.info("Tick data processing complete!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Run: python3 research/three_factor_regime/generate_volliqscore_all_timeframes.py")
    logger.info("2. Run: python3 research/three_factor_regime/generate_manipscore_all_timeframes.py")
    logger.info("")


if __name__ == "__main__":
    main()

