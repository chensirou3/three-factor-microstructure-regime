"""
Test script for Phase 4 framework.
"""

import sys
from pathlib import Path
import yaml

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.phase4.accounts import load_accounts_from_config
from research.strategy.phase4.realistic_backtest import run_account_backtest_for_variant

def test_accounts():
    """Test account loading."""
    print("="*80)
    print("Testing Account Loading")
    print("="*80)

    root = Path(__file__).resolve().parents[3]
    config_path = root / "research/strategy/phase4/config_phase4.yaml"
    
    accounts = load_accounts_from_config(config_path)
    print(f"\nLoaded {len(accounts)} accounts:")
    for acc in accounts:
        print(f"  {acc}")
    
    print("\n✅ Account loading successful!")
    return accounts


def test_single_backtest():
    """Test a single backtest run."""
    print("\n" + "="*80)
    print("Testing Single Backtest: low_cost × V2 × BTCUSD × 1h")
    print("="*80)

    root = Path(__file__).resolve().parents[3]
    config_path = root / "research/strategy/phase4/config_phase4.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Load accounts
    accounts = load_accounts_from_config(config_path)
    low_cost_account = [a for a in accounts if a.id == 'low_cost'][0]
    
    # Get settings
    exp_config = config['experiments']
    merged_dir = root / exp_config['merged_data_dir']
    output_root = root / exp_config['output_root']
    phase3_cfg_path = root / exp_config['phase3_config_path']
    baseline_params = exp_config['baseline_params']
    high_riskscore = exp_config['high_riskscore']
    
    # Test parameters
    variant_id = "V2_medium_plus_high_scaled"
    symbol = "BTCUSD"
    timeframe = "1h"
    
    output_dir = output_root / low_cost_account.id / variant_id
    
    print(f"\nRunning backtest...")
    print(f"  Account: {low_cost_account.id} (cost={low_cost_account.cost_per_side_pct}%)")
    print(f"  Variant: {variant_id}")
    print(f"  Symbol: {symbol}")
    print(f"  Timeframe: {timeframe}")
    
    try:
        results = run_account_backtest_for_variant(
            account=low_cost_account,
            variant_id=variant_id,
            symbol=symbol,
            timeframe=timeframe,
            merged_path=merged_dir,
            phase3_cfg_path=phase3_cfg_path,
            baseline_params=baseline_params,
            high_riskscore=high_riskscore,
            output_dir=output_dir
        )
        
        print("\n✅ Backtest successful!")
        print(f"\nResults:")
        print(f"  Trades: {len(results['trades'])}")
        print(f"  Equity points: {len(results['equity'])}")
        
        summary = results['summary']
        if len(summary) > 0:
            print(f"  Total Return: {summary['total_return'].iloc[0]*100:.2f}%")
            print(f"  Ann Return: {summary['annualized_return'].iloc[0]*100:.2f}%")
            print(f"  Max DD: {summary['max_drawdown'].iloc[0]*100:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test 1: Account loading
    accounts = test_accounts()
    
    # Test 2: Single backtest
    success = test_single_backtest()
    
    if success:
        print("\n" + "="*80)
        print("✅ All tests passed! Phase 4 framework is ready.")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ Tests failed. Please check errors above.")
        print("="*80)
        sys.exit(1)

