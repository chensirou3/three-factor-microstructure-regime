"""
Phase 2B: Regime Tail-Risk Analysis

Characterize regimes by tail risk metrics (not just mean returns) to understand
the true risk profile of each regime.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def compute_tail_stats_by_risk_regime(trades_df: pd.DataFrame, percentiles: List[int] = [1, 5, 10, 90, 95, 99]) -> pd.DataFrame:
    """
    Compute tail statistics grouped by risk_regime_entry.
    
    Args:
        trades_df: DataFrame with R_multiple and risk_regime_entry columns
        percentiles: List of percentiles to compute
    
    Returns:
        DataFrame with tail statistics by risk regime
    """
    if 'risk_regime_entry' not in trades_df.columns or 'R_multiple' not in trades_df.columns:
        raise ValueError("Required columns not found: risk_regime_entry, R_multiple")
    
    grouped = trades_df.groupby('risk_regime_entry')['R_multiple']
    
    stats = []
    for regime, group in grouped:
        stat_dict = {
            'risk_regime': regime,
            'n_trades': len(group),
            'mean_R': group.mean(),
            'median_R': group.median(),
            'std_R': group.std(),
            'win_rate_pct': (group > 0).mean() * 100
        }
        
        # Add percentiles
        for p in percentiles:
            stat_dict[f'p{p}_R'] = group.quantile(p / 100)
        
        stats.append(stat_dict)
    
    result = pd.DataFrame(stats)
    
    # Sort by risk regime order
    regime_order = {'low': 0, 'medium': 1, 'high': 2}
    result['_order'] = result['risk_regime'].map(regime_order)
    result = result.sort_values('_order').drop('_order', axis=1)
    
    return result


def compute_tail_stats_by_pressure(trades_df: pd.DataFrame, percentiles: List[int] = [1, 5, 10, 90, 95, 99]) -> pd.DataFrame:
    """
    Compute tail statistics grouped by high_pressure_entry.
    
    Args:
        trades_df: DataFrame with R_multiple and high_pressure_entry columns
        percentiles: List of percentiles to compute
    
    Returns:
        DataFrame with tail statistics by pressure
    """
    if 'high_pressure_entry' not in trades_df.columns or 'R_multiple' not in trades_df.columns:
        raise ValueError("Required columns not found: high_pressure_entry, R_multiple")
    
    grouped = trades_df.groupby('high_pressure_entry')['R_multiple']
    
    stats = []
    for pressure, group in grouped:
        stat_dict = {
            'high_pressure': pressure,
            'n_trades': len(group),
            'mean_R': group.mean(),
            'median_R': group.median(),
            'std_R': group.std(),
            'win_rate_pct': (group > 0).mean() * 100
        }
        
        # Add percentiles
        for p in percentiles:
            stat_dict[f'p{p}_R'] = group.quantile(p / 100)
        
        stats.append(stat_dict)
    
    return pd.DataFrame(stats)


def compute_tail_stats_by_box(
    trades_df: pd.DataFrame,
    percentiles: List[int] = [1, 5, 10, 90, 95, 99],
    min_samples: int = 50
) -> pd.DataFrame:
    """
    Compute tail statistics grouped by three_factor_box_entry.
    
    Args:
        trades_df: DataFrame with R_multiple and three_factor_box_entry columns
        percentiles: List of percentiles to compute
        min_samples: Minimum number of trades required for a box to be included
    
    Returns:
        DataFrame with tail statistics by box
    """
    if 'three_factor_box_entry' not in trades_df.columns or 'R_multiple' not in trades_df.columns:
        raise ValueError("Required columns not found: three_factor_box_entry, R_multiple")
    
    grouped = trades_df.groupby('three_factor_box_entry')['R_multiple']
    
    stats = []
    for box, group in grouped:
        if len(group) < min_samples:
            logger.debug(f"Skipping box {box}: only {len(group)} trades (< {min_samples})")
            continue
        
        stat_dict = {
            'three_factor_box': box,
            'n_trades': len(group),
            'mean_R': group.mean(),
            'median_R': group.median(),
            'std_R': group.std(),
            'win_rate_pct': (group > 0).mean() * 100
        }
        
        # Add percentiles
        for p in percentiles:
            stat_dict[f'p{p}_R'] = group.quantile(p / 100)
        
        stats.append(stat_dict)
    
    result = pd.DataFrame(stats)
    
    # Sort by mean_R descending
    if len(result) > 0:
        result = result.sort_values('mean_R', ascending=False)
    
    return result


def aggregate_tail_stats(
    trades_dir: Path,
    symbols: List[str],
    timeframes: List[str],
    percentiles: List[int] = [1, 5, 10, 90, 95, 99],
    min_samples: int = 50
) -> Dict[str, pd.DataFrame]:
    """
    Aggregate tail statistics across all symbol×timeframe combinations.
    
    Args:
        trades_dir: Directory containing trade CSV files
        symbols: List of symbols
        timeframes: List of timeframes
        percentiles: List of percentiles to compute
        min_samples: Minimum samples for box analysis
    
    Returns:
        Dictionary with aggregated statistics for each grouping
    """
    all_trades = []
    
    # Load all trades
    for symbol in symbols:
        for timeframe in timeframes:
            file_path = trades_dir / f"trades_{symbol}_{timeframe}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path)
                df['symbol'] = symbol
                df['timeframe'] = timeframe
                all_trades.append(df)
    
    if not all_trades:
        raise ValueError("No trade files found!")
    
    combined = pd.concat(all_trades, ignore_index=True)
    logger.info(f"Loaded {len(combined)} total trades for aggregation")
    
    # Compute aggregated statistics
    results = {}
    
    logger.info("Computing aggregated tail stats by risk_regime...")
    results['by_risk_regime'] = compute_tail_stats_by_risk_regime(combined, percentiles)
    
    logger.info("Computing aggregated tail stats by high_pressure...")
    results['by_pressure'] = compute_tail_stats_by_pressure(combined, percentiles)
    
    logger.info("Computing aggregated tail stats by three_factor_box...")
    results['by_box'] = compute_tail_stats_by_box(combined, percentiles, min_samples)
    
    return results


def run_phase2b_analysis(config_path: Path = Path("research/strategy/phase2/config_phase2.yaml")) -> None:
    """
    Main function to run Phase 2B tail-risk analysis.

    Args:
        config_path: Path to Phase 2 config file
    """
    logger.info("="*80)
    logger.info("Phase 2B: Regime Tail-Risk Analysis")
    logger.info("="*80)

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    phase2b_config = config['phase2B']
    global_config = config['global']

    # Setup paths
    trades_dir = Path(global_config['phase1_results_dir'])
    output_dir = Path(phase2b_config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    percentiles = phase2b_config['tail_percentiles']
    min_samples = phase2b_config['min_samples_per_box']

    # Step 1: Per symbol×timeframe analysis
    logger.info("\n" + "="*80)
    logger.info("Step 1: Computing tail stats per symbol×timeframe")
    logger.info("="*80)

    for symbol in global_config['symbols']:
        for timeframe in global_config['timeframes']:
            file_path = trades_dir / f"trades_{symbol}_{timeframe}.csv"

            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue

            try:
                trades_df = pd.read_csv(file_path)
                logger.info(f"\nProcessing {symbol}_{timeframe} ({len(trades_df)} trades)")

                # By risk regime
                risk_stats = compute_tail_stats_by_risk_regime(trades_df, percentiles)
                risk_stats.to_csv(
                    output_dir / f"tailrisk_by_risk_regime_{symbol}_{timeframe}.csv",
                    index=False
                )

                # By pressure
                pressure_stats = compute_tail_stats_by_pressure(trades_df, percentiles)
                pressure_stats.to_csv(
                    output_dir / f"tailrisk_by_pressure_{symbol}_{timeframe}.csv",
                    index=False
                )

                # By box
                box_stats = compute_tail_stats_by_box(trades_df, percentiles, min_samples)
                if len(box_stats) > 0:
                    box_stats.to_csv(
                        output_dir / f"tailrisk_by_box_{symbol}_{timeframe}.csv",
                        index=False
                    )

                logger.info(f"✅ Saved tail-risk stats for {symbol}_{timeframe}")

            except Exception as e:
                logger.error(f"Error processing {symbol}_{timeframe}: {e}")

    # Step 2: Aggregated analysis
    logger.info("\n" + "="*80)
    logger.info("Step 2: Computing aggregated tail stats across all combinations")
    logger.info("="*80)

    aggregated = aggregate_tail_stats(
        trades_dir,
        global_config['symbols'],
        global_config['timeframes'],
        percentiles,
        min_samples
    )

    # Save aggregated results
    for key, df in aggregated.items():
        output_file = output_dir / f"tailrisk_aggregated_{key}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"✅ Saved: {output_file}")
        logger.info(f"\n{df.to_string()}\n")

    # Step 3: Generate interpretation summary
    logger.info("\n" + "="*80)
    logger.info("Step 3: Generating interpretation summary")
    logger.info("="*80)

    risk_regime_stats = aggregated['by_risk_regime']

    # Analyze risk-return tradeoff
    logger.info("\n📊 Risk-Return Analysis by Regime:")
    for _, row in risk_regime_stats.iterrows():
        regime = row['risk_regime']
        mean_r = row['mean_R']
        std_r = row['std_R']
        p5_r = row['p5_R']
        sharpe = mean_r / std_r if std_r > 0 else 0

        logger.info(f"\n{regime.upper()} Regime:")
        logger.info(f"  Mean R: {mean_r:.3f}")
        logger.info(f"  Std R: {std_r:.3f}")
        logger.info(f"  Sharpe-like: {sharpe:.3f}")
        logger.info(f"  5th percentile (tail risk): {p5_r:.3f}")
        logger.info(f"  Win rate: {row['win_rate_pct']:.1f}%")

    # Identify best regime
    risk_regime_stats['sharpe_like'] = risk_regime_stats['mean_R'] / risk_regime_stats['std_R']
    best_regime = risk_regime_stats.loc[risk_regime_stats['sharpe_like'].idxmax()]

    logger.info(f"\n✅ Best risk-adjusted regime: {best_regime['risk_regime'].upper()}")
    logger.info(f"   Sharpe-like ratio: {best_regime['sharpe_like']:.3f}")

    # Save interpretation
    interpretation = pd.DataFrame([{
        'best_regime': best_regime['risk_regime'],
        'best_sharpe_like': best_regime['sharpe_like'],
        'best_mean_R': best_regime['mean_R'],
        'best_std_R': best_regime['std_R'],
        'best_p5_R': best_regime['p5_R']
    }])
    interpretation.to_csv(output_dir / "regime_interpretation.csv", index=False)

    logger.info("\n" + "="*80)
    logger.info("Phase 2B Analysis Complete!")
    logger.info("="*80)
    logger.info(f"\nOutputs saved to: {output_dir}")
    logger.info(f"\n📋 Key findings:")
    logger.info(f"   - Best regime: {best_regime['risk_regime']}")
    logger.info(f"   - Review tail-risk profiles to understand true risk")
    logger.info(f"   - Check if 'high risk' regime has worse tail behavior")


if __name__ == "__main__":
    run_phase2b_analysis()


