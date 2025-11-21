"""
Account models and cost functions for Phase 4.

Defines account configurations with different cost structures and
provides utilities for computing transaction costs.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import yaml


@dataclass
class AccountConfig:
    """
    Configuration for a trading account with specific cost structure.
    
    Attributes:
        id: Unique identifier for the account (e.g., "low_cost", "high_cost")
        description: Human-readable description
        initial_equity: Starting capital in USD
        cost_per_side_pct: Transaction cost as percentage per side (e.g., 0.003 for 0.003%)
    """
    id: str
    description: str
    initial_equity: float
    cost_per_side_pct: float
    
    def __repr__(self) -> str:
        return (f"AccountConfig(id='{self.id}', "
                f"cost={self.cost_per_side_pct}%, "
                f"equity=${self.initial_equity:,.0f})")


def load_accounts_from_config(cfg_path: Path) -> List[AccountConfig]:
    """
    Parse config_phase4.yaml and return a list of AccountConfig.
    
    Args:
        cfg_path: Path to config_phase4.yaml
        
    Returns:
        List of AccountConfig objects
    """
    with open(cfg_path, 'r') as f:
        config = yaml.safe_load(f)
    
    accounts = []
    for acc_dict in config.get('accounts', []):
        accounts.append(AccountConfig(
            id=acc_dict['id'],
            description=acc_dict['description'],
            initial_equity=acc_dict['initial_equity'],
            cost_per_side_pct=acc_dict['cost_per_side_pct']
        ))
    
    return accounts


def compute_trade_cost(
    notional: float,
    cost_per_side_pct: float,
    num_sides: int = 2
) -> float:
    """
    Compute transaction cost in currency for one trade.
    
    Args:
        notional: Trade size in currency (e.g., position value in USD)
        cost_per_side_pct: Cost as percentage per side (e.g., 0.003 for 0.003%)
        num_sides: Number of sides to charge (default 2 for entry + exit)
        
    Returns:
        Total transaction cost in currency
        
    Example:
        >>> compute_trade_cost(10000, 0.003, 2)
        0.6  # $10,000 * 0.003% * 2 = $0.60
    """
    return notional * (cost_per_side_pct / 100.0) * num_sides


def compute_cost_per_R(
    atr: float,
    cost_per_side_pct: float,
    num_sides: int = 2
) -> float:
    """
    Compute transaction cost in R-multiples.
    
    Since we use ATR-based position sizing, cost can be expressed as
    a fraction of 1R (where 1R = ATR).
    
    Args:
        atr: Average True Range (our risk unit)
        cost_per_side_pct: Cost as percentage per side
        num_sides: Number of sides to charge
        
    Returns:
        Cost in R-multiples
        
    Example:
        If ATR = $100 and cost = 0.003% per side:
        For a $10,000 position, cost = $0.60
        Cost in R = $0.60 / $100 = 0.006R
    """
    # Assuming position size is proportional to ATR
    # This is a simplified model; actual implementation may vary
    return (cost_per_side_pct / 100.0) * num_sides


if __name__ == "__main__":
    # Test loading accounts
    root = Path(__file__).resolve().parents[3]
    config_path = root / "research/strategy/phase4/config_phase4.yaml"
    accounts = load_accounts_from_config(config_path)
    
    print("Loaded accounts:")
    for acc in accounts:
        print(f"  {acc}")
        
        # Example cost calculation
        notional = 10000.0
        cost = compute_trade_cost(notional, acc.cost_per_side_pct)
        print(f"    Cost for ${notional:,.0f} trade: ${cost:.2f} ({cost/notional*100:.4f}%)")

