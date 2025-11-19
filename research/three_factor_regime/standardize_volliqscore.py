"""
Standardize VolLiqScore (Factor 3) Outputs

This script:
1. Loads raw bars data (OHLCV)
2. Computes VolLiqScore using the volume-liquidity-stress methodology
3. Saves standardized per-bar outputs to data/factors/vol_liq/

VolLiqScore = weight_vol * z_vol + weight_liq * z_liq_stress

Where:
- z_vol: Z-score of log(volume)
- z_liq_stress: Z-score of (range / ATR)

Author: Quant Research Team
Last Updated: 2025-11-20
"""

from pathlib import Path
import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Return the umbrella project root."""
    return Path(__file__).resolve().parent.parent.parent


def compute_log_volume_zscore(
    volume: pd.Series,
    lookback: int = 50,
    eps: float = 1e-10
) -> pd.Series:
    """Compute z-score of log(volume)."""
    vol = volume.clip(lower=eps)
    log_vol = np.log(vol)
    log_vol_mean = log_vol.rolling(window=lookback, min_periods=lookback//2).mean()
    log_vol_std = log_vol.rolling(window=lookback, min_periods=lookback//2).std()
    z_vol = (log_vol - log_vol_mean) / (log_vol_std + eps)
    return z_vol


def compute_true_range(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series
) -> pd.Series:
    """Compute True Range."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr


def compute_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    lookback: int = 50
) -> pd.Series:
    """Compute Average True Range."""
    tr = compute_true_range(high, low, close)
    atr = tr.rolling(window=lookback, min_periods=lookback//2).mean()
    return atr


def compute_liq_stress_zscore(
    high: pd.Series,
    low: pd.Series,
    atr: pd.Series,
    lookback: int = 50,
    eps: float = 1e-10
) -> pd.Series:
    """Compute z-score of liquidity stress (range / ATR)."""
    range_val = high - low
    liq_stress = range_val / (atr + eps)
    liq_mean = liq_stress.rolling(window=lookback, min_periods=lookback//2).mean()
    liq_std = liq_stress.rolling(window=lookback, min_periods=lookback//2).std()
    z_liq_stress = (liq_stress - liq_mean) / (liq_std + eps)
    return z_liq_stress


def compute_volliqscore(
    df: pd.DataFrame,
    lookback_vol: int = 50,
    lookback_atr: int = 50,
    lookback_liq_z: int = 50,
    weight_vol: float = 0.5,
    weight_liq: float = 0.5
) -> pd.DataFrame:
    """
    Compute VolLiqScore and intermediate factors.
    
    Returns DataFrame with columns:
    - z_vol: Volume surprise
    - ATR: Average True Range
    - z_liq_stress: Liquidity stress z-score
    - VolLiqScore: Combined score
    """
    result = pd.DataFrame(index=df.index)
    
    # Volume surprise
    result['z_vol'] = compute_log_volume_zscore(df['volume'], lookback_vol)
    
    # ATR
    result['ATR'] = compute_atr(df['high'], df['low'], df['close'], lookback_atr)
    
    # Liquidity stress
    result['z_liq_stress'] = compute_liq_stress_zscore(
        df['high'], df['low'], result['ATR'], lookback_liq_z
    )
    
    # Combined score
    result['VolLiqScore'] = weight_vol * result['z_vol'] + weight_liq * result['z_liq_stress']
    
    return result


def standardize_volliqscore_for_symbol_timeframe(
    symbol: str,
    timeframe: str,
    root: Path,
    raw_bar_subdir: str = "data/raw_bars/bars_with_ofi",
    output_subdir: str = "data/factors/vol_liq",
    timeframe_map: dict = None
) -> bool:
    """
    Load raw bars, compute VolLiqScore, save to parquet.
    
    Returns True if successful, False otherwise.
    """
    if timeframe_map is None:
        timeframe_map = {"4h": "4H", "1h": "1H", "2h": "2H", "8h": "8H", "1d": "1D"}
    
    file_tf = timeframe_map.get(timeframe, timeframe.upper())
    input_filename = f"{symbol}_{file_tf}_merged_bars_with_ofi.csv"
    input_path = root / raw_bar_subdir / input_filename
    
    if not input_path.exists():
        logger.warning(f"Raw bars file not found: {input_path}")
        return False
    
    logger.info(f"Processing {symbol} {timeframe}...")
    logger.info(f"  Loading from: {input_path.name}")
    
    # Load raw bars
    df = pd.read_csv(input_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    
    # Check required columns
    required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return False
    
    # Compute VolLiqScore
    logger.info(f"  Computing VolLiqScore...")
    vol_liq_df = compute_volliqscore(df)
    
    # Create output DataFrame
    output_df = pd.DataFrame({
        'symbol': symbol,
        'timeframe': timeframe,
        'timestamp': df['timestamp'],
        'z_vol': vol_liq_df['z_vol'],
        'ATR': vol_liq_df['ATR'],
        'z_liq_stress': vol_liq_df['z_liq_stress'],
        'VolLiqScore': vol_liq_df['VolLiqScore']
    })
    
    # Save to parquet
    output_dir = root / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = f"vol_liq_{symbol}_{timeframe}.parquet"
    output_path = output_dir / output_filename
    
    output_df.to_parquet(output_path, index=False)
    logger.info(f"  Saved to: {output_path.name}")
    logger.info(f"  Rows: {len(output_df)}, Non-null VolLiqScore: {output_df['VolLiqScore'].notna().sum()}")
    
    return True


def main():
    """Main entry point."""
    root = get_project_root()
    symbols = ["BTCUSD", "ETHUSD", "EURUSD"]
    timeframes = ["4h"]
    
    logger.info("=" * 80)
    logger.info("VolLiqScore Standardization")
    logger.info("=" * 80)
    logger.info(f"Root: {root}")
    logger.info(f"Symbols: {symbols}")
    logger.info(f"Timeframes: {timeframes}")
    logger.info("")
    
    success_count = 0
    fail_count = 0
    
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                success = standardize_volliqscore_for_symbol_timeframe(
                    symbol, timeframe, root
                )
                if success:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                logger.error(f"Error processing {symbol} {timeframe}: {e}")
                fail_count += 1
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("STANDARDIZATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Failed: {fail_count}")
    logger.info("")
    logger.info("✓ VolLiqScore standardization complete!")


if __name__ == "__main__":
    main()
