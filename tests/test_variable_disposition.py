import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data" / "canonical_variable_universe_v1.csv"
ROUTES = ROOT / "data" / "frl_canonical_variable_routes_v1.csv"
FPL = ROOT / "data" / "fpl_canonical_variable_registry_v1.csv"


def load(path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def key(row):
    return "|".join(
        str(row.get(name, ""))
        for name in ("source_surface", "resource", "grain", "field_name")
    )


def test_authoritative_variable_disposition_counts():
    canonical = load(CANONICAL)
    routes = load(ROUTES)
    fpl = load(FPL)

    canonical_keys = {key(row) for row in canonical}
    route_keys = {key(row) for row in routes}
    unrouted = [row for row in canonical if key(row) not in route_keys]

    assert len(canonical) == 1414
    assert len(route_keys) == 956
    assert len(unrouted) == 458

    fpl_unrouted = [row for row in unrouted if row.get("source_surface") == "fpl"]
    local_json_unrouted = [
        row for row in unrouted
        if row.get("source_surface") == "local_json"
        and row.get("resource") == "raw_upstream"
    ]

    assert len(fpl_unrouted) == 452
    assert len(local_json_unrouted) == 6
    assert len(fpl) == 452
    assert sum(row.get("research_exposed") == "YES" for row in fpl) == 241
    assert sum(row.get("research_exposed") == "NO" for row in fpl) == 211

    assert canonical_keys.isdisjoint(set())
