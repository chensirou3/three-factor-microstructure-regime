"""Test single Ladder + Regime experiment."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.ladder_phase.ladder_experiment_runner import run_single_ladder_experiment
from research.strategy.ladder_phase.ladder_regime_variants import load_ladder_policies_from_config

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    
    # Paths
    config_path = root / "research/strategy/ladder_phase/config_ladder_phase.yaml"
    ladder_dir = root / "data/ladder_features"
    output_dir = root / "results/strategy/ladder_phase"
    
    # Load policies
    policies = load_ladder_policies_from_config(config_path)
    
    # Test on BTCUSD 4h with L_V0_baseline
    result = run_single_ladder_experiment(
        symbol='BTCUSD',
        timeframe='4h',
        variant_id='L_V0_baseline',
        policy=policies['L_V0_baseline'],
        ladder_dir=ladder_dir,
        output_dir=output_dir,
        transaction_cost_bps=1.0
    )
    
    print(f"\nResult: {result}")

