#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Three-Factor Regime Statistics

This module computes risk-focused statistics for different regime classifications:
    1. High vs low pressure comparison
    2. 2×2×2 box statistics (8 boxes)
    3. RiskScore decile statistics

Focus: Risk & tail behavior
    - E(|ret|), not E(ret)
    - Tail probabilities (2R, 3R)
    - Volatility and extreme events

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

from pathlib import Path
from typing import List, Dict
import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Return the umbrella project root."""
    return Path(__file__).parent.parent.parent


def compute_high_vs_low_pressure_stats(
    df: pd.DataFrame,
    horizons: List[int],
    atr_col: str,
    symbol: str,
    timeframe: str,
    fwd_ret_cols: Dict[int, str],
) -> pd.DataFrame:
    """
    Compute statistics for high_pressure vs low_pressure regimes.
    
    For each regime (high/low) and horizon H:
        - count, share
        - mean_ret, mean_abs_ret
        - tail_prob_2R, tail_prob_3R
    """
    results = []
    
    for regime_type in ['high_pressure', 'low_pressure']:
        if regime_type not in df.columns:
            continue
        
        regime_df = df[df[regime_type] == True]
        count = len(regime_df)
        share = count / len(df) if len(df) > 0 else 0
        
        for H in horizons:
            ret_col = fwd_ret_cols.get(H)
            if ret_col is None or ret_col not in df.columns:
                continue
            
            # Mean return and mean absolute return
            mean_ret = regime_df[ret_col].mean()
            mean_abs_ret = regime_df[ret_col].abs().mean()
            
            # Tail probabilities
            if atr_col in regime_df.columns:
                abs_ret = regime_df[ret_col].abs()
                atr = regime_df[atr_col]
                tail_2R = (abs_ret > 2 * atr).mean()
                tail_3R = (abs_ret > 3 * atr).mean()
            else:
                tail_2R = np.nan
                tail_3R = np.nan
            
            results.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'regime_type': regime_type,
                'H': H,
                'count': count,
                'share': share,
                'mean_ret': mean_ret,
                'mean_abs_ret': mean_abs_ret,
                'tail_prob_2R': tail_2R,
                'tail_prob_3R': tail_3R,
            })
    
    return pd.DataFrame(results)


def compute_box_stats(
    df: pd.DataFrame,
    horizons: List[int],
    atr_col: str,
    symbol: str,
    timeframe: str,
    fwd_ret_cols: Dict[int, str],
) -> pd.DataFrame:
    """
    Compute statistics for each three_factor_box.
    
    For each box and horizon H:
        - count, share
        - mean_ret, median_ret, p10, p25, p75, p90
        - mean_abs_ret
        - tail_prob_2R, tail_prob_3R
    """
    results = []
    
    if 'three_factor_box' not in df.columns:
        logger.warning("three_factor_box column not found")
        return pd.DataFrame()
    
    boxes = df['three_factor_box'].unique()
    
    for box in boxes:
        box_df = df[df['three_factor_box'] == box]
        count = len(box_df)
        share = count / len(df) if len(df) > 0 else 0
        
        for H in horizons:
            ret_col = fwd_ret_cols.get(H)
            if ret_col is None or ret_col not in df.columns:
                continue
            
            # Return statistics
            returns = box_df[ret_col]
            mean_ret = returns.mean()
            median_ret = returns.median()
            p10 = returns.quantile(0.10)
            p25 = returns.quantile(0.25)
            p75 = returns.quantile(0.75)
            p90 = returns.quantile(0.90)
            mean_abs_ret = returns.abs().mean()
            
            # Tail probabilities
            if atr_col in box_df.columns:
                abs_ret = returns.abs()
                atr = box_df[atr_col]
                tail_2R = (abs_ret > 2 * atr).mean()
                tail_3R = (abs_ret > 3 * atr).mean()
            else:
                tail_2R = np.nan
                tail_3R = np.nan
            
            results.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'box': box,
                'H': H,
                'count': count,
                'share': share,
                'mean_ret': mean_ret,
                'median_ret': median_ret,
                'p10': p10,
                'p25': p25,
                'p75': p75,
                'p90': p90,
                'mean_abs_ret': mean_abs_ret,
                'tail_prob_2R': tail_2R,
                'tail_prob_3R': tail_3R,
            })

    return pd.DataFrame(results)


def compute_risk_score_decile_stats(
    df: pd.DataFrame,
    horizons: List[int],
    atr_col: str,
    symbol: str,
    timeframe: str,
    fwd_ret_cols: Dict[int, str],
) -> pd.DataFrame:
    """
    Compute decile statistics for RiskScore.

    Similar to single-factor deciles, but for the unified RiskScore.
    """
    results = []

    if 'RiskScore' not in df.columns:
        logger.warning("RiskScore column not found")
        return pd.DataFrame()

    # Define decile bins
    bins = np.linspace(0, 1, 11)  # [0.0, 0.1, 0.2, ..., 1.0]
    df['risk_decile'] = pd.cut(df['RiskScore'], bins=bins, labels=False, include_lowest=True)

    total_count = len(df)

    for decile in range(10):
        decile_df = df[df['risk_decile'] == decile]
        count = len(decile_df)
        share = count / total_count if total_count > 0 else 0

        for H in horizons:
            ret_col = fwd_ret_cols.get(H)
            if ret_col is None or ret_col not in df.columns:
                continue

            # Mean absolute return
            abs_ret = decile_df[ret_col].abs()
            mean_abs_ret = abs_ret.mean()

            # Tail probabilities
            if atr_col in decile_df.columns:
                atr = decile_df[atr_col]
                tail_2R = (abs_ret > 2 * atr).mean()
                tail_3R = (abs_ret > 3 * atr).mean()
            else:
                tail_2R = np.nan
                tail_3R = np.nan

            results.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'decile': decile,
                'H': H,
                'count': count,
                'share': share,
                'mean_abs_ret': mean_abs_ret,
                'tail_prob_2R': tail_2R,
                'tail_prob_3R': tail_3R,
            })

    return pd.DataFrame(results)


def run_regime_stats_for_symbol_timeframe(
    merged_file: Path,
    output_root: Path,
    symbol: str,
    timeframe: str,
    horizons: List[int],
    atr_col: str,
    fwd_ret_cols: Dict[int, str],
) -> None:
    """
    Compute all regime statistics for a single (symbol, timeframe).

    Saves three CSV files:
        - high_vs_low_{symbol}_{timeframe}.csv
        - boxes_{symbol}_{timeframe}.csv
        - risk_score_deciles_{symbol}_{timeframe}.csv
    """
    logger.info(f"Processing: {symbol} {timeframe}")

    # Load merged data with regime features
    if not merged_file.exists():
        logger.warning(f"  Merged file not found: {merged_file.name}")
        return

    df = pd.read_parquet(merged_file)
    logger.info(f"  Loaded {len(df):,} rows")

    # Compute high vs low pressure stats
    high_low_stats = compute_high_vs_low_pressure_stats(
        df, horizons, atr_col, symbol, timeframe, fwd_ret_cols
    )
    if not high_low_stats.empty:
        output_file = output_root / f"high_vs_low_{symbol}_{timeframe}.csv"
        high_low_stats.to_csv(output_file, index=False)
        logger.info(f"  Saved: {output_file.name}")

    # Compute box stats
    box_stats = compute_box_stats(
        df, horizons, atr_col, symbol, timeframe, fwd_ret_cols
    )
    if not box_stats.empty:
        output_file = output_root / f"boxes_{symbol}_{timeframe}.csv"
        box_stats.to_csv(output_file, index=False)
        logger.info(f"  Saved: {output_file.name}")

    # Compute RiskScore decile stats
    risk_decile_stats = compute_risk_score_decile_stats(
        df, horizons, atr_col, symbol, timeframe, fwd_ret_cols
    )
    if not risk_decile_stats.empty:
        output_file = output_root / f"risk_score_deciles_{symbol}_{timeframe}.csv"
        risk_decile_stats.to_csv(output_file, index=False)
        logger.info(f"  Saved: {output_file.name}")

    logger.info(f"  ✓ Success")


if __name__ == "__main__":
    # This module requires merged data with regime features already added
    # Run three_factor_regime_features.py first to add features to merged data

    root = get_project_root()
    merged_root = root / "data" / "factors" / "merged_three_factor"
    output_root = root / "results" / "three_factor_regime" / "regime_stats"
    output_root.mkdir(parents=True, exist_ok=True)

    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]
    horizons = [2, 5, 10]
    atr_col = "ATR"
    fwd_ret_cols = {2: "fut_ret_2", 5: "fut_ret_5", 10: "fut_ret_10"}

    logger.info("=" * 80)
    logger.info("Three-Factor Regime Statistics")
    logger.info("=" * 80)
    logger.info("")

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

    logger.info("=" * 80)
    logger.info("✓ Regime statistics complete!")
    logger.info("=" * 80)

