"""
Analyze regime-conditioned performance across all symbol×timeframe combinations.
Find optimal gating thresholds and identify truly risky regimes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_regime_performance():
    """Aggregate and analyze regime performance across all combinations."""
    
    results_dir = Path("results/strategy")
    
    # Collect all regime performance files
    risk_regime_files = list(results_dir.glob("perf_by_risk_regime_*.csv"))
    pressure_files = list(results_dir.glob("perf_by_pressure_*.csv"))
    box_files = list(results_dir.glob("perf_by_box_*.csv"))
    
    logger.info(f"Found {len(risk_regime_files)} risk_regime files")
    logger.info(f"Found {len(pressure_files)} pressure files")
    logger.info(f"Found {len(box_files)} box files")
    
    # 1. Analyze by risk_regime
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 1: Performance by Risk Regime")
    logger.info("="*80)
    
    all_risk_data = []
    for f in risk_regime_files:
        parts = f.stem.replace("perf_by_risk_regime_", "").split("_")
        symbol = parts[0]
        timeframe = "_".join(parts[1:])
        
        df = pd.read_csv(f)
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        all_risk_data.append(df)
    
    risk_df = pd.concat(all_risk_data, ignore_index=True)
    
    # Aggregate by risk_regime
    risk_summary = risk_df.groupby('risk_regime').agg({
        'n_trades': 'sum',
        'mean_R': 'mean',
        'median_R': 'mean',
        'win_rate_pct': 'mean',
        'total_pnl': 'sum'
    }).round(3)
    
    logger.info("\nAggregated Performance by Risk Regime:")
    logger.info(f"\n{risk_summary}")
    
    # 2. Analyze by high_pressure
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 2: Performance by High Pressure")
    logger.info("="*80)
    
    all_pressure_data = []
    for f in pressure_files:
        parts = f.stem.replace("perf_by_pressure_", "").split("_")
        symbol = parts[0]
        timeframe = "_".join(parts[1:])
        
        df = pd.read_csv(f)
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        all_pressure_data.append(df)
    
    pressure_df = pd.concat(all_pressure_data, ignore_index=True)
    
    # Aggregate by high_pressure
    pressure_summary = pressure_df.groupby('high_pressure').agg({
        'n_trades': 'sum',
        'mean_R': 'mean',
        'median_R': 'mean',
        'win_rate_pct': 'mean',
        'total_pnl': 'sum'
    }).round(3)
    
    logger.info("\nAggregated Performance by High Pressure:")
    logger.info(f"\n{pressure_summary}")
    
    # 3. Analyze by three_factor_box (top 10 and bottom 10)
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 3: Performance by Three-Factor Box")
    logger.info("="*80)
    
    all_box_data = []
    for f in box_files:
        parts = f.stem.replace("perf_by_box_", "").split("_")
        symbol = parts[0]
        timeframe = "_".join(parts[1:])
        
        df = pd.read_csv(f)
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        all_box_data.append(df)
    
    box_df = pd.concat(all_box_data, ignore_index=True)
    
    # Aggregate by box
    box_summary = box_df.groupby('three_factor_box').agg({
        'n_trades': 'sum',
        'mean_R': 'mean',
        'median_R': 'mean',
        'win_rate_pct': 'mean',
        'total_pnl': 'sum'
    }).round(3)
    
    # Sort by mean_R
    box_summary_sorted = box_summary.sort_values('mean_R', ascending=False)
    
    logger.info("\nTop 10 Best Performing Boxes (by mean_R):")
    logger.info(f"\n{box_summary_sorted.head(10)}")
    
    logger.info("\nTop 10 Worst Performing Boxes (by mean_R):")
    logger.info(f"\n{box_summary_sorted.tail(10)}")
    
    # 4. Find optimal gating thresholds
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 4: Optimal Gating Thresholds")
    logger.info("="*80)
    
    # Identify boxes with negative mean_R
    bad_boxes = box_summary_sorted[box_summary_sorted['mean_R'] < 0]
    logger.info(f"\nBoxes with NEGATIVE mean_R (should be blocked):")
    logger.info(f"\n{bad_boxes}")
    
    # Identify boxes with positive mean_R
    good_boxes = box_summary_sorted[box_summary_sorted['mean_R'] > 0]
    logger.info(f"\nBoxes with POSITIVE mean_R (should be allowed):")
    logger.info(f"\n{good_boxes}")
    
    # 5. Save aggregated results
    output_dir = Path("results/strategy/aggregated_analysis")
    output_dir.mkdir(exist_ok=True)
    
    risk_summary.to_csv(output_dir / "risk_regime_summary.csv")
    pressure_summary.to_csv(output_dir / "pressure_summary.csv")
    box_summary_sorted.to_csv(output_dir / "box_summary_sorted.csv")
    
    logger.info(f"\n✅ Saved aggregated analysis to {output_dir}/")
    
    # 6. Recommendations
    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATIONS")
    logger.info("="*80)
    
    # Check if high-risk regime is actually worse
    if 'high' in risk_summary.index and 'low' in risk_summary.index:
        high_mean_R = risk_summary.loc['high', 'mean_R']
        low_mean_R = risk_summary.loc['low', 'mean_R']
        
        if high_mean_R < low_mean_R:
            logger.info(f"\n✅ HIGH risk regime has LOWER mean_R ({high_mean_R:.3f}) than LOW ({low_mean_R:.3f})")
            logger.info("   → Gating high-risk entries makes sense")
        else:
            logger.info(f"\n⚠️  HIGH risk regime has HIGHER mean_R ({high_mean_R:.3f}) than LOW ({low_mean_R:.3f})")
            logger.info("   → Current regime definition may be inverted!")
    
    # Suggest boxes to block
    if len(bad_boxes) > 0:
        logger.info(f"\n📋 Suggested boxes to BLOCK ({len(bad_boxes)} total):")
        for box in bad_boxes.index[:5]:  # Top 5 worst
            logger.info(f"   - {box}: mean_R = {bad_boxes.loc[box, 'mean_R']:.3f}")
    
    logger.info("\n" + "="*80)
    logger.info("Analysis complete!")
    logger.info("="*80)

if __name__ == "__main__":
    analyze_regime_performance()

