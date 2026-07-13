"""Semantic layer (web sémantique) built on rdflib.

Loads the marketplace ontology and lets agents reason over a shared vocabulary
instead of hard-coded fields:

  * items and buyer preferences are RDF resources;
  * ``item_satisfies_buyer`` answers, via a SPARQL query, whether an item meets a
    buyer's needs — including **taxonomic** reasoning: a buyer who wants a broad
    category (Electronics) is satisfied by an item of a narrower one (Laptop),
    resolved with an ``rdfs:subClassOf*`` property path.

This is genuine semantic matching: change the ontology and the matching follows,
no code change.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import XSD

EX = Namespace("http://example.org/market#")
ONTOLOGY_PATH = Path(__file__).resolve().parents[2] / "ontology" / "marketplace.ttl"


class MarketOntology:
    def __init__(self, ontology_path: str | Path | None = None):
        self.graph = Graph()
        self.graph.parse(str(ontology_path or ONTOLOGY_PATH), format="turtle")
        self.graph.bind("ex", EX)
        self._subclass_cache: dict = {}

    # -- populate a market instance -------------------------------------- #
    def add_item(self, item_id: str, category: str, quality: int,
                 reserve: int) -> URIRef:
        item = EX[item_id]
        self.graph.add((item, RDF.type, EX.Item))
        self.graph.add((item, EX.hasCategory, EX[category]))
        self.graph.add((item, EX.hasQuality, Literal(quality, datatype=XSD.integer)))
        self.graph.add((item, EX.reservePrice, Literal(reserve, datatype=XSD.integer)))
        return item

    def add_buyer(self, buyer_id: str, wants_category: str, min_quality: int,
                  budget: int, valuation: int) -> URIRef:
        buyer = EX[buyer_id]
        self.graph.add((buyer, RDF.type, EX.Buyer))
        self.graph.add((buyer, EX.wantsCategory, EX[wants_category]))
        self.graph.add((buyer, EX.minQuality, Literal(min_quality, datatype=XSD.integer)))
        self.graph.add((buyer, EX.budget, Literal(budget, datatype=XSD.integer)))
        self.graph.add((buyer, EX.valuation, Literal(valuation, datatype=XSD.integer)))
        return buyer

    # -- semantic reasoning ---------------------------------------------- #
    def item_satisfies_buyer(self, item_id: str, buyer_id: str) -> bool:
        """True iff the item's category is (a subclass of) the wanted category
        AND its quality meets the buyer's minimum — decided by SPARQL."""
        q = """
        PREFIX ex:   <http://example.org/market#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        ASK {
            ?item a ex:Item ;
                  ex:hasCategory ?icat ;
                  ex:hasQuality ?iqual .
            ?buyer ex:wantsCategory ?wanted ;
                   ex:minQuality ?minq .
            ?icat rdfs:subClassOf* ?wanted .
            FILTER(?item = ?itemR && ?buyer = ?buyerR)
            FILTER(?iqual >= ?minq)
        }"""
        return bool(self.graph.query(
            q, initBindings={"itemR": EX[item_id], "buyerR": EX[buyer_id]}))

    def category_is_subclass(self, sub: str, sup: str) -> bool:
        """SPARQL taxonomic check ``sub rdfs:subClassOf* sup``, memoised (the set
        of category pairs is small, so a long simulation stays fast)."""
        key = (sub, sup)
        cached = self._subclass_cache.get(key)
        if cached is None:
            q = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                   ASK { ?sub rdfs:subClassOf* ?sup }"""
            cached = bool(self.graph.query(
                q, initBindings={"sub": EX[sub], "sup": EX[sup]}))
            self._subclass_cache[key] = cached
        return cached

    def remove_instance(self, *resource_ids: str) -> None:
        """Remove all triples about the given item/buyer resources, so a long
        simulation doesn't accumulate a giant graph (keeps SPARQL fast)."""
        for rid in resource_ids:
            self.graph.remove((EX[rid], None, None))

    def category_ancestors(self, category: str) -> list[str]:
        """All super-categories of a category (taxonomic closure)."""
        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?super WHERE { ?cat rdfs:subClassOf* ?super }"""
        rows = self.graph.query(q, initBindings={"cat": EX[category]})
        return sorted(str(r.super).split("#")[-1] for r in rows)

    def get_int(self, resource_id: str, prop: str) -> int:
        val = self.graph.value(EX[resource_id], EX[prop])
        return int(val) if val is not None else 0
