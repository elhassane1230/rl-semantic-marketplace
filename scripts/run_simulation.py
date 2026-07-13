"""Train the negotiating agents, compare to a random baseline, plot learning.

    python scripts/run_simulation.py
"""
from __future__ import annotations

import json
from pathlib import Path

from marketplace.simulation import learning_curve, run_simulation
from marketplace.viz import plot_learning

ROOT = Path(__file__).resolve().parents[1]


def main():
    print("Training buyer & seller with Q-learning ...")
    res = run_simulation(n_episodes=8000, seed=0)

    matched = [r for r in res.records if r.matched]
    print(f"{len(res.records)} episodes | {len(matched)} semantically matched "
          f"({len(matched)/len(res.records):.0%} — the ontology filtered the rest)")

    random = res.evaluate(n=3000, seed=999, mode="random")
    trained = res.evaluate(n=3000, seed=999, mode="greedy")

    print("\nSame held-out scenarios, learning disabled:")
    print(f"{'metric':<16}{'RANDOM':>10}{'TRAINED':>10}")
    print("-" * 36)
    for k in ["agreement_rate", "welfare", "buyer_surplus", "seller_surplus"]:
        print(f"{k:<16}{random[k]:>10.2f}{trained[k]:>10.2f}")

    figdir = ROOT / "reports" / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    fig = plot_learning(res.records, figdir / "learning.png", window=300)
    print(f"\nLearning curves -> {fig}")

    out = ROOT / "reports"
    (out / "results.json").write_text(json.dumps(
        {"random": random, "trained": trained,
         "learning_curve": learning_curve(res.records, window=300)}, indent=2))


if __name__ == "__main__":
    main()
