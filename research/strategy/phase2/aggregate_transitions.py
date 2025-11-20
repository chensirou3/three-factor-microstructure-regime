"""
Quick script to aggregate transition matrices from Phase 2D
"""
import pandas as pd
from pathlib import Path
import numpy as np

# Paths
results_dir = Path("results/strategy/phase2/regime_persistence")

# Load all transition matrices
all_transitions = []

symbols = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]

for symbol in symbols:
    for timeframe in timeframes:
        file_path = results_dir / f"regime_transition_matrix_{symbol}_{timeframe}.csv"
        if file_path.exists():
            df = pd.read_csv(file_path, index_col=0)
            all_transitions.append(df)
            print(f"Loaded: {symbol}_{timeframe}")

# Average all transition matrices
if all_transitions:
    # Stack all matrices and compute mean
    avg_transition = pd.concat(all_transitions).groupby(level=0).mean()
    
    # Save
    output_path = results_dir / "regime_transition_matrix_aggregated.csv"
    avg_transition.to_csv(output_path)
    
    print(f"\n✅ Aggregated transition matrix saved to: {output_path}")
    print(f"\nAverage Transition Probabilities:")
    print(avg_transition)
else:
    print("❌ No transition matrices found!")

