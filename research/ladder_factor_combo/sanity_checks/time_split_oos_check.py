"""
Check 3: Time-split Out-of-Sample Test

Split data into:
- In-sample (IS): 2010-01-01 to 2018-12-31
- Out-of-sample (OOS): 2019-01-01 to 2025-11-21

Run D3 strategy on both periods without retuning.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from research.ladder_factor_combo.mtf_timing import (
    load_and_align_mtf_data,
    generate_mtf_timing_signals
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_backtest_metrics(df: pd.DataFrame, segment_name: str) -> dict:
    """
    Compute backtest metrics for a segment.
    
    Args:
        df: DataFrame with signals and returns
        segment_name: Name of the segment (IS/OOS)
    
    Returns:
        dict of metrics
    """
    # Filter to trades
    trades = df[df['final_entry'] == True].copy()
    
    if len(trades) == 0:
        return {
            'segment': segment_name,
            'n_trades': 0,
            'total_return': 0,
            'annualized_return': 0,
            'max_drawdown': 0,
            'sharpe_like': 0,
            'win_rate': 0,
            'avg_trade_return': 0,
        }
    
    # Compute cumulative returns
    if 'ret_fwd_1' in df.columns:
        df['trade_return'] = df['final_entry'].shift(1).fillna(False) * df['ret_fwd_1']
    else:
        # Use close-to-close returns as proxy
        df['ret'] = df['close'].pct_change()
        df['trade_return'] = df['final_entry'].shift(1).fillna(False) * df['ret']
    
    df['cum_return'] = (1 + df['trade_return']).cumprod() - 1
    
    # Metrics
    total_return = df['cum_return'].iloc[-1] if len(df) > 0 else 0
    
    # Annualized return (assume 365 days per year)
    days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
    years = days / 365.25
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
    
    # Max drawdown
    cum_max = (1 + df['cum_return']).cummax()
    drawdown = (1 + df['cum_return']) / cum_max - 1
    max_drawdown = drawdown.min()
    
    # Sharpe-like
    trade_returns = df[df['trade_return'] != 0]['trade_return']
    sharpe_like = trade_returns.mean() / trade_returns.std() * np.sqrt(252) if len(trade_returns) > 0 and trade_returns.std() > 0 else 0
    
    # Win rate
    winning_trades = (trade_returns > 0).sum()
    win_rate = winning_trades / len(trade_returns) if len(trade_returns) > 0 else 0
    
    # Avg trade return
    avg_trade_return = trade_returns.mean() if len(trade_returns) > 0 else 0
    
    return {
        'segment': segment_name,
        'start_date': df['timestamp'].iloc[0].strftime('%Y-%m-%d'),
        'end_date': df['timestamp'].iloc[-1].strftime('%Y-%m-%d'),
        'n_trades': len(trades),
        'total_return': total_return * 100,  # percentage
        'annualized_return': annualized_return * 100,
        'max_drawdown': max_drawdown * 100,
        'sharpe_like': sharpe_like,
        'win_rate': win_rate * 100,
        'avg_trade_return': avg_trade_return * 100,
    }


def run_d3_timesplit_backtest(
    symbol: str,
    high_tf: str,
    low_tf: str,
    variant_id: str = "D3_ladder_high_tf_dir_only"
) -> pd.DataFrame:
    """
    Run D3 backtest with time-split IS/OOS.
    
    Args:
        symbol: Symbol name
        high_tf: High timeframe
        low_tf: Low timeframe
        variant_id: D3 variant ID
    
    Returns:
        DataFrame with IS and OOS metrics
    """
    logger.info(f"\nRunning time-split backtest for {symbol} {high_tf}->{low_tf}...")
    
    root = project_root
    ladder_dir = "data/ladder_features"
    
    # Load and align data
    try:
        high_df, low_aligned = load_and_align_mtf_data(
            symbol, high_tf, low_tf, root, ladder_dir
        )
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame()
    
    # Generate D3 signals (full history)
    use_factor_pullback = "factor_pullback" in variant_id
    pullback_conditions = {
        'volliq_range': [0.3, 0.7],
        'ofi_z_min': -0.5,
        'riskscore_max': 0.7
    }
    
    low_with_signals = generate_mtf_timing_signals(
        low_aligned,
        variant_id,
        use_factor_pullback,
        pullback_conditions
    )
    
    # Ensure timestamp is datetime
    low_with_signals['timestamp'] = pd.to_datetime(low_with_signals['timestamp'])

    # Split into IS and OOS (ensure timezone-aware comparison)
    if low_with_signals['timestamp'].dt.tz is not None:
        is_cutoff = pd.Timestamp('2018-12-31', tz='UTC')
        oos_start = pd.Timestamp('2019-01-01', tz='UTC')
    else:
        is_cutoff = pd.Timestamp('2018-12-31')
        oos_start = pd.Timestamp('2019-01-01')

    is_df = low_with_signals[low_with_signals['timestamp'] <= is_cutoff].copy()
    oos_df = low_with_signals[low_with_signals['timestamp'] >= oos_start].copy()
    
    logger.info(f"IS period: {len(is_df)} bars")
    logger.info(f"OOS period: {len(oos_df)} bars")
    
    # Compute metrics for each segment
    results = []
    
    if len(is_df) > 0:
        is_metrics = compute_backtest_metrics(is_df, "IS_2010_2018")
        results.append(is_metrics)
        logger.info(f"IS metrics: Return={is_metrics['total_return']:.2f}%, Sharpe={is_metrics['sharpe_like']:.3f}")
    
    if len(oos_df) > 0:
        oos_metrics = compute_backtest_metrics(oos_df, "OOS_2019_2025")
        results.append(oos_metrics)
        logger.info(f"OOS metrics: Return={oos_metrics['total_return']:.2f}%, Sharpe={oos_metrics['sharpe_like']:.3f}")
    
    return pd.DataFrame(results)


def run_time_split_oos_checks():
    """
    Run time-split OOS checks for key configurations.
    """
    logger.info("=" * 80)
    logger.info("CHECK 3: Time-split Out-of-Sample Test")
    logger.info("=" * 80)
    
    results_dir = project_root / "results" / "ladder_factor_combo" / "sanity"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Test configurations
    configs = [
        ("BTCUSD", "4h", "30min"),
        ("BTCUSD", "4h", "1h"),
    ]
    
    for symbol, high_tf, low_tf in configs:
        result_df = run_d3_timesplit_backtest(symbol, high_tf, low_tf)
        
        if len(result_df) > 0:
            # Save results
            output_file = results_dir / f"d3_timesplit_{symbol}_{high_tf}_{low_tf}.csv"
            result_df.to_csv(output_file, index=False)
            logger.info(f"✅ Results saved to: {output_file}")
            
            # Display
            logger.info(f"\n{result_df.to_string(index=False)}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Time-split OOS check complete")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_time_split_oos_checks()

