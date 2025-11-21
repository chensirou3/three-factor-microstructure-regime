"""
Stage L2: Ladder + Three-Factor Regime Integration

This module integrates the Ladder trend indicator with the three-factor regime framework.

Key differences from EMA-based Phase 3:
- Trend engine: Ladder (EMA bands on high/low) instead of EMA crossover
- Regime policies: Reuse V0/V1/V2/V3 from Phase 3
- Goal: Compare Ladder vs EMA under same regime framework
"""

__version__ = "1.0.0"

