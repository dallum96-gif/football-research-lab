"""Read-only census of unresolved player-match identity evidence.

This deliberately does not promote identities or write canonical data. It
combines only evidence pathways already approved by the FRL identity design:

1. season-local exact FPL -> source-player crosswalk candidates;
2. cross-season propagation from previously proven FPL-code -> source ID
   anchors;
3. existing source-player -> Player Research longitudinal closure;
4. source-ID name/season continuity already present in the source archive.

The purpose is to partition the unresolved tail into evidence classes before
any promotion logic is considered.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import player_identity_audit
import player_identity_crossseason_audit
import player_identity_crosswalk
import player_research
from source_family_adapters import player_match_source_rows_for_season


def _source_rows_by_season() -> dict[str, list[dict]]:
    rows_by_season: dict[str, list[dict]] = {}
    for season in player_research.available_seasons():
        rows_by_season[season] = list(player_match_source_rows_for_season(season))
    return rows_by_season


def _direct_crosswalk_maps():
    candidates = player_identity_crosswalk.build_crosswalk_candidates()
    pair_to_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    source_to_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in candidates:
        pair = (str(row["season"]).strip(), str(row["element"]).strip())
        source_id = str(row["source_player_id"]).strip()
        if not source_id:
            continue
        pair_to_sources[pair].add(source_id)
        source_to_pairs[source_id].add(pair)
    return pair_to_sources, source_to_pairs


def _research_closure_map(pair_to_sources):
    source_to_names: dict[str, set[str]] = defaultdict(set)
    for season in player_research.available_seasons():
        for row in player_research._load_season_rows(season):
            element = str(
                row.get("element") or row.get("player_code") or row.get("id") or ""
            ).strip()
            if not element:
                continue
            canonical = player_research.canonical_player_name(row)
            if not canonical:
                continue
            for source_id in pair_to_sources.get((season, element), set()):
                source_to_names[source_id].add(canonical)
    return source_to_names


def _source_continuity(rows_by_season):
    source_to_seasons: dict[str, set[str]] = defaultdict(set)
    source_to_names: dict[str, set[str]] = defaultdict(set)
    source_to_observations: Counter[str] = Counter()

    for season, rows in rows_by_season.items():
        for row in rows:
            source_id = str(
                row.get("playerId") or row.get("player_id") or row.get("pl_code") or ""
            ).strip()
            if not source_id:
                continue
            name = str(
                row.get("playerName") or row.get("player_name") or row.get("name") or ""
            ).strip()
            source_to_seasons[source_id].add(season)
            if name:
                source_to_names[source_id].add(name)
            source_to_observations[source_id] += 1

    return source_to_seasons, source_to_names, source_to_observations


def classify() -> dict:
    rows_by_season = _source_rows_by_season()
    pair_to_sources, source_to_pairs = _direct_crosswalk_maps()
    source_to_research = _research_closure_map(pair_to_sources)
    source_to_seasons, source_to_names, source_to_observations = _source_continuity(rows_by_season)

    audit = player_identity_audit.run_audit()
    crossseason = player_identity_crossseason_audit.audit_crossseason(audit)

    crossseason_by_source: dict[str, list[dict]] = defaultdict(list)
    for row in crossseason["confirmed"]:
        crossseason_by_source[str(row["source_player_id"]).strip()].append(row)

    verified_source_ids = {
        str(row["source_player_id"]).strip()
        for result in audit["seasons"].values()
        for row in result["exact"]
        if str(row.get("source_player_id", "")).strip()
    }

    classifications: Counter[str] = Counter()
    records: list[dict] = []

    for season, rows in rows_by_season.items():
        for row in rows:
            source_id = str(
                row.get("playerId") or row.get("player_id") or row.get("pl_code") or ""
            ).strip()
            if not source_id or source_id in verified_source_ids:
                continue

            direct_pairs = sorted(source_to_pairs.get(source_id, set()))
            research_names = sorted(source_to_research.get(source_id, set()))
            crossseason_rows = crossseason_by_source.get(source_id, [])
            season_span = sorted(source_to_seasons.get(source_id, set()))
            source_names = sorted(source_to_names.get(source_id, set()))

            if len(research_names) == 1:
                category = "UNRESOLVED_BUT_UNIQUE_RESEARCH_IDENTITY"
            elif crossseason_rows:
                category = "UNRESOLVED_WITH_CROSS_SEASON_ANCHOR"
            elif direct_pairs:
                category = "UNRESOLVED_WITH_DIRECT_CROSSWALK_EVIDENCE"
            elif len(season_span) > 1:
                category = "UNRESOLVED_WITH_SOURCE_CONTINUITY_ONLY"
            else:
                category = "UNRESOLVED_NO_CURRENT_IDENTITY_PATH"

            classifications[category] += 1
            records.append(
                {
                    "season": season,
                    "source_player_id": source_id,
                    "source_name": str(
                        row.get("playerName")
                        or row.get("player_name")
                        or row.get("name")
                        or ""
                    ).strip(),
                    "direct_crosswalk_pairs": direct_pairs,
                    "research_names": research_names,
                    "crossseason_confirmed": [
                        {
                            "season": item["season"],
                            "fpl_name": item["fpl_name"],
                            "fpl_player_codes": item["fpl_player_codes"],
                            "team_code": item["team_code"],
                        }
                        for item in crossseason_rows
                    ],
                    "source_seasons": season_span,
                    "source_name_variants": source_names,
                    "source_observation_count": source_to_observations.get(source_id, 0),
                    "evidence_category": category,
                }
            )

    return {
        "total_unresolved_observations": len(records),
        "classification_counts": dict(classifications),
        "records": records,
    }


def print_report(result: dict) -> None:
    print("=" * 104)
    print("FRL UNRESOLVED PLAYER-MATCH IDENTITY EVIDENCE CENSUS")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 104)
    print()
    print(f"Unresolved observations classified: {result['total_unresolved_observations']:,}")
    print()
    for category, count in sorted(result["classification_counts"].items()):
        print(f"  {category}: {count:,}")
    print()
    print("SAMPLE BY CATEGORY:")
    seen: set[str] = set()
    for row in result["records"]:
        category = row["evidence_category"]
        if category in seen:
            continue
        seen.add(category)
        print(
            f"  {category}: season={row['season']} source={row['source_player_id']} "
            f"name={row['source_name']} source_seasons={row['source_seasons']} "
            f"research={row['research_names']} crossseason={len(row['crossseason_confirmed'])}"
        )

    print()
    print("No identities were promoted. No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    print_report(classify())
