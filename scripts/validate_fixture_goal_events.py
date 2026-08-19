from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
import os
import sys
import tempfile
import unicodedata
import re
from collections import defaultdict

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


def normalize_name(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def fpl_players_by_name_team() -> dict[tuple[str, str, str], set[tuple[str, str]]]:
    """Index FPL players using the authoritative FRL team resolver.

    Do not trust the FPL file's numeric team_code here: FRL's canonical team
    identity is reconstructed from the player's club name through query_lab.
    """
    index: dict[tuple[str, str, str], set[tuple[str, str]]] = defaultdict(set)

    for season in player_identity_audit.SEASONS:
        for row in player_research._load_season_rows(season):
            element = player_research.seasonal_player_id(row)
            player_name = player_research.display_player_name(row)
            club_name = player_research._row_club(row)

            if not element or not player_name or not club_name:
                continue

            try:
                team = query_lab.resolve_team(season, club_name)
            except (ValueError, KeyError):
                continue

            team_code = str(team["persistent_team_code"]).strip()
            key = (season, normalize_name(player_name), team_code)
            index[key].add((str(element).strip(), player_name.strip()))

    return index


def archive_players_by_name_team() -> dict[tuple[str, str, str], set[tuple[str, str]]]:
    """Use the existing player identity audit's source-player namespace."""
    index: dict[tuple[str, str, str], set[tuple[str, str]]] = defaultdict(set)

    for season in player_identity_audit.SEASONS:
        for (name_norm, team_code), values in player_identity_audit.source_player_index(season).items():
            key = (season, name_norm, str(team_code).strip())
            index[key].update(values)

    return index


def verified_event_player_index() -> dict[tuple[str, str, str], tuple[str, str, str]]:
    """Bridge PulseLive event players without conflating ID namespaces."""
    fpl = fpl_players_by_name_team()
    archive = archive_players_by_name_team()
    resolved: dict[tuple[str, str, str], tuple[str, str, str]] = {}

    keys = set(fpl) & set(archive)
    for season, name_norm, team_code in keys:
        fpl_values = fpl[(season, name_norm, team_code)]
        archive_values = archive[(season, name_norm, team_code)]

        if len(fpl_values) != 1 or len(archive_values) != 1:
            raise RuntimeError(
                f"Authoritative player identity is ambiguous for "
                f"{season}/{name_norm}/{team_code}: "
                f"fpl={sorted(fpl_values)!r}, archive={sorted(archive_values)!r}"
            )

        fpl_element, fpl_display = next(iter(fpl_values))
        archive_player_id, archive_display = next(iter(archive_values))
        resolved[(season, name_norm, team_code)] = (
            archive_player_id,
            fpl_element,
            fpl_display or archive_display,
        )

    return resolved


def verified_team_index() -> dict[tuple[str, str], str]:
    """Resolve event team display names through the existing FRL team registry."""
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
            normalized = normalize_name(name)
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


def resolve_fixture_source_map(identity_rows, fixtures):
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
    player_index = verified_event_player_index()
    team_index = verified_team_index()

    fixtures = {
        (row["season"], str(row["fixture_id"])): row
        for row in query_lab.load_csv(query_lab.FIXTURE_FILE)[0]
    }

    fixture_source_map = resolve_fixture_source_map(identity_rows, fixtures)

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

        scorer_team_code = team_index.get((season, normalize_name(scorer_team)))
        if not scorer_team_code:
            raise RuntimeError(
                f"No verified FRL team identity for event scorer team "
                f"{season}/{scorer_team!r}"
            )

        identity_matches = player_index.get(
            (season, normalize_name(scorer_name), scorer_team_code)
        )

        if not identity_matches:
            unresolved_players.append(
                (season, source_match_id, pulse_player_id, scorer_name, scorer_team)
            )
            continue

        archive_player_id, element, player_name = identity_matches

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
            f"could not be bridged through the authoritative FRL player identity audit. "
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
