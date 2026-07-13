from marketplace.ontology import MarketOntology


def test_taxonomy_ancestors():
    o = MarketOntology()
    anc = o.category_ancestors("Laptop")
    assert {"Laptop", "Computer", "Electronics", "Category"} <= set(anc)


def test_subclass_reasoning():
    o = MarketOntology()
    assert o.category_is_subclass("Laptop", "Electronics")     # transitive
    assert o.category_is_subclass("Laptop", "Laptop")          # reflexive
    assert not o.category_is_subclass("Chair", "Electronics")


def test_semantic_match_uses_taxonomy_and_quality():
    o = MarketOntology()
    o.add_item("i1", "Laptop", quality=8, reserve=500)
    o.add_buyer("b1", "Electronics", min_quality=7, budget=900, valuation=800)
    assert o.item_satisfies_buyer("i1", "b1")                  # subclass + quality ok
    o.add_buyer("b2", "Electronics", min_quality=9, budget=900, valuation=800)
    assert not o.item_satisfies_buyer("i1", "b2")              # quality too low
    o.add_buyer("b3", "Furniture", min_quality=1, budget=900, valuation=800)
    assert not o.item_satisfies_buyer("i1", "b3")              # wrong category


def test_remove_instance_keeps_graph_small():
    o = MarketOntology()
    base = len(o.graph)
    o.add_item("x", "Phone", quality=5, reserve=100)
    assert len(o.graph) > base
    o.remove_instance("x")
    assert len(o.graph) == base
