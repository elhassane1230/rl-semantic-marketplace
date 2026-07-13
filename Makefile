.PHONY: help install simulate ontology spade test lint clean

PY := PYTHONPATH=src python3

help:
	@echo "rl-semantic-marketplace — tasks"
	@echo "  make simulate   Train agents, compare to random, plot learning curves"
	@echo "  make ontology   Semantic matching demo (SPARQL taxonomy)"
	@echo "  make test       Run tests"
	@echo "  make lint       ruff"
	@echo "  make spade      Run the negotiation on real SPADE agents (needs XMPP, see docs/RUNNING_SPADE.md)"

install:
	pip install -r requirements.txt && pip install -e .
simulate:
	$(PY) scripts/run_simulation.py
ontology:
	$(PY) scripts/ontology_demo.py
spade:
	$(PY) scripts/run_spade.py
test:
	$(PY) -m pytest tests/ -q
lint:
	ruff check src tests scripts
clean:
	rm -f reports/*.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
