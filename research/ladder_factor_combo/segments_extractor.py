"""
Direction 1: Extract Ladder trend segments

Extract continuous Ladder upTrend/downTrend periods as segments for analysis.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import logging
from dataclasses import dataclass
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SegmentConfig:
    """Configuration for segment extraction."""
    root: Path
    symbols: List[str]
    timeframes: List[str]
    merged_dir: str
    ladder_dir: str
    min_segment_bars: int = 3
    output_dir: Path = None


def extract_ladder_segments(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    min_segment_bars: int = 3
) -> pd.DataFrame:
    """
    Extract Ladder trend segments from dataframe.
    
    Args:
        df: DataFrame with ladder_state column (+1 upTrend, -1 downTrend, 0 neutral)
        symbol: Symbol name
        timeframe: Timeframe
        min_segment_bars: Minimum bars for a valid segment
    
    Returns:
        DataFrame where each row is one segment with:
            - symbol, timeframe
            - segment_id
            - direction ('up' or 'down')
            - start_time, end_time
            - length_bars
            - segment_return (close_end / close_start - 1)
            - segment_max_drawdown
            - segment_max_runup
    """
    df = df.copy().reset_index(drop=True)
    
    # Ensure ladder_state exists
    if 'ladder_state' not in df.columns:
        logger.warning(f"No ladder_state column for {symbol}_{timeframe}, skipping")
        return pd.DataFrame()
    
    segments = []
    segment_id = 0
    
    # Track current segment
    current_state = 0
    segment_start_idx = None
    
    for idx in range(len(df)):
        state = df.loc[idx, 'ladder_state']
        
        # State change or end of data
        if state != current_state or idx == len(df) - 1:
            # Save previous segment if valid
            if current_state != 0 and segment_start_idx is not None:
                segment_end_idx = idx - 1 if state != current_state else idx
                segment_length = segment_end_idx - segment_start_idx + 1
                
                if segment_length >= min_segment_bars:
                    segment_data = df.iloc[segment_start_idx:segment_end_idx+1]
                    
                    # Calculate segment metrics
                    start_close = segment_data.iloc[0]['close']
                    end_close = segment_data.iloc[-1]['close']
                    segment_return = (end_close / start_close - 1) * 100  # Percentage
                    
                    # Calculate max drawdown and runup during segment
                    cumulative_returns = (segment_data['close'] / start_close - 1) * 100
                    max_runup = cumulative_returns.max()
                    max_drawdown = cumulative_returns.min()
                    
                    segments.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'segment_id': segment_id,
                        'direction': 'up' if current_state == 1 else 'down',
                        'start_time': segment_data.iloc[0]['timestamp'],
                        'end_time': segment_data.iloc[-1]['timestamp'],
                        'start_idx': segment_start_idx,
                        'end_idx': segment_end_idx,
                        'length_bars': segment_length,
                        'segment_return': segment_return,
                        'segment_max_drawdown': max_drawdown,
                        'segment_max_runup': max_runup,
                        'start_close': start_close,
                        'end_close': end_close,
                    })
                    segment_id += 1
            
            # Start new segment
            if state != 0:
                current_state = state
                segment_start_idx = idx
            else:
                current_state = 0
                segment_start_idx = None
    
    return pd.DataFrame(segments)


def run_extract_segments(cfg: SegmentConfig) -> None:
    """
    Extract segments for all symbol×timeframe combinations.
    
    Args:
        cfg: SegmentConfig with paths and parameters
    """
    logger.info("="*80)
    logger.info("Extracting Ladder trend segments")
    logger.info(f"  Symbols: {len(cfg.symbols)}")
    logger.info(f"  Timeframes: {len(cfg.timeframes)}")
    logger.info(f"  Min segment bars: {cfg.min_segment_bars}")
    logger.info("="*80)
    
    all_segments = []
    
    for symbol in cfg.symbols:
        for timeframe in cfg.timeframes:
            logger.info(f"Processing {symbol} {timeframe}...")
            
            # Load Ladder-enriched data
            ladder_file = cfg.root / cfg.ladder_dir / f"ladder_{symbol}_{timeframe}.parquet"
            
            if not ladder_file.exists():
                logger.warning(f"  Ladder file not found: {ladder_file}")
                continue
            
            df = pd.read_parquet(ladder_file)
            
            # Extract segments
            segments = extract_ladder_segments(df, symbol, timeframe, cfg.min_segment_bars)
            
            if len(segments) > 0:
                # Save individual file
                output_file = cfg.output_dir / f"segments_{symbol}_{timeframe}.csv"
                segments.to_csv(output_file, index=False)
                logger.info(f"  ✓ Extracted {len(segments)} segments → {output_file.name}")
                
                all_segments.append(segments)
            else:
                logger.warning(f"  No segments extracted for {symbol}_{timeframe}")
    
    # Concatenate all segments
    if all_segments:
        all_segments_df = pd.concat(all_segments, ignore_index=True)
        all_file = cfg.output_dir / "segments_all.csv"
        all_segments_df.to_csv(all_file, index=False)
        logger.info("="*80)
        logger.info(f"✓ Total segments extracted: {len(all_segments_df)}")
        logger.info(f"✓ Saved to: {all_file}")
        logger.info("="*80)
    else:
        logger.warning("No segments extracted!")


def main():
    """Main entry point."""
    # Load config
    config_path = Path(__file__).parent / "config_ladder_factor.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    root = Path(__file__).resolve().parents[2]
    output_dir = root / config['outputs']['root']
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cfg = SegmentConfig(
        root=root,
        symbols=config['symbols'],
        timeframes=config['all_timeframes'],
        merged_dir=config['merged_dir'],
        ladder_dir=config['ladder_dir'],
        min_segment_bars=config['direction1']['min_segment_bars'],
        output_dir=output_dir
    )
    
    run_extract_segments(cfg)


if __name__ == "__main__":
    main()

