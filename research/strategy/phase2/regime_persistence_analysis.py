"""
Phase 2D: Regime Persistence & Transition Analysis

Analyze regime dynamics: duration, transitions, and impact on trade performance.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def compute_regime_durations(
    df: pd.DataFrame,
    regime_col: str = "risk_regime"
) -> pd.DataFrame:
    """
    Compute duration of consecutive regime segments.
    
    Args:
        df: DataFrame with timestamp and regime column
        regime_col: Name of regime column
    
    Returns:
        DataFrame with regime duration statistics
    """
    if regime_col not in df.columns:
        raise ValueError(f"Column {regime_col} not found in DataFrame")
    
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Identify regime changes
    regime_changes = df[regime_col] != df[regime_col].shift(1)
    regime_groups = regime_changes.cumsum()
    
    # Compute duration for each segment
    durations = []
    for group_id in regime_groups.unique():
        segment = df[regime_groups == group_id]
        
        if len(segment) == 0:
            continue
        
        durations.append({
            'regime': segment[regime_col].iloc[0],
            'start_time': segment['timestamp'].iloc[0],
            'end_time': segment['timestamp'].iloc[-1],
            'duration_bars': len(segment),
            'start_idx': segment.index[0],
            'end_idx': segment.index[-1]
        })
    
    return pd.DataFrame(durations)


def summarize_regime_durations(
    durations_df: pd.DataFrame,
    percentiles: List[int] = [50, 75, 90, 95]
) -> pd.DataFrame:
    """
    Summarize regime duration statistics.
    
    Args:
        durations_df: DataFrame from compute_regime_durations
        percentiles: Percentiles to compute
    
    Returns:
        Summary DataFrame
    """
    grouped = durations_df.groupby('regime')['duration_bars']
    
    stats = []
    for regime, group in grouped:
        stat_dict = {
            'regime': regime,
            'n_segments': len(group),
            'mean_duration': group.mean(),
            'median_duration': group.median(),
            'std_duration': group.std(),
            'min_duration': group.min(),
            'max_duration': group.max()
        }
        
        # Add percentiles
        for p in percentiles:
            stat_dict[f'p{p}_duration'] = group.quantile(p / 100)
        
        stats.append(stat_dict)
    
    result = pd.DataFrame(stats)
    
    # Sort by regime order
    regime_order = {'low': 0, 'medium': 1, 'high': 2}
    result['_order'] = result['regime'].map(regime_order)
    result = result.sort_values('_order').drop('_order', axis=1)
    
    return result


def build_transition_matrix(
    df: pd.DataFrame,
    regime_col: str = "risk_regime"
) -> pd.DataFrame:
    """
    Build regime transition probability matrix.
    
    Args:
        df: DataFrame with regime column
        regime_col: Name of regime column
    
    Returns:
        Transition matrix DataFrame
    """
    if regime_col not in df.columns:
        raise ValueError(f"Column {regime_col} not found in DataFrame")
    
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Get current and next regime
    current = df[regime_col]
    next_regime = current.shift(-1)
    
    # Remove last row (no next state)
    transitions = pd.DataFrame({
        'from': current[:-1],
        'to': next_regime[:-1]
    })
    
    # Count transitions
    transition_counts = transitions.groupby(['from', 'to']).size().unstack(fill_value=0)
    
    # Normalize to probabilities
    transition_probs = transition_counts.div(transition_counts.sum(axis=1), axis=0)
    
    return transition_probs


def analyze_entry_vs_holding_regime(
    trades_df: pd.DataFrame,
    data_df: pd.DataFrame,
    regime_col: str = "risk_regime"
) -> pd.DataFrame:
    """
    Analyze how regime evolves during trade holding period.
    
    Args:
        trades_df: DataFrame with trade data (entry_time, exit_time, R_multiple)
        data_df: Full bar data with regime information
        regime_col: Name of regime column
    
    Returns:
        DataFrame with entry vs holding regime analysis
    """
    if 'entry_time' not in trades_df.columns or 'exit_time' not in trades_df.columns:
        raise ValueError("trades_df must have entry_time and exit_time columns")
    
    if regime_col not in data_df.columns:
        raise ValueError(f"Column {regime_col} not found in data_df")
    
    data_df = data_df.set_index('timestamp').sort_index()
    
    results = []
    
    for idx, trade in trades_df.iterrows():
        entry_time = pd.to_datetime(trade['entry_time'])
        exit_time = pd.to_datetime(trade['exit_time'])
        
        try:
            # Get regime at entry
            entry_regime = trade.get('risk_regime_entry', None)
            if entry_regime is None:
                # Try to get from data
                entry_regime = data_df.loc[entry_time, regime_col]
            
            # Get regime sequence during holding
            holding_regimes = data_df.loc[entry_time:exit_time, regime_col]
            
            if len(holding_regimes) == 0:
                continue
            
            # Analyze holding period
            regime_counts = holding_regimes.value_counts()
            dominant_regime = regime_counts.idxmax()
            regime_changed = len(holding_regimes.unique()) > 1
            hit_high = 'high' in holding_regimes.values
            
            results.append({
                'entry_regime': entry_regime,
                'dominant_holding_regime': dominant_regime,
                'regime_changed': regime_changed,
                'hit_high_during_holding': hit_high,
                'holding_bars': len(holding_regimes),
                'R_multiple': trade['R_multiple']
            })
            
        except Exception as e:
            logger.debug(f"Error analyzing trade {idx}: {e}")
            continue
    
    return pd.DataFrame(results)


def run_phase2d_analysis(config_path: Path = Path("research/strategy/phase2/config_phase2.yaml")) -> None:
    """
    Main function to run Phase 2D regime persistence analysis.

    Args:
        config_path: Path to Phase 2 config file
    """
    logger.info("="*80)
    logger.info("Phase 2D: Regime Persistence & Transition Analysis")
    logger.info("="*80)

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    phase2d_config = config['phase2D']
    global_config = config['global']

    # Setup paths
    data_dir = Path(global_config['data_dir'])
    trades_dir = Path(global_config['phase1_results_dir'])
    output_dir = Path(phase2d_config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    regime_col = phase2d_config['regime_col']
    duration_percentiles = phase2d_config['duration_percentiles']

    all_durations = []
    all_transitions = []

    # Process each symbol×timeframe
    for symbol in global_config['symbols']:
        for timeframe in global_config['timeframes']:
            data_file = data_dir / f"merged_{symbol}_{timeframe}.parquet"
            trades_file = trades_dir / f"trades_{symbol}_{timeframe}.csv"

            if not data_file.exists() or not trades_file.exists():
                logger.warning(f"Missing files for {symbol}_{timeframe}")
                continue

            try:
                logger.info(f"\nProcessing {symbol}_{timeframe}...")

                # Load data
                data_df = pd.read_parquet(data_file)
                trades_df = pd.read_csv(trades_file)

                # Step 1: Regime durations
                durations = compute_regime_durations(data_df, regime_col)
                duration_summary = summarize_regime_durations(durations, duration_percentiles)

                duration_summary['symbol'] = symbol
                duration_summary['timeframe'] = timeframe
                all_durations.append(duration_summary)

                # Save per-combination
                durations.to_csv(
                    output_dir / f"regime_durations_{symbol}_{timeframe}.csv",
                    index=False
                )

                logger.info(f"  Regime durations computed: {len(durations)} segments")

                # Step 2: Transition matrix
                transition_matrix = build_transition_matrix(data_df, regime_col)

                # Save transition matrix
                transition_matrix.to_csv(
                    output_dir / f"regime_transition_matrix_{symbol}_{timeframe}.csv"
                )

                logger.info(f"  Transition matrix computed")

                # Store for aggregation
                transition_matrix['symbol'] = symbol
                transition_matrix['timeframe'] = timeframe
                all_transitions.append(transition_matrix.reset_index())

                # Step 3: Entry vs holding regime
                entry_vs_holding = analyze_entry_vs_holding_regime(
                    trades_df,
                    data_df,
                    regime_col
                )

                if len(entry_vs_holding) > 0:
                    entry_vs_holding.to_csv(
                        output_dir / f"entry_vs_holding_regime_{symbol}_{timeframe}.csv",
                        index=False
                    )

                    # Analyze performance by regime change pattern
                    pattern_perf = entry_vs_holding.groupby(['entry_regime', 'regime_changed'])['R_multiple'].agg([
                        'count', 'mean', 'median', 'std'
                    ]).reset_index()

                    logger.info(f"  Entry vs holding analysis: {len(entry_vs_holding)} trades")
                    logger.info(f"\n{pattern_perf.to_string()}\n")

            except Exception as e:
                logger.error(f"Error processing {symbol}_{timeframe}: {e}")

    # Aggregate results
    logger.info("\n" + "="*80)
    logger.info("Aggregating results across all combinations")
    logger.info("="*80)

    if all_durations:
        # Combine duration summaries
        combined_durations = pd.concat(all_durations, ignore_index=True)

        # Global duration summary
        global_duration_summary = combined_durations.groupby('regime').agg({
            'mean_duration': 'mean',
            'median_duration': 'median',
            'n_segments': 'sum'
        }).reset_index()

        global_duration_summary.to_csv(
            output_dir / "regime_durations_aggregated.csv",
            index=False
        )

        logger.info("\n📊 Global Regime Duration Summary:")
        logger.info(f"\n{global_duration_summary.to_string()}\n")

    if all_transitions:
        # Average transition probabilities
        combined_transitions = pd.concat(all_transitions, ignore_index=True)

        # Group by from→to and average probabilities
        avg_transitions = combined_transitions.groupby('from').mean()

        avg_transitions.to_csv(
            output_dir / "regime_transition_matrix_aggregated.csv"
        )

        logger.info("\n📊 Global Transition Matrix (averaged):")
        logger.info(f"\n{avg_transitions.to_string()}\n")

    logger.info("\n" + "="*80)
    logger.info("Phase 2D Analysis Complete!")
    logger.info("="*80)
    logger.info(f"\nOutputs saved to: {output_dir}")
    logger.info(f"\n📋 Key insights:")
    logger.info(f"   - Review regime duration distributions")
    logger.info(f"   - Check transition probabilities for regime predictability")
    logger.info(f"   - Analyze if regime changes during holding affect performance")


if __name__ == "__main__":
    run_phase2d_analysis()


