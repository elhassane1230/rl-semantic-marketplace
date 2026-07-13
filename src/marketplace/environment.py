"""The negotiation environment: scenarios and outcomes.

A scenario pairs a seller's item (category, quality, secret reserve price) with a
buyer (wanted category, min quality, budget, secret valuation). Prices live on a
small integer grid so the Q-tables stay compact and the learning is easy to see.

The buyer first uses the **ontology** to decide whether the item is even relevant
(category taxonomy + quality). Only semantically-matching pairs go to price
negotiation — that's where the semantic layer gates the multi-agent interaction.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from .ontology import MarketOntology

CATEGORIES = ["Laptop", "Phone", "Computer", "Chair"]
WANTED = ["Electronics", "Computer", "Furniture"]
PRICE_MIN, PRICE_MAX = 0, 10
MAX_ROUNDS = 4


@dataclass
class Scenario:
    item_id: str
    buyer_id: str
    category: str
    quality: int
    reserve: int          # seller's secret floor
    wanted: str
    min_quality: int
    valuation: int        # buyer's secret ceiling
    semantically_matches: bool


@dataclass
class Outcome:
    deal: bool
    price: int | None
    buyer_surplus: float
    seller_surplus: float
    rounds: int
    matched: bool


def sample_scenario(rng: random.Random, onto: MarketOntology, idx: int) -> Scenario:
    category = rng.choice(CATEGORIES)
    quality = rng.randint(4, 10)
    reserve = rng.randint(2, 6)
    wanted = rng.choice(WANTED)
    min_quality = rng.randint(4, 8)
    valuation = rng.randint(5, 10)

    item_id, buyer_id = f"item{idx}", f"buyer{idx}"
    # semantic gate: category taxonomy (SPARQL, memoised) + quality threshold
    matches = onto.category_is_subclass(category, wanted) and quality >= min_quality

    return Scenario(item_id, buyer_id, category, quality, reserve, wanted,
                    min_quality, valuation, matches)
