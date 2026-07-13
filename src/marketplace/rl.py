"""Tabular Q-learning — the reinforcement-learning core.

A small, dependency-light Q-learner (a dict-backed Q-table with ε-greedy action
selection and the standard temporal-difference update). Both the buyer and the
seller wrap one of these to learn their negotiation policy from the reward they
get at the end of each episode.

    Q(s,a) ← Q(s,a) + α · [ r + γ · max_a' Q(s',a') − Q(s,a) ]
"""
from __future__ import annotations

import random
from collections import defaultdict


class QLearner:
    def __init__(self, actions: list, alpha: float = 0.1, gamma: float = 0.95,
                 epsilon: float = 0.2, seed: int = 0):
        self.actions = list(actions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = random.Random(seed)
        self.Q: dict = defaultdict(lambda: {a: 0.0 for a in self.actions})

    def select(self, state, explore: bool = True):
        """ε-greedy action selection."""
        if explore and self.rng.random() < self.epsilon:
            return self.rng.choice(self.actions)
        q = self.Q[state]
        best = max(q.values())
        # random tie-break among best actions
        return self.rng.choice([a for a, v in q.items() if v == best])

    def update(self, state, action, reward: float, next_state=None) -> None:
        future = 0.0 if next_state is None else max(self.Q[next_state].values())
        target = reward + self.gamma * future
        self.Q[state][action] += self.alpha * (target - self.Q[state][action])

    def greedy_policy(self) -> dict:
        return {s: max(q, key=q.get) for s, q in self.Q.items()}

    def decay_epsilon(self, factor: float = 0.999, floor: float = 0.01) -> None:
        self.epsilon = max(floor, self.epsilon * factor)
