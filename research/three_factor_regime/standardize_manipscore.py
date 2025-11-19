"""
ManipScore Standardization Module

This module standardizes ManipScore outputs from the market-manipulation project
into a clean per-bar format for use in three-factor regime analysis.

Current ManipScore Source:
- Location: repos/market-manipulation/results/{SYMBOL}_{timeframe}_manipscore.csv
- Format: CSV with columns: timestamp, open, high, low, close, volume, ManipScore, ManipScore_z
- Computation: src/anomaly/ modules (price_volume_anomaly.py, structure_anomaly.py, etc.)

Target Schema:
- symbol: str
- timeframe: str  
- timestamp: datetime64[ns]
- ManipScore_raw: float (original ManipScore)
- ManipScore_z: float (z-score within symbol×timeframe)

Assumptions:
- ManipScore_z in source files is already computed within (symbol, timeframe) panel
- We will use existing ManipScore_z and rename ManipScore to ManipScore_raw
- Output format: Parquet files in data/factors/manip/manip_{symbol}_{timeframe}.parquet
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import pandas as pd
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ManipStandardizationConfig:
    """Configuration for ManipScore standardization"""
    root: Path  # Umbrella project root
    symbols: List[str]
    timeframes: List[str]
    
    @property
    def manip_repo_path(self) -> Path:
        """Path to market-manipulation repo"""
        return self.root / "repos" / "market-manipulation"
    
    @property
    def manip_results_path(self) -> Path:
        """Path to ManipScore results"""
        return self.manip_repo_path / "results"
    
    @property
    def output_path(self) -> Path:
        """Path to standardized output directory"""
        return self.root / "data" / "factors" / "manip"


def load_raw_manip_outputs(
    symbol: str,
    timeframe: str,
    cfg: ManipStandardizationConfig
) -> Optional[pd.DataFrame]:
    """
    Load raw ManipScore outputs for a given (symbol, timeframe).
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSD', 'ETHUSD', 'EURUSD')
        timeframe: Timeframe string (e.g., '4h', '1h', '30min')
        cfg: Configuration object
    
    Returns:
        DataFrame with at least (timestamp, ManipScore, ManipScore_z) or None if file not found
    """
    # Construct filename: {SYMBOL}_{timeframe}_manipscore.csv
    filename = f"{symbol}_{timeframe}_manipscore.csv"
    filepath = cfg.manip_results_path / filename
    
    if not filepath.exists():
        logger.warning(f"ManipScore file not found: {filepath}")
        return None
    
    logger.info(f"Loading ManipScore from: {filepath}")
    
    try:
        df = pd.read_csv(filepath)
        
        # Parse timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Check required columns
        required_cols = ['timestamp', 'ManipScore', 'ManipScore_z']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns {missing_cols} in {filepath}")
            return None
        
        logger.info(f"Loaded {len(df)} rows from {filename}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return None


def standardize_manip_df(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
) -> pd.DataFrame:
    """
    Standardize a ManipScore DataFrame to canonical schema.
    
    Args:
        df: Raw DataFrame with at least (timestamp, ManipScore, ManipScore_z)
        symbol: Asset symbol
        timeframe: Timeframe string
    
    Returns:
        Standardized DataFrame with columns:
            symbol, timeframe, timestamp, ManipScore_raw, ManipScore_z
    """
    # Create standardized DataFrame
    std_df = pd.DataFrame({
        'symbol': symbol,
        'timeframe': timeframe,
        'timestamp': df['timestamp'],
        'ManipScore_raw': df['ManipScore'],
        'ManipScore_z': df['ManipScore_z']
    })
    
    # Sort by timestamp
    std_df = std_df.sort_values('timestamp').reset_index(drop=True)
    
    # Log statistics
    logger.info(f"Standardized {symbol} {timeframe}:")
    logger.info(f"  Rows: {len(std_df)}")
    logger.info(f"  Date range: {std_df['timestamp'].min()} to {std_df['timestamp'].max()}")
    logger.info(f"  ManipScore_raw range: [{std_df['ManipScore_raw'].min():.4f}, {std_df['ManipScore_raw'].max():.4f}]")
    logger.info(f"  ManipScore_z range: [{std_df['ManipScore_z'].min():.4f}, {std_df['ManipScore_z'].max():.4f}]")
    logger.info(f"  Non-zero ManipScore: {(std_df['ManipScore_raw'] != 0).sum()} / {len(std_df)}")
    
    return std_df


def run_standardization(cfg: ManipStandardizationConfig) -> None:
    """
    Run standardization for all (symbol, timeframe) combinations.
    
    Args:
        cfg: Configuration object
    """
    # Create output directory if it doesn't exist
    cfg.output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {cfg.output_path}")
    
    # Track statistics
    total_processed = 0
    total_failed = 0
    
    # Loop through all combinations
    for symbol in cfg.symbols:
        for timeframe in cfg.timeframes:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {symbol} {timeframe}")
            logger.info(f"{'='*60}")
            
            try:
                # Load raw ManipScore data
                raw_df = load_raw_manip_outputs(symbol, timeframe, cfg)
                
                if raw_df is None:
                    logger.warning(f"Skipping {symbol} {timeframe} - no data found")
                    total_failed += 1
                    continue
                
                # Standardize
                std_df = standardize_manip_df(raw_df, symbol, timeframe)
                
                # Save to parquet
                output_filename = f"manip_{symbol}_{timeframe}.parquet"
                output_filepath = cfg.output_path / output_filename
                
                std_df.to_parquet(output_filepath, index=False)
                logger.info(f"✓ Saved to: {output_filepath}")
                
                total_processed += 1
                
            except Exception as e:
                logger.error(f"✗ Failed to process {symbol} {timeframe}: {e}")
                total_failed += 1
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info(f"STANDARDIZATION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Successfully processed: {total_processed}")
    logger.info(f"Failed: {total_failed}")
    logger.info(f"Output directory: {cfg.output_path}")


if __name__ == "__main__":
    # Detect umbrella project root via __file__
    # This file is at: ~/microstructure-three-factor-regime/research/three_factor_regime/standardize_manipscore.py
    # Root is 2 levels up
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]
    
    logger.info(f"Project root: {project_root}")
    
    # Define symbols and timeframes based on available data
    # From inspection, we have: BTCUSD, ETHUSD, EURUSD with 4h timeframe
    symbols = ['BTCUSD', 'ETHUSD', 'EURUSD']
    timeframes = ['4h']
    
    # Create configuration
    cfg = ManipStandardizationConfig(
        root=project_root,
        symbols=symbols,
        timeframes=timeframes
    )
    
    # Run standardization
    run_standardization(cfg)
    
    logger.info("\n✓ ManipScore standardization complete!")
    logger.info(f"Standardized files available at: {cfg.output_path}")
