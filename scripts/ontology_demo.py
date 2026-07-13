"""Demonstrate the semantic layer: taxonomic matching via SPARQL.

    python scripts/ontology_demo.py
"""
from __future__ import annotations

from marketplace.ontology import MarketOntology


def main():
    o = MarketOntology()

    o.add_item("laptop1", "Laptop", quality=8, reserve=600)
    o.add_item("chair1", "Chair", quality=9, reserve=50)
    o.add_buyer("alice", "Electronics", min_quality=7, budget=900, valuation=800)
    o.add_buyer("bob", "Electronics", min_quality=9, budget=900, valuation=800)
    o.add_buyer("carol", "Furniture", min_quality=5, budget=100, valuation=90)

    print("Category taxonomy (SPARQL rdfs:subClassOf*):")
    print("  Laptop is a:", o.category_ancestors("Laptop"))
    print("  Chair  is a:", o.category_ancestors("Chair"))

    print("\nSemantic matching (does the item satisfy the buyer?):")
    cases = [
        ("laptop1", "alice", "wants Electronics, minQ 7 — Laptop⊂Electronics, q8≥7"),
        ("chair1", "alice", "wants Electronics — Chair is Furniture, no"),
        ("laptop1", "bob", "wants Electronics but minQ 9 — q8<9, no"),
        ("chair1", "carol", "wants Furniture, minQ 5 — Chair⊂Furniture, q9≥5"),
    ]
    for item, buyer, why in cases:
        ok = o.item_satisfies_buyer(item, buyer)
        print(f"  {item:<8} -> {buyer:<6}: {'MATCH ' if ok else 'no    '} ({why})")


if __name__ == "__main__":
    main()
