# Architecture

## Flow

```
sample_scenario ──► ontology gate (SPARQL subClassOf* + quality)
     │                       │ matches?
     │                       ▼
     │             negotiation dialogue (message bus)
     │        buyer CFP ─► seller PROPOSE(price) ─► buyer ACCEPT/REJECT ─► ...
     │                       │ outcome (deal, price, rounds)
     ▼                       ▼
  reward = surplus ──► Q-learning update (buyer + seller) ──► ε decay
                               │
                               ▼
                      metrics + learning curve
```

## Components

### Semantic layer (`ontology.py`, `marketplace.ttl`)
The ontology defines a category taxonomy (`Laptop ⊂ Computer ⊂ Electronics`),
item properties (category, quality, reserve price) and buyer preferences (wanted
category, min quality, budget, valuation). `item_satisfies_buyer` answers, via a
SPARQL `ASK` with an `rdfs:subClassOf*` property path, whether an item's category
falls under the wanted one and meets the quality bar. The subclass check is
memoised (a small, fixed set of category pairs), so long runs stay fast while the
reasoning is still done by SPARQL.

### Agent runtime (`runtime.py`, `messages.py`)
A minimal FIPA-style runtime: `MessageBus` routes `Message`s to per-agent
`asyncio.Queue` inboxes; an `Agent` owns an inbox and `Behaviour`s; a `Behaviour`
has `send`/`receive`. These are the same concepts SPADE/PADE expose, so the
`spade_adapter` maps onto them one-to-one. Messages carry FIPA performatives
(CFP, PROPOSE, ACCEPT, REJECT, COUNTER).

### Reinforcement learning (`rl.py`, `agents.py`)
A tabular `QLearner` (dict Q-table, ε-greedy, TD update). The **seller** learns a
pricing policy keyed on the round; the **buyer** an acceptance policy keyed on
(round, proposed price). Rewards are the end-of-episode surplus (valuation−price
for the buyer, price−reserve for the seller; 0 on no deal). Each agent records
its (state, action) trajectory; the simulation assigns the terminal reward and
back-propagates it with the standard Q-learning chaining across rounds.

### Simulation (`simulation.py`)
Trains both agents over many episodes with ε decay, then evaluates the learned
(greedy) policies against a random baseline on held-out scenarios. Because
asyncio queues are bound to their event loop, evaluation builds fresh agents in
its own loop and re-injects the trained Q-tables.

### SPADE adapter (`spade_adapter.py`)
The same buyer/seller as real SPADE agents (`spade.agent.Agent`,
`spade.behaviour.*`, `spade.message.Message`) over XMPP. Imported lazily so the
package works without SPADE installed.

## Why a local runtime and SPADE both
SPADE requires a running XMPP server (and TLS certificates) — a poor prerequisite
for training or CI. The local asyncio runtime makes the RL + semantics run
anywhere and deterministically; SPADE is the networked deployment of the exact
same policy and protocol. This mirrors how you'd separate "train/simulate" from
"deploy" in practice.
