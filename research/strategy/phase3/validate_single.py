"""
Validation script for Phase 3 - Test single symbol/timeframe

Tests all variants on BTCUSD 4h to validate framework before full run.
"""

import sys
from pathlib import Path
import yaml
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.phase3.experiment_runner import run_single_experiment
from research.strategy.phase3.regime_policies import load_policies_from_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_phase3_framework():
    """
    Run validation experiment on BTCUSD 4h for all variants.
    """
    logger.info("="*80)
    logger.info("PHASE 3 VALIDATION - BTCUSD 4h")
    logger.info("="*80)
    
    # Load config
    config_path = Path("research/strategy/phase3/config_phase3.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Load policies
    policies = load_policies_from_config(config_path)
    
    # Test parameters
    symbol = "BTCUSD"
    timeframe = "4h"
    data_dir = Path("data/factors/merged_three_factor")
    output_dir = Path("results/strategy/phase3_validation")
    
    # Run each variant
    results = []
    for policy_id, policy in policies.items():
        if not policy.enabled:
            logger.info(f"Skipping disabled variant: {policy_id}")
            continue
        
        try:
            logger.info(f"\nTesting {policy_id}...")
            summary = run_single_experiment(
                symbol=symbol,
                timeframe=timeframe,
                policy=policy,
                config=config,
                data_dir=data_dir,
                output_dir=output_dir
            )
            results.append(summary)
            
            logger.info(f"✅ {policy_id}: {summary['total_trades']} trades, "
                       f"Sharpe={summary['sharpe_like']:.4f}, "
                       f"Net R={summary['net_mean_R']:.3f}")
            
        except Exception as e:
            logger.error(f"❌ {policy_id} failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*80)
    
    if results:
        import pandas as pd
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('sharpe_like', ascending=False)
        
        logger.info(f"\nRanking by Sharpe-like:")
        for i, row in results_df.iterrows():
            logger.info(f"  {row['variant_id']:30s} | Sharpe: {row['sharpe_like']:7.4f} | "
                       f"Net R: {row['net_mean_R']:6.3f} | Trades: {int(row['total_trades']):5d}")
        
        # Save validation results
        validation_path = output_dir / "validation_summary.csv"
        results_df.to_csv(validation_path, index=False)
        logger.info(f"\n✅ Validation results saved to {validation_path}")
        
        logger.info("\n🎉 Validation complete! Framework is working correctly.")
        logger.info("Next step: Run full experiments with experiment_runner.py")
    else:
        logger.error("\n❌ No successful experiments. Check errors above.")
    
    return results


if __name__ == "__main__":
    validate_phase3_framework()

