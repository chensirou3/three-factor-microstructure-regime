"""Test Ladder features generation on a small sample."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research.ladder.ladder_features import LadderConfig, generate_ladder_features_for_all

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    
    # Test on BTCUSD 4h only
    cfg = LadderConfig(
        root=root,
        symbols=['BTCUSD'],
        timeframes=['4h'],
        fast_len=25,
        slow_len=90
    )
    
    generate_ladder_features_for_all(cfg)

