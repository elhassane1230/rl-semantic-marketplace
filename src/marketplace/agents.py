"""Buyer and seller agents.

Both negotiate through the message runtime using FIPA performatives, and both
choose their moves with a Q-learner:

  * the **seller** learns a *pricing/concession* policy: given the round, which
    price to propose (state = round, action = price);
  * the **buyer** learns an *acceptance* policy: given the round and the proposed
    price, whether to accept or reject (state = (round, price), action = 0/1).

Each agent records the (state, action) pairs it took during an episode; the
simulation assigns the end-of-episode reward and updates the Q-learners.
"""
from __future__ import annotations

from .environment import MAX_ROUNDS, PRICE_MAX, Scenario
from .messages import Message, Performative
from .rl import QLearner
from .runtime import Agent, Behaviour, MessageBus

SELLER_ACTIONS = list(range(2, PRICE_MAX + 1))   # prices the seller may propose
BUYER_ACTIONS = [0, 1]                            # 0 = reject, 1 = accept


class SellerAgent(Agent):
    def __init__(self, name: str, bus: MessageBus, seed: int = 0):
        super().__init__(name, bus)
        self.q = QLearner(SELLER_ACTIONS, seed=seed)
        self.transitions: list = []
        self.scenario: Scenario | None = None
        self.outcome = {"deal": False, "price": None, "rounds": 0}
        self.add_behaviour(self._Sell())

    class _Sell(Behaviour):
        async def run(self):
            ag = self.agent
            cfp = await self.receive()
            if cfp is None or cfp.performative != Performative.CFP:
                return
            buyer = cfp.sender
            for r in range(MAX_ROUNDS):
                # never propose below the reserve price (individual rationality)
                valid = [p for p in ag.q.actions if p >= ag.scenario.reserve]
                state = r
                price = ag.q.select(state)
                if price < ag.scenario.reserve:
                    price = min(valid) if valid else ag.scenario.reserve
                ag.transitions.append((state, price))
                await self.send(Message(ag.name, buyer, Performative.PROPOSE,
                                        {"price": price, "round": r}))
                reply = await self.receive()
                ag.outcome["rounds"] = r + 1
                if reply and reply.performative == Performative.ACCEPT:
                    ag.outcome.update(deal=True, price=price)
                    return
            # no acceptance within the rounds -> no deal


class BuyerAgent(Agent):
    def __init__(self, name: str, bus: MessageBus, seed: int = 0):
        super().__init__(name, bus)
        self.q = QLearner(BUYER_ACTIONS, seed=seed)
        self.transitions: list = []
        self.scenario: Scenario | None = None
        self.seller_name = "seller"
        self.add_behaviour(self._Buy())

    class _Buy(Behaviour):
        async def run(self):
            ag = self.agent
            await self.send(Message(ag.name, ag.seller_name, Performative.CFP,
                                    {"item": ag.scenario.item_id}))
            for _r in range(MAX_ROUNDS):
                msg = await self.receive()
                if msg is None or msg.performative != Performative.PROPOSE:
                    return
                price = msg.content["price"]
                r = msg.content["round"]
                state = (r, price)
                action = ag.q.select(state)
                # never accept above valuation (individual rationality)
                if price > ag.scenario.valuation:
                    action = 0
                ag.transitions.append((state, action))
                if action == 1:
                    await self.send(msg.reply(ag.name, Performative.ACCEPT))
                    return
                await self.send(msg.reply(ag.name, Performative.REJECT))
