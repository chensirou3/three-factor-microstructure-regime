"""
Monitor Phase 3 experiment progress

Checks how many experiments have completed by counting result files.
"""

from pathlib import Path
import yaml

def monitor_progress():
    """Monitor experiment progress."""
    
    # Load config
    config_path = Path("research/strategy/phase3/config_phase3.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    exp_config = config['experiments']
    symbols = exp_config['symbols']
    timeframes = exp_config['timeframes']
    variants = [v['id'] for v in config['variants'] if v.get('enabled', True)]
    
    total_experiments = len(variants) * len(symbols) * len(timeframes)
    
    # Count completed experiments
    results_dir = Path(exp_config['output_dir'])
    completed = 0
    
    for variant_id in variants:
        variant_dir = results_dir / variant_id
        if not variant_dir.exists():
            continue
        
        for symbol in symbols:
            for timeframe in timeframes:
                summary_file = variant_dir / f"summary_{symbol}_{timeframe}.csv"
                if summary_file.exists():
                    completed += 1
    
    # Display progress
    progress_pct = (completed / total_experiments) * 100
    
    print("="*80)
    print("PHASE 3 EXPERIMENT PROGRESS")
    print("="*80)
    print(f"Completed: {completed}/{total_experiments} ({progress_pct:.1f}%)")
    print(f"Remaining: {total_experiments - completed}")
    print()
    
    # Show per-variant progress
    print("Per-variant progress:")
    for variant_id in variants:
        variant_dir = results_dir / variant_id
        variant_completed = 0
        
        if variant_dir.exists():
            for symbol in symbols:
                for timeframe in timeframes:
                    summary_file = variant_dir / f"summary_{symbol}_{timeframe}.csv"
                    if summary_file.exists():
                        variant_completed += 1
        
        variant_total = len(symbols) * len(timeframes)
        variant_pct = (variant_completed / variant_total) * 100
        print(f"  {variant_id:30s}: {variant_completed:3d}/{variant_total} ({variant_pct:5.1f}%)")
    
    print("="*80)
    
    return completed, total_experiments


if __name__ == "__main__":
    monitor_progress()

