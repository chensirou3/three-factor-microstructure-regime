#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standardize OFI (Order Flow Imbalance) Factor

This script extracts OFI data from raw bars CSV files and standardizes them
into per-bar parquet format for the three-factor regime analysis.

Source:
    - Raw bars with OFI: data/raw_bars/bars_with_ofi/{symbol}_{timeframe}_merged_bars_with_ofi.csv
    - Contains: OFI_raw, OFI_mean, OFI_std, OFI_z

Target schema per bar:
    - symbol: str
    - timeframe: str
    - timestamp: datetime64[ns, UTC]
    - OFI_raw: float (buy_vol - sell_vol)
    - OFI_z: float (z-score within symbol×timeframe)
    - OFI_abs_z: float (|OFI_z| for pressure strength)

Output:
    - data/factors/ofi/ofi_{symbol}_{timeframe}.parquet

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@dataclass
class OFIStandardizationConfig:
    """Configuration for OFI standardization."""
    root: Path
    symbols: List[str]
    timeframes: List[str]
    raw_bar_subdir: str = "data/raw_bars/bars_with_ofi"
    output_subdir: str = "data/factors/ofi"
    
    # Timeframe mapping for file names
    tf_map: dict = None
    
    def __post_init__(self):
        if self.tf_map is None:
            self.tf_map = {
                "5min": "5min",
                "15min": "15min",
                "30min": "30min",
                "1h": "1H",
                "4h": "4H",
                "1d": "1D"
            }


def load_raw_ofi_from_bars(symbol: str, timeframe: str, cfg: OFIStandardizationConfig) -> pd.DataFrame:
    """
    Load OFI data from raw bars CSV file.
    
    Args:
        symbol: Symbol name (e.g., 'BTCUSD')
        timeframe: Timeframe (e.g., '5min', '1h')
        cfg: Configuration object
        
    Returns:
        DataFrame with OFI columns from raw bars
    """
    # Map timeframe to file naming convention
    file_tf = cfg.tf_map.get(timeframe, timeframe)
    
    # Construct file path
    csv_path = cfg.root / cfg.raw_bar_subdir / f"{symbol}_{file_tf}_merged_bars_with_ofi.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Raw bars file not found: {csv_path}")
    
    logger.info(f"Loading: {csv_path.name}")
    
    # Load CSV with relevant columns
    df = pd.read_csv(csv_path)
    
    # Check required columns
    required_cols = ['timestamp', 'OFI_raw', 'OFI_z']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return df


def standardize_ofi_df(df: pd.DataFrame, symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Standardize OFI DataFrame to target schema.
    
    Args:
        df: Raw DataFrame with OFI columns
        symbol: Symbol name
        timeframe: Timeframe
        
    Returns:
        Standardized DataFrame with schema:
            symbol, timeframe, timestamp, OFI_raw, OFI_z, OFI_abs_z
    """
    # Create standardized DataFrame
    std_df = pd.DataFrame()
    
    # Add metadata
    std_df['symbol'] = symbol
    std_df['timeframe'] = timeframe
    
    # Convert timestamp to datetime
    std_df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    
    # Add OFI factors
    std_df['OFI_raw'] = df['OFI_raw']
    std_df['OFI_z'] = df['OFI_z']
    std_df['OFI_abs_z'] = df['OFI_z'].abs()
    
    # Sort by timestamp
    std_df = std_df.sort_values('timestamp').reset_index(drop=True)
    
    logger.info(f"  Standardized: {len(std_df):,} rows, "
                f"date range: {std_df['timestamp'].min()} to {std_df['timestamp'].max()}")
    
    return std_df


def save_standardized_ofi(df: pd.DataFrame, symbol: str, timeframe: str, cfg: OFIStandardizationConfig) -> None:
    """Save standardized OFI to parquet."""
    output_dir = cfg.root / cfg.output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"ofi_{symbol}_{timeframe}.parquet"
    df.to_parquet(output_file, index=False)
    
    file_size = output_file.stat().st_size
    size_str = f"{file_size / 1024:.0f}K" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f}M"
    
    logger.info(f"  Saved: {output_file.name} ({size_str}, {len(df):,} rows)")


def run_standardization(cfg: OFIStandardizationConfig) -> None:
    """
    Run OFI standardization for all (symbol, timeframe) combinations.

    For each combination:
        1) Load raw OFI from bars CSV
        2) Standardize to target schema
        3) Save to data/factors/ofi/ofi_{symbol}_{timeframe}.parquet
    """
    logger.info("=" * 80)
    logger.info("OFI Factor Standardization")
    logger.info("=" * 80)
    logger.info(f"Symbols: {cfg.symbols}")
    logger.info(f"Timeframes: {cfg.timeframes}")
    logger.info("")

    total = len(cfg.symbols) * len(cfg.timeframes)
    success_count = 0
    fail_count = 0

    for symbol in cfg.symbols:
        for timeframe in cfg.timeframes:
            logger.info(f"Processing: {symbol} {timeframe}")

            try:
                # Load raw OFI from bars
                df = load_raw_ofi_from_bars(symbol, timeframe, cfg)

                # Standardize
                std_df = standardize_ofi_df(df, symbol, timeframe)

                # Save
                save_standardized_ofi(std_df, symbol, timeframe, cfg)

                success_count += 1
                logger.info(f"  ✓ Success")

            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                fail_count += 1

            logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info(f"Successfully processed: {success_count}/{total}")
    logger.info(f"Failed: {fail_count}/{total}")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✓ OFI standardization complete!")


if __name__ == "__main__":
    root = get_project_root()

    # All 6 symbols and 6 timeframes
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]

    cfg = OFIStandardizationConfig(
        root=root,
        symbols=symbols,
        timeframes=timeframes
    )

    run_standardization(cfg)

