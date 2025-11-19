#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Three-Factor Regime Features

This module constructs regime classification features based on three factors:
    - ManipScore (price-path abnormality)
    - OFI (order flow imbalance)
    - VolLiqScore (volume/liquidity stress)

Features constructed:
    - q_manip, q_ofi, q_vol: quantile scores [0,1]
    - high_pressure: all three factors > high_threshold
    - low_pressure: all three factors < low_threshold
    - three_factor_box: 2×2×2 classification (8 boxes)
    - RiskScore: unified risk intensity score
    - risk_regime: 3-level classification (low/medium/high)

Author: Three-Factor Regime Research Team
Date: 2025-11-20
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Dict
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
    return Path(__file__).parent.parent.parent


@dataclass
class RegimeFeatureConfig:
    """Configuration for regime feature construction."""
    high_threshold: float = 0.8
    low_threshold: float = 0.5
    
    # RiskScore weights (default: equal weights)
    risk_weights: Dict[str, float] = None
    
    # Risk regime thresholds
    risk_low_threshold: float = 0.3
    risk_high_threshold: float = 0.7
    
    def __post_init__(self):
        if self.risk_weights is None:
            self.risk_weights = {
                'manip': 1/3,
                'ofi': 1/3,
                'vol': 1/3
            }


def add_quantile_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add quantile scores for all three factors.
    
    Computes:
        - q_manip: from |ManipScore_z|
        - q_ofi: from OFI_abs_z
        - q_vol: from VolLiqScore
    
    Quantiles are computed within (symbol, timeframe) groups if those columns exist.
    """
    df = df.copy()
    
    # Check if we should group by symbol×timeframe
    group_cols = []
    if 'symbol' in df.columns and 'timeframe' in df.columns:
        group_cols = ['symbol', 'timeframe']
    
    # q_manip: from |ManipScore_z|
    if 'ManipScore_z' in df.columns:
        if group_cols:
            df['q_manip'] = df.groupby(group_cols)['ManipScore_z'].transform(
                lambda x: x.abs().rank(pct=True)
            )
        else:
            df['q_manip'] = df['ManipScore_z'].abs().rank(pct=True)
    
    # q_ofi: from OFI_abs_z
    if 'OFI_abs_z' in df.columns:
        if group_cols:
            df['q_ofi'] = df.groupby(group_cols)['OFI_abs_z'].rank(pct=True)
        else:
            df['q_ofi'] = df['OFI_abs_z'].rank(pct=True)
    
    # q_vol: from VolLiqScore
    if 'VolLiqScore' in df.columns:
        if group_cols:
            df['q_vol'] = df.groupby(group_cols)['VolLiqScore'].rank(pct=True)
        else:
            df['q_vol'] = df['VolLiqScore'].rank(pct=True)
    
    return df


def add_pressure_flags(df: pd.DataFrame, cfg: RegimeFeatureConfig) -> pd.DataFrame:
    """
    Add high_pressure and low_pressure flags.
    
    high_pressure: all three q_* > high_threshold
    low_pressure: all three q_* < low_threshold
    """
    df = df.copy()
    
    # Check if all quantile columns exist
    required_cols = ['q_manip', 'q_ofi', 'q_vol']
    if not all(col in df.columns for col in required_cols):
        logger.warning("Missing quantile columns, cannot compute pressure flags")
        return df
    
    # High pressure: all three factors high
    df['high_pressure'] = (
        (df['q_manip'] > cfg.high_threshold) &
        (df['q_ofi'] > cfg.high_threshold) &
        (df['q_vol'] > cfg.high_threshold)
    )
    
    # Low pressure: all three factors low
    df['low_pressure'] = (
        (df['q_manip'] < cfg.low_threshold) &
        (df['q_ofi'] < cfg.low_threshold) &
        (df['q_vol'] < cfg.low_threshold)
    )
    
    return df


def add_three_factor_box(df: pd.DataFrame, cfg: RegimeFeatureConfig) -> pd.DataFrame:
    """
    Add three_factor_box classification (2×2×2 = 8 boxes).
    
    Each factor is classified as high/low based on high_threshold.
    Box labels: "M_{high/low}_O_{high/low}_V_{high/low}"
    """
    df = df.copy()
    
    # Check if all quantile columns exist
    required_cols = ['q_manip', 'q_ofi', 'q_vol']
    if not all(col in df.columns for col in required_cols):
        logger.warning("Missing quantile columns, cannot compute three_factor_box")
        return df
    
    # Classify each factor as high/low
    M_high = df['q_manip'] > cfg.high_threshold
    O_high = df['q_ofi'] > cfg.high_threshold
    V_high = df['q_vol'] > cfg.high_threshold
    
    # Create box labels
    df['three_factor_box'] = (
        'M_' + np.where(M_high, 'high', 'low') + '_' +
        'O_' + np.where(O_high, 'high', 'low') + '_' +
        'V_' + np.where(V_high, 'high', 'low')
    )
    
    return df


def add_risk_score(df: pd.DataFrame, cfg: RegimeFeatureConfig) -> pd.DataFrame:
    """
    Add RiskScore: weighted combination of quantile scores.

    RiskScore = w_manip * q_manip + w_ofi * q_ofi + w_vol * q_vol

    Default: equal weights (1/3, 1/3, 1/3)
    """
    df = df.copy()

    # Check if all quantile columns exist
    required_cols = ['q_manip', 'q_ofi', 'q_vol']
    if not all(col in df.columns for col in required_cols):
        logger.warning("Missing quantile columns, cannot compute RiskScore")
        return df

    # Compute weighted RiskScore
    df['RiskScore'] = (
        cfg.risk_weights['manip'] * df['q_manip'] +
        cfg.risk_weights['ofi'] * df['q_ofi'] +
        cfg.risk_weights['vol'] * df['q_vol']
    )

    return df


def add_risk_regime(df: pd.DataFrame, cfg: RegimeFeatureConfig) -> pd.DataFrame:
    """
    Add risk_regime: 3-level classification based on RiskScore.

    - low: RiskScore < risk_low_threshold
    - medium: risk_low_threshold <= RiskScore < risk_high_threshold
    - high: RiskScore >= risk_high_threshold
    """
    df = df.copy()

    if 'RiskScore' not in df.columns:
        logger.warning("RiskScore not found, cannot compute risk_regime")
        return df

    df['risk_regime'] = pd.cut(
        df['RiskScore'],
        bins=[-np.inf, cfg.risk_low_threshold, cfg.risk_high_threshold, np.inf],
        labels=['low', 'medium', 'high']
    )

    return df


def add_three_factor_regime_features(df: pd.DataFrame, cfg: RegimeFeatureConfig) -> pd.DataFrame:
    """
    Add all three-factor regime features to DataFrame.

    Given merged data with ManipScore_z, OFI_abs_z, VolLiqScore, etc.,
    adds:
      - q_manip, q_ofi, q_vol
      - high_pressure, low_pressure
      - three_factor_box
      - RiskScore
      - risk_regime
    """
    logger.info("Adding three-factor regime features...")

    # Add quantile scores
    df = add_quantile_scores(df)
    logger.info("  ✓ Quantile scores added")

    # Add pressure flags
    df = add_pressure_flags(df, cfg)
    logger.info("  ✓ Pressure flags added")

    # Add three-factor box
    df = add_three_factor_box(df, cfg)
    logger.info("  ✓ Three-factor box added")

    # Add RiskScore
    df = add_risk_score(df, cfg)
    logger.info("  ✓ RiskScore added")

    # Add risk regime
    df = add_risk_regime(df, cfg)
    logger.info("  ✓ Risk regime added")

    return df


if __name__ == "__main__":
    # Example usage
    root = get_project_root()
    merged_root = root / "data" / "factors" / "merged_three_factor"

    # Load a sample merged file
    sample_file = merged_root / "merged_BTCUSD_4h.parquet"
    if sample_file.exists():
        logger.info(f"Loading sample file: {sample_file.name}")
        df = pd.read_parquet(sample_file)

        # Add regime features
        cfg = RegimeFeatureConfig()
        df = add_three_factor_regime_features(df, cfg)

        # Display summary
        logger.info("\nRegime Feature Summary:")
        logger.info(f"  Total rows: {len(df):,}")
        logger.info(f"  High pressure: {df['high_pressure'].sum():,} ({df['high_pressure'].mean()*100:.1f}%)")
        logger.info(f"  Low pressure: {df['low_pressure'].sum():,} ({df['low_pressure'].mean()*100:.1f}%)")
        logger.info(f"\nThree-factor box distribution:")
        logger.info(df['three_factor_box'].value_counts())
        logger.info(f"\nRisk regime distribution:")
        logger.info(df['risk_regime'].value_counts())
        logger.info(f"\nRiskScore statistics:")
        logger.info(df['RiskScore'].describe())
    else:
        logger.warning(f"Sample file not found: {sample_file}")
        logger.info("Please run data_loader.py first to generate merged files.")

