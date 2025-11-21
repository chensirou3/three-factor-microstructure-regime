"""
Generate comprehensive sanity check summary report.

Aggregates results from all four checks into a single markdown report.
"""

import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_sanity_check_report():
    """
    Generate comprehensive sanity check summary report.
    """
    logger.info("=" * 80)
    logger.info("Generating Sanity Check Summary Report")
    logger.info("=" * 80)
    
    results_dir = project_root / "results" / "ladder_factor_combo" / "sanity"
    
    # Check if results exist
    if not results_dir.exists():
        logger.error(f"Results directory not found: {results_dir}")
        logger.error("Please run all sanity checks first!")
        return
    
    report_lines = []
    
    # Header
    report_lines.append("# Ladder D3 Strategy Sanity Check Report")
    report_lines.append("")
    report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Check 1: Multi-timeframe Alignment
    report_lines.append("## Check 1: Multi-timeframe Alignment (No Look-ahead Bias)")
    report_lines.append("")
    
    mtf_file = results_dir / "multitimeframe_alignment_report.csv"
    if mtf_file.exists():
        mtf_df = pd.read_csv(mtf_file)
        try:
            report_lines.append(mtf_df.to_markdown(index=False))
        except ImportError:
            report_lines.append(mtf_df.to_string(index=False))
        report_lines.append("")
        
        all_pass = all(mtf_df['status'] == 'PASS')
        if all_pass:
            report_lines.append("✅ **PASS**: No look-ahead violations detected in multi-timeframe alignment")
        else:
            report_lines.append("❌ **FAIL**: Look-ahead violations detected - see details above")
    else:
        report_lines.append("⚠️ **NOT RUN**: Multi-timeframe alignment check not found")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Check 2: Ladder Signal Check
    report_lines.append("## Check 2: Ladder Signal Computation")
    report_lines.append("")
    
    signal_file = results_dir / "ladder_signal_check_report.md"
    if signal_file.exists():
        with open(signal_file, 'r', encoding='utf-8') as f:
            signal_content = f.read()
        # Extract key parts
        report_lines.append("### Summary")
        report_lines.append("")
        if "PASS" in signal_content:
            report_lines.append("✅ **PASS**: Ladder EMA computation is causal, no ret_fwd_* usage in signal generation")
        else:
            report_lines.append("⚠️ **REVIEW NEEDED**: See detailed report for issues")
        report_lines.append("")
        report_lines.append(f"See full report: `{signal_file.name}`")
    else:
        report_lines.append("⚠️ **NOT RUN**: Ladder signal check not found")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Check 3: Time-split OOS
    report_lines.append("## Check 3: Time-split Out-of-Sample Test")
    report_lines.append("")
    
    oos_files = list(results_dir.glob("d3_timesplit_*.csv"))
    if oos_files:
        for oos_file in sorted(oos_files):
            config_name = oos_file.stem.replace("d3_timesplit_", "")
            report_lines.append(f"### {config_name}")
            report_lines.append("")
            
            oos_df = pd.read_csv(oos_file)
            try:
                report_lines.append(oos_df.to_markdown(index=False))
            except ImportError:
                report_lines.append(oos_df.to_string(index=False))
            report_lines.append("")
            
            # Analysis
            if len(oos_df) >= 2:
                is_row = oos_df[oos_df['segment'].str.contains('IS')].iloc[0]
                oos_row = oos_df[oos_df['segment'].str.contains('OOS')].iloc[0]
                
                oos_sharpe = oos_row['sharpe_like']
                oos_dd = oos_row['max_drawdown']
                
                if oos_sharpe > 0.2 and oos_dd > -20:
                    report_lines.append(f"✅ **STABLE**: OOS performance acceptable (Sharpe={oos_sharpe:.3f}, DD={oos_dd:.2f}%)")
                else:
                    report_lines.append(f"⚠️ **DEGRADED**: OOS performance shows degradation (Sharpe={oos_sharpe:.3f}, DD={oos_dd:.2f}%)")
            
            report_lines.append("")
    else:
        report_lines.append("⚠️ **NOT RUN**: Time-split OOS tests not found")
    
    report_lines.append("---")
    report_lines.append("")
    
    # Check 4: Cost Sensitivity
    report_lines.append("## Check 4: Cost Sensitivity Analysis")
    report_lines.append("")
    
    cost_files = list(results_dir.glob("d3_cost_sensitivity_*.csv"))
    if cost_files:
        for cost_file in sorted(cost_files):
            config_name = cost_file.stem.replace("d3_cost_sensitivity_", "")
            report_lines.append(f"### {config_name}")
            report_lines.append("")
            
            cost_df = pd.read_csv(cost_file)
            try:
                report_lines.append(cost_df.to_markdown(index=False))
            except ImportError:
                report_lines.append(cost_df.to_string(index=False))
            report_lines.append("")
            
            # Analysis
            if len(cost_df) >= 2:
                low_cost = cost_df[cost_df['account_id'] == 'low_cost'].iloc[0]
                high_cost = cost_df[cost_df['account_id'] == 'high_cost'].iloc[0]
                
                degradation = low_cost['annualized_return_net'] - high_cost['annualized_return_net']
                
                if high_cost['annualized_return_net'] > 10:
                    report_lines.append(f"✅ **ROBUST**: Strategy remains profitable under high cost (degradation: {degradation:.2f}%)")
                else:
                    report_lines.append(f"⚠️ **SENSITIVE**: Strategy performance significantly impacted by high cost")
            
            report_lines.append("")
    else:
        report_lines.append("⚠️ **NOT RUN**: Cost sensitivity tests not found")
    
    report_lines.append("---")
    report_lines.append("")
    
    # Overall Conclusion
    report_lines.append("## Overall Conclusion")
    report_lines.append("")
    
    # Count passes
    checks_run = sum([
        mtf_file.exists(),
        signal_file.exists(),
        len(oos_files) > 0,
        len(cost_files) > 0
    ])
    
    if checks_run == 4:
        report_lines.append("### ✅ All Checks Complete")
        report_lines.append("")
        report_lines.append("All four sanity checks have been executed. Review the results above to determine if the D3 strategy is ready for production consideration.")
        report_lines.append("")
        report_lines.append("**Next Steps**:")
        report_lines.append("1. Review any warnings or failures above")
        report_lines.append("2. If all checks pass, proceed to production code review")
        report_lines.append("3. Set up small capital testing environment")
        report_lines.append("4. Implement monitoring and alerting")
    else:
        report_lines.append(f"### ⚠️ Incomplete ({checks_run}/4 checks run)")
        report_lines.append("")
        report_lines.append("Not all sanity checks have been completed. Please run:")
        if not mtf_file.exists():
            report_lines.append("- `python mtf_alignment_check.py`")
        if not signal_file.exists():
            report_lines.append("- `python ladder_signal_check.py`")
        if len(oos_files) == 0:
            report_lines.append("- `python time_split_oos_check.py`")
        if len(cost_files) == 0:
            report_lines.append("- `python cost_sensitivity_check.py`")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append(f"**Report generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Write report
    report_file = results_dir / "LADDER_D3_SANITY_CHECK_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logger.info(f"\n✅ Sanity check report generated: {report_file}")
    logger.info("=" * 80)
    
    # Also print to console
    print("\n" + '\n'.join(report_lines))


if __name__ == "__main__":
    generate_sanity_check_report()

