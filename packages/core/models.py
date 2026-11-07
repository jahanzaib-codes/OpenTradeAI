"""
OpenTradeAI - Core Data Models and Domain Schemas
Defines strictly typed Pydantic models for instruments, market data, agent outputs, risk validations, and orders.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    STOCK = "STOCK"
    OPTION = "OPTION"
    FUTURES = "FUTURES"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"


class OrderAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STP_LMT"
    TRAILING_STOP = "TRAIL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class TradingMode(str, Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"


class Instrument(BaseModel):
    symbol: str
    asset_class: AssetClass = AssetClass.STOCK
    currency: str = "USD"
    exchange: str = "SMART"
    multiplier: float = 1.0


class MarketDataTick(BaseModel):
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    price: float
    bid: float
    ask: float
    volume: float
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    vwap: Optional[float] = None


class AgentOpinion(BaseModel):
    agent_name: str
    stance: str  # "BULLISH", "BEARISH", "NEUTRAL"
    confidence_score: float = Field(ge=0.0, le=100.0)
    key_drivers: List[str]
    evidence_metrics: Dict[str, Any]
    suggested_entry: Optional[float] = None
    suggested_stop_loss: Optional[float] = None
    suggested_take_profit: Optional[float] = None


class MultiAgentResearchReport(BaseModel):
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    consensus_stance: str
    overall_confidence: float = Field(ge=0.0, le=100.0)
    market_regime: str
    agent_opinions: List[AgentOpinion]
    synthesized_thesis: str
    actionable_signal: bool = False


class RiskValidationResult(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None
    symbol: str
    requested_qty: float
    approved_qty: float
    calculated_risk_usd: float
    max_account_risk_pct: float
    portfolio_drawdown_pct: float
    kill_switch_active: bool = False


class TradeOrder(BaseModel):
    order_id: str
    symbol: str
    action: OrderAction
    order_type: OrderType
    quantity: float
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = None
    avg_fill_price: Optional[float] = None
    trading_mode: TradingMode = TradingMode.PAPER
    execution_notes: Optional[str] = None


class Position(BaseModel):
    symbol: str
    quantity: float
    average_entry_price: float
    current_market_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    market_value: float


class AccountSummary(BaseModel):
    account_id: str
    trading_mode: TradingMode = TradingMode.PAPER
    net_liquidation_value: float
    available_funds: float
    buying_power: float
    realized_daily_pnl: float
    unrealized_pnl: float
    active_positions_count: int

