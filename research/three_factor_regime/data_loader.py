#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Data Loader for Three-Factor Regime Analysis

This module provides a unified, config-driven interface for loading and merging:
    - Raw bars (OHLCV, forward returns)
    - Factor 1: ManipScore
    - Factor 2: OFI (Order Flow Imbalance)
    - Factor 3: VolLiqScore

Design principles:
    - Modular and upgrade-friendly
    - Config-driven, not hard-coded
    - Reusable across different analysis phases
    - Handles missing data gracefully

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Return the umbrella project root."""
    return Path(__file__).parent.parent.parent


@dataclass
class BarDataConfig:
    """Configuration for bar data loading and merging."""
    root: Path
    symbols: List[str]
    timeframes: List[str]
    
    raw_bar_subdir: str = "data/raw_bars/bars_with_ofi"
    manip_subdir: str = "data/factors/manip"
    ofi_subdir: str = "data/factors/ofi"
    vol_liq_subdir: str = "data/factors/vol_liq"
    merged_subdir: str = "data/factors/merged_three_factor"
    
    atr_col: str = "ATR"
    
    fwd_ret_cols: Dict[int, str] = field(default_factory=lambda: {
        2: "fut_ret_2",
        5: "fut_ret_5",
        10: "fut_ret_10"
    })
    
    tf_map: Dict[str, str] = field(default_factory=lambda: {
        "5min": "5min",
        "15min": "15min",
        "30min": "30min",
        "1h": "1H",
        "4h": "4H",
        "1d": "1D"
    })


def load_raw_bars(symbol: str, timeframe: str, cfg: BarDataConfig) -> pd.DataFrame:
    """Load base bar data (OHLCV, forward returns) from CSV."""
    file_tf = cfg.tf_map.get(timeframe, timeframe)
    csv_path = cfg.root / cfg.raw_bar_subdir / f"{symbol}_{file_tf}_merged_bars_with_ofi.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Raw bars file not found: {csv_path}")
    
    logger.info(f"  Loading raw bars: {csv_path.name}")
    
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['symbol'] = symbol
    df['timeframe'] = timeframe
    
    base_cols = ['symbol', 'timeframe', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
    fwd_ret_cols = list(cfg.fwd_ret_cols.values())
    cols_to_keep = base_cols + [col for col in fwd_ret_cols if col in df.columns]
    df = df[cols_to_keep]
    
    logger.info(f"    Loaded {len(df):,} bars, date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    return df


def load_factor_manip(symbol: str, timeframe: str, cfg: BarDataConfig) -> Optional[pd.DataFrame]:
    """Load standardized ManipScore from parquet."""
    parquet_path = cfg.root / cfg.manip_subdir / f"manip_{symbol}_{timeframe}.parquet"
    
    if not parquet_path.exists():
        logger.warning(f"    ManipScore file not found: {parquet_path.name}")
        return None
    
    logger.info(f"  Loading ManipScore: {parquet_path.name}")
    df = pd.read_parquet(parquet_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    logger.info(f"    Loaded {len(df):,} rows")
    return df


def load_factor_ofi(symbol: str, timeframe: str, cfg: BarDataConfig) -> Optional[pd.DataFrame]:
    """Load standardized OFI factor from parquet."""
    parquet_path = cfg.root / cfg.ofi_subdir / f"ofi_{symbol}_{timeframe}.parquet"
    
    if not parquet_path.exists():
        logger.warning(f"    OFI file not found: {parquet_path.name}")
        return None
    
    logger.info(f"  Loading OFI: {parquet_path.name}")
    df = pd.read_parquet(parquet_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    logger.info(f"    Loaded {len(df):,} rows")
    return df


def load_factor_vol_liq(symbol: str, timeframe: str, cfg: BarDataConfig) -> Optional[pd.DataFrame]:
    """Load standardized VolLiqScore factor from parquet."""
    parquet_path = cfg.root / cfg.vol_liq_subdir / f"vol_liq_{symbol}_{timeframe}.parquet"

    if not parquet_path.exists():
        logger.warning(f"    VolLiqScore file not found: {parquet_path.name}")
        return None

    logger.info(f"  Loading VolLiqScore: {parquet_path.name}")
    df = pd.read_parquet(parquet_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    logger.info(f"    Loaded {len(df):,} rows")
    return df


def merge_factors_for_symbol_timeframe(
    symbol: str,
    timeframe: str,
    cfg: BarDataConfig,
    include_ofi: bool = True,
    include_vol_liq: bool = True,
) -> pd.DataFrame:
    """
    Merge raw bars + ManipScore + (optionally) OFI + VolLiqScore for a given (symbol, timeframe).

    - Start from raw bars as the base.
    - Left join factors on ['symbol', 'timeframe', 'timestamp'].
    - Keep all bars; factor columns can be NaN if missing.
    - Log row counts and non-null percentages for each factor.
    """
    logger.info(f"Merging factors for {symbol} {timeframe}")

    # Load raw bars (base)
    bars = load_raw_bars(symbol, timeframe, cfg)
    base_count = len(bars)

    # Load ManipScore
    manip = load_factor_manip(symbol, timeframe, cfg)
    if manip is not None:
        # Select only factor columns (exclude metadata that's already in bars)
        manip_cols = ['timestamp', 'ManipScore_raw', 'ManipScore_z']
        manip = manip[manip_cols]
        bars = bars.merge(manip, on='timestamp', how='left')
        non_null_pct = (bars['ManipScore_z'].notna().sum() / base_count) * 100
        logger.info(f"    ManipScore merged: {non_null_pct:.1f}% non-null")

    # Load OFI
    if include_ofi:
        ofi = load_factor_ofi(symbol, timeframe, cfg)
        if ofi is not None:
            ofi_cols = ['timestamp', 'OFI_raw', 'OFI_z', 'OFI_abs_z']
            ofi = ofi[ofi_cols]
            bars = bars.merge(ofi, on='timestamp', how='left')
            non_null_pct = (bars['OFI_z'].notna().sum() / base_count) * 100
            logger.info(f"    OFI merged: {non_null_pct:.1f}% non-null")

    # Load VolLiqScore
    if include_vol_liq:
        vol_liq = load_factor_vol_liq(symbol, timeframe, cfg)
        if vol_liq is not None:
            vol_liq_cols = ['timestamp', 'z_vol', 'ATR', 'z_liq_stress', 'VolLiqScore']
            vol_liq = vol_liq[vol_liq_cols]
            bars = bars.merge(vol_liq, on='timestamp', how='left')
            non_null_pct = (bars['VolLiqScore'].notna().sum() / base_count) * 100
            logger.info(f"    VolLiqScore merged: {non_null_pct:.1f}% non-null")

    logger.info(f"    Final merged data: {len(bars):,} rows, {len(bars.columns)} columns")

    return bars


def save_merged_three_factors(cfg: BarDataConfig) -> None:
    """
    For each (symbol, timeframe) in cfg:
      - load & merge
      - save to cfg.merged_subdir / f"merged_{symbol}_{timeframe}.parquet"
    """
    logger.info("=" * 80)
    logger.info("Merging Three Factors for All Symbol×Timeframe Combinations")
    logger.info("=" * 80)
    logger.info(f"Symbols: {cfg.symbols}")
    logger.info(f"Timeframes: {cfg.timeframes}")
    logger.info("")

    # Create output directory
    output_dir = cfg.root / cfg.merged_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(cfg.symbols) * len(cfg.timeframes)
    success_count = 0
    fail_count = 0

    for symbol in cfg.symbols:
        for timeframe in cfg.timeframes:
            try:
                # Merge factors
                merged_df = merge_factors_for_symbol_timeframe(symbol, timeframe, cfg)

                # Save to parquet
                output_file = output_dir / f"merged_{symbol}_{timeframe}.parquet"
                merged_df.to_parquet(output_file, index=False)

                file_size = output_file.stat().st_size
                size_str = f"{file_size / 1024:.0f}K" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f}M"

                logger.info(f"  Saved: {output_file.name} ({size_str}, {len(merged_df):,} rows)")
                logger.info(f"  ✓ Success")
                success_count += 1

            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1

            logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info(f"Successfully processed: {success_count}/{total}")
    logger.info(f"Failed: {fail_count}/{total}")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✓ Three-factor merge complete!")


if __name__ == "__main__":
    root = get_project_root()

    # All 6 symbols and 6 timeframes
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]

    cfg = BarDataConfig(
        root=root,
        symbols=symbols,
        timeframes=timeframes
    )

    save_merged_three_factors(cfg)

