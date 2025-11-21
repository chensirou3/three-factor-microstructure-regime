"""
Regime Policy Layer for Phase 3

Defines declarative policies for how to treat each regime:
- Entry permissions
- Position sizing multipliers
- Dynamic exit rules based on regime transitions
"""

from dataclasses import dataclass
from typing import Dict, Literal, List
from pathlib import Path
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Regime = Literal["low", "medium", "high"]


@dataclass
class RegimeAction:
    """Action to take for a specific regime"""
    allow_entry: bool
    size_multiplier: float


@dataclass
class DynamicExitRule:
    """Rules for dynamic exit based on regime changes"""
    enabled: bool
    high_persistence_bars: int = 0  # Exit if HIGH for this many consecutive bars


@dataclass
class RegimePolicy:
    """Complete policy definition for a strategy variant"""
    id: str
    description: str
    enabled: bool
    use_regime_policy: bool  # If False, use baseline behavior
    actions: Dict[Regime, RegimeAction]
    dynamic_exit: DynamicExitRule


def load_policies_from_config(cfg_path: Path) -> Dict[str, RegimePolicy]:
    """
    Parse config_phase3.yaml and construct regime policies.
    
    Args:
        cfg_path: Path to config_phase3.yaml
        
    Returns:
        Dictionary mapping policy_id to RegimePolicy object
    """
    with open(cfg_path, 'r') as f:
        config = yaml.safe_load(f)
    
    policies = {}
    
    for variant_cfg in config['variants']:
        variant_id = variant_cfg['id']
        policy_cfg = variant_cfg['policy']
        
        # Parse regime actions
        actions = {}
        if policy_cfg.get('use_regime_policy', False):
            for regime_name, regime_cfg in policy_cfg.get('regimes', {}).items():
                actions[regime_name] = RegimeAction(
                    allow_entry=regime_cfg['allow_entry'],
                    size_multiplier=regime_cfg['size_multiplier']
                )
        
        # Parse dynamic exit rules
        exit_cfg = policy_cfg.get('dynamic_exit', {})
        dynamic_exit = DynamicExitRule(
            enabled=exit_cfg.get('enabled', False),
            high_persistence_bars=exit_cfg.get('high_persistence_bars', 0)
        )
        
        # Create policy
        policy = RegimePolicy(
            id=variant_id,
            description=variant_cfg['description'],
            enabled=variant_cfg.get('enabled', True),
            use_regime_policy=policy_cfg.get('use_regime_policy', False),
            actions=actions,
            dynamic_exit=dynamic_exit
        )
        
        policies[variant_id] = policy
        
        logger.info(f"Loaded policy: {variant_id}")
        logger.info(f"  Description: {policy.description}")
        logger.info(f"  Use regime policy: {policy.use_regime_policy}")
        if policy.use_regime_policy:
            for regime, action in policy.actions.items():
                logger.info(f"    {regime}: entry={action.allow_entry}, size={action.size_multiplier}")
            if policy.dynamic_exit.enabled:
                logger.info(f"  Dynamic exit: HIGH persistence >= {policy.dynamic_exit.high_persistence_bars} bars")
    
    return policies


def get_regime_action(policy: RegimePolicy, regime: str) -> RegimeAction:
    """
    Get the action for a specific regime.
    
    Args:
        policy: RegimePolicy object
        regime: Regime name ('low', 'medium', 'high')
        
    Returns:
        RegimeAction for the specified regime
    """
    if not policy.use_regime_policy:
        # Default: allow all entries with full size
        return RegimeAction(allow_entry=True, size_multiplier=1.0)
    
    return policy.actions.get(regime, RegimeAction(allow_entry=False, size_multiplier=0.0))


if __name__ == "__main__":
    # Test loading policies
    config_path = Path("research/strategy/phase3/config_phase3.yaml")
    policies = load_policies_from_config(config_path)
    
    print(f"\nLoaded {len(policies)} policies:")
    for policy_id, policy in policies.items():
        print(f"\n{policy_id}:")
        print(f"  {policy.description}")
        print(f"  Enabled: {policy.enabled}")

