# Running the negotiation on real SPADE agents

The negotiation runs on real **SPADE** agents over a local Prosody XMPP server
(Ubuntu/Debian). The offline simulation (`make simulate`) trains the policy and
runs anywhere; this is the networked deployment.

## 1. Project

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -e .
pip install -r requirements-spade.txt      # SPADE
```

## 2. XMPP server (Prosody)

```bash
sudo apt-get update && sudo apt-get install -y prosody

sudo tee /etc/prosody/conf.d/localhost.cfg.lua > /dev/null <<'CFG'
VirtualHost "localhost"
  authentication = "internal_hashed"
  allow_registration = true
CFG

sudo prosodyctl cert generate localhost
sudo systemctl restart prosody            # or: sudo prosodyctl start

sudo prosodyctl register seller localhost secret
sudo prosodyctl register buyer  localhost secret
```

## 3. Trust the certificate (makes TLS work)

SPADE (via slixmpp) verifies the server certificate against the system trust
store:

```bash
sudo cp /var/lib/prosody/localhost.crt /usr/local/share/ca-certificates/prosody-localhost.crt
sudo update-ca-certificates
```

## 4. Run

```bash
make spade            # or: PYTHONPATH=src python scripts/run_spade.py
```

The script trains the policy with the offline simulator, then injects the learned
Q-tables into the SPADE agents, so the networked negotiation uses the learned
strategy.

## Expected output

```
Training policies with the offline simulator...
Scenario: seller reserve=3, buyer valuation=8 (zone of agreement 3..8)

[seller] round 0: PROPOSE price=7
[buyer]  round 0: got price=7 (valuation=8) -> REJECT
[seller] round 1: PROPOSE price=6
[buyer]  round 1: got price=6 (valuation=8) -> ACCEPT
[buyer]  deal! surplus 2
[seller] deal closed at 6 (surplus 3)

SPADE negotiation finished.
```

Two real SPADE agents negotiated over XMPP with the **learned** strategy: the
seller opens high and concedes, the buyer holds out a round then accepts. The
split (buyer +2, seller +3) reflects the seller's first-mover advantage described
in [`docs/RESULTS.md`](RESULTS.md).

## Troubleshooting

- **`Invalid certificate trust chain`** — step 3 didn't take. Re-copy
  `/var/lib/prosody/localhost.crt` and re-run `update-ca-certificates`.
- **`No appropriate login method`** — keep TLS enabled and make sure the
  certificate is trusted (step 3).
- **`Connection refused`** — Prosody isn't running:
  `sudo systemctl status prosody`.
