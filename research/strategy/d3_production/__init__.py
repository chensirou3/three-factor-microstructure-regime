"""
D3 Production Strategy Module.

Production-ready implementation of the D3 multi-timeframe Ladder strategy.
"""

from .d3_core import D3Config, D3Signal, generate_d3_signals_for_pair, align_high_low_tf_ladder
from .risk_management import RiskConfig, PositionState, apply_risk_management
from .execution_interface import ExecutionInterface, LoggingExecutionStub, Order, Position
from .logging_utils import setup_logger, log_trade_event, log_performance_summary, log_risk_event

__all__ = [
    # Core strategy
    'D3Config',
    'D3Signal',
    'generate_d3_signals_for_pair',
    'align_high_low_tf_ladder',
    
    # Risk management
    'RiskConfig',
    'PositionState',
    'apply_risk_management',
    
    # Execution
    'ExecutionInterface',
    'LoggingExecutionStub',
    'Order',
    'Position',
    
    # Logging
    'setup_logger',
    'log_trade_event',
    'log_performance_summary',
    'log_risk_event',
]

