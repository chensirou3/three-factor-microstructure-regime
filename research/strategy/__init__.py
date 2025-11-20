"""
Strategy Phase 1: Regime-aware baseline strategy and backtest.

This module implements a simple trend-following baseline strategy wrapped with
three-factor regime information for gating and position sizing.

Modules:
- baseline_strategy: Simple EMA-based trend-following (regime-agnostic)
- regime_wrapper: Apply three-factor regime rules (gating & sizing)
- backtest_engine: Event-based backtester with regime-conditioned performance
- run_regime_strategy: Orchestrator script to run full pipeline
"""

__version__ = "0.1.0"

