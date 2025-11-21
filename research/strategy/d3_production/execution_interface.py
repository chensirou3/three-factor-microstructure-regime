"""
Execution Interface for D3 Production Strategy.

Defines abstract interface for order execution that can be implemented
for different brokers (MT5, Interactive Brokers, Exness, etc.) or
for paper trading / backtesting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Order:
    """Represents a trading order."""
    symbol: str
    side: str           # 'buy' or 'sell'
    order_type: str     # 'market', 'limit', 'stop'
    quantity: float     # Position size (can be notional or lots depending on broker)
    price: Optional[float] = None       # For limit/stop orders
    stop_loss: Optional[float] = None   # Stop loss price
    take_profit: Optional[float] = None # Take profit price
    
    def __str__(self) -> str:
        parts = [
            f"{self.side.upper()} {self.quantity:.4f} {self.symbol}",
            f"@ {self.order_type.upper()}"
        ]
        if self.price:
            parts.append(f"price={self.price:.2f}")
        if self.stop_loss:
            parts.append(f"SL={self.stop_loss:.2f}")
        if self.take_profit:
            parts.append(f"TP={self.take_profit:.2f}")
        return " ".join(parts)


@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    side: str           # 'long' or 'short'
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class ExecutionInterface(ABC):
    """
    Abstract interface for order execution.
    
    Implementations should handle:
    - Order submission
    - Position management
    - Account information retrieval
    """
    
    @abstractmethod
    def send_order(self, order: Order) -> bool:
        """
        Send an order to the broker/exchange.
        
        Args:
            order: Order to execute
        
        Returns:
            True if order was successfully submitted
        """
        pass
    
    @abstractmethod
    def close_position(self, symbol: str) -> bool:
        """
        Close an open position for a symbol.
        
        Args:
            symbol: Symbol to close
        
        Returns:
            True if position was successfully closed
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict[str, Position]:
        """
        Get all open positions.
        
        Returns:
            Dictionary mapping symbol to Position
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, float]:
        """
        Get account information.
        
        Returns:
            Dictionary with keys like 'equity', 'balance', 'margin', etc.
        """
        pass
    
    @abstractmethod
    def modify_position(
        self,
        symbol: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """
        Modify stop loss / take profit for an open position.
        
        Args:
            symbol: Symbol to modify
            stop_loss: New stop loss price (None to leave unchanged)
            take_profit: New take profit price (None to leave unchanged)
        
        Returns:
            True if modification was successful
        """
        pass


class LoggingExecutionStub(ExecutionInterface):
    """
    Stub implementation that only logs execution requests.
    
    Used for:
    - Testing strategy logic without real execution
    - Paper trading simulation
    - Development and debugging
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.positions: Dict[str, Position] = {}
        self.account_equity = 10000.0
    
    def send_order(self, order: Order) -> bool:
        self.logger.info(f"[EXEC STUB] send_order: {order}")
        
        # Simulate position opening
        if order.side == 'buy':
            self.positions[order.symbol] = Position(
                symbol=order.symbol,
                side='long',
                quantity=order.quantity,
                entry_price=order.price if order.price else 0.0,
                current_price=order.price if order.price else 0.0,
                unrealized_pnl=0.0,
                stop_loss=order.stop_loss,
                take_profit=order.take_profit
            )
        
        return True
    
    def close_position(self, symbol: str) -> bool:
        self.logger.info(f"[EXEC STUB] close_position for {symbol}")
        
        if symbol in self.positions:
            del self.positions[symbol]
        
        return True
    
    def get_positions(self) -> Dict[str, Position]:
        return self.positions.copy()
    
    def get_account_info(self) -> Dict[str, float]:
        return {
            'equity': self.account_equity,
            'balance': self.account_equity,
            'margin': 0.0,
            'free_margin': self.account_equity
        }
    
    def modify_position(
        self,
        symbol: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        self.logger.info(
            f"[EXEC STUB] modify_position {symbol}: SL={stop_loss}, TP={take_profit}"
        )
        
        if symbol in self.positions:
            if stop_loss is not None:
                self.positions[symbol].stop_loss = stop_loss
            if take_profit is not None:
                self.positions[symbol].take_profit = take_profit
        
        return True

