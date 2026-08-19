from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_identity_audit
import player_research
import query_lab
from match_stats import fixture_source_match

RAW = ROOT / "data" / "raw" / "fixture_goal_events_pulselive.csv"
OUT = ROOT / "data" / "fixture_goal_events.csv"

FIELDS = (
    "season",
    "fixture_id",
    "source_match_id",
    "source_pulse_fixture_id",
    "source_event_id",
    "source_event_type",
    "source_event_seconds",
    "source_event_time_label",
    "source_event_text",
    "source_scorer_name",
    "source_scorer_team",
    "source_scorer_id",
    "pulse_player_id",
    "archive_player_id",
    "identity_status",
    "fpl_element",
    "player_name",
    "side",
    "own_goal",
    "source_url",
    "retrieved_at_utc",
    "goal_count_match",
)


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Source file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verified_team_index() -> dict[tuple[str, str], str]:
    """Resolve season + source team name to verified persistent team code."""
    rows = query_lab.load_identity_registry()
    index: dict[tuple[str, str], set[str]] = defaultdict(set)

    for row in rows:
        if row["mapping_status"] != "VERIFIED":
            continue
        season = str(row["season"]).strip()
        code = str(row["persistent_team_code"]).strip()
        for name in (
            row.get("canonical_name"),
            row.get("source_name"),
            row.get("club_id"),
            code,
        ):
            normalized = player_identity_audit.normalize_name(name)
            if normalized:
                index[(season, normalized)].add(code)

    resolved: dict[tuple[str, str], str] = {}
    for key, values in index.items():
        if len(values) != 1:
            raise RuntimeError(
                f"Verified team identity is ambiguous for {key}: {sorted(values)!r}"
            )
        resolved[key] = next(iter(values))
    return resolved


def source_name_team_code(
    team_index: dict[tuple[str, str], str],
    season: str,
    team_name: str,
) -> str:
    code = team_index.get(
        (season, player_identity_audit.normalize_name(team_name))
    )
    if not code:
        raise RuntimeError(
            f"No verified FRL team identity for {season}/{team_name!r}"
        )
    return code


def verified_player_bridge(season: str, team_code: str):
    """Use the existing read-only FRL player identity audit as the bridge.

    The audit explicitly maps FPL season-local records to persistent team codes,
    then matches them to the archive playerId namespace. PulseLive event player IDs
    remain separate provenance identifiers.
    """
    fpl_index = player_identity_audit.fpl_player_index(season)
    source_index = player_identity_audit.source_player_index(season)

    bridge = {}

    for (name_norm, code), fpl_players in fpl_index.items():
        if code != team_code:
            continue

        source_players = source_index.get((name_norm, code), set())

        if len(fpl_players) != 1 or len(source_players) != 1:
            continue

        fpl_element, player_name = next(iter(fpl_players))
        archive_player_id, source_name = next(iter(source_players))

        bridge[name_norm] = (
            archive_player_id,
            fpl_element,
            player_name,
            source_name,
        )

    return bridge


def resolve_fixture_source_map(identity_rows, fixtures):
    """Resolve source match IDs once through the existing canonical mechanism."""
    source_map: dict[tuple[str, str], tuple[dict[str, str], tuple]] = {}

    for fixture in fixtures.values():
        resolved = fixture_source_match(fixture, identity_rows)
        if not resolved:
            continue

        source_id = str(resolved[0]).strip()
        key = (str(fixture["season"]).strip(), source_id)

        if key in source_map:
            raise RuntimeError(
                f"Multiple canonical fixtures resolve to source match {key}: "
                f"{source_map[key][0]['fixture_id']} and {fixture['fixture_id']}"
            )

        source_map[key] = (fixture, resolved)

    return source_map


def atomic_write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.stem}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> None:
    raw = load_rows(RAW)
    identity_rows = query_lab.load_identity_registry()
    team_index = verified_team_index()

    fixtures = {
        (row["season"], str(row["fixture_id"])): row
        for row in query_lab.load_csv(query_lab.FIXTURE_FILE)[0]
    }
    fixture_source_map = resolve_fixture_source_map(identity_rows, fixtures)

    player_bridges: dict[tuple[str, str], dict[str, tuple]] = {}
    canonical_rows: list[dict[str, str]] = []
    skipped = 0
    unresolved_players: list[tuple[str, str, str, str, str]] = []

    for row in raw:
        season = str(row.get("season") or "").strip()
        source_match_id = str(row.get("source_match_id") or "").strip()
        scorer_name = str(row.get("source_scorer_name") or "").strip()
        scorer_team = str(row.get("source_scorer_team") or "").strip()
        pulse_player_id = str(row.get("source_scorer_id") or "").strip()

        if not season or not source_match_id:
            skipped += 1
            continue

        fixture_entry = fixture_source_map.get((season, source_match_id))
        if not fixture_entry:
            raise RuntimeError(
                f"Expected exactly one canonical fixture for source match "
                f"{season}/{source_match_id}; found 0"
            )

        fixture, (resolved_source_id, source_home, source_away) = fixture_entry
        if str(resolved_source_id) != source_match_id:
            raise RuntimeError("Source-match reconciliation changed the source identifier")

        scorer_team_code = source_name_team_code(
            team_index,
            season,
            scorer_team,
        )

        bridge_key = (season, scorer_team_code)
        if bridge_key not in player_bridges:
            player_bridges[bridge_key] = verified_player_bridge(
                season,
                scorer_team_code,
            )

        player_index = player_bridges[bridge_key]
        name_norm = player_identity_audit.normalize_name(scorer_name)
        identity_match = player_index.get(name_norm)

        if not identity_match:
            unresolved_players.append(
                (season, source_match_id, pulse_player_id, scorer_name, scorer_team)
            )
            continue

        archive_player_id, element, player_name, source_name = identity_match

        if player_identity_audit.normalize_name(source_name) != name_norm:
            raise RuntimeError(
                f"Archive player name reconciliation changed for {season}/{source_match_id}: "
                f"{scorer_name!r} -> {source_name!r}"
            )

        home_team_code = str(source_home.get("team_id") or "").strip()
        away_team_code = str(source_away.get("team_id") or "").strip()
        scorer_side = (
            "home" if scorer_team_code == home_team_code
            else "away" if scorer_team_code == away_team_code
            else ""
        )

        if not scorer_side:
            raise RuntimeError(
                f"Verified player {archive_player_id} cannot be reconciled to either "
                f"source team for {season}/{fixture['fixture_id']}"
            )

        own_goal = str(row.get("own_goal") or "false").casefold() == "true"
        scoring_side = (
            "away" if scorer_side == "home" else "home"
            if own_goal else scorer_side
        )

        canonical_rows.append(
            {
                **row,
                "fixture_id": str(fixture["fixture_id"]),
                "source_scorer_id": pulse_player_id,
                "pulse_player_id": pulse_player_id,
                "archive_player_id": archive_player_id,
                "identity_status": "VERIFIED",
                "fpl_element": element,
                "player_name": player_name,
                "side": scoring_side,
            }
        )

    if unresolved_players:
        sample = "; ".join(
            f"{season}/{match}:{pulse_id}/{name}/{team}"
            for season, match, pulse_id, name, team in unresolved_players[:10]
        )
        raise RuntimeError(
            f"Refusing canonical promotion: {len(unresolved_players)} PulseLive scorer rows "
            f"could not be bridged through the established FRL player identity audit. "
            f"Sample: {sample}"
        )

    atomic_write(OUT, canonical_rows)

    print("=" * 88)
    print("FRL GOAL EVENT VALIDATION")
    print("=" * 88)
    print(f"Raw rows inspected:        {len(raw):,}")
    print(f"Canonical rows written:    {len(canonical_rows):,}")
    print(f"Rows skipped:              {skipped:,}")
    print(f"Output:                    {OUT}")
    print(f"Validated at:              {datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}")
    print("PulseLive player IDs remain separate from archive playerId identifiers.")
    print("Canonical promotion requires verified fixture, team and player identity.")


if __name__ == "__main__":
    main()
