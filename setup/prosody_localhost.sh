#!/usr/bin/env bash
# Set up a local XMPP server (Prosody) for the SPADE deployment.
# Tested on Debian/Ubuntu. Run with sudo.
set -e

apt-get update && apt-get install -y prosody

cat > /etc/prosody/conf.d/localhost.cfg.lua <<'CFG'
VirtualHost "localhost"
  authentication = "internal_hashed"
  allow_registration = true
CFG

prosodyctl cert generate localhost || true
systemctl restart prosody || prosodyctl start

# Create the two demo accounts
prosodyctl register seller localhost secret || true
prosodyctl register buyer  localhost secret || true

echo "Prosody ready on localhost:5222 with accounts seller@localhost / buyer@localhost"
echo "If SPADE reports a TLS trust error, trust the generated cert:"
echo "  cp /var/lib/prosody/localhost.crt /usr/local/share/ca-certificates/ && update-ca-certificates"
