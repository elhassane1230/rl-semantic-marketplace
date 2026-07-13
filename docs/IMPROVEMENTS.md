# Improvements & roadmap

1. **Richer negotiation protocol.** Let the buyer make counter-offers (COUNTER is
   already in the performatives) so both sides move on price; study how the
   surplus split rebalances versus the current seller-first protocol.

2. **Deep RL for larger state/continuous prices.** Replace the tabular Q-table
   with a small function approximator (DQN) to handle continuous prices, richer
   item features, and more agents.

3. **More agents and a real market.** Many buyers and sellers matched each round
   via the ontology, with competition — study emergent prices and whether they
   approach a competitive equilibrium.

4. **Ontology-driven utility.** Derive the buyer's valuation from item properties
   in the ontology (quality, category) via SPARQL, so preferences and matching
   share one semantic source of truth.

5. **OWL reasoning.** Add an OWL reasoner (owlready2 / HermiT) for inferred class
   membership and property restrictions, beyond RDFS subclass paths.

6. **Full SPADE experiment.** Run the trained policies on SPADE across several
   machines, measuring that networked outcomes match the simulation, plus latency.

7. **Evaluation depth.** Report convergence speed, sensitivity to α/γ/ε, and
   robustness to opponents with different (or adversarial) strategies.
