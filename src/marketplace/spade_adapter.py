"""SPADE adapter — the same negotiation on real networked agents.

This maps the in-process agents onto **SPADE** (agents over XMPP). It's the
deployment path: run it against an XMPP server (see ``setup/prosody_localhost.sh``
and ``scripts/run_spade.py``). The negotiation logic and the Q-learning policy
are identical to the offline runtime; only the transport changes (SPADE's
``Message`` + XMPP instead of the asyncio bus).

SPADE is an optional dependency (``pip install -r requirements-spade.txt``); this
module imports it lazily so the rest of the package works without it.
"""
from __future__ import annotations

from .environment import MAX_ROUNDS
from .rl import QLearner
from .agents import BUYER_ACTIONS, SELLER_ACTIONS


def build_seller(jid: str, password: str, reserve: int, q: QLearner | None = None):
    from spade.agent import Agent
    from spade.behaviour import CyclicBehaviour
    from spade.message import Message

    learner = q or QLearner(SELLER_ACTIONS)

    class SellerBehaviour(CyclicBehaviour):
        async def run(self):
            cfp = await self.receive(timeout=10)
            if not cfp:
                return
            buyer = str(cfp.sender)
            for r in range(MAX_ROUNDS):
                price = max(learner.select(r, explore=False), reserve)
                msg = Message(to=buyer)
                msg.set_metadata("performative", "propose")
                msg.body = f"{price}|{r}"
                await self.send(msg)
                print(f"[seller] round {r}: PROPOSE price={price}")
                reply = await self.receive(timeout=10)
                if reply and reply.get_metadata("performative") == "accept":
                    print(f"[seller] deal closed at {price} "
                          f"(surplus {price - reserve})")
                    return
            print("[seller] no deal")

    class SellerAgent(Agent):
        async def setup(self):
            self.add_behaviour(SellerBehaviour())

    return SellerAgent(jid, password)


def build_buyer(jid: str, password: str, seller_jid: str, valuation: int,
                q: QLearner | None = None):
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour
    from spade.message import Message

    learner = q or QLearner(BUYER_ACTIONS)

    class BuyerBehaviour(OneShotBehaviour):
        async def run(self):
            cfp = Message(to=seller_jid)
            cfp.set_metadata("performative", "cfp")
            cfp.body = "cfp"
            await self.send(cfp)
            for _ in range(MAX_ROUNDS):
                msg = await self.receive(timeout=10)
                if not msg or msg.get_metadata("performative") != "propose":
                    return
                price, r = map(int, msg.body.split("|"))
                action = learner.select((r, price), explore=False)
                if price > valuation:
                    action = 0
                decision = "ACCEPT" if action == 1 else "REJECT"
                print(f"[buyer]  round {r}: got price={price} (valuation={valuation}) "
                      f"-> {decision}")
                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "accept" if action == 1 else "reject")
                await self.send(reply)
                if action == 1:
                    print(f"[buyer]  deal! surplus {valuation - price}")
                    await self.agent.stop()
                    return
            await self.agent.stop()

    class BuyerAgent(Agent):
        async def setup(self):
            self.add_behaviour(BuyerBehaviour())

    return BuyerAgent(jid, password)
