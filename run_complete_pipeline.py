#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Three-Factor Regime Research Pipeline

This script runs the complete analysis pipeline:
    1. Data merging (already done)
    2. Add regime features to merged data
    3. Single-factor decile analysis (ManipScore)
    4. Three-factor regime statistics
    5. Generate summary report

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

from pathlib import Path
import pandas as pd
import logging
import sys

# Import our modules
sys.path.insert(0, str(Path(__file__).parent / "research" / "three_factor_regime"))

from three_factor_regime_features import (
    add_three_factor_regime_features,
    RegimeFeatureConfig
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Return the umbrella project root."""
    return Path(__file__).parent


def add_regime_features_to_all_merged_files():
    """
    Load each merged file, add regime features, and save back.
    """
    logger.info("=" * 80)
    logger.info("Step 1: Adding Regime Features to All Merged Files")
    logger.info("=" * 80)
    logger.info("")
    
    root = get_project_root()
    merged_dir = root / "data" / "factors" / "merged_three_factor"
    
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]
    
    cfg = RegimeFeatureConfig()
    
    success_count = 0
    fail_count = 0
    
    for symbol in symbols:
        for timeframe in timeframes:
            merged_file = merged_dir / f"merged_{symbol}_{timeframe}.parquet"
            
            if not merged_file.exists():
                logger.warning(f"File not found: {merged_file.name}")
                fail_count += 1
                continue
            
            try:
                logger.info(f"Processing: {symbol} {timeframe}")
                
                # Load merged data
                df = pd.read_parquet(merged_file)
                logger.info(f"  Loaded {len(df):,} rows")
                
                # Add regime features
                df = add_three_factor_regime_features(df, cfg)
                
                # Save back
                df.to_parquet(merged_file, index=False)
                logger.info(f"  Saved with regime features")
                logger.info(f"  ✓ Success")
                success_count += 1
                
            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
            
            logger.info("")
    
    logger.info("=" * 80)
    logger.info(f"Successfully processed: {success_count}/{success_count + fail_count}")
    logger.info(f"Failed: {fail_count}/{success_count + fail_count}")
    logger.info("=" * 80)
    logger.info("")


def run_single_factor_analysis():
    """
    Run single-factor decile analysis for ManipScore.
    """
    logger.info("=" * 80)
    logger.info("Step 2: Running Single-Factor Decile Analysis (ManipScore)")
    logger.info("=" * 80)
    logger.info("")
    
    from single_factor_decile_analysis import run_single_factor_decile_analysis_for_manip
    
    root = get_project_root()
    merged_root = root / "data" / "factors" / "merged_three_factor"
    output_root = root / "results" / "three_factor_regime" / "single_factor_deciles"
    
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]
    horizons = [2, 5, 10]
    atr_col = "ATR"
    fwd_ret_cols = {2: "fut_ret_2", 5: "fut_ret_5", 10: "fut_ret_10"}
    
    run_single_factor_decile_analysis_for_manip(
        merged_root=merged_root,
        output_root=output_root,
        symbols=symbols,
        timeframes=timeframes,
        horizons=horizons,
        atr_col=atr_col,
        fwd_ret_cols=fwd_ret_cols,
    )


def run_regime_statistics():
    """
    Run three-factor regime statistics.
    """
    logger.info("=" * 80)
    logger.info("Step 3: Running Three-Factor Regime Statistics")
    logger.info("=" * 80)
    logger.info("")
    
    from three_factor_regime_stats import run_regime_stats_for_symbol_timeframe
    
    root = get_project_root()
    merged_root = root / "data" / "factors" / "merged_three_factor"
    output_root = root / "results" / "three_factor_regime" / "regime_stats"
    output_root.mkdir(parents=True, exist_ok=True)
    
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]
    horizons = [2, 5, 10]
    atr_col = "ATR"
    fwd_ret_cols = {2: "fut_ret_2", 5: "fut_ret_5", 10: "fut_ret_10"}
    
    for symbol in symbols:
        for timeframe in timeframes:
            merged_file = merged_root / f"merged_{symbol}_{timeframe}.parquet"
            
            try:
                run_regime_stats_for_symbol_timeframe(
                    merged_file=merged_file,
                    output_root=output_root,
                    symbol=symbol,
                    timeframe=timeframe,
                    horizons=horizons,
                    atr_col=atr_col,
                    fwd_ret_cols=fwd_ret_cols,
                )
            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
            
            logger.info("")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("THREE-FACTOR REGIME RESEARCH - COMPLETE PIPELINE")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Add regime features to all merged files
    add_regime_features_to_all_merged_files()
    
    # Step 2: Run single-factor analysis
    run_single_factor_analysis()
    
    # Step 3: Run regime statistics
    run_regime_statistics()
    
    logger.info("=" * 80)
    logger.info("✓ COMPLETE PIPELINE FINISHED!")
    logger.info("=" * 80)

