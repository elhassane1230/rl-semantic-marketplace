"""Run many negotiation episodes, let both agents learn, and track metrics.

Each episode: sample a scenario, gate it through the ontology, run the message
dialogue if the item matches, then assign the end-of-episode reward and update
both Q-learners. ε decays over time so the agents shift from exploring to
exploiting what they've learned. Returns the per-episode records and a smoothed
learning curve.
"""
from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass

from .agents import BuyerAgent, SellerAgent
from .environment import sample_scenario
from .ontology import MarketOntology
from .runtime import MessageBus


@dataclass
class EpisodeRecord:
    matched: bool
    deal: bool
    price: int | None
    buyer_surplus: float
    seller_surplus: float
    rounds: int


def _update(q, transitions, terminal_reward: float) -> None:
    for i, (s, a) in enumerate(transitions):
        if i == len(transitions) - 1:
            q.update(s, a, terminal_reward, None)
        else:
            q.update(s, a, 0.0, transitions[i + 1][0])


async def _run_episode(buyer: BuyerAgent, seller: SellerAgent) -> None:
    # drain any stale messages, reset per-episode state
    for ag in (buyer, seller):
        while not ag.inbox.empty():
            ag.inbox.get_nowait()
    buyer.transitions, seller.transitions = [], []
    seller.outcome = {"deal": False, "price": None, "rounds": 0}
    await asyncio.gather(buyer.behaviours[0].run(), seller.behaviours[0].run())


async def _train(n_episodes: int, seed: int):
    rng = random.Random(seed)
    onto = MarketOntology()
    bus = MessageBus()
    seller = SellerAgent("seller", bus, seed=seed)
    buyer = BuyerAgent("buyer0", bus, seed=seed + 1)
    buyer.seller_name = "seller"

    records: list[EpisodeRecord] = []
    for i in range(n_episodes):
        scenario = sample_scenario(rng, onto, i)
        buyer.scenario = scenario
        seller.scenario = scenario

        if not scenario.semantically_matches:
            records.append(EpisodeRecord(False, False, None, 0, 0, 0))
            continue

        await _run_episode(buyer, seller)

        deal = seller.outcome["deal"]
        price = seller.outcome["price"]
        rounds = seller.outcome["rounds"]
        if deal:
            b_surplus = scenario.valuation - price
            s_surplus = price - scenario.reserve
        else:
            b_surplus = s_surplus = 0

        _update(buyer.q, buyer.transitions, b_surplus)
        _update(seller.q, seller.transitions, s_surplus)
        buyer.q.decay_epsilon()
        seller.q.decay_epsilon()

        records.append(EpisodeRecord(True, deal, price, b_surplus, s_surplus, rounds))

    return records, buyer, seller


async def _evaluate(buyer_q, seller_q, n: int, seed: int, mode: str):
    """Run n episodes WITHOUT learning, with fresh agents (own event loop) that
    reuse the trained Q-tables. mode='greedy' exploits the learned policy;
    mode='random' ignores it (ε=1) as a baseline."""
    rng = random.Random(seed)
    onto = MarketOntology()
    bus = MessageBus()
    seller = SellerAgent("seller", bus, seed=seed)
    buyer = BuyerAgent("buyer0", bus, seed=seed + 1)
    seller.q, buyer.q = seller_q, buyer_q
    seller.q.epsilon = buyer.q.epsilon = 1.0 if mode == "random" else 0.0

    records = []
    for i in range(n):
        scenario = sample_scenario(rng, onto, 10_000_000 + i)
        buyer.scenario = seller.scenario = scenario
        if not scenario.semantically_matches:
            records.append(EpisodeRecord(False, False, None, 0, 0, 0))
            continue
        await _run_episode(buyer, seller)
        deal, price = seller.outcome["deal"], seller.outcome["price"]
        bs = (scenario.valuation - price) if deal else 0
        ss = (price - scenario.reserve) if deal else 0
        records.append(EpisodeRecord(True, deal, price, bs, ss,
                                     seller.outcome["rounds"]))
    return records


class SimulationResult:
    def __init__(self, records, buyer, seller):
        self.records = records
        self.buyer = buyer
        self.seller = seller

    def evaluate(self, n: int = 2000, seed: int = 999, mode: str = "greedy") -> dict:
        import copy
        bq = copy.deepcopy(self.buyer.q)
        sq = copy.deepcopy(self.seller.q)
        recs = asyncio.run(_evaluate(bq, sq, n, seed, mode))
        matched = [r for r in recs if r.matched]
        if not matched:
            return {"matched": 0}
        return {
            "matched": len(matched),
            "agreement_rate": round(sum(r.deal for r in matched) / len(matched), 3),
            "welfare": round(sum(r.buyer_surplus + r.seller_surplus
                                 for r in matched) / len(matched), 3),
            "buyer_surplus": round(sum(r.buyer_surplus for r in matched) / len(matched), 3),
            "seller_surplus": round(sum(r.seller_surplus for r in matched) / len(matched), 3),
        }


def run_simulation(n_episodes: int = 6000, seed: int = 0) -> SimulationResult:
    records, buyer, seller = asyncio.run(_train(n_episodes, seed))
    return SimulationResult(records, buyer, seller)


def learning_curve(records: list[EpisodeRecord], window: int = 300) -> dict:
    """Rolling averages over matched episodes, for plotting the learning."""
    matched = [r for r in records if r.matched]
    xs, agree, welfare, bsurp, ssurp = [], [], [], [], []
    for end in range(window, len(matched) + 1, window):
        chunk = matched[end - window:end]
        xs.append(end)
        agree.append(sum(r.deal for r in chunk) / len(chunk))
        welfare.append(sum(r.buyer_surplus + r.seller_surplus for r in chunk) / len(chunk))
        bsurp.append(sum(r.buyer_surplus for r in chunk) / len(chunk))
        ssurp.append(sum(r.seller_surplus for r in chunk) / len(chunk))
    return {"episodes": xs, "agreement_rate": agree, "welfare": welfare,
            "buyer_surplus": bsurp, "seller_surplus": ssurp}
