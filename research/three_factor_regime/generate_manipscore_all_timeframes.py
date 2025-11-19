#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate ManipScore for All Timeframes

This script computes ManipScore from raw OHLCV bars for all symbols and timeframes.
It uses the manipulation_score module from the market-manipulation project.

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

import sys
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


def add_market_manip_to_path():
    """Add market-manipulation project to Python path."""
    manip_path = Path.home() / "market-manimpulation-analysis"
    if manip_path.exists():
        sys.path.insert(0, str(manip_path))
        logger.info(f"Added to path: {manip_path}")
        return manip_path
    else:
        raise FileNotFoundError(f"Market-manipulation project not found at {manip_path}")


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
    filename = f"{symbol}_{file_tf}_merged_bars_with_ofi.csv"
    filepath = root / "data" / "raw_bars" / "bars_with_ofi" / filename
    
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return None
    
    logger.info(f"Loading: {filepath.name}")
    df = pd.read_csv(filepath)
    
    # Ensure timestamp column
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    else:
        raise ValueError(f"No timestamp column in {filepath}")
    
    # Ensure required OHLCV columns
    required = ['open', 'high', 'low', 'close', 'volume']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns {missing} in {filepath}")
    
    logger.info(f"  Loaded {len(df)} rows, date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    return df


def compute_manipscore_from_bars(bars: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ManipScore from OHLCV bars.
    
    This uses the manipulation_score module from market-manipulation project.
    """
    from src.factors.manipulation_score import compute_manipulation_score
    
    # Configuration for ManipScore calculation
    config = {
        'weights': {
            'price_volume': 0.25,
            'volume_spike': 0.25,
            'structure': 0.25,
            'wash_trade': 0.25
        },
        'normalize': True,
        'normalization_method': 'minmax',
        'smooth': False
    }
    
    logger.info("  Computing ManipScore...")
    
    # Compute manipulation score
    bars_with_score = compute_manipulation_score(bars.copy(), config=config)
    
    if 'manip_score' not in bars_with_score.columns:
        raise ValueError("ManipScore computation failed - no 'manip_score' column")
    
    # Extract ManipScore and create output DataFrame
    result = pd.DataFrame({
        'timestamp': bars['timestamp'],
        'ManipScore_raw': bars_with_score['manip_score'],
    })
    
    # Compute z-score standardization (rolling 50-period)
    lookback = 50
    mean = result['ManipScore_raw'].rolling(window=lookback, min_periods=lookback//2).mean()
    std = result['ManipScore_raw'].rolling(window=lookback, min_periods=lookback//2).std()
    result['ManipScore_z'] = (result['ManipScore_raw'] - mean) / (std + 1e-10)
    
    non_null = result['ManipScore_z'].notna().sum()
    logger.info(f"  ManipScore computed: {non_null} / {len(result)} ({non_null/len(result)*100:.1f}%)")
    
    return result


def save_manipscore_parquet(df: pd.DataFrame, symbol: str, timeframe: str, root: Path):
    """Save ManipScore to parquet format."""
    output_dir = root / "data" / "factors" / "manip"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Add metadata columns
    df_out = df.copy()
    df_out.insert(0, 'symbol', symbol)
    df_out.insert(1, 'timeframe', timeframe)
    
    output_file = output_dir / f"manip_{symbol}_{timeframe}.parquet"
    df_out.to_parquet(output_file, index=False)
    
    file_size = output_file.stat().st_size / 1024  # KB
    logger.info(f"  Saved: {output_file.name} ({file_size:.0f}K, {len(df_out)} rows)")


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("ManipScore Generation for All Timeframes")
    logger.info("=" * 80)
    
    # Setup paths
    root = get_project_root()
    logger.info(f"Project root: {root}")
    
    # Add market-manipulation to path
    try:
        manip_path = add_market_manip_to_path()
    except FileNotFoundError as e:
        logger.error(str(e))
        return
    
    # Define symbols and timeframes
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]
    
    total = len(symbols) * len(timeframes)
    success_count = 0
    fail_count = 0
    
    logger.info(f"Processing {total} combinations...")
    logger.info("")
    
    # Process each combination
    for symbol in symbols:
        for timeframe in timeframes:
            logger.info(f"Processing: {symbol} {timeframe}")
            
            try:
                # Load raw bars
                bars = load_raw_bars(symbol, timeframe, root)
                if bars is None:
                    fail_count += 1
                    continue
                
                # Compute ManipScore
                manip_df = compute_manipscore_from_bars(bars)
                
                # Save to parquet
                save_manipscore_parquet(manip_df, symbol, timeframe, root)
                
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
    logger.info("✓ ManipScore generation complete!")


if __name__ == "__main__":
    main()

