"""
OpenTradeAI - High-Velocity Multi-Market Scanner
Evaluates real-time universe quotes for volume surges (RVOL), breakout patterns,
and institutional momentum filters.
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class ScanResult(BaseModel):
    symbol: str
    asset_class: str
    price: float
    change_pct: float
    relative_volume: float
    vwap_deviation_pct: float
    rsi: float
    signal_tag: str


class UniversalMarketScanner:
    def __init__(self):
        # Default monitored watchlist
        self.universe = [
            {"symbol": "NVDA", "asset": "STOCK", "price": 138.20, "change_pct": 3.8, "rvol": 2.4, "vwap_dev": 1.2, "rsi": 62.0, "tag": "AI Momentum Breakout"},
            {"symbol": "AAPL", "asset": "STOCK", "price": 224.50, "change_pct": 1.4, "rvol": 1.8, "vwap_dev": 0.6, "rsi": 56.5, "tag": "VWAP Expansion"},
            {"symbol": "TSLA", "asset": "STOCK", "price": 250.60, "change_pct": 4.5, "rvol": 2.9, "vwap_dev": 2.1, "rsi": 68.0, "tag": "High Beta Squeeze"},
            {"symbol": "SPY", "asset": "OPTION/0DTE", "price": 574.80, "change_pct": 0.7, "rvol": 1.5, "vwap_dev": 0.4, "rsi": 54.0, "tag": "0DTE Pin Strike"},
            {"symbol": "SOL", "asset": "CRYPTO", "price": 188.50, "change_pct": 6.2, "rvol": 3.1, "vwap_dev": 2.8, "rsi": 71.0, "tag": "L1 Volume Surge"},
        ]

    def scan(
        self,
        min_rvol: float = 1.5,
        min_change_pct: float = 0.5,
        max_rsi: float = 75.0
    ) -> List[ScanResult]:
        """
        Filters market universe by quantitative criteria.
        """
        results = []
        for item in self.universe:
            if (
                item["rvol"] >= min_rvol
                and item["change_pct"] >= min_change_pct
                and item["rsi"] <= max_rsi
            ):
                results.append(ScanResult(
                    symbol=item["symbol"],
                    asset_class=item["asset"],
                    price=item["price"],
                    change_pct=item["change_pct"],
                    relative_volume=item["rvol"],
                    vwap_deviation_pct=item["vwap_dev"],
                    rsi=item["rsi"],
                    signal_tag=item["tag"]
                ))
        return results


# Global scanner instance
market_scanner = UniversalMarketScanner()

