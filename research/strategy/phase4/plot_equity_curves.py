"""
Equity curve plotting for Phase 4.

Generates visual equity curve plots for selected account × variant × symbol × timeframe combinations.
"""

import sys
from pathlib import Path
from typing import List
import pandas as pd
import yaml
import logging
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from research.strategy.phase4.accounts import AccountConfig, load_accounts_from_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def plot_equity_curve(
    equity_df: pd.DataFrame,
    account_id: str,
    variant_id: str,
    symbol: str,
    timeframe: str,
    output_path: Path,
    figsize: tuple = (12, 6),
    dpi: int = 100
) -> None:
    """
    Plot equity curve and save as PNG.
    
    Args:
        equity_df: DataFrame with 'timestamp' and 'equity' columns
        account_id: Account identifier
        variant_id: Variant identifier
        symbol: Trading symbol
        timeframe: Timeframe
        output_path: Path to save PNG
        figsize: Figure size (width, height)
        dpi: Resolution
    """
    if equity_df.empty:
        logger.warning(f"Empty equity curve for {account_id} × {variant_id} × {symbol} × {timeframe}")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # Plot equity
    ax.plot(equity_df['timestamp'], equity_df['equity'], linewidth=1.5, color='#2E86AB')
    
    # Add horizontal line at initial equity
    initial_equity = equity_df['equity'].iloc[0]
    ax.axhline(y=initial_equity, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Initial Equity')
    
    # Formatting
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Equity ($)', fontsize=11)
    ax.set_title(f'Equity Curve: {account_id} × {variant_id} × {symbol} × {timeframe}', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    
    logger.info(f"Saved equity curve to {output_path}")


def plot_selected_equity_curves(
    phase4_root: Path,
    accounts: List[AccountConfig],
    variants: List[str],
    symbols_to_plot: List[str],
    timeframes_to_plot: List[str],
    figsize: tuple = (12, 6),
    dpi: int = 100
) -> None:
    """
    Generate equity curve plots for selected combinations.
    
    Args:
        phase4_root: Root directory for Phase 4 results
        accounts: List of account configurations
        variants: List of variant IDs
        symbols_to_plot: Symbols to plot
        timeframes_to_plot: Timeframes to plot
        figsize: Figure size
        dpi: Resolution
    """
    logger.info("Generating equity curve plots...")
    
    plots_dir = phase4_root / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    plot_count = 0
    
    for account in accounts:
        for variant_id in variants:
            for symbol in symbols_to_plot:
                for timeframe in timeframes_to_plot:
                    # Load equity file
                    equity_file = (phase4_root / account.id / variant_id / 
                                  f"equity_{symbol}_{timeframe}.csv")
                    
                    if not equity_file.exists():
                        logger.warning(f"Missing equity file: {equity_file}")
                        continue
                    
                    equity_df = pd.read_csv(equity_file)
                    equity_df['timestamp'] = pd.to_datetime(equity_df['timestamp'])
                    
                    # Generate plot
                    output_file = plots_dir / f"equity_{account.id}_{variant_id}_{symbol}_{timeframe}.png"
                    
                    plot_equity_curve(
                        equity_df=equity_df,
                        account_id=account.id,
                        variant_id=variant_id,
                        symbol=symbol,
                        timeframe=timeframe,
                        output_path=output_file,
                        figsize=figsize,
                        dpi=dpi
                    )
                    
                    plot_count += 1

    logger.info(f"Generated {plot_count} equity curve plots")


def run_plot_generation():
    """
    Run equity curve plot generation for Phase 4 results.
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
    output_root = root / exp_config['output_root']

    # Get strategy variants
    variants = [v['id'] for v in config['strategies']]

    # Get plotting settings
    plot_config = config.get('plotting', {})
    key_symbols = plot_config.get('key_symbols', ['BTCUSD', 'ETHUSD'])
    key_timeframes = plot_config.get('key_timeframes', ['1h', '4h', '1d'])
    figsize = tuple(plot_config.get('figsize', [12, 6]))
    dpi = plot_config.get('dpi', 100)

    logger.info("="*80)
    logger.info("Phase 4 Equity Curve Plotting")
    logger.info("="*80)
    logger.info(f"Plotting {len(key_symbols)} symbols × {len(key_timeframes)} timeframes")

    # Generate plots
    plot_selected_equity_curves(
        phase4_root=output_root,
        accounts=accounts,
        variants=variants,
        symbols_to_plot=key_symbols,
        timeframes_to_plot=key_timeframes,
        figsize=figsize,
        dpi=dpi
    )

    logger.info("="*80)
    logger.info("Equity curve plotting complete!")
    logger.info("="*80)


if __name__ == "__main__":
    run_plot_generation()

