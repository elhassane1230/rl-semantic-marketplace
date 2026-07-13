"""Run the negotiation on real SPADE agents over XMPP, using a trained policy.

Prerequisites:
  1. An XMPP server with accounts (see setup/prosody_localhost.sh).
  2. pip install -r requirements-spade.txt

    python scripts/run_spade.py

The policy is trained *before* the SPADE event loop starts (the offline
simulator uses asyncio internally, so it can't run inside spade.run), then the
learned Q-tables are injected into the SPADE agents.
"""
from __future__ import annotations

import asyncio

import spade

from marketplace.simulation import run_simulation
from marketplace.spade_adapter import build_buyer, build_seller

XMPP = "localhost"
RESERVE = 3       # seller's secret floor
VALUATION = 8     # buyer's secret ceiling


async def negotiate(seller_q, buyer_q):
    print(f"Scenario: seller reserve={RESERVE}, buyer valuation={VALUATION} "
          f"(zone of agreement {RESERVE}..{VALUATION})\n")
    seller = build_seller(f"seller@{XMPP}", "secret", reserve=RESERVE, q=seller_q)
    await seller.start(auto_register=True)
    buyer = build_buyer(f"buyer@{XMPP}", "secret", f"seller@{XMPP}",
                        valuation=VALUATION, q=buyer_q)
    await buyer.start(auto_register=True)

    while buyer.is_alive():
        await asyncio.sleep(0.5)
    await seller.stop()
    print("\nSPADE negotiation finished.")


def main():
    # Train BEFORE starting SPADE's event loop (the simulator calls asyncio.run
    # internally, which can't be nested inside spade.run).
    print("Training policies with the offline simulator...")
    res = run_simulation(n_episodes=6000, seed=0)
    spade.run(negotiate(res.seller.q, res.buyer.q))


if __name__ == "__main__":
    main()
