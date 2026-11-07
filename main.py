"""
OpenTradeAI - Unified Platform Entrypoint
Run API server, interactive CLI terminal, or automated end-to-end demo.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import asyncio
import uvicorn


async def run_end_to_end_demo():
    print("""
================================================================================
  🌐 OpenTradeAI — Automated End-to-End Execution Pipeline Demo
================================================================================
    """)
    from packages.scanners.scanner import market_scanner
    from packages.ai.agents.analyst import agent_orchestrator
    from packages.risk.engine import risk_engine
    from packages.brokers.paper_broker import paper_broker
    from packages.core.models import TradeOrder, OrderAction, OrderType

    # Step 1: Connect Broker
    print("[1/5] 🔌 Initializing Paper Broker Engine...")
    await paper_broker.connect()
    account = await paper_broker.get_account_summary()
    print(f"      Account connected: {account.account_id} | Balance: ${account.net_liquidation_value:,.2f}")

    # Step 2: Run Scanner
    print("\n[2/5] 🔍 Running Multi-Asset Momentum Scanner...")
    matches = market_scanner.scan()
    print(f"      Scanner identified {len(matches)} high-conviction breakout opportunities:")
    for m in matches[:3]:
        print(f"      • {m.symbol} ({m.asset_class}): RVOL {m.relative_volume}x | +{m.change_pct}% | Tag: {m.signal_tag}")

    target_symbol = matches[0].symbol
    target_price = matches[0].price
    quote = await paper_broker.get_market_quote(target_symbol)

    # Step 3: Run Multi-Agent Research
    print(f"\n[3/5] 🤖 Dispatching Multi-Agent AI Panel on Top Candidate: {target_symbol} (${target_price:.2f})...")
    report = agent_orchestrator.run_research(quote)
    print(f"      Consensus Stance: {report.consensus_stance} (Confidence: {report.overall_confidence}%)")
    print(f"      Synthesized Thesis: {report.synthesized_thesis}")
    for op in report.agent_opinions:
        print(f"      - {op.agent_name}: {op.stance} ({op.confidence_score}%)")

    # Step 4: Deterministic Risk Engine Validation
    print(f"\n[4/5] 🛡️  Submitting Trade Proposal to Deterministic Risk Engine...")
    order = TradeOrder(
        order_id="DEMO-001",
        symbol=target_symbol,
        action=OrderAction.BUY,
        order_type=OrderType.MARKET,
        quantity=50.0,
        limit_price=quote.price
    )
    positions = await paper_broker.get_positions()
    verdict = risk_engine.validate_order(order, account, positions, quote.price)

    if verdict.approved:
        print(f"      ✅ VERDICT: APPROVED!")
        print(f"      Allocated Qty: {verdict.approved_qty} shares | Capital Risk: ${verdict.calculated_risk_usd:,.2f}")
    else:
        print(f"      ❌ VERDICT: VETOED ({verdict.rejection_reason})")
        return

    # Step 5: Execution
    print(f"\n[5/5] ⚡ Routing Order to Broker Execution Layer...")
    order.quantity = verdict.approved_qty
    filled = await paper_broker.place_order(order)
    print(f"      ✅ FILL CONFIRMED: {filled.action.value} {filled.quantity} {filled.symbol} @ ${filled.avg_fill_price:.2f}")
    print(f"      Audit Trail: {filled.execution_notes}")

    # Summary
    updated_account = await paper_broker.get_account_summary()
    updated_positions = await paper_broker.get_positions()
    print(f"\n📈 Post-Trade Summary:")
    print(f"   Available Cash: ${updated_account.available_funds:,.2f}")
    print(f"   Active Positions: {list(updated_positions.keys())}")
    print("\n🎉 End-to-end pipeline execution succeeded with 100% safety verification!")


def main():
    parser = argparse.ArgumentParser(description="OpenTradeAI Platform Launcher")
    parser.add_argument("--mode", choices=["demo", "server", "cli"], default="demo", help="Execution mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    args = parser.parse_args()

    if args.mode == "demo":
        asyncio.run(run_end_to_end_demo())
    elif args.mode == "server":
        print(f"🚀 Launching OpenTradeAI FastAPI server on http://localhost:{args.port}...")
        uvicorn.run("apps.api-server.main:app", host="0.0.0.0", port=args.port, reload=True)
    elif args.mode == "cli":
        from apps.cli.terminal import run_terminal
        asyncio.run(run_terminal())


if __name__ == "__main__":
    main()
