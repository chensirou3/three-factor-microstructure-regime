"""
Check 2: Ladder Signal Computation

Verify:
1. Ladder EMA bands are computed causally (no future data)
2. ret_fwd_* columns are NOT used in signal generation (only for evaluation)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import inspect

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_ladder_ema_causality(
    df: pd.DataFrame,
    fast_len: int = 25,
    slow_len: int = 90,
    tolerance: float = 1e-6
) -> dict:
    """
    Verify Ladder EMA bands are computed causally.
    
    Recompute EMA bands and compare with existing values.
    
    Args:
        df: DataFrame with existing Ladder bands
        fast_len: Fast EMA length
        slow_len: Slow EMA length
        tolerance: Numerical tolerance for comparison
    
    Returns:
        dict with check results
    """
    df = df.copy()
    
    # Recompute EMA bands
    df['fastU_recomputed'] = df['high'].ewm(span=fast_len, adjust=False).mean()
    df['fastL_recomputed'] = df['low'].ewm(span=fast_len, adjust=False).mean()
    df['slowU_recomputed'] = df['high'].ewm(span=slow_len, adjust=False).mean()
    df['slowL_recomputed'] = df['low'].ewm(span=slow_len, adjust=False).mean()
    
    # Compare with existing
    results = {
        'fast_len': fast_len,
        'slow_len': slow_len,
        'total_bars': len(df),
        'checks': {}
    }
    
    for band in ['fastU', 'fastL', 'slowU', 'slowL']:
        if band not in df.columns:
            results['checks'][band] = {
                'status': 'SKIP',
                'message': f'{band} column not found in data'
            }
            continue
        
        recomputed_col = f'{band}_recomputed'
        
        # Compare (skip NaN values)
        valid_mask = ~(df[band].isna() | df[recomputed_col].isna())
        diff = (df.loc[valid_mask, band] - df.loc[valid_mask, recomputed_col]).abs()
        
        max_diff = diff.max() if len(diff) > 0 else 0
        mean_diff = diff.mean() if len(diff) > 0 else 0
        
        if max_diff < tolerance:
            results['checks'][band] = {
                'status': 'PASS',
                'max_diff': max_diff,
                'mean_diff': mean_diff,
                'message': 'EMA values match recomputed values'
            }
        else:
            results['checks'][band] = {
                'status': 'FAIL',
                'max_diff': max_diff,
                'mean_diff': mean_diff,
                'message': f'EMA values differ by up to {max_diff:.6f}'
            }
    
    return results


def check_ret_fwd_usage_in_code():
    """
    Static code inspection: check if ret_fwd_* is used in signal generation.
    
    Inspect key D3 modules for ret_fwd usage.
    """
    logger.info("\nStatic code inspection for ret_fwd_* usage...")
    
    # Files to inspect
    files_to_check = [
        project_root / "research" / "ladder_factor_combo" / "mtf_timing.py",
        project_root / "research" / "ladder" / "ladder_features.py",
    ]
    
    findings = []
    
    for file_path in files_to_check:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue
        
        logger.info(f"\nInspecting: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Search for ret_fwd usage
        ret_fwd_lines = []
        for i, line in enumerate(lines, 1):
            if 'ret_fwd' in line.lower() and not line.strip().startswith('#'):
                ret_fwd_lines.append((i, line.strip()))
        
        if ret_fwd_lines:
            logger.warning(f"Found {len(ret_fwd_lines)} lines with 'ret_fwd':")
            for line_num, line_content in ret_fwd_lines[:5]:  # Show first 5
                logger.warning(f"  Line {line_num}: {line_content}")
            
            findings.append({
                'file': file_path.name,
                'ret_fwd_mentions': len(ret_fwd_lines),
                'status': 'REVIEW_NEEDED',
                'message': 'ret_fwd found in code - manual review needed'
            })
        else:
            logger.info(f"✅ No ret_fwd usage found")
            findings.append({
                'file': file_path.name,
                'ret_fwd_mentions': 0,
                'status': 'PASS',
                'message': 'No ret_fwd usage detected'
            })
    
    return findings


def run_ladder_signal_checks():
    """
    Run Ladder signal computation checks.
    """
    logger.info("=" * 80)
    logger.info("CHECK 2: Ladder Signal Computation")
    logger.info("=" * 80)
    
    root = project_root
    ladder_dir = "data/ladder_features"
    results_dir = root / "results" / "ladder_factor_combo" / "sanity"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Part 1: EMA causality check
    logger.info("\n--- Part 1: EMA Causality Check ---")
    
    # Check BTCUSD 4h and 30min
    ema_results = []
    
    for symbol, tf in [("BTCUSD", "4h"), ("BTCUSD", "30min"), ("BTCUSD", "1h")]:
        logger.info(f"\nChecking {symbol} {tf}...")
        
        file_path = root / ladder_dir / f"ladder_{symbol}_{tf}.parquet"
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue
        
        df = pd.read_parquet(file_path)
        result = check_ladder_ema_causality(df)
        
        # Log results
        all_pass = all(c['status'] == 'PASS' for c in result['checks'].values())
        if all_pass:
            logger.info(f"✅ PASS: All EMA bands match recomputed values")
        else:
            logger.error(f"❌ FAIL: Some EMA bands do not match")
            for band, check in result['checks'].items():
                if check['status'] != 'PASS':
                    logger.error(f"  {band}: {check['message']}")
        
        ema_results.append({
            'symbol': symbol,
            'timeframe': tf,
            'status': 'PASS' if all_pass else 'FAIL',
            **{f'{band}_status': result['checks'].get(band, {}).get('status', 'N/A') 
               for band in ['fastU', 'fastL', 'slowU', 'slowL']}
        })
    
    # Part 2: ret_fwd usage check
    logger.info("\n--- Part 2: ret_fwd_* Usage Check ---")
    ret_fwd_findings = check_ret_fwd_usage_in_code()
    
    # Generate report
    report_file = results_dir / "ladder_signal_check_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Ladder Signal Check Report\n\n")
        f.write("## Part 1: EMA Causality Check\n\n")
        try:
            f.write(pd.DataFrame(ema_results).to_markdown(index=False))
        except ImportError:
            # Fallback if tabulate not available
            df = pd.DataFrame(ema_results)
            f.write(df.to_string(index=False))
        f.write("\n\n## Part 2: ret_fwd_* Usage Check\n\n")
        try:
            f.write(pd.DataFrame(ret_fwd_findings).to_markdown(index=False))
        except ImportError:
            # Fallback if tabulate not available
            df = pd.DataFrame(ret_fwd_findings)
            f.write(df.to_string(index=False))
        f.write("\n\n## Conclusion\n\n")
        
        ema_pass = all(r['status'] == 'PASS' for r in ema_results)
        ret_fwd_pass = all(f['status'] == 'PASS' for f in ret_fwd_findings)
        
        if ema_pass and ret_fwd_pass:
            f.write("✅ **PASS**: All checks passed\n")
        else:
            f.write("⚠️ **REVIEW NEEDED**: Some checks require attention\n")
    
    logger.info(f"\n✅ Report saved to: {report_file}")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_ladder_signal_checks()

