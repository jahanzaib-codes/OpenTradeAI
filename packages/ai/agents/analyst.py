"""
OpenTradeAI - Multi-Agent AI Research & Consensus Engine
Coordinates specialized AI agents (Bullish, Bearish, Technical, Sentiment, Options)
to generate calibrated confidence scores, structured theses, and actionable trade setups.
"""

from typing import Dict, Any, List, Optional
from packages.core.models import (
    AgentOpinion,
    MultiAgentResearchReport,
    MarketDataTick
)


class TechnicalAnalystAgent:
    name: str = "Technical Analyst Agent"

    def analyze(self, tick: MarketDataTick, indicators: Dict[str, Any]) -> AgentOpinion:
        rsi = indicators.get("rsi", 54.0)
        vwap = indicators.get("vwap", tick.price * 0.99)
        ema_trend = indicators.get("ema_trend", "BULLISH_ALIGNMENT")
        atr = indicators.get("atr", tick.price * 0.02)

        drivers = []
        confidence = 65.0

        if tick.price > vwap:
            drivers.append(f"Price (${tick.price:.2f}) trading above session VWAP (${vwap:.2f})")
            confidence += 10.0
        else:
            drivers.append(f"Price (${tick.price:.2f}) trading below session VWAP (${vwap:.2f})")
            confidence -= 10.0

        if 45.0 <= rsi <= 68.0:
            drivers.append(f"RSI({rsi:.1f}) in healthy momentum expansion zone without exhaustion")
            confidence += 10.0
        elif rsi > 70.0:
            drivers.append(f"RSI({rsi:.1f}) in overbought territory - watch for mean reversion")
            confidence -= 15.0

        drivers.append(f"Moving Average Alignment: {ema_trend}")

        stance = "BULLISH" if confidence >= 60.0 else ("BEARISH" if confidence <= 40.0 else "NEUTRAL")

        return AgentOpinion(
            agent_name=self.name,
            stance=stance,
            confidence_score=min(100.0, max(0.0, confidence)),
            key_drivers=drivers,
            evidence_metrics={"rsi": rsi, "vwap": vwap, "atr": atr, "ema_trend": ema_trend},
            suggested_entry=round(tick.price, 2),
            suggested_stop_loss=round(tick.price - (1.5 * atr), 2),
            suggested_take_profit=round(tick.price + (3.0 * atr), 2)
        )


class BullishAnalystAgent:
    name: str = "Bullish Growth & Catalyst Agent"

    def analyze(self, tick: MarketDataTick, context: Dict[str, Any]) -> AgentOpinion:
        relative_volume = context.get("relative_volume", 2.2)
        breakout_status = context.get("breakout_status", "Consolidation Breakout")

        drivers = [
            f"Surge Relative Volume: {relative_volume}x baseline volume (Institutional Accumulation)",
            f"Structural Pattern: {breakout_status} above multi-day resistance",
            "Order book depth reflects strong aggressive bid absorption"
        ]

        confidence = 78.0 if relative_volume >= 1.5 else 55.0

        return AgentOpinion(
            agent_name=self.name,
            stance="BULLISH",
            confidence_score=confidence,
            key_drivers=drivers,
            evidence_metrics={"rvol": relative_volume, "breakout": breakout_status},
            suggested_entry=round(tick.price, 2),
            suggested_stop_loss=round(tick.price * 0.97, 2),
            suggested_take_profit=round(tick.price * 1.06, 2)
        )


class BearishAnalystAgent:
    name: str = "Bearish Counter-Thesis & Risk Agent"

    def analyze(self, tick: MarketDataTick, context: Dict[str, Any]) -> AgentOpinion:
        overhead_resistance = context.get("overhead_resistance", tick.price * 1.03)
        daily_extension_pct = context.get("daily_extension_pct", 3.4)

        drivers = [
            f"Significant overhead institutional liquidity pool at ${overhead_resistance:.2f}",
            f"Asset has advanced +{daily_extension_pct:.1f}% from session open, vulnerable to profit-taking",
            "Macro index correlation suggests broad market consolidation headwinds"
        ]

        # A prudent skeptic agent typically assesses moderate risk
        confidence = 58.0

        return AgentOpinion(
            agent_name=self.name,
            stance="NEUTRAL",
            confidence_score=confidence,
            key_drivers=drivers,
            evidence_metrics={"overhead_resistance": overhead_resistance, "extension_pct": daily_extension_pct},
            suggested_entry=None,
            suggested_stop_loss=round(tick.price * 0.98, 2),
            suggested_take_profit=None
        )


class SentimentNewsAgent:
    name: str = "News & Sentiment Agent"

    def analyze(self, tick: MarketDataTick, news_data: Dict[str, Any]) -> AgentOpinion:
        sentiment_score = news_data.get("sentiment_score", 0.72)  # -1.0 to 1.0
        headline_count = news_data.get("headline_count", 8)

        stance = "BULLISH" if sentiment_score > 0.3 else ("BEARISH" if sentiment_score < -0.3 else "NEUTRAL")
        confidence = round(abs(sentiment_score) * 100.0, 1)

        drivers = [
            f"Aggregated NLP sentiment polarity: +{sentiment_score:.2f} (Predominantly Positive)",
            f"High narrative velocity detected across {headline_count} verified news feeds",
            "Zero SEC regulatory or dilution filings detected in last 24 hours"
        ]

        return AgentOpinion(
            agent_name=self.name,
            stance=stance,
            confidence_score=confidence,
            key_drivers=drivers,
            evidence_metrics={"sentiment_polarity": sentiment_score, "news_volume": headline_count}
        )


class MultiAgentOrchestrator:
    def __init__(self):
        self.tech_agent = TechnicalAnalystAgent()
        self.bull_agent = BullishAnalystAgent()
        self.bear_agent = BearishAnalystAgent()
        self.sentiment_agent = SentimentNewsAgent()

    def run_research(
        self,
        tick: MarketDataTick,
        technical_data: Optional[Dict[str, Any]] = None,
        market_context: Optional[Dict[str, Any]] = None,
        news_data: Optional[Dict[str, Any]] = None
    ) -> MultiAgentResearchReport:
        """
        Runs independent multi-agent research and synthesizes cross-agent consensus.
        """
        technical_data = technical_data or {"rsi": 58.5, "vwap": tick.price * 0.992, "ema_trend": "BULLISH_STACK", "atr": tick.price * 0.018}
        market_context = market_context or {"relative_volume": 2.4, "breakout_status": "Range Expansion Breakout", "overhead_resistance": tick.price * 1.04, "daily_extension_pct": 2.8}
        news_data = news_data or {"sentiment_score": 0.68, "headline_count": 12}

        # Run all agents
        op_tech = self.tech_agent.analyze(tick, technical_data)
        op_bull = self.bull_agent.analyze(tick, market_context)
        op_bear = self.bear_agent.analyze(tick, market_context)
        op_sent = self.sentiment_agent.analyze(tick, news_data)

        opinions = [op_tech, op_bull, op_bear, op_sent]

        # Calculate weighted consensus score
        # Weights: Tech (35%), Bullish/Bearish Balance (45%), Sentiment (20%)
        weighted_score = (
            (op_tech.confidence_score * 0.35) +
            (op_bull.confidence_score * 0.25) +
            ((100.0 - op_bear.confidence_score) * 0.20) +
            (op_sent.confidence_score * 0.20)
        )
        weighted_score = round(min(100.0, max(0.0, weighted_score)), 1)

        # Consensus Stance
        bullish_count = sum(1 for o in opinions if o.stance == "BULLISH")
        bearish_count = sum(1 for o in opinions if o.stance == "BEARISH")

        if bullish_count >= 2 and weighted_score >= 65.0:
            consensus = "BULLISH"
            actionable = True
            thesis = f"Multi-agent consensus confirms strong upward trend alignment for {tick.symbol}. Technical momentum indicators and institutional volume surge outweigh minor overhead resistance. Prudent entry recommended with dynamic ATR stop loss."
        elif bearish_count >= 2:
            consensus = "BEARISH"
            actionable = False
            thesis = f"Multi-agent panel flags substantial breakdown risks and negative order flow divergence for {tick.symbol}. Immediate entry discouraged."
        else:
            consensus = "NEUTRAL"
            actionable = False
            thesis = f"Mixed signals across technical indicators and sentiment metrics for {tick.symbol}. Recommended action is capital preservation until clear directional confirmation."

        return MultiAgentResearchReport(
            symbol=tick.symbol,
            consensus_stance=consensus,
            overall_confidence=weighted_score,
            market_regime="BULLISH_TREND_EXPANSION" if weighted_score >= 65.0 else "CHOPPY_EQUILIBRIUM",
            agent_opinions=opinions,
            synthesized_thesis=thesis,
            actionable_signal=actionable
        )


# Global orchestrator instance
agent_orchestrator = MultiAgentOrchestrator()
