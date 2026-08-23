"""Read-only census of evidence for the canonical Player edge.

This deliberately mirrors the frozen V1 Player attachment resolver semantics:
- one verified season-local source-player registry candidate;
- existing verified-registry -> Player Research closure;
- existing crosswalk/cross-season evidence;
- source identity continuity.

No canonical IDs are promoted and no files are written.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import player_identity_audit
import player_identity_crossseason_audit
import player_identity_crosswalk
import player_research
from source_family_adapters import player_match_source_rows_for_season


def _source_rows_by_season() -> dict[str, tuple[dict, ...]]:
    return {
        season: player_match_source_rows_for_season(season)
        for season in player_research.available_seasons()
    }


def _verified_direct_map() -> dict[tuple[str, str], list[dict[str, str]]]:
    """Existing verified source-player registry candidates, indexed once."""
    from player_identity_registry import build_registry

    out: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in build_registry():
        if str(row.get("identity_status") or "").strip() != "VERIFIED":
            continue
        season = str(row.get("season") or "").strip()
        source_id = str(row.get("source_player_id") or "").strip()
        if season and source_id:
            out[(season, source_id)].append(row)
    return out


def _research_map() -> dict[str, set[str]]:
    """Existing verified-registry source ID -> Player Research identity closure."""
    from materialize_variable_entity_attachment_schema_v1 import _verified_registry_research_map
    from player_identity_registry import build_registry

    return _verified_registry_research_map(build_registry())


def _crosswalk_evidence():
    pair_to_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    source_to_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in player_identity_crosswalk.build_crosswalk_candidates():
        season = str(row.get("season") or "").strip()
        element = str(row.get("element") or "").strip()
        source_id = str(row.get("source_player_id") or "").strip()
        if not season or not element or not source_id:
            continue
        pair_to_sources[(season, element)].add(source_id)
        source_to_pairs[source_id].add((season, element))
    return pair_to_sources, source_to_pairs


def _source_continuity(rows_by_season):
    source_to_seasons: dict[str, set[str]] = defaultdict(set)
    source_to_names: dict[str, set[str]] = defaultdict(set)
    for season, rows in rows_by_season.items():
        for row in rows:
            source_id = str(
                row.get("playerId") or row.get("player_id") or row.get("pl_code") or ""
            ).strip()
            if not source_id:
                continue
            source_to_seasons[source_id].add(season)
            name = str(
                row.get("playerName") or row.get("player_name") or row.get("name") or ""
            ).strip()
            if name:
                source_to_names[source_id].add(name)
    return source_to_seasons, source_to_names


def _crossseason_confirmed():
    audit = player_identity_audit.run_audit()
    result = player_identity_crossseason_audit.audit_crossseason(audit)
    out: dict[str, list[dict]] = defaultdict(list)
    for row in result["confirmed"]:
        out[str(row["source_player_id"]).strip()].append(row)
    return out


def classify() -> dict:
    rows_by_season = _source_rows_by_season()
    direct_map = _verified_direct_map()
    research_map = _research_map()
    _, source_to_pairs = _crosswalk_evidence()
    source_to_seasons, source_to_names = _source_continuity(rows_by_season)
    crossseason = _crossseason_confirmed()

    counts: Counter[str] = Counter()
    records: list[dict] = []

    for season, rows in rows_by_season.items():
        for row in rows:
            source_id = str(
                row.get("playerId") or row.get("player_id") or row.get("pl_code") or ""
            ).strip()
            if not source_id:
                continue

            direct = direct_map.get((season, source_id), [])
            research = research_map.get(source_id, set())

            if len(direct) == 1 and len(research) == 1:
                category = "CANONICAL_VERIFIED_DIRECT_REGISTRY_CLOSURE"
            elif len(direct) == 1:
                category = "SOURCE_VERIFIED_CANONICAL_UNCLOSED"
            elif len(direct) > 1:
                category = "REVIEW_MULTIPLE_DIRECT_REGISTRY_CANDIDATES"
            elif len(research) == 1:
                category = "CANONICAL_VERIFIED_REGISTRY_CROSSSEASON_CLOSURE"
            elif len(research) > 1:
                category = "REVIEW_MULTIPLE_RESEARCH_IDENTITIES"
            elif crossseason.get(source_id):
                category = "UNRESOLVED_WITH_CROSS_SEASON_ANCHOR"
            elif source_to_pairs.get(source_id):
                category = "UNRESOLVED_WITH_DIRECT_CROSSWALK_EVIDENCE"
            elif len(source_to_seasons.get(source_id, set())) > 1:
                category = "UNRESOLVED_WITH_SOURCE_CONTINUITY_ONLY"
            else:
                category = "UNRESOLVED_NO_CURRENT_IDENTITY_PATH"

            counts[category] += 1
            records.append({
                "season": season,
                "source_player_id": source_id,
                "source_name": str(
                    row.get("playerName") or row.get("player_name") or row.get("name") or ""
                ).strip(),
                "direct_registry_candidates": len(direct),
                "research_identities": sorted(research),
                "crossseason_confirmed": len(crossseason.get(source_id, [])),
                "direct_crosswalk_pairs": sorted(source_to_pairs.get(source_id, set())),
                "source_seasons": sorted(source_to_seasons.get(source_id, set())),
                "source_name_variants": sorted(source_to_names.get(source_id, set())),
                "evidence_category": category,
            })

    return {
        "total_observations": len(records),
        "counts": dict(counts),
        "records": records,
    }


def print_report(result: dict) -> None:
    print("=" * 104)
    print("FRL PLAYER-MATCH CANONICAL PLAYER EVIDENCE CENSUS")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 104)
    print()
    print(f"Player-match observations classified: {result['total_observations']:,}")
    print()
    for category, count in sorted(result["counts"].items()):
        print(f"  {category}: {count:,}")
    print()
    print("CANONICAL-UNRESOLVED CHECK")
    unresolved = sum(
        count
        for category, count in result["counts"].items()
        if not category.startswith("CANONICAL_VERIFIED")
    )
    verified = sum(
        count
        for category, count in result["counts"].items()
        if category.startswith("CANONICAL_VERIFIED")
    )
    print(f"  canonical verified:   {verified:,}")
    print(f"  canonical unresolved: {unresolved:,}")
    print(f"  total:                {verified + unresolved:,}")
    print()
    print("SAMPLE BY CATEGORY")
    seen: set[str] = set()
    for row in result["records"]:
        category = row["evidence_category"]
        if category in seen:
            continue
        seen.add(category)
        print(
            f"  {category}: season={row['season']} source={row['source_player_id']} "
            f"name={row['source_name']} direct={row['direct_registry_candidates']} "
            f"research={row['research_identities']} source_seasons={row['source_seasons']}"
        )
    print()
    print("No identities were promoted. No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    print_report(classify())
