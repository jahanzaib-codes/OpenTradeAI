"""
OpenTradeAI - High-Fidelity Paper Trading Simulation Broker
Emulates real-world execution with simulated slippage, commissions, instant fills, and position ledger tracking.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional
from packages.brokers.base import BaseBrokerAdapter
from packages.core.models import (
    TradeOrder,
    Position,
    AccountSummary,
    MarketDataTick,
    OrderStatus,
    OrderAction,
    TradingMode
)


class PaperBroker(BaseBrokerAdapter):
    def __init__(self, starting_cash: float = 100000.0):
        self.starting_cash = starting_cash
        self.cash_balance = starting_cash
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, TradeOrder] = {}
        self.realized_daily_pnl = 0.0
        self.connected = False

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def disconnect(self):
        self.connected = False

    async def get_account_summary(self) -> AccountSummary:
        total_market_value = sum(p.market_value for p in self.positions.values())
        unrealized = sum(p.unrealized_pnl for p in self.positions.values())
        net_liquidation = self.cash_balance + total_market_value

        return AccountSummary(
            account_id="PAPER-DU100098",
            trading_mode=TradingMode.PAPER,
            net_liquidation_value=round(net_liquidation, 2),
            available_funds=round(self.cash_balance, 2),
            buying_power=round(self.cash_balance * 2.0, 2),  # 2x margin simulation
            realized_daily_pnl=round(self.realized_daily_pnl, 2),
            unrealized_pnl=round(unrealized, 2),
            active_positions_count=len(self.positions)
        )

    async def get_positions(self) -> Dict[str, Position]:
        return self.positions

    async def get_market_quote(self, symbol: str) -> Optional[MarketDataTick]:
        # Simulated realistic default quote dictionary
        mock_prices = {
            "AAPL": 224.50,
            "NVDA": 138.20,
            "SPY": 574.80,
            "QQQ": 492.30,
            "TSLA": 250.60,
            "MSFT": 420.10,
            "SOL": 188.50,
        }
        price = mock_prices.get(symbol.upper(), 100.00)
        spread = price * 0.0002

        return MarketDataTick(
            symbol=symbol.upper(),
            price=price,
            bid=round(price - spread, 2),
            ask=round(price + spread, 2),
            volume=4500000.0,
            vwap=round(price * 0.998, 2)
        )

    async def place_order(self, order: TradeOrder) -> TradeOrder:
        quote = await self.get_market_quote(order.symbol)
        fill_price = quote.ask if order.action == OrderAction.BUY else quote.bid

        # Simulate execution
        commission = min(1.0, max(0.5, order.quantity * 0.005))
        order.avg_fill_price = fill_price
        order.filled_at = datetime.utcnow()
        order.status = OrderStatus.FILLED
        order.execution_notes = f"Simulated fill at ${fill_price:.2f} (Comm: ${commission:.2f})"

        # Update position ledger
        if order.action == OrderAction.BUY:
            notional = order.quantity * fill_price + commission
            self.cash_balance -= notional

            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                new_qty = pos.quantity + order.quantity
                avg_price = ((pos.quantity * pos.average_entry_price) + (order.quantity * fill_price)) / new_qty
                pos.quantity = new_qty
                pos.average_entry_price = round(avg_price, 2)
                pos.market_value = round(new_qty * fill_price, 2)
            else:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    average_entry_price=fill_price,
                    current_market_price=fill_price,
                    unrealized_pnl=0.0,
                    unrealized_pnl_pct=0.0,
                    market_value=round(order.quantity * fill_price, 2)
                )

        elif order.action == OrderAction.SELL:
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                sell_qty = min(order.quantity, pos.quantity)
                revenue = (sell_qty * fill_price) - commission
                self.cash_balance += revenue

                realized_trade_pnl = (fill_price - pos.average_entry_price) * sell_qty - commission
                self.realized_daily_pnl += realized_trade_pnl

                pos.quantity -= sell_qty
                if pos.quantity <= 0:
                    del self.positions[order.symbol]
                else:
                    pos.market_value = round(pos.quantity * fill_price, 2)

        self.orders[order.order_id] = order
        return order

    async def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
            return True
        return False


# Global paper broker instance
paper_broker = PaperBroker()

