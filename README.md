# 🌐 OpenTradeAI — The Open-Source AI Quantitative Trading Platform

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/AI-LangGraph_Multi--Agent-FF6F00?style=flat-square)](https://langchain.com)
[![Interactive Brokers](https://img.shields.io/badge/Broker-IBKR_API-E01E2E?style=flat-square)](https://interactivebrokers.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> An open-source, multi-asset, multi-broker quantitative trading ecosystem. Unites real-time market scanners, multi-agent AI research, institutional risk validation, event-driven backtesting, and automated execution across **US Equities, Options, Futures, Crypto, and Forex**.

---

### 💼 Need Custom Quantitative Systems, Trading Bots, or Custom Integrations?
I engineer high-performance trading software, broker API integrations, and machine learning models for hedge funds, prop traders, and private syndicates.
* 💬 **Telegram:** [@JanzebBlockdev](https://t.me/JanzebBlockdev)
* 💼 **Fiverr Profile:** [Verified Quantitative Developer (Fiverr)](https://tinyurl.com/2wruxnsx)
* 📧 **Email:** `jahanzaibchanna70@gmail.com`

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Market Data Layer
        MD1["Polygon.io / Databento"] --> DP["Data Normalization Pipeline"]
        MD2["Interactive Brokers TWS"] --> DP
        MD3["Crypto Exchanges (CCXT)"] --> DP
    end

    subgraph Intelligence & Quant Core
        DP --> MS["Universal Market Scanner"]
        MS --> AI["Multi-Agent AI Research (LangGraph)"]
        AI --> STRAT["Quant Strategy Engine"]
    end

    subgraph Risk & Decision Gate
        STRAT --> RE["Deterministic Risk Engine (Pre-Trade Hard Limits)"]
        RE -->|Veto on Breach| REJ["[REJECT ORDER]"]
        RE -->|Approved| EX["Execution & Order Manager"]
    end

    subgraph Brokers & Execution
        EX --> B1["IBKR TWS / Gateway"]
        EX --> B2["MetaTrader 5 (MT5)"]
        EX --> B3["Crypto Spot / Perp"]
    end
```

## 📑 Core Modules
* **`apps/`**: Dashboard (Next.js/React), API Server (FastAPI), Desktop Terminal, CLI.
* **`packages/core/`**: Normalized instrument schemas, event bus, clock, and configuration.
* **`packages/market-data/`**: Streaming tick aggregators and historical parquet storage.
* **`packages/brokers/`**: Modular adapters for IBKR, MT5, and Crypto exchanges.
* **`packages/ai/`**: Multi-agent consensus (Bullish, Bearish, Sentiment, Options, Risk).
* **`packages/risk/`**: Pre-trade limits, position sizing, correlation matrix, emergency kill switch.
* **`packages/execution/`**: Smart order routing, bracket orders, fill reconciliation.
* **`mcp/`**: Model Context Protocol server exposing guarded trading tools to Claude/ChatGPT.

---
*Maintained by **Jahanzaib** ([@jahanzaib-codes](https://github.com/jahanzaib-codes))*
