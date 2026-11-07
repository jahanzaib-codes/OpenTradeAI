"""
OpenTradeAI - High-Speed Asynchronous Event Bus
Dispatches ticks, agent analysis, risk verdicts, and order updates to connected subscribers.
"""

import asyncio
from typing import Callable, Dict, List, Any


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, topic: str, handler: Callable):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    async def publish(self, topic: str, event_data: Any):
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data)
                    else:
                        handler(event_data)
                except Exception as e:
                    print(f"[EventBus Error] Exception handling topic '{topic}': {e}")


# Global EventBus singleton
event_bus = EventBus()

