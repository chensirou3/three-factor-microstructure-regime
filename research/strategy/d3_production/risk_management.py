"""
Risk Management Layer for D3 Production Strategy.

Wraps pure D3 signals with:
- Position sizing
- ATR-based stop loss
- Maximum holding period enforcement
- Daily loss limits
- Portfolio-level exposure control
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    """Risk management configuration."""
    base_notional: float = 1000.0
    max_positions_per_symbol: int = 1
    max_total_positions: int = 3
    atr_stop_R: float = 3.0
    use_atr_stop: bool = True
    max_holding_bars: int = 200
    daily_loss_limit_pct: float = 5.0
    use_daily_limit: bool = True
    max_portfolio_exposure_pct: float = 30.0


@dataclass
class PositionState:
    """Track state of an open position."""
    entry_idx: int
    entry_price: float
    entry_atr: float
    notional: float
    bars_held: int
    stop_price: Optional[float] = None


def calculate_position_size(
    base_notional: float,
    current_equity: float,
    max_exposure_pct: float,
    current_exposure: float
) -> float:
    """
    Calculate position size based on risk limits.
    
    Args:
        base_notional: Base position size in USD
        current_equity: Current account equity
        max_exposure_pct: Maximum portfolio exposure as % of equity
        current_exposure: Current total exposure across all positions
    
    Returns:
        Position notional (0 if risk limits prevent opening)
    """
    max_allowed_exposure = current_equity * (max_exposure_pct / 100.0)
    remaining_capacity = max_allowed_exposure - current_exposure
    
    if remaining_capacity < base_notional:
        logger.warning(
            f"Insufficient exposure capacity: "
            f"remaining={remaining_capacity:.2f}, required={base_notional:.2f}"
        )
        return 0.0
    
    return base_notional


def calculate_atr_stop(
    entry_price: float,
    entry_atr: float,
    atr_stop_R: float,
    side: str = 'long'
) -> float:
    """
    Calculate ATR-based stop loss price.
    
    Args:
        entry_price: Entry price
        entry_atr: ATR value at entry
        atr_stop_R: Number of ATRs for stop distance
        side: Position side ('long' or 'short')
    
    Returns:
        Stop loss price
    """
    if side == 'long':
        stop_price = entry_price - (atr_stop_R * entry_atr)
    else:
        stop_price = entry_price + (atr_stop_R * entry_atr)
    
    return stop_price


def check_stop_hit(
    current_price: float,
    stop_price: float,
    side: str = 'long'
) -> bool:
    """
    Check if stop loss has been hit.
    
    Args:
        current_price: Current market price
        stop_price: Stop loss price
        side: Position side ('long' or 'short')
    
    Returns:
        True if stop has been hit
    """
    if side == 'long':
        return current_price <= stop_price
    else:
        return current_price >= stop_price


def apply_risk_management(
    df: pd.DataFrame,
    risk_cfg: RiskConfig,
    initial_equity: float,
    atr_col: str = "ATR",
    symbol: str = "UNKNOWN"
) -> pd.DataFrame:
    """
    Apply risk management layer to D3 core signals.
    
    Input df must have:
    - d3_side, d3_entry, d3_exit (from D3 core)
    - close, high, low, timestamp
    - ATR column (for stop calculation)
    
    Applies:
    - Position sizing based on risk limits
    - ATR-based stop loss
    - Max holding period enforcement
    - Daily loss limit tracking
    
    Output df will have:
    - final_side, final_entry, final_exit (risk-adjusted signals)
    - position_notional
    - entry_price, stop_price (for tracking)
    - stop_hit (True if position closed by stop)
    
    Args:
        df: DataFrame with D3 core signals
        risk_cfg: Risk management configuration
        initial_equity: Starting equity for position sizing
        atr_col: Name of ATR column
        symbol: Symbol name for logging
    
    Returns:
        DataFrame with risk-managed signals
    """
    df = df.copy()
    
    # Initialize output columns
    df['final_side'] = 'flat'
    df['final_entry'] = False
    df['final_exit'] = False
    df['position_notional'] = 0.0
    df['entry_price'] = np.nan
    df['stop_price'] = np.nan
    df['stop_hit'] = False
    
    # Track state
    current_equity = initial_equity
    current_exposure = 0.0
    position: Optional[PositionState] = None
    daily_pnl = 0.0
    current_date = None
    trading_halted_today = False
    
    for idx in df.index:
        row = df.loc[idx]
        
        # Check if new trading day
        if current_date is None:
            current_date = pd.to_datetime(row['timestamp']).date()
        
        bar_date = pd.to_datetime(row['timestamp']).date()
        if bar_date != current_date:
            # New day: reset daily tracking
            current_date = bar_date
            daily_pnl = 0.0
            trading_halted_today = False

        # If in position, check stop loss first
        if position is not None:
            current_price = row['close']

            # Check ATR stop
            if risk_cfg.use_atr_stop and position.stop_price is not None:
                if check_stop_hit(current_price, position.stop_price, side='long'):
                    # Stop hit - force exit
                    df.loc[idx, 'final_exit'] = True
                    df.loc[idx, 'final_side'] = 'flat'
                    df.loc[idx, 'stop_hit'] = True

                    # Calculate PnL
                    pnl = (current_price - position.entry_price) * (position.notional / position.entry_price)
                    daily_pnl += pnl
                    current_equity += pnl
                    current_exposure -= position.notional

                    logger.info(
                        f"[{symbol}] Stop hit at {current_price:.2f}, "
                        f"entry={position.entry_price:.2f}, stop={position.stop_price:.2f}, "
                        f"PnL={pnl:.2f}"
                    )

                    position = None
                    continue

        # Check daily loss limit
        if risk_cfg.use_daily_limit and not trading_halted_today:
            daily_loss_limit = current_equity * (risk_cfg.daily_loss_limit_pct / 100.0)
            if daily_pnl <= -daily_loss_limit:
                trading_halted_today = True
                logger.warning(
                    f"[{symbol}] Daily loss limit hit: {daily_pnl:.2f} <= -{daily_loss_limit:.2f}"
                )

        # Process D3 signals
        if row['d3_entry'] and position is None and not trading_halted_today:
            # D3 wants to enter - check risk limits
            notional = calculate_position_size(
                risk_cfg.base_notional,
                current_equity,
                risk_cfg.max_portfolio_exposure_pct,
                current_exposure
            )

            if notional > 0:
                # Open position
                entry_price = row['close']
                entry_atr = row[atr_col] if atr_col in row.index else 0.0

                # Calculate stop
                stop_price = None
                if risk_cfg.use_atr_stop and entry_atr > 0:
                    stop_price = calculate_atr_stop(
                        entry_price, entry_atr, risk_cfg.atr_stop_R, side='long'
                    )

                position = PositionState(
                    entry_idx=idx,
                    entry_price=entry_price,
                    entry_atr=entry_atr,
                    notional=notional,
                    bars_held=0,
                    stop_price=stop_price
                )

                df.loc[idx, 'final_entry'] = True
                df.loc[idx, 'final_side'] = 'long'
                df.loc[idx, 'position_notional'] = notional
                df.loc[idx, 'entry_price'] = entry_price
                df.loc[idx, 'stop_price'] = stop_price if stop_price else np.nan

                current_exposure += notional

                stop_str = f"{stop_price:.2f}" if stop_price is not None else "None"
                logger.info(
                    f"[{symbol}] Entry at {entry_price:.2f}, "
                    f"notional={notional:.2f}, stop={stop_str}"
                )

        elif row['d3_exit'] and position is not None:
            # D3 wants to exit
            exit_price = row['close']

            df.loc[idx, 'final_exit'] = True
            df.loc[idx, 'final_side'] = 'flat'

            # Calculate PnL
            pnl = (exit_price - position.entry_price) * (position.notional / position.entry_price)
            daily_pnl += pnl
            current_equity += pnl
            current_exposure -= position.notional

            logger.info(
                f"[{symbol}] Exit at {exit_price:.2f}, "
                f"entry={position.entry_price:.2f}, PnL={pnl:.2f}"
            )

            position = None

        elif position is not None:
            # Continue holding
            position.bars_held += 1
            df.loc[idx, 'final_side'] = 'long'
            df.loc[idx, 'position_notional'] = position.notional
            df.loc[idx, 'entry_price'] = position.entry_price
            df.loc[idx, 'stop_price'] = position.stop_price if position.stop_price else np.nan

    return df

