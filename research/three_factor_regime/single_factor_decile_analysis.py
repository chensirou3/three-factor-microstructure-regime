#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single-Factor Decile Analysis for Three-Factor Regime Research

This module performs risk-focused decile analysis on each factor independently.

Focus: Risk & tail behavior (not alpha)
- Uses |ManipScore_z| and OFI_abs_z (strength, not direction)
- Computes E(|ret|) and tail probabilities, not E(ret)
- Time-series analysis within each (symbol, timeframe), not cross-sectional

For each factor:
    1. Compute quantile scores (q_factor) within symbol×timeframe
    2. Divide into 10 deciles
    3. For each decile and horizon H:
        - count, share
        - mean_abs_ret = E(|ret_fwd_H|)
        - tail_prob_2R = P(|ret_fwd_H| > 2 * ATR)
        - tail_prob_3R = P(|ret_fwd_H| > 3 * ATR)

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
    # Adjust based on where this file is located
    return Path(__file__).parent.parent.parent


def add_quantile_scores(
    df: pd.DataFrame,
    factor_cols: Dict[str, str],
) -> pd.DataFrame:
    """
    Add quantile scores for each factor.
    
    factor_cols: mapping label -> column name
      e.g. {"manip": "ManipScore_z", "ofi": "OFI_abs_z", "vol": "VolLiqScore"}
    
    For each factor:
      - take abs() for 'manip' and 'ofi' (risk strength),
        keep raw for 'vol' (VolLiqScore).
      - compute q_{label} in [0,1] using rank(pct=True).
    
    If df has 'symbol' and 'timeframe', group by them.
    Otherwise, treat entire df as one panel.
    """
    df = df.copy()
    
    # Check if we should group by symbol×timeframe
    group_cols = []
    if 'symbol' in df.columns and 'timeframe' in df.columns:
        group_cols = ['symbol', 'timeframe']
    
    for label, col in factor_cols.items():
        if col not in df.columns:
            logger.warning(f"Column {col} not found in DataFrame, skipping {label}")
            continue
        
        # Determine if we need abs()
        if label in ['manip', 'ofi']:
            # Use absolute value for risk strength
            values = df[col].abs()
        else:
            # Use raw value for vol
            values = df[col]
        
        # Compute quantile rank
        if group_cols:
            df[f'q_{label}'] = df.groupby(group_cols)[col].rank(pct=True)
        else:
            df[f'q_{label}'] = values.rank(pct=True)
    
    return df


def compute_decile_stats_for_factor(
    df: pd.DataFrame,
    q_col: str,               # e.g. "q_manip"
    horizons: List[int],
    atr_col: str,
    symbol: str,
    timeframe: str,
    factor_name: str,         # "manip" / "ofi" / "vol"
    fwd_ret_cols: Dict[int, str],
) -> pd.DataFrame:
    """
    Return DataFrame with columns:
      ['symbol', 'timeframe', 'factor', 'decile', 'H',
       'count', 'share', 'mean_abs_ret', 'tail_prob_2R', 'tail_prob_3R']
    """
    results = []
    
    # Define decile bins
    bins = np.linspace(0, 1, 11)  # [0.0, 0.1, 0.2, ..., 1.0]
    df['decile'] = pd.cut(df[q_col], bins=bins, labels=False, include_lowest=True)
    
    total_count = len(df)
    
    for decile in range(10):
        decile_df = df[df['decile'] == decile]
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
                'factor': factor_name,
                'decile': decile,
                'H': H,
                'count': count,
                'share': share,
                'mean_abs_ret': mean_abs_ret,
                'tail_prob_2R': tail_2R,
                'tail_prob_3R': tail_3R,
            })
    
    return pd.DataFrame(results)


def run_single_factor_decile_analysis_for_manip(
    merged_root: Path,
    output_root: Path,
    symbols: List[str],
    timeframes: List[str],
    horizons: List[int],
    atr_col: str,
    fwd_ret_cols: Dict[int, str],
) -> None:
    """
    For each (symbol, timeframe):
      1) load merged_{symbol}_{timeframe}.parquet
      2) add q_manip
      3) compute decile stats
      4) save CSV to:
         output_root / f"single_factor_deciles_manip_{symbol}_{timeframe}.csv"
    """
    logger.info("=" * 80)
    logger.info("Single-Factor Decile Analysis - ManipScore")
    logger.info("=" * 80)
    logger.info(f"Symbols: {symbols}")
    logger.info(f"Timeframes: {timeframes}")
    logger.info(f"Horizons: {horizons}")
    logger.info("")
    
    output_root.mkdir(parents=True, exist_ok=True)
    
    for symbol in symbols:
        for timeframe in timeframes:
            logger.info(f"Processing: {symbol} {timeframe}")
            
            try:
                # Load merged data
                merged_file = merged_root / f"merged_{symbol}_{timeframe}.parquet"
                if not merged_file.exists():
                    logger.warning(f"  Merged file not found: {merged_file.name}")
                    continue
                
                df = pd.read_parquet(merged_file)
                logger.info(f"  Loaded {len(df):,} rows")
                
                # Add quantile score for ManipScore
                df = add_quantile_scores(df, {"manip": "ManipScore_z"})
                
                # Compute decile stats
                stats_df = compute_decile_stats_for_factor(
                    df=df,
                    q_col='q_manip',
                    horizons=horizons,
                    atr_col=atr_col,
                    symbol=symbol,
                    timeframe=timeframe,
                    factor_name='manip',
                    fwd_ret_cols=fwd_ret_cols,
                )
                
                # Save to CSV
                output_file = output_root / f"single_factor_deciles_manip_{symbol}_{timeframe}.csv"
                stats_df.to_csv(output_file, index=False)
                logger.info(f"  Saved: {output_file.name}")
                logger.info(f"  ✓ Success")
                
            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
            
            logger.info("")

    logger.info("=" * 80)
    logger.info("✓ ManipScore decile analysis complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
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

