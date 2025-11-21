"""
Strategy Phase 3: Regime-aware Strategy Variants & Systematic Experiments

This package implements a comprehensive experiment framework for testing
multiple regime-aware trading strategy variants.

Modules:
- regime_policies: Define regime-based entry/exit/sizing policies
- strategy_variants: Apply policies to baseline signals
- experiment_runner: Run systematic experiments across variants × symbols × timeframes
- performance_comparator: Aggregate and compare variant performance
- report_phase3: Generate automated summary reports

Strategy Variants:
- V0: Baseline (Phase 1/2 behavior for comparison)
- V1: Medium-only entries
- V2: Medium + High entries with scaled sizing
- V3: Medium-only entries with dynamic exit on High persistence
"""

__version__ = "3.0.0"
__author__ = "Quant Research Team"

