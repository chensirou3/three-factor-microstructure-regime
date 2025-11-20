"""
Simple event-based backtesting engine with regime-conditioned performance analysis.

Simulates long-only trading with:
- Entry/exit at bar close
- Position sizing based on regime
- Per-trade logging with regime information
- Regime-conditioned performance metrics

This is a diagnostic backtester designed to understand how strategy performance
varies across different regime states.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def run_backtest(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    initial_equity: float = 100000.0,
    transaction_cost_pct: float = 0.0,
    slippage_pct: float = 0.0
) -> Dict[str, pd.DataFrame]:
    """
    Run simple long-only backtest with regime tracking.
    
    Parameters
    ----------
    df : pd.DataFrame
        Must contain:
        - timestamp, close
        - final_side, final_entry, final_exit, position_size
        - ATR (or similar volatility measure)
        - Regime features: RiskScore, risk_regime, high_pressure, three_factor_box
    symbol : str
        Symbol being backtested
    timeframe : str
        Timeframe being backtested
    initial_equity : float
        Starting capital
    transaction_cost_pct : float
        Transaction cost as percentage of trade value (default 0.0)
    slippage_pct : float
        Slippage as percentage of price (default 0.0)
    
    Returns
    -------
    dict
        Dictionary with DataFrames:
        - 'trades': Per-trade log with regime info
        - 'equity': Equity curve
        - 'summary': Overall performance metrics
        - 'perf_by_risk_regime': Performance by risk_regime at entry
        - 'perf_by_pressure': Performance by high_pressure at entry
        - 'perf_by_box': Performance by three_factor_box at entry
    """
    logger.info(f"Running backtest for {symbol} {timeframe}")
    
    # Initialize tracking
    trades = []
    equity_curve = []
    
    current_equity = initial_equity
    in_trade = False
    entry_idx = None
    entry_price = None
    entry_size = None
    entry_regime_info = {}
    
    # Process each bar
    for idx in df.index:
        row = df.loc[idx]
        
        # Handle entry
        if row['final_entry'] and not in_trade:
            in_trade = True
            entry_idx = idx
            entry_price = row['close']
            entry_size = row['position_size']
            
            # Store regime info at entry
            entry_regime_info = {
                'RiskScore_entry': row.get('RiskScore', np.nan),
                'risk_regime_entry': row.get('risk_regime', 'unknown'),
                'high_pressure_entry': row.get('high_pressure', False),
                'three_factor_box_entry': row.get('three_factor_box', 'unknown'),
                'ATR_entry': row.get('ATR', np.nan)
            }
        
        # Handle exit
        elif row['final_exit'] and in_trade:
            exit_price = row['close']
            
            # Calculate PnL
            price_change = exit_price - entry_price
            gross_pnl = entry_size * price_change
            
            # Apply costs
            trade_value = entry_size * entry_price
            costs = trade_value * (transaction_cost_pct + slippage_pct) * 2  # Entry + exit
            net_pnl = gross_pnl - costs
            
            # Calculate R-multiple
            atr_entry = entry_regime_info.get('ATR_entry', np.nan)
            if not pd.isna(atr_entry) and atr_entry > 0:
                r_multiple = net_pnl / (atr_entry * entry_size)
            else:
                r_multiple = np.nan
            
            # Update equity
            current_equity += net_pnl
            
            # Log trade
            trade_record = {
                'symbol': symbol,
                'timeframe': timeframe,
                'entry_time': df.loc[entry_idx, 'timestamp'],
                'exit_time': row['timestamp'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'side': 'long',
                'position_size': entry_size,
                'gross_pnl': gross_pnl,
                'costs': costs,
                'net_pnl': net_pnl,
                'return_pct': (exit_price / entry_price - 1) * 100,
                'R_multiple': r_multiple,
                **entry_regime_info
            }
            trades.append(trade_record)
            
            # Reset trade state
            in_trade = False
            entry_idx = None
            entry_price = None
            entry_size = None
            entry_regime_info = {}
        
        # Record equity
        equity_curve.append({
            'timestamp': row['timestamp'],
            'equity': current_equity,
            'in_trade': in_trade
        })
    
    # Convert to DataFrames
    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame(equity_curve)
    
    # Calculate summary metrics
    summary_df = calculate_summary_metrics(trades_df, equity_df, initial_equity)
    
    # Calculate regime-conditioned performance
    perf_by_regime = calculate_performance_by_regime(trades_df)
    perf_by_pressure = calculate_performance_by_pressure(trades_df)
    perf_by_box = calculate_performance_by_box(trades_df)
    
    logger.info(f"Backtest complete: {len(trades_df)} trades, "
               f"Final equity: ${current_equity:,.2f}, "
               f"Return: {(current_equity/initial_equity - 1)*100:.2f}%")
    
    return {
        'trades': trades_df,
        'equity': equity_df,
        'summary': summary_df,
        'perf_by_risk_regime': perf_by_regime,
        'perf_by_pressure': perf_by_pressure,
        'perf_by_box': perf_by_box
    }


def calculate_summary_metrics(
    trades_df: pd.DataFrame,
    equity_df: pd.DataFrame,
    initial_equity: float
) -> pd.DataFrame:
    """Calculate overall performance summary metrics."""
    if len(trades_df) == 0:
        return pd.DataFrame([{
            'n_trades': 0,
            'total_return_pct': 0.0,
            'win_rate_pct': 0.0,
            'mean_R': 0.0,
            'median_R': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown_pct': 0.0
        }])

    final_equity = equity_df['equity'].iloc[-1]
    total_return = (final_equity / initial_equity - 1) * 100

    # Win rate
    wins = (trades_df['net_pnl'] > 0).sum()
    win_rate = wins / len(trades_df) * 100

    # R-multiples
    r_multiples = trades_df['R_multiple'].dropna()
    mean_r = r_multiples.mean() if len(r_multiples) > 0 else 0
    median_r = r_multiples.median() if len(r_multiples) > 0 else 0

    # Sharpe ratio (simplified: using trade returns)
    if len(r_multiples) > 1:
        sharpe = r_multiples.mean() / r_multiples.std() if r_multiples.std() > 0 else 0
    else:
        sharpe = 0

    # Max drawdown
    equity_df['peak'] = equity_df['equity'].cummax()
    equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
    max_dd = equity_df['drawdown'].min()

    return pd.DataFrame([{
        'n_trades': len(trades_df),
        'total_return_pct': round(total_return, 2),
        'win_rate_pct': round(win_rate, 2),
        'mean_R': round(mean_r, 3),
        'median_R': round(median_r, 3),
        'sharpe_ratio': round(sharpe, 3),
        'max_drawdown_pct': round(max_dd, 2),
        'mean_pnl': round(trades_df['net_pnl'].mean(), 2),
        'total_pnl': round(trades_df['net_pnl'].sum(), 2)
    }])


def calculate_performance_by_regime(trades_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate performance metrics grouped by risk_regime at entry."""
    if len(trades_df) == 0 or 'risk_regime_entry' not in trades_df.columns:
        return pd.DataFrame()

    grouped = trades_df.groupby('risk_regime_entry')

    results = []
    for regime, group in grouped:
        r_multiples = group['R_multiple'].dropna()

        results.append({
            'risk_regime': regime,
            'n_trades': len(group),
            'win_rate_pct': round((group['net_pnl'] > 0).sum() / len(group) * 100, 2),
            'mean_R': round(r_multiples.mean(), 3) if len(r_multiples) > 0 else np.nan,
            'median_R': round(r_multiples.median(), 3) if len(r_multiples) > 0 else np.nan,
            'tail_R_p5': round(r_multiples.quantile(0.05), 3) if len(r_multiples) > 0 else np.nan,
            'tail_R_p95': round(r_multiples.quantile(0.95), 3) if len(r_multiples) > 0 else np.nan,
            'mean_pnl': round(group['net_pnl'].mean(), 2),
            'total_pnl': round(group['net_pnl'].sum(), 2)
        })

    return pd.DataFrame(results)


def calculate_performance_by_pressure(trades_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate performance metrics grouped by high_pressure at entry."""
    if len(trades_df) == 0 or 'high_pressure_entry' not in trades_df.columns:
        return pd.DataFrame()

    grouped = trades_df.groupby('high_pressure_entry')

    results = []
    for pressure, group in grouped:
        r_multiples = group['R_multiple'].dropna()

        results.append({
            'high_pressure': pressure,
            'n_trades': len(group),
            'win_rate_pct': round((group['net_pnl'] > 0).sum() / len(group) * 100, 2),
            'mean_R': round(r_multiples.mean(), 3) if len(r_multiples) > 0 else np.nan,
            'median_R': round(r_multiples.median(), 3) if len(r_multiples) > 0 else np.nan,
            'mean_pnl': round(group['net_pnl'].mean(), 2),
            'total_pnl': round(group['net_pnl'].sum(), 2)
        })

    return pd.DataFrame(results)


def calculate_performance_by_box(trades_df: pd.DataFrame, min_trades: int = 5) -> pd.DataFrame:
    """Calculate performance metrics grouped by three_factor_box at entry."""
    if len(trades_df) == 0 or 'three_factor_box_entry' not in trades_df.columns:
        return pd.DataFrame()

    grouped = trades_df.groupby('three_factor_box_entry')

    results = []
    for box, group in grouped:
        # Only include boxes with enough trades
        if len(group) < min_trades:
            continue

        r_multiples = group['R_multiple'].dropna()

        results.append({
            'three_factor_box': box,
            'n_trades': len(group),
            'win_rate_pct': round((group['net_pnl'] > 0).sum() / len(group) * 100, 2),
            'mean_R': round(r_multiples.mean(), 3) if len(r_multiples) > 0 else np.nan,
            'median_R': round(r_multiples.median(), 3) if len(r_multiples) > 0 else np.nan,
            'mean_pnl': round(group['net_pnl'].mean(), 2),
            'total_pnl': round(group['net_pnl'].sum(), 2)
        })

    return pd.DataFrame(results).sort_values('mean_R', ascending=False)

