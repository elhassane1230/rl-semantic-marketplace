# Results

Reproduce with `make simulate` (writes `reports/results.json` and the figure).

## Setup
8,000 training episodes, seed 0. Each episode samples an item + buyer; the
ontology gate (SPARQL) lets ~36% through to negotiation. Prices are integers on a
0–10 grid; up to 4 rounds per negotiation.

## Trained vs random (held-out scenarios, learning disabled)

| Metric | Random | Trained |
|--------|:------:|:-------:|
| agreement rate | 0.79 | 0.96 |
| total welfare | 3.02 | 3.52 |
| buyer surplus | 1.82 | 1.14 |
| seller surplus | 1.20 | 2.37 |

## Interpretation
- **Agreement rate ↑ (0.79 → 0.96)**: the agents learn to reach deals instead of
  failing to agree within the round limit.
- **Welfare ↑ (3.02 → 3.52)**: outcomes are more efficient — more of the possible
  surplus is realised.
- **Split shifts to the seller**: the seller proposes first and learns a pricing
  policy that captures more surplus; the buyer learns mainly to reject clearly
  bad offers. This is a real multi-agent equilibrium driven by the protocol's
  first-mover structure, not a bug. Changing the protocol (e.g. buyer counter-
  offers) would rebalance it — see IMPROVEMENTS.

## Honesty notes
- The environment is a small, stylised negotiation game; absolute surplus numbers
  are only meaningful relative to the random baseline on the same scenarios.
- Q-learning here is tabular on a discretised price grid; scaling to continuous
  prices or richer state would need function approximation.
- The semantic gate is real SPARQL reasoning but on a compact ontology; the point
  is the *integration* (ontology decides who negotiates, RL decides how), which
  carries over to larger ontologies.
