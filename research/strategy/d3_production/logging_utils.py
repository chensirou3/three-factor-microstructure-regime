"""
Logging utilities for D3 production strategy.

Provides standardized logging setup for production trading.
"""

import logging
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_dir: Path,
    level: str = "INFO",
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and optional console handlers.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Whether to also log to console
    
    Returns:
        Configured logger instance
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    log_file = log_dir / f"{name}.log"
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(logger.level)
    
    # Console handler (optional)
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(logger.level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    if console:
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    return logger


def log_trade_event(
    logger: logging.Logger,
    event_type: str,
    symbol: str,
    timestamp: str,
    price: float,
    size: Optional[float] = None,
    **kwargs
) -> None:
    """
    Log a trade event with standardized format.
    
    Args:
        logger: Logger instance
        event_type: Type of event (ENTRY, EXIT, STOP, etc.)
        symbol: Trading symbol
        timestamp: Event timestamp
        price: Trade price
        size: Position size (optional)
        **kwargs: Additional event details
    """
    msg_parts = [
        f"[{event_type}]",
        f"Symbol={symbol}",
        f"Time={timestamp}",
        f"Price={price:.2f}"
    ]
    
    if size is not None:
        msg_parts.append(f"Size={size:.4f}")
    
    for key, value in kwargs.items():
        msg_parts.append(f"{key}={value}")
    
    logger.info(" | ".join(msg_parts))


def log_performance_summary(
    logger: logging.Logger,
    summary: dict
) -> None:
    """
    Log performance summary metrics.
    
    Args:
        logger: Logger instance
        summary: Dictionary of performance metrics
    """
    logger.info("=" * 80)
    logger.info("PERFORMANCE SUMMARY")
    logger.info("=" * 80)
    
    for key, value in summary.items():
        if isinstance(value, float):
            logger.info(f"{key:30s}: {value:12.4f}")
        else:
            logger.info(f"{key:30s}: {value}")
    
    logger.info("=" * 80)


def log_risk_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    **kwargs
) -> None:
    """
    Log a risk management event.
    
    Args:
        logger: Logger instance
        event_type: Type of risk event (STOP_HIT, DAILY_LIMIT, etc.)
        message: Event message
        **kwargs: Additional event details
    """
    msg_parts = [f"[RISK:{event_type}]", message]
    
    for key, value in kwargs.items():
        msg_parts.append(f"{key}={value}")
    
    logger.warning(" | ".join(msg_parts))

