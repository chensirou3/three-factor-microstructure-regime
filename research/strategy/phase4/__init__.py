"""
Strategy Phase 4: Account-level Performance with Realistic Costs

This module evaluates strategy performance from a realistic account perspective,
incorporating actual transaction costs and computing practical metrics like
annualized returns, max drawdown, and equity curves.

Key Features:
- Two account types with different cost structures (0.003% vs 0.07%)
- Uses best Phase 3 variants (V2_medium_plus_high_scaled, V1_medium_only)
- Computes account-level metrics: total return, annualized return, max drawdown
- Generates equity curves and per-symbol performance breakdowns
- Produces practical, non-academic performance reports

Modules:
- accounts.py: Account models and cost functions
- realistic_backtest.py: Run backtests with per-account costs
- equity_analysis.py: Aggregate metrics and per-symbol performance
- plot_equity_curves.py: Generate equity curve visualizations
- report_phase4.py: Generate practical summary reports

Usage:
    # Run all Phase 4 backtests
    python3 -m research.strategy.phase4.realistic_backtest
    
    # Aggregate performance
    python3 -m research.strategy.phase4.equity_analysis
    
    # Generate plots
    python3 -m research.strategy.phase4.plot_equity_curves
    
    # Generate report
    python3 -m research.strategy.phase4.report_phase4
"""

__version__ = "1.0.0"
__author__ = "Microstructure Research Team"

