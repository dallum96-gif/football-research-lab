"""Audit how the discovered FRL variable universe can be attached to canonical entities.

Evidence-first and fail-closed. This is a discovery/relationship audit only.
It does not promote fields or invent joins. It reads the local source-audit
artifacts when executed from frl-source-audit and distinguishes direct grain
scope from unresolved relationship coverage.

Inputs:
- data/master_variable_universe_decomposed.csv
- data/frl_variable_dictionary.csv (when present)

Outputs:
- data/variable_entity_relationship_coverage.csv

The audit is intentionally conservative:
- direct grain scope is derived only from an explicit resolved/decomposed grain;
- canonical entity attachment is trusted only when the dictionary explicitly
  supplies canonical_attachment / relationship_kind / identity_contract metadata;
- otherwise the entity link is REVIEW rather than guessed.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
UNIVERSE = DATA / "master_variable_universe_decomposed.csv"
DICTIONARY = DATA / "frl_variable_dictionary.csv"
OUT = DATA / "variable_entity_relationship_coverage.csv"

ENTITY_COLUMNS = ("player", "fixture", "club")


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def canonical_attachment_tokens(value: str) -> set[str]:
    low = value.lower()
    tokens: set[str] = set()
    for token in ENTITY_COLUMNS:
        if token in low:
            tokens.add(token)
    if "team" in low or "club" in low:
        tokens.add("club")
    return tokens


def grain_scope(grain: str) -> tuple[str, set[str]]:
    g = grain.strip().lower()
    if g == "player":
        return "player", {"player"}
    if g == "player_season":
        return "player_season", {"player"}
    if g == "player_match":
        return "player_match", {"player", "fixture"}
    if g == "team":
        return "team", {"club"}
    if g == "team_season":
        return "team_season", {"club"}
    if g == "team_match":
        return "team_match", {"club", "fixture"}
    if g == "fixture":
        return "fixture", {"fixture"}
    if g == "event":
        return "event", set()
    if g in {"squad", "registration"}:
        return g, {"club", "player"}
    return g or "UNKNOWN", set()


def merge_dictionary(universe: list[dict[str, str]], dictionary: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_field: dict[str, dict[str, str]] = {}
    for row in dictionary:
        field = first(row, "field_name", "field", "variable", "name")
        if field:
            by_field[field] = row
    for row in universe:
        field = first(row, "field_name", "field", "variable", "name")
        if field and field not in by_field:
            by_field[field] = {}
    return by_field


def status_for_entity(entity: str, explicit_entities: set[str], scope_entities: set[str], metadata: dict[str, str]) -> str:
    if entity in explicit_entities:
        return "VERIFIED_METADATA_SCOPE"
    if entity in scope_entities:
        # A player_match can scope to fixture, but this is not the same as a
        # verified canonical fixture join; keep that distinction explicit.
        if first(metadata, "canonical_attachment", "relationship_kind", "identity_contract"):
            return "RELATIONSHIP_METADATA_PRESENT"
        return "RELATIONSHIP_REVIEW"
    return "NOT_IN_DIRECT_GRAIN"


def main() -> list[dict[str, str]]:
    universe = load_rows(UNIVERSE)
    dictionary = load_rows(DICTIONARY)
    meta_by_field = merge_dictionary(universe, dictionary)

    rows: list[dict[str, str]] = []
    for source_row in universe:
        field = first(source_row, "field_name", "field", "variable", "name")
        if not field:
            continue

        grain = first(source_row, "decomposed_grain", "resolved_grain", "grain", "original_grain")
        scope, scope_entities = grain_scope(grain)
        meta = meta_by_field.get(field, {})
        explicit_attachment = first(meta, "canonical_attachment")
        explicit_entities = canonical_attachment_tokens(explicit_attachment)

        # A source-local identity is not a canonical identity. We only report
        # that it exists and keep the canonical relationship status separate.
        source_identity = first(meta, "source_identity_required")
        relationship_kind = first(meta, "relationship_kind")
        identity_contract = first(meta, "identity_contract")
        relationship_note = first(meta, "relationship_note")

        rows.append({
            "field_name": field,
            "source_surface": first(source_row, "source_surface"),
            "resource": first(source_row, "resource"),
            "grain": scope,
            "decomposition_basis": first(source_row, "decomposition_basis"),
            "field_type": first(source_row, "field_type"),
            "player_link": status_for_entity("player", explicit_entities, scope_entities, meta),
            "fixture_link": status_for_entity("fixture", explicit_entities, scope_entities, meta),
            "club_link": status_for_entity("club", explicit_entities, scope_entities, meta),
            "canonical_attachment": explicit_attachment,
            "relationship_kind": relationship_kind,
            "identity_contract": identity_contract,
            "source_identity_required": source_identity,
            "relationship_note": relationship_note,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "field_name", "source_surface", "resource", "grain", "decomposition_basis", "field_type",
        "player_link", "fixture_link", "club_link", "canonical_attachment",
        "relationship_kind", "identity_contract", "source_identity_required", "relationship_note",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    return rows


if __name__ == "__main__":
    rows = main()
    print("FRL VARIABLE -> ENTITY RELATIONSHIP COVERAGE AUDIT")
    print("=" * 100)
    print(f"Variables audited: {len(rows)}")
    for entity in ENTITY_COLUMNS:
        counts = Counter(r[f"{entity}_link"] for r in rows)
        print(f"\n{entity.upper()}")
        for key, value in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {value:5d}  {key}")
    print(f"\nOutput: {OUT}")
    print("Evidence-only relationship coverage; no canonical promotion and no inferred joins.")
