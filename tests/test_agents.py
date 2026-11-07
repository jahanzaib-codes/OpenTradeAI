"""
Unit tests for Market Scanner and Multi-Agent Orchestrator.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from packages.scanners.scanner import market_scanner
from packages.ai.agents.analyst import agent_orchestrator
from packages.core.models import MarketDataTick


def test_market_scanner_filters():
    results = market_scanner.scan(min_rvol=1.5, min_change_pct=0.5)
    assert len(results) > 0
    for r in results:
        assert r.relative_volume >= 1.5
        assert r.change_pct >= 0.5


def test_multi_agent_consensus():
    tick = MarketDataTick(
        symbol="NVDA",
        price=138.20,
        bid=138.18,
        ask=138.22,
        volume=5000000.0,
        vwap=137.50
    )

    report = agent_orchestrator.run_research(tick)
    assert report.symbol == "NVDA"
    assert report.overall_confidence > 0.0
    assert len(report.agent_opinions) == 4
    assert report.consensus_stance in ["BULLISH", "BEARISH", "NEUTRAL"]
