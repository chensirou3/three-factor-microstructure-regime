"""
Check 1: Multi-timeframe Alignment (No Look-ahead Bias)

Verify that low timeframe bars only use high timeframe Ladder states
from bars with timestamp <= low_tf_timestamp.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from research.ladder_factor_combo.mtf_timing import align_high_low_tf_ladder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_mtf_alignment(
    high_df: pd.DataFrame,
    low_df: pd.DataFrame,
    high_tf_state_col: str = 'ladder_state',
    aligned_state_col: str = 'high_tf_ladder_state'
) -> pd.DataFrame:
    """
    Verify multi-timeframe alignment has no look-ahead bias.
    
    For each low_tf row:
    1) The aligned high_tf_state corresponds to a high TF bar with timestamp <= low_tf timestamp
    2) No case where aligned high_tf_state depends on future high TF bar
    
    Args:
        high_df: High timeframe DataFrame with ladder_state
        low_df: Low timeframe DataFrame with aligned high_tf_ladder_state
        high_tf_state_col: Column name for high TF state
        aligned_state_col: Column name for aligned state in low TF
    
    Returns:
        DataFrame of violations (empty if all pass)
    """
    violations = []
    
    # Ensure timestamps are datetime
    high_df = high_df.copy()
    low_df = low_df.copy()
    high_df['timestamp'] = pd.to_datetime(high_df['timestamp'])
    low_df['timestamp'] = pd.to_datetime(low_df['timestamp'])
    
    # Sort
    high_df = high_df.sort_values('timestamp').reset_index(drop=True)
    low_df = low_df.sort_values('timestamp').reset_index(drop=True)
    
    # For each low TF bar, find the corresponding high TF state
    for idx, low_row in low_df.iterrows():
        low_ts = low_row['timestamp']
        aligned_state = low_row.get(aligned_state_col, np.nan)
        
        # Find all high TF bars with timestamp <= low_ts
        valid_high_bars = high_df[high_df['timestamp'] <= low_ts]
        
        if len(valid_high_bars) == 0:
            # No valid high TF bar yet (beginning of data)
            if not pd.isna(aligned_state):
                violations.append({
                    'low_tf_idx': idx,
                    'low_tf_timestamp': low_ts,
                    'aligned_state': aligned_state,
                    'issue': 'No valid high TF bar available, but state is not NaN'
                })
            continue
        
        # The most recent valid high TF bar
        most_recent_high = valid_high_bars.iloc[-1]
        expected_state = most_recent_high[high_tf_state_col]
        
        # Check if aligned state matches expected
        if pd.isna(aligned_state) and pd.isna(expected_state):
            continue  # Both NaN is OK
        
        if aligned_state != expected_state:
            violations.append({
                'low_tf_idx': idx,
                'low_tf_timestamp': low_ts,
                'aligned_state': aligned_state,
                'expected_state': expected_state,
                'most_recent_high_ts': most_recent_high['timestamp'],
                'issue': 'Aligned state does not match most recent valid high TF state'
            })
    
    return pd.DataFrame(violations)


def run_mtf_alignment_checks():
    """
    Run multi-timeframe alignment checks for key configurations.
    
    Focus on:
    - BTCUSD 4h -> 30min
    - BTCUSD 4h -> 1h
    """
    logger.info("=" * 80)
    logger.info("CHECK 1: Multi-timeframe Alignment (No Look-ahead Bias)")
    logger.info("=" * 80)
    
    root = project_root
    ladder_dir = "data/ladder_features"
    results_dir = root / "results" / "ladder_factor_combo" / "sanity"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Test configurations
    configs = [
        ("BTCUSD", "4h", "30min"),
        ("BTCUSD", "4h", "1h"),
    ]
    
    all_results = []
    
    for symbol, high_tf, low_tf in configs:
        logger.info(f"\nChecking {symbol} {high_tf} -> {low_tf}...")
        
        try:
            # Load high TF
            high_file = root / ladder_dir / f"ladder_{symbol}_{high_tf}.parquet"
            if not high_file.exists():
                logger.warning(f"High TF file not found: {high_file}")
                continue
            
            high_df = pd.read_parquet(high_file)
            
            # Load low TF
            low_file = root / ladder_dir / f"ladder_{symbol}_{low_tf}.parquet"
            if not low_file.exists():
                logger.warning(f"Low TF file not found: {low_file}")
                continue
            
            low_df = pd.read_parquet(low_file)
            
            # Align using the same function as D3
            low_aligned = align_high_low_tf_ladder(high_df, low_df)
            
            # Check alignment
            violations = check_mtf_alignment(high_df, low_aligned)
            
            if len(violations) == 0:
                logger.info(f"✅ PASS: No look-ahead violations found")
                all_results.append({
                    'symbol': symbol,
                    'high_tf': high_tf,
                    'low_tf': low_tf,
                    'status': 'PASS',
                    'violations': 0,
                    'message': 'No look-ahead bias detected'
                })
            else:
                logger.error(f"❌ FAIL: {len(violations)} violations found")
                logger.error(f"First few violations:\n{violations.head()}")
                all_results.append({
                    'symbol': symbol,
                    'high_tf': high_tf,
                    'low_tf': low_tf,
                    'status': 'FAIL',
                    'violations': len(violations),
                    'message': f'{len(violations)} look-ahead violations detected'
                })
                
                # Save violations
                viol_file = results_dir / f"mtf_violations_{symbol}_{high_tf}_{low_tf}.csv"
                violations.to_csv(viol_file, index=False)
                logger.info(f"Violations saved to: {viol_file}")
        
        except Exception as e:
            logger.error(f"Error checking {symbol} {high_tf}->{low_tf}: {e}")
            all_results.append({
                'symbol': symbol,
                'high_tf': high_tf,
                'low_tf': low_tf,
                'status': 'ERROR',
                'violations': -1,
                'message': str(e)
            })
    
    # Save summary
    summary_df = pd.DataFrame(all_results)
    summary_file = results_dir / "multitimeframe_alignment_report.csv"
    summary_df.to_csv(summary_file, index=False)
    
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY:")
    logger.info(summary_df.to_string(index=False))
    logger.info(f"\nReport saved to: {summary_file}")
    logger.info("=" * 80)
    
    return summary_df


if __name__ == "__main__":
    run_mtf_alignment_checks()

