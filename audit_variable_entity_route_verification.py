"""Verify variable/entity routes against existing FRL evidence artifacts.

Evidence-only: this does not create joins or promote identities.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ROUTES = DATA / "variable_entity_route_propagation.csv"
OUT = DATA / "variable_entity_route_verification.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r), r.fieldnames or []


def n(v):
    return str(v or "").strip()


def file_exists(name: str) -> bool:
    return (DATA / name).is_file() or (ROOT / name).is_file()


def evidence_status(row: dict[str, str], entity: str) -> tuple[str, str]:
    grain = n(row.get("grain")).lower()
    contract = n(row.get("identity_contract")).lower()
    source_surface = n(row.get("source_surface")).lower()
    resource = n(row.get("resource")).lower()

    if entity == "FIXTURE":
        if contract == "canonical_fixture_to_source_match":
            if file_exists("fixture_match_stats.csv") or file_exists("fixtures_master.csv"):
                return "ROUTE_EVIDENCE_PRESENT", "canonical_fixture_to_source_match + fixture registry/match evidence"
            return "CONTRACT_PRESENT_EVIDENCE_ARTIFACT_MISSING", "canonical_fixture_to_source_match"
        if grain in {"fixture", "team_match", "player_match", "event"}:
            return "GRAIN_ROUTE_EVIDENCE_REQUIRED", f"grain={grain}"
        return "NOT_APPLICABLE", "grain/contract not fixture-compatible"

    if entity == "TEAM":
        if contract == "canonical_team_season_to_source_team":
            if file_exists("../identity/team_seasons.csv") or (ROOT / "identity" / "team_seasons.csv").is_file():
                return "ROUTE_EVIDENCE_PRESENT", "canonical_team_season_to_source_team + team-season registry"
            return "CONTRACT_PRESENT_EVIDENCE_ARTIFACT_MISSING", "canonical_team_season_to_source_team"
        if grain in {"team", "team_match", "squad"}:
            return "GRAIN_ROUTE_EVIDENCE_REQUIRED", f"grain={grain}"
        return "NOT_APPLICABLE", "grain/contract not team-compatible"

    # PLAYER
    if contract == "source_player_identity_to_player_season":
        # Existing player-season adapter contract is explicit; source rows are season-scoped.
        return "ROUTE_EVIDENCE_PRESENT", "source_player_identity_to_player_season + season-scoped player_season adapter"
    if contract == "player_identity_to_player_match_observations":
        return "ROUTE_EVIDENCE_PRESENT", "player_identity_to_player_match_observations + player-match adapter"
    if contract == "fpl_player_to_frl_player_identity":
        if (ROOT / "player_identity_registry.csv").is_file():
            return "ROUTE_EVIDENCE_PRESENT_REQUIRES_SEASONAL_IDENTITY_CHECK", "FPL->FRL contract + player identity registry"
        return "CONTRACT_PRESENT_EVIDENCE_ARTIFACT_MISSING", "fpl_player_to_frl_player_identity"
    if grain in {"player", "player_season", "player_match"}:
        return "GRAIN_ROUTE_EVIDENCE_REQUIRED", f"grain={grain}"
    return "NOT_APPLICABLE", "grain/contract not player-compatible"


def main():
    rows, cols = read_csv(ROUTES)
    print("FRL VARIABLE -> ENTITY ROUTE VERIFICATION AUDIT")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows)}")
    print("Existing repository evidence only; no inferred joins and no canonical promotion.")

    # Current route-propagation output is one row per variable.
    out = []
    counters = {e: Counter() for e in ("PLAYER", "FIXTURE", "TEAM")}

    for row in rows:
        item = dict(row)
        for entity in ("PLAYER", "FIXTURE", "TEAM"):
            status, basis = evidence_status(row, entity)
            counters[entity][status] += 1
            item[f"{entity.lower()}_route_verification"] = status
            item[f"{entity.lower()}_route_evidence_basis"] = basis
        out.append(item)

    for entity in ("PLAYER", "FIXTURE", "TEAM"):
        print(f"\n{entity}")
        for k, v in counters[entity].most_common():
            print(f"  {v:6}  {k}")

    fields = list(dict.fromkeys(cols + [
        "player_route_verification", "player_route_evidence_basis",
        "fixture_route_verification", "fixture_route_evidence_basis",
        "team_route_verification", "team_route_evidence_basis",
    ]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    print(f"\nOutput: {OUT}")
    print("Evidence-only route verification; no inferred joins and no canonical promotion.")


if __name__ == "__main__":
    main()
