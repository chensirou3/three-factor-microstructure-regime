"""
Run all sanity checks in sequence.

This is the main entry point for running the complete sanity check suite.
"""

import sys
from pathlib import Path
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


def run_all_sanity_checks():
    """
    Run all four sanity checks in sequence.
    """
    start_time = datetime.now()
    
    logger.info("=" * 80)
    logger.info("LADDER D3 STRATEGY - COMPLETE SANITY CHECK SUITE")
    logger.info("=" * 80)
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Import check modules
    from mtf_alignment_check import run_mtf_alignment_checks
    from ladder_signal_check import run_ladder_signal_checks
    from time_split_oos_check import run_time_split_oos_checks
    from cost_sensitivity_check import run_cost_sensitivity_checks
    from report_sanity_checks import generate_sanity_check_report
    
    checks = [
        ("Multi-timeframe Alignment", run_mtf_alignment_checks),
        ("Ladder Signal Computation", run_ladder_signal_checks),
        ("Time-split Out-of-Sample", run_time_split_oos_checks),
        ("Cost Sensitivity", run_cost_sensitivity_checks),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Running: {check_name}")
        logger.info(f"{'=' * 80}\n")
        
        try:
            check_func()
            results.append((check_name, "SUCCESS"))
            logger.info(f"\n✅ {check_name} completed successfully\n")
        except Exception as e:
            logger.error(f"\n❌ {check_name} failed with error: {e}\n")
            results.append((check_name, f"FAILED: {e}"))
    
    # Generate summary report
    logger.info(f"\n{'=' * 80}")
    logger.info("Generating Summary Report")
    logger.info(f"{'=' * 80}\n")
    
    try:
        generate_sanity_check_report()
        results.append(("Summary Report", "SUCCESS"))
    except Exception as e:
        logger.error(f"Failed to generate summary report: {e}")
        results.append(("Summary Report", f"FAILED: {e}"))
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "=" * 80)
    logger.info("SANITY CHECK SUITE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duration: {duration}")
    logger.info("")
    logger.info("Results:")
    for check_name, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        logger.info(f"  {status_icon} {check_name}: {status}")
    logger.info("")
    
    success_count = sum(1 for _, status in results if status == "SUCCESS")
    total_count = len(results)
    
    if success_count == total_count:
        logger.info(f"🎉 All {total_count} checks completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Review the summary report: results/ladder_factor_combo/sanity/LADDER_D3_SANITY_CHECK_REPORT.md")
        logger.info("2. If all checks pass, proceed to production code review")
        logger.info("3. Set up small capital testing environment")
    else:
        logger.warning(f"⚠️ {total_count - success_count}/{total_count} checks failed or had issues")
        logger.warning("Please review the errors above and fix before proceeding")
    
    logger.info("=" * 80)


if __name__ == "__main__":
    run_all_sanity_checks()

