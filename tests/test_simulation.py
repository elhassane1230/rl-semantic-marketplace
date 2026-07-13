from marketplace.simulation import learning_curve, run_simulation


def test_simulation_runs_and_matches_are_gated():
    res = run_simulation(n_episodes=2000, seed=0)
    matched = [r for r in res.records if r.matched]
    # ontology filters some scenarios out
    assert 0 < len(matched) < len(res.records)


def test_training_beats_random():
    res = run_simulation(n_episodes=8000, seed=0)
    random = res.evaluate(n=2000, seed=123, mode="random")
    trained = res.evaluate(n=2000, seed=123, mode="greedy")
    # learning should raise both agreement rate and total welfare
    assert trained["agreement_rate"] > random["agreement_rate"]
    assert trained["welfare"] >= random["welfare"]


def test_learning_curve_shape():
    res = run_simulation(n_episodes=3000, seed=0)
    lc = learning_curve(res.records, window=300)
    assert len(lc["episodes"]) == len(lc["agreement_rate"]) > 0
    assert all(0 <= a <= 1 for a in lc["agreement_rate"])
