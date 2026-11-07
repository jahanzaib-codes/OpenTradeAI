"""
OpenTradeAI - Abstract Broker Adapter Interface
Standardizes order execution, account querying, and position tracking across IBKR, MT5, and Crypto exchanges.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from packages.core.models import (
    TradeOrder,
    Position,
    AccountSummary,
    MarketDataTick
)


class BaseBrokerAdapter(ABC):
    @abstractmethod
    async def connect(self) -> bool:
        """Establishes connection with broker gateway or exchange API."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Cleanly terminates broker session."""
        pass

    @abstractmethod
    async def get_account_summary(self) -> AccountSummary:
        """Fetches live balance, buying power, and daily realized PnL."""
        pass

    @abstractmethod
    async def get_positions(self) -> Dict[str, Position]:
        """Returns map of active portfolio holdings."""
        pass

    @abstractmethod
    async def place_order(self, order: TradeOrder) -> TradeOrder:
        """Submits an authorized order for execution."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancels an open order."""
        pass

    @abstractmethod
    async def get_market_quote(self, symbol: str) -> Optional[MarketDataTick]:
        """Fetches latest quote for pricing and validation."""
        pass

