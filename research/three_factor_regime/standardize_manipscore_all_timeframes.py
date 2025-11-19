"""
Standardize ManipScore (Factor 1) Outputs - All Timeframes

This script generates ManipScore data for ALL timeframes:
- 5min, 15min, 30min, 1h, 4h, 1d

For each symbol-timeframe combination.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Return the umbrella project root."""
    return Path(__file__).resolve().parent.parent.parent


def load_manip_csv(symbol: str, timeframe: str, manip_repo_path: Path) -> Optional[pd.DataFrame]:
    """
    Load ManipScore CSV from the market-manipulation repo.
    
    Returns DataFrame with columns: timestamp, ManipScore_raw
    """
    # Try different possible file naming patterns
    possible_patterns = [
        f"{symbol}_{timeframe}_manip_scores.csv",
        f"{symbol}_{timeframe}_manipulation_scores.csv",
        f"manip_scores_{symbol}_{timeframe}.csv",
        f"{symbol}_{timeframe}.csv"
    ]
    
    results_dir = manip_repo_path / "results"
    
    for pattern in possible_patterns:
        filepath = results_dir / pattern
        if filepath.exists():
            logger.info(f"  Found ManipScore file: {filepath.name}")
            df = pd.read_csv(filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            return df
    
    # If not found, return None
    logger.warning(f"  ManipScore CSV not found for {symbol} {timeframe}")
    return None


def standardize_manipscore_for_symbol_timeframe(
    symbol: str,
    timeframe: str,
    root: Path,
    manip_repo_subdir: str = "repos/market-manipulation",
    output_subdir: str = "data/factors/manip"
) -> bool:
    """
    Load ManipScore CSV, standardize, and save to parquet.
    
    Returns True if successful, False otherwise.
    """
    manip_repo_path = root / manip_repo_subdir
    
    logger.info(f"Processing {symbol} {timeframe}...")
    
    # Load ManipScore CSV
    df = load_manip_csv(symbol, timeframe, manip_repo_path)
    
    if df is None:
        logger.warning(f"  Skipping {symbol} {timeframe} - no ManipScore data found")
        return False
    
    # Check for ManipScore column
    score_col = None
    for possible_col in ['ManipScore', 'manip_score', 'manipulation_score', 'score']:
        if possible_col in df.columns:
            score_col = possible_col
            break
    
    if score_col is None:
        logger.error(f"  No ManipScore column found in {symbol} {timeframe}")
        return False
    
    # Standardize column names
    df = df.rename(columns={score_col: 'ManipScore_raw'})
    
    # Compute z-score normalization (within this symbol-timeframe panel)
    mean_score = df['ManipScore_raw'].mean()
    std_score = df['ManipScore_raw'].std()
    
    if std_score > 0:
        df['ManipScore_z'] = (df['ManipScore_raw'] - mean_score) / std_score
    else:
        df['ManipScore_z'] = 0.0
    
    # Create output DataFrame
    output_df = pd.DataFrame({
        'symbol': symbol,
        'timeframe': timeframe,
        'timestamp': df['timestamp'],
        'ManipScore_raw': df['ManipScore_raw'],
        'ManipScore_z': df['ManipScore_z']
    })
    
    # Save to parquet
    output_dir = root / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = f"manip_{symbol}_{timeframe}.parquet"
    output_path = output_dir / output_filename
    
    output_df.to_parquet(output_path, index=False)
    logger.info(f"  ✓ Saved to: {output_path.name}")
    logger.info(f"  Rows: {len(output_df)}, Non-null ManipScore: {output_df['ManipScore_z'].notna().sum()}")
    
    return True


def main():
    """Main entry point."""
    root = get_project_root()
    symbols = ["BTCUSD", "ETHUSD", "EURUSD"]
    timeframes = ["5min", "15min", "30min", "1h", "4h", "1d"]
    
    logger.info("=" * 80)
    logger.info("ManipScore Standardization - All Timeframes")
    logger.info("=" * 80)
    logger.info(f"Root: {root}")
    logger.info(f"Symbols: {symbols}")
    logger.info(f"Timeframes: {timeframes}")
    logger.info("")
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                success = standardize_manipscore_for_symbol_timeframe(
                    symbol, timeframe, root
                )
                if success:
                    success_count += 1
                else:
                    skip_count += 1
            except Exception as e:
                logger.error(f"Error processing {symbol} {timeframe}: {e}")
                fail_count += 1
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("STANDARDIZATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Skipped (no data): {skip_count}")
    logger.info(f"Failed (errors): {fail_count}")
    logger.info("")
    logger.info("✓ ManipScore standardization complete!")


if __name__ == "__main__":
    main()
