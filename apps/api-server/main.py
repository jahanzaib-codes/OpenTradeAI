"""
OpenTradeAI - High-Performance FastAPI Application Server
REST API & WebSocket endpoints powering the web dashboard, CLI, and multi-agent execution pipeline.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from packages.core.models import (
    TradeOrder,
    OrderStatus,
    OrderAction,
    OrderType,
    TradingMode,
    MultiAgentResearchReport,
    RiskValidationResult,
    AccountSummary
)
from packages.scanners.scanner import market_scanner, ScanResult
from packages.ai.agents.analyst import agent_orchestrator
from packages.risk.engine import risk_engine
from packages.brokers.paper_broker import paper_broker

app = FastAPI(
    title="OpenTradeAI Execution & Research API",
    version="1.0.0",
    description="Production-grade AI Quantitative Trading Platform API."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderExecutionRequest(BaseModel):
    symbol: str
    action: OrderAction
    order_type: OrderType = OrderType.MARKET
    quantity: float
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    trading_mode: TradingMode = TradingMode.PAPER


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "OpenTradeAI Core API",
        "kill_switch_active": risk_engine.kill_switch_engaged
    }


@app.get("/api/v1/account", response_model=AccountSummary)
async def get_account():
    return await paper_broker.get_account_summary()


@app.get("/api/v1/positions")
async def get_positions():
    return await paper_broker.get_positions()


@app.get("/api/v1/scan")
async def run_market_scan(
    min_rvol: float = Query(1.5, description="Minimum relative volume"),
    min_change: float = Query(0.5, description="Minimum percentage change")
):
    return market_scanner.scan(min_rvol=min_rvol, min_change_pct=min_change)


@app.get("/api/v1/market-data/{symbol}")
async def get_market_quote(symbol: str):
    quote = await paper_broker.get_market_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail="Symbol quote unavailable")
    return quote


@app.post("/api/v1/agents/research", response_model=MultiAgentResearchReport)
async def run_agent_research(symbol: str):
    """
    Triggers concurrent multi-agent research panel across Technical,
    Bullish, Bearish, and Sentiment specialist agents.
    """
    quote = await paper_broker.get_market_quote(symbol)
    report = agent_orchestrator.run_research(quote)
    return report


@app.post("/api/v1/orders/preview", response_model=RiskValidationResult)
async def preview_order(req: OrderExecutionRequest):
    """
    Simulates order through the Deterministic Risk Engine before submission.
    Ensures AI agents and users cannot breach drawdown or allocation caps.
    """
    quote = await paper_broker.get_market_quote(req.symbol)
    account = await paper_broker.get_account_summary()
    positions = await paper_broker.get_positions()

    temp_order = TradeOrder(
        order_id="PREVIEW-" + str(uuid.uuid4())[:8],
        symbol=req.symbol.upper(),
        action=req.action,
        order_type=req.order_type,
        quantity=req.quantity,
        limit_price=req.limit_price or quote.price,
        status=OrderStatus.PENDING
    )

    verdict = risk_engine.validate_order(temp_order, account, positions, quote.price)
    return verdict


@app.post("/api/v1/orders/execute")
async def execute_order(req: OrderExecutionRequest):
    """
    Submits order for live or simulated execution strictly subject to risk approval.
    """
    quote = await paper_broker.get_market_quote(req.symbol)
    account = await paper_broker.get_account_summary()
    positions = await paper_broker.get_positions()

    order = TradeOrder(
        order_id="ORD-" + str(uuid.uuid4())[:8],
        symbol=req.symbol.upper(),
        action=req.action,
        order_type=req.order_type,
        quantity=req.quantity,
        limit_price=req.limit_price or quote.price,
        trading_mode=req.trading_mode
    )

    # 1. Deterministic Risk Gate
    verdict = risk_engine.validate_order(order, account, positions, quote.price)
    if not verdict.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Risk Engine Veto: {verdict.rejection_reason}"
        )

    # 2. Adjust quantity to risk-approved cap if partial sizing enforced
    order.quantity = verdict.approved_qty

    # 3. Execute
    executed_order = await paper_broker.place_order(order)
    return {
        "verdict": verdict,
        "execution": executed_order
    }


@app.post("/api/v1/risk/kill-switch")
async def toggle_kill_switch(engage: bool, reason: str = "Manual Admin Request"):
    if engage:
        risk_engine.engage_kill_switch(reason)
    else:
        risk_engine.disengage_kill_switch()
    return {
        "kill_switch_engaged": risk_engine.kill_switch_engaged,
        "message": f"Kill switch {'engaged' if engage else 'disengaged'} successfully."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
