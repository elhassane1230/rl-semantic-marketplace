"""Multi-agent negotiation with a shared ontology and reinforcement learning.

Buyer and seller agents negotiate over items described by a shared RDF/OWL
ontology (semantic matching via SPARQL) and learn their negotiation strategy by
Q-learning, exchanging FIPA-ACL messages over a lightweight asyncio runtime. A
SPADE adapter maps the same agents onto a real XMPP deployment.
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
