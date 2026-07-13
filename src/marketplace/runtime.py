"""A compact asyncio agent runtime — the same concepts as SPADE/PADE (Agent,
Behaviour, asynchronous message passing), but in-process so the whole system
runs deterministically with no XMPP server. The SPADE adapter
(``spade_adapter.py``) maps these classes onto real networked SPADE agents.

  * ``MessageBus`` routes messages to each agent's inbox (an asyncio.Queue).
  * ``Agent`` has an inbox, a name, and behaviours.
  * ``Behaviour`` is an async unit of work with ``send`` / ``receive`` helpers.
"""
from __future__ import annotations

import asyncio

from .messages import Message


class MessageBus:
    def __init__(self):
        self._inboxes: dict[str, asyncio.Queue] = {}

    def register(self, name: str) -> asyncio.Queue:
        self._inboxes[name] = asyncio.Queue()
        return self._inboxes[name]

    async def deliver(self, message: Message) -> None:
        inbox = self._inboxes.get(message.receiver)
        if inbox is not None:
            await inbox.put(message)


class Behaviour:
    """Base class for an agent behaviour (override ``run``)."""

    def __init__(self):
        self.agent: "Agent" = None  # set on attachment

    async def send(self, message: Message) -> None:
        await self.agent.bus.deliver(message)

    async def receive(self, timeout: float = 2.0) -> Message | None:
        try:
            return await asyncio.wait_for(self.agent.inbox.get(), timeout)
        except asyncio.TimeoutError:
            return None

    async def run(self) -> None:                     # pragma: no cover
        raise NotImplementedError


class Agent:
    def __init__(self, name: str, bus: MessageBus):
        self.name = name
        self.bus = bus
        self.inbox = bus.register(name)
        self.behaviours: list[Behaviour] = []

    def add_behaviour(self, behaviour: Behaviour) -> None:
        behaviour.agent = self
        self.behaviours.append(behaviour)

    async def run(self) -> None:
        await asyncio.gather(*(b.run() for b in self.behaviours))
