"""
Sanity Check Suite for Ladder D3 Multi-timeframe Strategy

This module provides rigorous verification of the D3 strategy before production deployment.

Four key checks:
1. Multi-timeframe alignment (no look-ahead bias)
2. Ladder signal computation (EMA causality, no ret_fwd leakage)
3. Time-split out-of-sample test (2010-2018 vs 2019-2025)
4. Cost sensitivity analysis (0.003% vs 0.07% per side)
"""

__version__ = "1.0.0"

