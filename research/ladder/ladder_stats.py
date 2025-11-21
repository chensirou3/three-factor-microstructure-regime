"""
Ladder Trend Indicator - Statistical Analysis

Analyzes Ladder behavior without factors:
  - Trend state frequency (% of bars in up/down/neutral)
  - Trend duration distribution (consecutive bars in same state)
  - Forward return behavior conditional on Ladder state
  - Tail risk analysis
"""

import sys
from pathlib import Path
from typing import List, Tuple
import pandas as pd
import numpy as np
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_forward_returns(df: pd.DataFrame, horizons: List[int]) -> pd.DataFrame:
    """
    Compute forward returns for multiple horizons.
    
    Args:
        df: DataFrame with 'close' column
        horizons: List of forward horizons (e.g., [1, 3, 5, 10])
    
    Returns:
        DataFrame with added columns: ret_fwd_1, ret_fwd_3, etc.
    """
    df = df.copy()
    
    for H in horizons:
        df[f'ret_fwd_{H}'] = df['close'].pct_change(H).shift(-H)
    
    return df


def analyze_ladder_state_stats(df: pd.DataFrame,
                               symbol: str,
                               timeframe: str,
                               horizons: List[int],
                               atr_col: str = "ATR") -> pd.DataFrame:
    """
    Analyze forward return behavior conditional on Ladder state.
    
    For each state (up/down/neutral) and horizon H:
      - count: number of bars
      - share: percentage of total bars
      - mean_ret: E(ret_fwd_H)
      - mean_abs_ret: E(|ret_fwd_H|)
      - tail_prob_2R: P(|ret_fwd_H| > 2*ATR)
      - tail_prob_3R: P(|ret_fwd_H| > 3*ATR)
    
    Args:
        df: Ladder-enriched DataFrame
        symbol: Symbol name
        timeframe: Timeframe
        horizons: Forward return horizons
        atr_col: ATR column name
    
    Returns:
        DataFrame with statistics per state × horizon
    """
    # Compute forward returns
    df = compute_forward_returns(df, horizons)
    
    # Map ladder_state to readable names
    state_map = {1: 'up', -1: 'down', 0: 'neutral'}
    df['state_name'] = df['ladder_state'].map(state_map)
    
    results = []
    
    for state_val, state_name in state_map.items():
        subset = df[df['ladder_state'] == state_val].copy()
        
        if len(subset) == 0:
            continue
        
        for H in horizons:
            ret_col = f'ret_fwd_{H}'
            
            # Drop NaN returns
            valid = subset[ret_col].dropna()
            
            if len(valid) == 0:
                continue
            
            # Compute statistics
            count = len(valid)
            share = count / len(df)
            mean_ret = valid.mean()
            mean_abs_ret = valid.abs().mean()
            
            # Tail probabilities (if ATR available)
            tail_prob_2R = np.nan
            tail_prob_3R = np.nan
            
            if atr_col in subset.columns:
                atr_mean = subset[atr_col].mean()
                if atr_mean > 0:
                    tail_prob_2R = (valid.abs() > 2 * atr_mean).mean()
                    tail_prob_3R = (valid.abs() > 3 * atr_mean).mean()
            
            results.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'state': state_name,
                'H': H,
                'count': count,
                'share': share,
                'mean_ret': mean_ret,
                'mean_abs_ret': mean_abs_ret,
                'tail_prob_2R': tail_prob_2R,
                'tail_prob_3R': tail_prob_3R
            })
    
    return pd.DataFrame(results)


def compute_ladder_trend_durations(df: pd.DataFrame,
                                   symbol: str,
                                   timeframe: str) -> pd.DataFrame:
    """
    Compute consecutive upTrend/downTrend durations.
    
    For each continuous segment of ladder_state = +1 or -1:
      - state: 'up' or 'down'
      - duration_bars: number of consecutive bars
      - start_time, end_time: segment timestamps
    
    Args:
        df: Ladder-enriched DataFrame
        symbol: Symbol name
        timeframe: Timeframe
    
    Returns:
        DataFrame with all trend segments
    """
    df = df.copy()
    
    # Only consider non-neutral states
    df_trend = df[df['ladder_state'] != 0].copy()
    
    if len(df_trend) == 0:
        return pd.DataFrame()
    
    # Identify segment changes
    df_trend['state_change'] = df_trend['ladder_state'].ne(df_trend['ladder_state'].shift())
    df_trend['segment_id'] = df_trend['state_change'].cumsum()
    
    # Group by segment
    segments = []
    
    for seg_id, group in df_trend.groupby('segment_id'):
        state_val = group['ladder_state'].iloc[0]
        state_name = 'up' if state_val == 1 else 'down'
        
        segments.append({
            'symbol': symbol,
            'timeframe': timeframe,
            'state': state_name,
            'duration_bars': len(group),
            'start_time': group['timestamp'].iloc[0],
            'end_time': group['timestamp'].iloc[-1]
        })
    
    return pd.DataFrame(segments)


def run_ladder_stats_analysis(symbols: List[str],
                              timeframes: List[str],
                              ladder_dir: Path,
                              output_dir: Path,
                              horizons: List[int] = [1, 3, 5, 10]) -> None:
    """
    Run complete Ladder statistical analysis for all symbol×timeframe.

    Args:
        symbols: List of symbols
        timeframes: List of timeframes
        ladder_dir: Directory with ladder_{symbol}_{timeframe}.parquet files
        output_dir: Output directory for results
        horizons: Forward return horizons
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    all_state_stats = []
    all_durations = []

    total = len(symbols) * len(timeframes)
    completed = 0

    logger.info("="*80)
    logger.info(f"Running Ladder statistical analysis for {total} combinations")
    logger.info(f"  Horizons: {horizons}")
    logger.info("="*80)

    for symbol in symbols:
        for timeframe in timeframes:
            try:
                # Load Ladder data
                ladder_file = ladder_dir / f"ladder_{symbol}_{timeframe}.parquet"
                if not ladder_file.exists():
                    logger.warning(f"Ladder file not found: {ladder_file}")
                    continue

                df = pd.read_parquet(ladder_file)
                logger.info(f"Analyzing {symbol}_{timeframe}: {len(df)} bars")

                # Analyze state statistics
                state_stats = analyze_ladder_state_stats(
                    df, symbol, timeframe, horizons
                )
                all_state_stats.append(state_stats)

                # Save per-symbol×timeframe
                state_file = output_dir / f"ladder_state_stats_{symbol}_{timeframe}.csv"
                state_stats.to_csv(state_file, index=False)
                logger.info(f"  ✓ Saved state stats: {state_file.name}")

                # Compute trend durations
                durations = compute_ladder_trend_durations(df, symbol, timeframe)
                all_durations.append(durations)

                # Save per-symbol×timeframe
                duration_file = output_dir / f"ladder_durations_{symbol}_{timeframe}.csv"
                durations.to_csv(duration_file, index=False)
                logger.info(f"  ✓ Saved durations: {duration_file.name}")

                completed += 1
                logger.info(f"  Progress: {completed}/{total} ({completed/total*100:.1f}%)")

            except Exception as e:
                logger.error(f"Failed: {symbol}_{timeframe}")
                logger.error(f"  Error: {e}")

    # Aggregate all results
    if all_state_stats:
        agg_state_stats = pd.concat(all_state_stats, ignore_index=True)
        agg_file = output_dir / "ladder_state_stats_aggregated.csv"
        agg_state_stats.to_csv(agg_file, index=False)
        logger.info(f"✓ Saved aggregated state stats: {agg_file.name}")

    if all_durations:
        agg_durations = pd.concat(all_durations, ignore_index=True)
        agg_file = output_dir / "ladder_durations_aggregated.csv"
        agg_durations.to_csv(agg_file, index=False)
        logger.info(f"✓ Saved aggregated durations: {agg_file.name}")

    logger.info("="*80)
    logger.info("Ladder statistical analysis complete!")
    logger.info("="*80)


if __name__ == "__main__":
    # Project root
    root = Path(__file__).resolve().parents[2]

    # Paths
    ladder_dir = root / "data/ladder_features"
    output_dir = root / "results/ladder"

    # Configuration - ALL symbols × ALL timeframes
    symbols = ['BTCUSD', 'ETHUSD', 'EURUSD', 'USDJPY', 'XAGUSD', 'XAUUSD']
    timeframes = ['5min', '15min', '30min', '1h', '4h', '1d']
    horizons = [1, 3, 5, 10]

    # Run analysis
    run_ladder_stats_analysis(symbols, timeframes, ladder_dir, output_dir, horizons)


