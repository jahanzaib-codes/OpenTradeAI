"""
OpenTradeAI - Interactive Terminal & CLI Runner
Executes scans, multi-agent debates, and risk audits from the command line.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
from packages.scanners.scanner import market_scanner
from packages.ai.agents.analyst import agent_orchestrator
from packages.risk.engine import risk_engine
from packages.brokers.paper_broker import paper_broker
from packages.core.models import (
    TradeOrder,
    OrderAction,
    OrderType,
    OrderStatus
)


def print_banner():
    banner = """
================================================================================
  🌐 OpenTradeAI — Multi-Agent Quantitative Trading Terminal
  Author: Jahanzaib | License: MIT | Mode: PAPER SIMULATION
================================================================================
    """
    print(banner)


async def run_terminal():
    print_banner()

    while True:
        print("\n[MAIN MENU]")
        print("1. 🔍 Run Universal Market Scanner")
        print("2. 🤖 Run Multi-Agent AI Research on Ticker")
        print("3. 🛡️  Simulate Deterministic Risk Engine Check")
        print("4. ⚡ Execute Paper Trade Order")
        print("5. 📊 View Portfolio Positions & Account Summary")
        print("6. 🚨 Toggle Emergency Kill Switch")
        print("7. ❌ Exit Terminal")

        choice = input("\nEnter choice [1-7]: ").strip()

        if choice == "1":
            print("\n--- Scanning Universe (RVOL >= 1.5x, Change >= 0.5%) ---")
            results = market_scanner.scan()
            print(f"{'SYMBOL':<8} {'CLASS':<12} {'PRICE':<10} {'CHG%':<8} {'RVOL':<8} {'RSI':<6} {'SIGNAL TAG'}")
            print("-" * 75)
            for r in results:
                print(f"{r.symbol:<8} {r.asset_class:<12} ${r.price:<9.2f} {r.change_pct:<7.1f}% {r.relative_volume:<7.1f}x {r.rsi:<6.1f} {r.signal_tag}")

        elif choice == "2":
            ticker = input("Enter ticker symbol (e.g., NVDA, AAPL, SPY, TSLA, SOL): ").strip().upper()
            quote = await paper_broker.get_market_quote(ticker)
            print(f"\n--- Running Multi-Agent Panel on {ticker} (${quote.price:.2f}) ---")
            report = agent_orchestrator.run_research(quote)

            print(f"\n📊 Consensus: {report.consensus_stance} | Calibrated Confidence: {report.overall_confidence}%")
            print(f"🏛️ Market Regime: {report.market_regime}")
            print(f"📝 Synthesized Thesis:\n   {report.synthesized_thesis}\n")

            print("--- Individual Agent Breakdown ---")
            for op in report.agent_opinions:
                print(f"🔹 {op.agent_name} ({op.stance} | {op.confidence_score}%):")
                for driver in op.key_drivers:
                    print(f"   • {driver}")
                if op.suggested_stop_loss:
                    print(f"   [Target Entry: ${op.suggested_entry} | Stop: ${op.suggested_stop_loss} | TP: ${op.suggested_take_profit}]")

        elif choice == "3":
            ticker = input("Enter ticker symbol: ").strip().upper()
            qty = float(input("Enter quantity shares: ").strip())
            quote = await paper_broker.get_market_quote(ticker)
            account = await paper_broker.get_account_summary()
            positions = await paper_broker.get_positions()

            temp_order = TradeOrder(
                order_id="TEST-001",
                symbol=ticker,
                action=OrderAction.BUY,
                order_type=OrderType.MARKET,
                quantity=qty,
                limit_price=quote.price
            )

            verdict = risk_engine.validate_order(temp_order, account, positions, quote.price)
            print("\n--- Risk Engine Verdict ---")
            if verdict.approved:
                print(f"✅ APPROVED! Approved Qty: {verdict.approved_qty} | Exposure Risk: ${verdict.calculated_risk_usd:.2f}")
            else:
                print(f"❌ VETOED! Reason: {verdict.rejection_reason}")

        elif choice == "4":
            ticker = input("Enter ticker symbol: ").strip().upper()
            action_input = input("Enter action (BUY/SELL): ").strip().upper()
            qty = float(input("Enter quantity: ").strip())

            action = OrderAction.BUY if action_input == "BUY" else OrderAction.SELL
            quote = await paper_broker.get_market_quote(ticker)
            account = await paper_broker.get_account_summary()
            positions = await paper_broker.get_positions()

            order = TradeOrder(
                order_id="ORD-CLI",
                symbol=ticker,
                action=action,
                order_type=OrderType.MARKET,
                quantity=qty,
                limit_price=quote.price
            )

            verdict = risk_engine.validate_order(order, account, positions, quote.price)
            if not verdict.approved:
                print(f"\n❌ Execution Blocked by Risk Engine: {verdict.rejection_reason}")
            else:
                order.quantity = verdict.approved_qty
                filled = await paper_broker.place_order(order)
                print(f"\n✅ ORDER EXECUTED: {filled.action.value} {filled.quantity} {filled.symbol} @ ${filled.avg_fill_price:.2f}")
                print(f"   Notes: {filled.execution_notes}")

        elif choice == "5":
            account = await paper_broker.get_account_summary()
            positions = await paper_broker.get_positions()

            print("\n--- Account Summary ---")
            print(f"Account ID: {account.account_id} ({account.trading_mode.value})")
            print(f"Net Liquidation: ${account.net_liquidation_value:,.2f}")
            print(f"Available Cash:  ${account.available_funds:,.2f}")
            print(f"Buying Power:    ${account.buying_power:,.2f}")
            print(f"Daily Realized:  ${account.realized_daily_pnl:,.2f}")

            print("\n--- Active Positions ---")
            if not positions:
                print("No open positions.")
            else:
                for sym, pos in positions.items():
                    print(f"• {sym}: {pos.quantity} shares @ Avg Entry ${pos.average_entry_price:.2f} | Mkt: ${pos.current_market_price:.2f} | Value: ${pos.market_value:,.2f}")

        elif choice == "6":
            state = not risk_engine.kill_switch_engaged
            if state:
                risk_engine.engage_kill_switch("CLI User Toggled")
            else:
                risk_engine.disengage_kill_switch()

        elif choice == "7":
            print("\nTerminating OpenTradeAI terminal session. Goodbye!\n")
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(run_terminal())
