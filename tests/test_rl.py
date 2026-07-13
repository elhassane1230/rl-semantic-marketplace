from marketplace.rl import QLearner


def test_learns_higher_value_action():
    q = QLearner(actions=["a", "b"], epsilon=0.0, seed=0)
    for _ in range(200):
        q.update("s", "a", reward=1.0)
        q.update("s", "b", reward=0.0)
    assert q.select("s", explore=False) == "a"


def test_epsilon_greedy_explores_then_exploits():
    q = QLearner(actions=[0, 1, 2], epsilon=1.0, seed=1)
    # with epsilon=1 it explores (can pick any action)
    picks = {q.select("s") for _ in range(50)}
    assert len(picks) > 1
    for _ in range(500):
        q.decay_epsilon(factor=0.9)
    assert q.epsilon <= 0.02


def test_td_update_propagates_future_value():
    q = QLearner(actions=[0, 1], gamma=0.9, alpha=1.0, epsilon=0.0)
    q.Q["s2"][1] = 10.0                      # future state has value
    q.update("s1", 0, reward=0.0, next_state="s2")
    assert q.Q["s1"][0] == 9.0               # 0 + 0.9 * 10
