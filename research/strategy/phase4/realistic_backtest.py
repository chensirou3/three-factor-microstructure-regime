"""
Realistic backtest runner with account-specific costs.

Runs backtests for each account × variant × symbol × timeframe combination,
applying realistic transaction costs and computing practical metrics.
"""

import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np
import yaml
import logging

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.baseline_strategy import generate_baseline_signals
from research.strategy.regime_wrapper import apply_regime_wrapper
from research.strategy.backtest_engine import run_backtest as core_run_backtest
from research.strategy.phase4.accounts import AccountConfig, load_accounts_from_config
from research.strategy.phase3.regime_policies import load_policies_from_config
from research.strategy.phase3.strategy_variants import apply_regime_policy_to_signals

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_max_drawdown(equity_series: pd.Series) -> float:
    """
    Compute maximum drawdown as percentage.
    
    Args:
        equity_series: Series of equity values over time
        
    Returns:
        Maximum drawdown as decimal (e.g., -0.15 for -15%)
    """
    cummax = equity_series.cummax()
    drawdown = (equity_series - cummax) / cummax
    return drawdown.min()


def compute_annualized_return(
    equity_series: pd.Series,
    timestamps: pd.Series,
) -> float:
    """
    Compute annualized return based on time span.
    
    Args:
        equity_series: Series of equity values
        timestamps: Corresponding timestamps
        
    Returns:
        Annualized return as decimal (e.g., 0.25 for 25% per year)
    """
    if len(equity_series) < 2:
        return 0.0
    
    initial_equity = equity_series.iloc[0]
    final_equity = equity_series.iloc[-1]
    
    if initial_equity <= 0:
        return 0.0
    
    total_return = (final_equity / initial_equity) - 1.0
    
    # Compute time span in years
    time_span_days = (timestamps.iloc[-1] - timestamps.iloc[0]).days
    if time_span_days <= 0:
        return 0.0
    
    years = time_span_days / 365.25
    
    # Annualize: (1 + total_return)^(1/years) - 1
    if total_return <= -1.0:  # Avoid negative base for fractional exponent
        return -1.0
    
    annualized_return = (1.0 + total_return) ** (1.0 / years) - 1.0
    
    return annualized_return


def load_merged_data(symbol: str, timeframe: str, merged_dir: Path) -> pd.DataFrame:
    """Load merged three-factor data for a symbol×timeframe."""
    filename = f"merged_{symbol}_{timeframe}.parquet"
    filepath = merged_dir / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Merged data not found: {filepath}")

    df = pd.read_parquet(filepath)
    logger.info(f"Loaded {len(df)} bars for {symbol}_{timeframe}")

    return df


def run_account_backtest_for_variant(
    account: AccountConfig,
    variant_id: str,
    symbol: str,
    timeframe: str,
    merged_path: Path,
    phase3_cfg_path: Path,
    baseline_params: dict,
    high_riskscore: float,
    output_dir: Path,
) -> Dict[str, pd.DataFrame]:
    """
    Run backtest for one account × variant × symbol × timeframe combination.

    Args:
        account: Account configuration with cost structure
        variant_id: Strategy variant ID (e.g., "V2_medium_plus_high_scaled")
        symbol: Trading symbol
        timeframe: Timeframe
        merged_path: Path to merged data directory
        phase3_cfg_path: Path to Phase 3 config (for regime policies)
        baseline_params: EMA parameters (fast_len, slow_len)
        high_riskscore: RiskScore threshold for high pressure
        output_dir: Output directory for results

    Returns:
        Dictionary with 'trades', 'equity', 'summary' DataFrames
    """
    logger.info(f"Running: {account.id} × {variant_id} × {symbol} × {timeframe}")

    # 1. Load data
    df = load_merged_data(symbol, timeframe, merged_path)

    # 2. Generate baseline EMA signals
    df = generate_baseline_signals(
        df,
        fast_len=baseline_params['fast_len'],
        slow_len=baseline_params['slow_len']
    )

    # 3. Apply regime wrapper with Phase 2 threshold
    gating_cfg = {
        'block_new_entries_in_high_pressure': True,
        'block_new_entries_in_triple_high_box': False
    }

    sizing_cfg = {
        'base_size': 1.0,
        'size_by_riskregime': {
            'low': 1.0,
            'medium': 0.7,
            'high': 0.3
        }
    }

    # Add high_pressure column based on RiskScore threshold
    df['high_pressure'] = df['RiskScore'] >= high_riskscore

    df = apply_regime_wrapper(
        df,
        gating_cfg=gating_cfg,
        sizing_cfg=sizing_cfg,
        triple_high_box_name="M_high_O_high_V_high"
    )

    # 4. Load Phase 3 regime policy and apply variant logic
    policies = load_policies_from_config(phase3_cfg_path)
    policy = policies[variant_id]

    df = apply_regime_policy_to_signals(df, policy)

    # 5. Run backtest with account-specific costs
    # Convert cost from percentage to decimal for backtest engine
    cost_pct = account.cost_per_side_pct / 100.0  # e.g., 0.003% -> 0.00003

    backtest_results = core_run_backtest(
        df,
        symbol=symbol,
        timeframe=timeframe,
        initial_equity=account.initial_equity,
        transaction_cost_pct=cost_pct,  # Per-side cost
        slippage_pct=0.0
    )

    trades_df = backtest_results['trades']
    equity_df = backtest_results['equity']
    summary = backtest_results['summary']

    # 6. Compute additional metrics
    if len(equity_df) > 0:
        equity_series = equity_df['equity']
        timestamps = equity_df['timestamp']

        max_dd = compute_max_drawdown(equity_series)
        ann_return = compute_annualized_return(equity_series, timestamps)

        total_return = (equity_series.iloc[-1] / account.initial_equity) - 1.0
    else:
        max_dd = 0.0
        ann_return = 0.0
        total_return = 0.0

    # 7. Add account-level metrics to summary
    summary['account_id'] = account.id
    summary['variant_id'] = variant_id
    summary['initial_equity'] = account.initial_equity
    summary['final_equity'] = equity_series.iloc[-1] if len(equity_series) > 0 else account.initial_equity
    summary['total_return'] = total_return
    summary['annualized_return'] = ann_return
    summary['max_drawdown'] = max_dd
    summary['cost_per_side_pct'] = account.cost_per_side_pct

    # 8. Save results
    output_dir.mkdir(parents=True, exist_ok=True)

    trades_file = output_dir / f"trades_{symbol}_{timeframe}.csv"
    equity_file = output_dir / f"equity_{symbol}_{timeframe}.csv"
    summary_file = output_dir / f"summary_{symbol}_{timeframe}.csv"

    trades_df.to_csv(trades_file, index=False)
    equity_df.to_csv(equity_file, index=False)
    summary.to_csv(summary_file, index=False)

    logger.info(f"Saved results to {output_dir}")
    logger.info(f"  Total Return: {total_return*100:.2f}%, Ann Return: {ann_return*100:.2f}%, Max DD: {max_dd*100:.2f}%")

    return {
        'trades': trades_df,
        'equity': equity_df,
        'summary': summary
    }


def run_phase4_backtests():
    """
    Run all Phase 4 backtests for all account × variant × symbol × timeframe combinations.
    """
    # Load configuration
    root = Path(__file__).resolve().parents[3]
    config_path = root / "research/strategy/phase4/config_phase4.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Load accounts
    accounts = load_accounts_from_config(config_path)

    # Get experiment settings
    exp_config = config['experiments']
    symbols = exp_config['symbols']
    timeframes = exp_config['timeframes']
    merged_dir = root / exp_config['merged_data_dir']
    output_root = root / exp_config['output_root']
    phase3_cfg_path = root / exp_config['phase3_config_path']
    baseline_params = exp_config['baseline_params']
    high_riskscore = exp_config['high_riskscore']

    # Get strategy variants
    variants = [v['id'] for v in config['strategies']]

    # Count total experiments
    total_experiments = len(accounts) * len(variants) * len(symbols) * len(timeframes)
    logger.info(f"Starting Phase 4: {total_experiments} backtests")
    logger.info(f"  Accounts: {len(accounts)}")
    logger.info(f"  Variants: {len(variants)}")
    logger.info(f"  Symbols: {len(symbols)}")
    logger.info(f"  Timeframes: {len(timeframes)}")

    completed = 0
    failed = 0

    # Run all combinations
    for account in accounts:
        for variant_id in variants:
            for symbol in symbols:
                for timeframe in timeframes:
                    try:
                        # Define output directory
                        output_dir = output_root / account.id / variant_id

                        # Run backtest
                        run_account_backtest_for_variant(
                            account=account,
                            variant_id=variant_id,
                            symbol=symbol,
                            timeframe=timeframe,
                            merged_path=merged_dir,
                            phase3_cfg_path=phase3_cfg_path,
                            baseline_params=baseline_params,
                            high_riskscore=high_riskscore,
                            output_dir=output_dir
                        )

                        completed += 1
                        logger.info(f"Progress: {completed}/{total_experiments} ({completed/total_experiments*100:.1f}%)")

                    except Exception as e:
                        failed += 1
                        logger.error(f"Failed: {account.id} × {variant_id} × {symbol} × {timeframe}")
                        logger.error(f"  Error: {e}")
                        continue

    logger.info("="*80)
    logger.info(f"Phase 4 backtests complete!")
    logger.info(f"  Completed: {completed}/{total_experiments}")
    logger.info(f"  Failed: {failed}")
    logger.info("="*80)


if __name__ == "__main__":
    run_phase4_backtests()

