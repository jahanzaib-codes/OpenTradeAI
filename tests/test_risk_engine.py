"""
Unit tests for Deterministic Risk Engine.
Validates drawdown limits, daily loss limits, and emergency kill switches.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from packages.risk.engine import DeterministicRiskEngine
from packages.core.models import (
    TradeOrder,
    AccountSummary,
    OrderAction,
    OrderType,
    TradingMode
)


def test_kill_switch_blocks_orders():
    engine = DeterministicRiskEngine()
    engine.engage_kill_switch("Unit Test")

    account = AccountSummary(
        account_id="TEST",
        trading_mode=TradingMode.PAPER,
        net_liquidation_value=100000.0,
        available_funds=100000.0,
        buying_power=200000.0,
        realized_daily_pnl=0.0,
        unrealized_pnl=0.0,
        active_positions_count=0
    )

    order = TradeOrder(
        order_id="ORD-1",
        symbol="AAPL",
        action=OrderAction.BUY,
        order_type=OrderType.MARKET,
        quantity=10.0
    )

    verdict = engine.validate_order(order, account, {}, 200.0)
    assert verdict.approved is False
    assert "Kill Switch" in verdict.rejection_reason


def test_daily_loss_limit_veto():
    engine = DeterministicRiskEngine(max_daily_loss_usd=500.0)

    account = AccountSummary(
        account_id="TEST",
        trading_mode=TradingMode.PAPER,
        net_liquidation_value=99000.0,
        available_funds=99000.0,
        buying_power=198000.0,
        realized_daily_pnl=-600.0,  # Exceeds $500 limit
        unrealized_pnl=0.0,
        active_positions_count=0
    )

    order = TradeOrder(
        order_id="ORD-2",
        symbol="NVDA",
        action=OrderAction.BUY,
        order_type=OrderType.MARKET,
        quantity=10.0
    )

    verdict = engine.validate_order(order, account, {}, 140.0)
    assert verdict.approved is False
    assert "Daily loss limit breached" in verdict.rejection_reason


def test_approved_order():
    engine = DeterministicRiskEngine()

    account = AccountSummary(
        account_id="TEST",
        trading_mode=TradingMode.PAPER,
        net_liquidation_value=100000.0,
        available_funds=100000.0,
        buying_power=200000.0,
        realized_daily_pnl=100.0,
        unrealized_pnl=0.0,
        active_positions_count=0
    )

    order = TradeOrder(
        order_id="ORD-3",
        symbol="MSFT",
        action=OrderAction.BUY,
        order_type=OrderType.MARKET,
        quantity=10.0
    )

    verdict = engine.validate_order(order, account, {}, 400.0)
    assert verdict.approved is True
    assert verdict.approved_qty == 10.0
