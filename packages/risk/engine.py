"""
OpenTradeAI - Deterministic Institutional Risk Engine
Enforces pre-trade hard risk limits, maximum drawdown barriers, position sizing guards,
and emergency kill switches. AI agents cannot bypass this layer.
"""

from typing import Dict, Optional
from packages.core.models import (
    TradeOrder,
    RiskValidationResult,
    AccountSummary,
    Position,
    OrderAction
)


class DeterministicRiskEngine:
    def __init__(
        self,
        max_daily_loss_usd: float = 1000.0,
        max_portfolio_drawdown_pct: float = 5.0,
        max_single_trade_risk_pct: float = 2.0,
        max_open_positions: int = 5,
        max_position_size_usd: float = 10000.0,
    ):
        self.max_daily_loss_usd = max_daily_loss_usd
        self.max_portfolio_drawdown_pct = max_portfolio_drawdown_pct
        self.max_single_trade_risk_pct = max_single_trade_risk_pct
        self.max_open_positions = max_open_positions
        self.max_position_size_usd = max_position_size_usd

        # State flags
        self.kill_switch_engaged: bool = False
        self.daily_starting_equity: Optional[float] = None
        self.current_peak_equity: float = 0.0

    def engage_kill_switch(self, reason: str = "Manual Emergency Halt"):
        self.kill_switch_engaged = True
        print(f"🚨 [KILL SWITCH ENGAGED]: {reason}. All outbound order execution blocked.")

    def disengage_kill_switch(self):
        self.kill_switch_engaged = False
        print("✅ [KILL SWITCH DISENGAGED]: Order execution resumed.")

    def validate_order(
        self,
        order: TradeOrder,
        account: AccountSummary,
        active_positions: Dict[str, Position],
        market_price: float
    ) -> RiskValidationResult:
        """
        Conducts rigorous pre-trade validation against strict deterministic risk metrics.
        """
        # 1. Check Emergency Kill Switch
        if self.kill_switch_engaged:
            return RiskValidationResult(
                approved=False,
                rejection_reason="Emergency Kill Switch is active. No new executions permitted.",
                symbol=order.symbol,
                requested_qty=order.quantity,
                approved_qty=0.0,
                calculated_risk_usd=0.0,
                max_account_risk_pct=self.max_single_trade_risk_pct,
                portfolio_drawdown_pct=0.0,
                kill_switch_active=True
            )

        # Initialize equity baseline if not yet set
        if self.daily_starting_equity is None:
            self.daily_starting_equity = account.net_liquidation_value
            self.current_peak_equity = account.net_liquidation_value

        if account.net_liquidation_value > self.current_peak_equity:
            self.current_peak_equity = account.net_liquidation_value

        # 2. Check Daily Realized Loss Threshold
        if account.realized_daily_pnl <= -abs(self.max_daily_loss_usd):
            return RiskValidationResult(
                approved=False,
                rejection_reason=f"Daily loss limit breached: Realized PnL is ${account.realized_daily_pnl:.2f} (Max: -${self.max_daily_loss_usd:.2f})",
                symbol=order.symbol,
                requested_qty=order.quantity,
                approved_qty=0.0,
                calculated_risk_usd=0.0,
                max_account_risk_pct=self.max_single_trade_risk_pct,
                portfolio_drawdown_pct=0.0
            )

        # 3. Check Peak Portfolio Drawdown Barrier
        current_drawdown_pct = 0.0
        if self.current_peak_equity > 0:
            current_drawdown_pct = ((self.current_peak_equity - account.net_liquidation_value) / self.current_peak_equity) * 100.0

        if current_drawdown_pct >= self.max_portfolio_drawdown_pct:
            return RiskValidationResult(
                approved=False,
                rejection_reason=f"Max portfolio drawdown breached: {current_drawdown_pct:.2f}% (Limit: {self.max_portfolio_drawdown_pct:.2f}%)",
                symbol=order.symbol,
                requested_qty=order.quantity,
                approved_qty=0.0,
                calculated_risk_usd=0.0,
                max_account_risk_pct=self.max_single_trade_risk_pct,
                portfolio_drawdown_pct=current_drawdown_pct
            )

        # 4. Check Maximum Open Positions Count (only for new BUY entries)
        if order.action == OrderAction.BUY and order.symbol not in active_positions:
            if len(active_positions) >= self.max_open_positions:
                return RiskValidationResult(
                    approved=False,
                    rejection_reason=f"Maximum concurrent open positions reached ({len(active_positions)}/{self.max_open_positions})",
                    symbol=order.symbol,
                    requested_qty=order.quantity,
                    approved_qty=0.0,
                    calculated_risk_usd=0.0,
                    max_account_risk_pct=self.max_single_trade_risk_pct,
                    portfolio_drawdown_pct=current_drawdown_pct
                )

        # 5. Position Sizing & Maximum Single Trade Capital Cap
        requested_notional = order.quantity * market_price
        max_allowed_notional_by_pct = account.net_liquidation_value * (self.max_single_trade_risk_pct / 100.0) * 10.0  # e.g., 20% max notional for 2% stop risk
        max_notional_allowed = min(self.max_position_size_usd, max_allowed_notional_by_pct)

        approved_qty = order.quantity
        if requested_notional > max_notional_allowed and market_price > 0:
            approved_qty = round(max_notional_allowed / market_price, 2)
            if approved_qty <= 0:
                return RiskValidationResult(
                    approved=False,
                    rejection_reason=f"Order size exceeds maximum allowed notional capital cap of ${max_notional_allowed:.2f}",
                    symbol=order.symbol,
                    requested_qty=order.quantity,
                    approved_qty=0.0,
                    calculated_risk_usd=requested_notional,
                    max_account_risk_pct=self.max_single_trade_risk_pct,
                    portfolio_drawdown_pct=current_drawdown_pct
                )

        # 6. Buying Power Check
        if order.action == OrderAction.BUY and (approved_qty * market_price) > account.buying_power:
            return RiskValidationResult(
                approved=False,
                rejection_reason=f"Insufficient buying power: Required ${approved_qty * market_price:.2f}, Available: ${account.buying_power:.2f}",
                symbol=order.symbol,
                requested_qty=order.quantity,
                approved_qty=0.0,
                calculated_risk_usd=approved_qty * market_price,
                max_account_risk_pct=self.max_single_trade_risk_pct,
                portfolio_drawdown_pct=current_drawdown_pct
            )

        # All checks passed!
        return RiskValidationResult(
            approved=True,
            rejection_reason=None,
            symbol=order.symbol,
            requested_qty=order.quantity,
            approved_qty=approved_qty,
            calculated_risk_usd=approved_qty * market_price,
            max_account_risk_pct=self.max_single_trade_risk_pct,
            portfolio_drawdown_pct=current_drawdown_pct,
            kill_switch_active=False
        )


# Global deterministic risk engine instance
risk_engine = DeterministicRiskEngine()

