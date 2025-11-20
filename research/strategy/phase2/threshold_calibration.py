"""
Phase 2A: Threshold Calibration

Analyze RiskScore distribution from Phase 1 trades and calibrate gating thresholds
to achieve meaningful block rates (10-30% target).
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_all_trades(trades_dir: Path, symbols: List[str], timeframes: List[str]) -> pd.DataFrame:
    """
    Load all trades_{symbol}_{timeframe}.csv from trades_dir and concatenate.
    
    Args:
        trades_dir: Directory containing trade CSV files
        symbols: List of symbols to load
        timeframes: List of timeframes to load
    
    Returns:
        DataFrame with all trades concatenated
    """
    all_trades = []
    
    for symbol in symbols:
        for timeframe in timeframes:
            file_path = trades_dir / f"trades_{symbol}_{timeframe}.csv"
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                df = pd.read_csv(file_path)
                df['symbol'] = symbol
                df['timeframe'] = timeframe
                all_trades.append(df)
                logger.info(f"Loaded {len(df)} trades from {symbol}_{timeframe}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
    
    if not all_trades:
        raise ValueError("No trade files loaded!")
    
    combined = pd.concat(all_trades, ignore_index=True)
    logger.info(f"Total trades loaded: {len(combined)}")
    
    return combined


def analyze_riskscore_distribution(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute RiskScore_entry distribution statistics.
    
    Args:
        trades_df: DataFrame with RiskScore_entry column
    
    Returns:
        DataFrame with distribution statistics
    """
    if 'RiskScore_entry' not in trades_df.columns:
        raise ValueError("RiskScore_entry column not found in trades DataFrame")
    
    riskscore = trades_df['RiskScore_entry'].dropna()
    
    # Compute quantiles
    quantiles = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    quantile_values = riskscore.quantile(quantiles)
    
    # Create summary table
    summary = pd.DataFrame({
        'quantile': quantiles,
        'RiskScore_value': quantile_values.values
    })
    
    # Add basic stats
    stats = pd.DataFrame({
        'statistic': ['count', 'mean', 'std', 'min', 'max'],
        'value': [
            len(riskscore),
            riskscore.mean(),
            riskscore.std(),
            riskscore.min(),
            riskscore.max()
        ]
    })
    
    logger.info("\nRiskScore Distribution Summary:")
    logger.info(f"\n{summary}")
    logger.info(f"\nBasic Statistics:")
    logger.info(f"\n{stats}")
    
    return summary, stats


def evaluate_candidate_thresholds(
    trades_df: pd.DataFrame,
    candidate_thresholds: List[float]
) -> pd.DataFrame:
    """
    Evaluate how many trades would be blocked at each candidate threshold.
    
    Args:
        trades_df: DataFrame with RiskScore_entry column
        candidate_thresholds: List of threshold values to test
    
    Returns:
        DataFrame with threshold evaluation results
    """
    total_trades = len(trades_df)
    results = []
    
    for threshold in candidate_thresholds:
        blockable = (trades_df['RiskScore_entry'] >= threshold).sum()
        blockable_rate = blockable / total_trades
        
        results.append({
            'threshold': threshold,
            'total_trades': total_trades,
            'blockable_trades': blockable,
            'blockable_rate': blockable_rate
        })
        
        logger.info(f"Threshold {threshold:.2f}: {blockable} trades ({blockable_rate:.1%}) would be blocked")
    
    return pd.DataFrame(results)


def suggest_threshold(
    threshold_eval: pd.DataFrame,
    target_range: Tuple[float, float] = (0.10, 0.30)
) -> Optional[float]:
    """
    Suggest optimal threshold based on target block rate range.
    
    Args:
        threshold_eval: DataFrame from evaluate_candidate_thresholds
        target_range: Tuple of (min_rate, max_rate) for target block rate
    
    Returns:
        Suggested threshold value, or None if no suitable threshold found
    """
    min_rate, max_rate = target_range
    
    # Find thresholds within target range
    in_range = threshold_eval[
        (threshold_eval['blockable_rate'] >= min_rate) &
        (threshold_eval['blockable_rate'] <= max_rate)
    ]
    
    if len(in_range) == 0:
        logger.warning(f"No threshold found in target range {min_rate:.1%}-{max_rate:.1%}")
        # Find closest
        threshold_eval['distance'] = abs(
            threshold_eval['blockable_rate'] - (min_rate + max_rate) / 2
        )
        closest = threshold_eval.loc[threshold_eval['distance'].idxmin()]
        logger.info(f"Closest threshold: {closest['threshold']:.2f} ({closest['blockable_rate']:.1%})")
        return closest['threshold']
    
    # Pick the smallest threshold in range (most conservative)
    suggested = in_range.loc[in_range['threshold'].idxmin()]
    logger.info(f"\n✅ Suggested threshold: {suggested['threshold']:.2f}")
    logger.info(f"   Block rate: {suggested['blockable_rate']:.1%}")
    logger.info(f"   Trades blocked: {suggested['blockable_trades']:.0f} / {suggested['total_trades']:.0f}")
    
    return suggested['threshold']


def update_high_riskscore_in_config(config_path: Path, new_value: float) -> None:
    """
    Update high_riskscore value in config_strategy.yaml.

    Args:
        config_path: Path to config_strategy.yaml
        new_value: New high_riskscore threshold value
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Update value
    old_value = config.get('high_riskscore', None)
    config['high_riskscore'] = new_value

    # Write back
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    logger.info(f"✅ Updated config: high_riskscore {old_value} → {new_value}")
    logger.info(f"   Config file: {config_path}")


def compare_baseline_vs_phase2(
    baseline_dir: Path,
    phase2_dir: Path,
    symbols: List[str],
    timeframes: List[str]
) -> pd.DataFrame:
    """
    Compare key metrics between baseline (Phase 1) and Phase 2 results.

    Args:
        baseline_dir: Directory with Phase 1 results
        phase2_dir: Directory with Phase 2 results
        symbols: List of symbols
        timeframes: List of timeframes

    Returns:
        DataFrame with comparison metrics
    """
    comparisons = []

    for symbol in symbols:
        for timeframe in timeframes:
            baseline_file = baseline_dir / f"summary_{symbol}_{timeframe}.csv"
            phase2_file = phase2_dir / f"summary_{symbol}_{timeframe}.csv"

            if not baseline_file.exists() or not phase2_file.exists():
                continue

            try:
                baseline = pd.read_csv(baseline_file).iloc[0]
                phase2 = pd.read_csv(phase2_file).iloc[0]

                comparisons.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'baseline_n_trades': baseline.get('n_trades', 0),
                    'phase2_n_trades': phase2.get('n_trades', 0),
                    'trades_blocked': baseline.get('n_trades', 0) - phase2.get('n_trades', 0),
                    'baseline_mean_R': baseline.get('mean_R', 0),
                    'phase2_mean_R': phase2.get('mean_R', 0),
                    'baseline_sharpe': baseline.get('sharpe', 0),
                    'phase2_sharpe': phase2.get('sharpe', 0),
                    'baseline_max_dd': baseline.get('max_drawdown_pct', 0),
                    'phase2_max_dd': phase2.get('max_drawdown_pct', 0),
                })
            except Exception as e:
                logger.error(f"Error comparing {symbol}_{timeframe}: {e}")

    if not comparisons:
        logger.warning("No comparisons generated")
        return pd.DataFrame()

    df = pd.DataFrame(comparisons)

    # Add improvement columns
    df['mean_R_improvement'] = df['phase2_mean_R'] - df['baseline_mean_R']
    df['sharpe_improvement'] = df['phase2_sharpe'] - df['baseline_sharpe']
    df['max_dd_improvement'] = df['baseline_max_dd'] - df['phase2_max_dd']  # Lower is better

    return df


def run_phase2a_analysis(config_path: Path = Path("research/strategy/phase2/config_phase2.yaml")) -> None:
    """
    Main function to run Phase 2A threshold calibration analysis.

    Args:
        config_path: Path to Phase 2 config file
    """
    logger.info("="*80)
    logger.info("Phase 2A: Threshold Calibration Analysis")
    logger.info("="*80)

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    phase2a_config = config['phase2A']
    global_config = config['global']

    # Setup paths
    trades_dir = Path(phase2a_config['trades_dir'])
    output_dir = Path(phase2a_config['compare_output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all trades
    logger.info("\n" + "="*80)
    logger.info("Step 1: Loading all Phase 1 trades")
    logger.info("="*80)

    trades_df = load_all_trades(
        trades_dir,
        global_config['symbols'],
        global_config['timeframes']
    )

    # Analyze RiskScore distribution
    logger.info("\n" + "="*80)
    logger.info("Step 2: Analyzing RiskScore distribution")
    logger.info("="*80)

    quantile_summary, stats_summary = analyze_riskscore_distribution(trades_df)

    # Save distribution analysis
    quantile_summary.to_csv(output_dir / "riskscore_distribution.csv", index=False)
    stats_summary.to_csv(output_dir / "riskscore_basic_stats.csv", index=False)
    logger.info(f"✅ Saved: {output_dir / 'riskscore_distribution.csv'}")

    # Evaluate candidate thresholds
    logger.info("\n" + "="*80)
    logger.info("Step 3: Evaluating candidate thresholds")
    logger.info("="*80)

    threshold_eval = evaluate_candidate_thresholds(
        trades_df,
        phase2a_config['candidate_high_riskscore']
    )

    # Save threshold evaluation
    threshold_eval.to_csv(output_dir / "threshold_blockable_rates.csv", index=False)
    logger.info(f"✅ Saved: {output_dir / 'threshold_blockable_rates.csv'}")

    # Suggest optimal threshold
    logger.info("\n" + "="*80)
    logger.info("Step 4: Suggesting optimal threshold")
    logger.info("="*80)

    suggested = suggest_threshold(
        threshold_eval,
        tuple(phase2a_config['target_block_rate_range'])
    )

    # Save suggestion
    suggestion_df = pd.DataFrame([{
        'suggested_threshold': suggested,
        'target_min_rate': phase2a_config['target_block_rate_range'][0],
        'target_max_rate': phase2a_config['target_block_rate_range'][1]
    }])
    suggestion_df.to_csv(output_dir / "suggested_threshold.csv", index=False)
    logger.info(f"✅ Saved: {output_dir / 'suggested_threshold.csv'}")

    logger.info("\n" + "="*80)
    logger.info("Phase 2A Analysis Complete!")
    logger.info("="*80)
    logger.info(f"\nOutputs saved to: {output_dir}")
    logger.info(f"\n📋 Next steps:")
    logger.info(f"   1. Review suggested threshold: {suggested:.2f}")
    logger.info(f"   2. Update config_strategy.yaml with new threshold")
    logger.info(f"   3. Re-run backtest: python research/strategy/run_regime_strategy.py")
    logger.info(f"   4. Compare results using compare_baseline_vs_phase2()")


if __name__ == "__main__":
    run_phase2a_analysis()


