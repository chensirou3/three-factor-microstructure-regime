"""
Check 4: Cost Sensitivity Analysis

Test D3 strategy performance under different transaction cost scenarios:
- low_cost: ~0.003% per side (institutional)
- high_cost: ~0.07% per side (retail)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from research.ladder_factor_combo.mtf_timing import (
    load_and_align_mtf_data,
    generate_mtf_timing_signals
)
from research.strategy.phase4.accounts import AccountConfig
from research.strategy.backtest_engine import run_backtest as core_run_backtest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_backtest_with_costs(
    df: pd.DataFrame,
    account: AccountConfig,
    symbol: str
) -> dict:
    """
    Compute backtest metrics with transaction costs using proper backtest engine.

    Args:
        df: DataFrame with signals (final_entry, final_exit, final_side, close)
        account: AccountConfig with cost settings
        symbol: Symbol name

    Returns:
        dict of metrics
    """
    df = df.copy()

    # Ensure required columns exist
    if 'position_size' not in df.columns:
        df['position_size'] = 1.0
        df.loc[df['final_side'] == 'flat', 'position_size'] = 0.0

    # Add ATR if not present (required by backtest engine)
    if 'ATR' not in df.columns:
        # Simple ATR approximation using close price volatility
        df['returns'] = df['close'].pct_change()
        df['ATR'] = df['returns'].rolling(14).std() * df['close']
        df['ATR'] = df['ATR'].fillna(df['ATR'].mean())

    # Add regime columns if not present (required by backtest engine)
    if 'RiskScore' not in df.columns:
        df['RiskScore'] = 0.5
    if 'risk_regime' not in df.columns:
        df['risk_regime'] = 'medium'
    if 'high_pressure' not in df.columns:
        df['high_pressure'] = False
    if 'three_factor_box' not in df.columns:
        df['three_factor_box'] = 'M_medium_O_medium_V_medium'

    # Convert cost from percentage to decimal
    cost_pct = account.cost_per_side_pct / 100.0

    # Run backtest using core engine
    try:
        backtest_results = core_run_backtest(
            df,
            symbol=symbol,
            timeframe='unknown',
            initial_equity=account.initial_equity,
            transaction_cost_pct=cost_pct,
            slippage_pct=0.0
        )

        trades_df = backtest_results['trades']
        equity_df = backtest_results['equity']
        summary_df = backtest_results['summary']

        if len(trades_df) == 0 or len(equity_df) == 0:
            return {
                'account_id': account.id,
                'cost_per_side_pct': account.cost_per_side_pct,
                'n_trades': 0,
                'total_return_gross': 0,
                'total_return_net': 0,
                'annualized_return_net': 0,
                'max_drawdown_net': 0,
                'sharpe_like_net': 0,
                'win_rate': 0,
                'avg_trade_return_net': 0,
            }

        # Extract metrics
        final_equity = equity_df['equity'].iloc[-1]
        total_return_net = (final_equity / account.initial_equity - 1) * 100

        # Annualized return
        days = (equity_df['timestamp'].iloc[-1] - equity_df['timestamp'].iloc[0]).days
        years = days / 365.25
        annualized_return_net = ((final_equity / account.initial_equity) ** (1 / years) - 1) * 100 if years > 0 else 0

        # Max drawdown
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        max_drawdown_net = equity_df['drawdown'].min()

        # Win rate
        wins = (trades_df['net_pnl'] > 0).sum()
        win_rate = (wins / len(trades_df) * 100) if len(trades_df) > 0 else 0

        # Sharpe-like (using R-multiples if available)
        if 'R_multiple' in trades_df.columns:
            r_multiples = trades_df['R_multiple'].dropna()
            sharpe_like_net = (r_multiples.mean() / r_multiples.std()) if len(r_multiples) > 1 and r_multiples.std() > 0 else 0
        else:
            sharpe_like_net = 0

        # Avg trade return
        avg_trade_return_net = trades_df['return_pct'].mean() if len(trades_df) > 0 else 0

        # Gross return (approximate by adding back costs)
        total_costs = trades_df['costs'].sum()
        total_return_gross = ((final_equity + total_costs) / account.initial_equity - 1) * 100

        return {
            'account_id': account.id,
            'cost_per_side_pct': account.cost_per_side_pct,
            'n_trades': len(trades_df),
            'total_return_gross': total_return_gross,
            'total_return_net': total_return_net,
            'annualized_return_net': annualized_return_net,
            'max_drawdown_net': max_drawdown_net,
            'sharpe_like_net': sharpe_like_net,
            'win_rate': win_rate,
            'avg_trade_return_net': avg_trade_return_net,
        }

    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        return {
            'account_id': account.id,
            'cost_per_side_pct': account.cost_per_side_pct,
            'n_trades': 0,
            'total_return_gross': 0,
            'total_return_net': 0,
            'annualized_return_net': 0,
            'max_drawdown_net': 0,
            'sharpe_like_net': 0,
            'win_rate': 0,
            'avg_trade_return_net': 0,
        }


def run_d3_cost_sensitivity(
    symbol: str,
    high_tf: str,
    low_tf: str,
    variant_id: str,
    accounts: list
) -> pd.DataFrame:
    """
    Run D3 backtest with different cost scenarios.
    
    Args:
        symbol: Symbol name
        high_tf: High timeframe
        low_tf: Low timeframe
        variant_id: D3 variant ID
        accounts: List of AccountConfig
    
    Returns:
        DataFrame with metrics for each account
    """
    logger.info(f"\nRunning cost sensitivity for {symbol} {high_tf}->{low_tf}...")
    
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
    
    # Generate D3 signals
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
    
    # Ensure timestamp
    low_with_signals['timestamp'] = pd.to_datetime(low_with_signals['timestamp'])
    
    # Run backtest for each account
    results = []
    for account in accounts:
        metrics = compute_backtest_with_costs(low_with_signals, account, symbol)
        results.append(metrics)
        logger.info(f"{account.id}: Net Return={metrics['total_return_net']:.2f}%, "
                   f"Sharpe={metrics['sharpe_like_net']:.3f}, Trades={metrics['n_trades']}")

    return pd.DataFrame(results)


def run_cost_sensitivity_checks():
    """
    Run cost sensitivity checks for key configurations.
    """
    logger.info("=" * 80)
    logger.info("CHECK 4: Cost Sensitivity Analysis")
    logger.info("=" * 80)
    
    results_dir = project_root / "results" / "ladder_factor_combo" / "sanity"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Define accounts
    accounts = [
        AccountConfig(id="low_cost", description="Institutional", initial_equity=10000, cost_per_side_pct=0.003),
        AccountConfig(id="high_cost", description="Retail", initial_equity=10000, cost_per_side_pct=0.07),
    ]
    
    # Test configurations
    configs = [
        ("BTCUSD", "4h", "30min"),
        ("BTCUSD", "4h", "1h"),
    ]
    
    variant_id = "D3_ladder_high_tf_dir_only"
    
    for symbol, high_tf, low_tf in configs:
        result_df = run_d3_cost_sensitivity(symbol, high_tf, low_tf, variant_id, accounts)
        
        if len(result_df) > 0:
            # Save results
            output_file = results_dir / f"d3_cost_sensitivity_{symbol}_{high_tf}_{low_tf}.csv"
            result_df.to_csv(output_file, index=False)
            logger.info(f"✅ Results saved to: {output_file}")
            
            # Display
            logger.info(f"\n{result_df.to_string(index=False)}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Cost sensitivity check complete")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_cost_sensitivity_checks()

