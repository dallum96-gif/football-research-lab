from canonical_route_registry import validate_route_registry


def test_canonical_route_registry_is_authoritative_and_coherent():
    result = validate_route_registry()

    assert result["canonical_variables"] == 1414
    assert result["unique_routes"] == 956
    assert result["orphan_routes"] == 0
    assert result["unrouted_variables"] == 458
