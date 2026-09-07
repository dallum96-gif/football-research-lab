"""Common access layer for the FRL's broad Premier League source families.

This module does not replace the existing verified identity bridges or curated
query adapters. It exposes source-native records through one reusable seam so
new variables can be consumed without creating a new bespoke extractor.

Source identity is kept distinct from FRL identity throughout.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from match_stats import (
    PL_ROOT,
    canonical_to_utc,
    fixture_source_match,
    source_to_utc,
    verified_fixture_correction,
)
from query_lab import load_identity_registry
from pulselive_fixture_evidence import (
    load_player_stats_packages,
    load_snapshot,
    resource_payload,
)
from player_match_stats import (
    fixture_player_match_rows,
    source_player_id,
    classify_participation,
)
from player_identity_registry import build_registry as build_player_identity_registry
from relationship_enforcement import (
    evaluate_identity,
    require_verified,
    classify_observation,
    decision_dict,
)

ROOT = Path(__file__).resolve().parent
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
FPL_PLAYER_IDENTITY_FILE = ROOT / "data" / "fpl_player_identity_relationships.csv"


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                return list(reader), reader.fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def _number(value: object):
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


@lru_cache(maxsize=1)
def _identity_rows() -> tuple[dict, ...]:
    return tuple(load_identity_registry())


@lru_cache(maxsize=1)
def _player_identity_rows() -> tuple[dict[str, str], ...]:
    return tuple(build_player_identity_registry())


@lru_cache(maxsize=1)
def _fixture_rows() -> tuple[dict[str, str], ...]:
    rows, _ = _read_csv(FIXTURE_FILE)
    return tuple(rows)


def canonical_fixture(season: str, fixture_id: str) -> dict[str, str] | None:
    for row in _fixture_rows():
        if row.get("season") == season and str(row.get("fixture_id", "")).strip() == str(fixture_id).strip():
            return dict(row)
    return None


def season_fixtures(season: str) -> tuple[dict[str, str], ...]:
    return tuple(row for row in _fixture_rows() if row.get("season") == season)


def resolve_source_match(season: str, fixture_id: str) -> dict:
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    resolved = fixture_source_match(fixture, _identity_rows())
    if resolved is None:
        raise ValueError(f"No verified source match for {season}/{fixture_id}")

    match_id, home_row, away_row = resolved
    correction = verified_fixture_correction(fixture)
    correction_applied = False
    if correction is not None:
        try:
            source_kickoff = source_to_utc(home_row["kickoff"])
            actual_kickoff = canonical_to_utc(correction["actual_kickoff"])
            canonical_kickoff = canonical_to_utc(fixture["kickoff_time"])
            correction_applied = source_kickoff == actual_kickoff and source_kickoff != canonical_kickoff
        except (KeyError, TypeError, ValueError):
            correction_applied = False
    decision = evaluate_identity(
        "canonical_fixture_to_source_match",
        source_context_available=True,
        candidates=({"source_match_id": str(match_id)},),
    )
    require_verified(decision)

    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": str(match_id),
        "home": dict(home_row),
        "away": dict(away_row),
        "relationship_contract": decision.contract,
        "relationship_status": decision.status,
        "resolution_basis": "VERIFIED_FIXTURE_CORRECTION" if correction_applied else "CANONICAL_FIXTURE",
        "fixture_correction": dict(correction) if correction_applied else None,
    }


def fixture_metadata(season: str, fixture_id: str) -> dict:
    """Return source-native fixture metadata without changing canonical identity."""
    resolved = resolve_source_match(season, fixture_id)
    home = resolved["home"]
    away = resolved["away"]

    metadata = {
        "source_match_id": resolved["source_match_id"],
        "ground": home.get("ground") or away.get("ground"),
        "attendance": _number(home.get("attendance") or away.get("attendance")),
        "half_time_home_score": _number(home.get("halfTimeFor")),
        "half_time_away_score": _number(away.get("halfTimeFor")),
        "home_source_result": home.get("result"),
        "away_source_result": away.get("result"),
        "source_kickoff": home.get("kickoff") or away.get("kickoff"),
        "source_resolution_basis": resolved.get("resolution_basis"),
        "fixture_correction": resolved.get("fixture_correction"),
    }
    metadata["metadata_consistent"] = (
        home.get("ground") in (None, "", away.get("ground"))
        and home.get("attendance") in (None, "", away.get("attendance"))
    )
    return metadata


def _verified_source_team_id(season: str, local_team_id: str) -> str:
    """Resolve one season-local FRL team id to its verified persistent source club id."""
    candidates = {
        str(row.get("club_id") or row.get("persistent_team_code") or "").strip()
        for row in _identity_rows()
        if row.get("season") == season
        and str(row.get("local_team_id", "")).strip() == str(local_team_id).strip()
        and str(row.get("mapping_status", "")).upper() == "VERIFIED"
        and str(row.get("club_id") or row.get("persistent_team_code") or "").strip()
    }
    if len(candidates) != 1:
        raise ValueError(
            f"Expected one verified source team identity for {season}/local_team_id={local_team_id}; "
            f"found {sorted(candidates)}"
        )
    return next(iter(candidates))


def _pulselive_team_match_source_rows(season: str, fixture_id: str) -> tuple[dict, dict]:
    """Adapt preserved PulseLive stats rows to the established team-match source-row contract."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    source_match_id = str(fixture.get("fixture_code") or "").strip()
    if not source_match_id or not source_match_id.isdigit():
        raise ValueError(f"Canonical fixture has no verified numeric fixture_code: {season}/{fixture_id}")

    snapshot, snapshot_file = load_snapshot(source_match_id)
    if snapshot is None or snapshot_file is None:
        raise ValueError(f"No preserved PulseLive snapshot for {season}/{fixture_id} ({source_match_id})")

    match_payload = resource_payload(snapshot, "match")
    if not isinstance(match_payload, dict):
        raise ValueError(f"PulseLive match payload is unavailable for {season}/{fixture_id}")

    payload_match_id = str(match_payload.get("matchId") or "").strip()
    if payload_match_id != source_match_id:
        raise ValueError(
            f"PulseLive matchId mismatch for {season}/{fixture_id}: "
            f"expected {source_match_id}, got {payload_match_id or '<blank>'}"
        )

    stats_payload = resource_payload(snapshot, "stats")
    if not isinstance(stats_payload, list):
        raise ValueError(f"PulseLive stats payload is not a list for {season}/{fixture_id}")

    by_side: dict[str, dict] = {}
    for item in stats_payload:
        if not isinstance(item, dict):
            continue
        side = str(item.get("side") or "").strip().lower()
        if side in {"home", "away"}:
            if side in by_side:
                raise ValueError(f"Duplicate PulseLive {side} stats row for {season}/{fixture_id}")
            by_side[side] = item

    if set(by_side) != {"home", "away"}:
        raise ValueError(
            f"PulseLive stats must contain exactly Home and Away rows for {season}/{fixture_id}; "
            f"found {sorted(by_side)}"
        )

    expected_ids = {
        "home": _verified_source_team_id(season, fixture.get("home_team_id", "")),
        "away": _verified_source_team_id(season, fixture.get("away_team_id", "")),
    }

    adapted: dict[str, dict] = {}
    for side in ("home", "away"):
        item = by_side[side]
        source_team_id = str(item.get("teamId") or "").strip()

        if source_team_id != expected_ids[side]:
            raise ValueError(
                f"PulseLive {side} team identity mismatch for {season}/{fixture_id}: "
                f"expected source team {expected_ids[side]}, got {source_team_id or '<blank>'}"
            )

        stats = item.get("stats")
        if not isinstance(stats, dict):
            raise ValueError(f"PulseLive {side} stats object is unavailable for {season}/{fixture_id}")

        row = dict(stats)
        row["matchId"] = source_match_id
        row["team_id"] = source_team_id
        row["source_team_id"] = source_team_id
        row["side"] = item.get("side")
        row["venue"] = side
        adapted[side] = row

    return adapted["home"], adapted["away"]


def team_match_source_rows(season: str, fixture_id: str) -> tuple[dict, dict]:
    """Return complete native team-match rows for both fixture sides."""
    if season == "2026-27":
        return _pulselive_team_match_source_rows(season, fixture_id)

    resolved = resolve_source_match(season, fixture_id)
    return resolved["home"], resolved["away"]


def team_match_source_rows_for_season(season: str) -> tuple[dict, ...]:
    """Return source team-match rows reconciled to canonical fixtures."""
    rows: list[dict] = []
    for fixture in season_fixtures(season):
        try:
            home, away = team_match_source_rows(season, fixture["fixture_id"])
        except ValueError:
            continue
        for venue, source_row in (("home", home), ("away", away)):
            item = dict(source_row)
            item["frl_season"] = season
            item["frl_fixture_id"] = str(fixture["fixture_id"])
            item["frl_venue"] = venue
            item["frl_home_team_id"] = fixture.get("home_team_id", "")
            item["frl_away_team_id"] = fixture.get("away_team_id", "")
            rows.append(item)
    return tuple(rows)


@lru_cache(maxsize=16)
def team_match_source_fields(season: str) -> tuple[str, ...]:
    fields: set[str] = set()

    if season == "2026-27":
        for fixture in season_fixtures(season):
            source_match_id = str(fixture.get("fixture_code") or "").strip()
            if not source_match_id:
                continue

            snapshot, _ = load_snapshot(source_match_id)
            if snapshot is None:
                continue

            stats_payload = resource_payload(snapshot, "stats")
            if not isinstance(stats_payload, list):
                continue

            for item in stats_payload:
                if not isinstance(item, dict):
                    continue
                stats = item.get("stats")
                if isinstance(stats, dict):
                    fields.update(str(field) for field in stats.keys())

        return tuple(sorted(fields))

    root = Path(PL_ROOT)
    expected = f"{season}_events_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")

    for club_dir in sorted(root.iterdir()):
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "events_stats" / expected
        if not path.is_file():
            continue
        _, columns = _read_csv(path)
        fields.update(columns)
    return tuple(sorted(fields))



_PULSELIVE_PLAYER_MATCH_COMPATIBILITY_ALIASES = {
    # Governed current PulseLive -> historical FRL compatibility.
    # Native current fields remain preserved.
    #
    # FRL shots means TOTAL SHOT ATTEMPTS.
    # Blocked attempts are a subset of those attempts.
    "totalShots": "totalScoringAtt",
    "onTargetScoringAttempt": "ontargetScoringAtt",
    "blockedScoringAttempt": "blockedScoringAtt",

    # Same-player reconciliation:
    # 375/377 exact against successfulPassesOppositionHalf.
    "accurateOppositionHalfPasses": "accurateFwdZonePass",

    "possessionLostCtrl": "possLostCtrl",
    "errorLeadToAShot": "errorLeadToShot",
    "errorLeadToAGoal": "errorLeadToGoal",
    "savedShotsFromInsideTheBox": "savedIbox",
    "goodHighClaim": "totalHighClaim",
}


def _pulselive_player_match_source_rows(
    season: str,
    fixture_id: str,
) -> tuple[dict, ...]:
    """Return preserved 2026/27 fixture-native PulseLive player rows.

    This function never performs network acquisition. It reads only companion
    raw evidence already materialised beside the five-resource snapshot.
    """
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(
            f"Canonical fixture not found: {season}/{fixture_id}"
        )

    source_match_id = str(fixture.get("fixture_code") or "").strip()
    if not source_match_id:
        raise ValueError(
            f"Canonical fixture has no source match id: "
            f"{season}/{fixture_id}"
        )

    snapshot, _ = load_snapshot(source_match_id)
    if snapshot is None:
        raise ValueError(
            f"No PulseLive snapshot for {season}/{fixture_id}."
        )

    lineups = resource_payload(snapshot, "lineups")
    match_payload = resource_payload(snapshot, "match")

    player_context: dict[str, dict] = {}

    if isinstance(lineups, dict):
        for side_key, venue in (
            ("home_team", "home"),
            ("away_team", "away"),
        ):
            side = lineups.get(side_key)
            if not isinstance(side, dict):
                continue

            for player in side.get("players", []):
                if not isinstance(player, dict):
                    continue

                pid = str(player.get("id") or "").strip()
                if not pid:
                    continue

                listed_position = str(
                    player.get("position") or ""
                ).strip()

                actual_position = (
                    str(player.get("subPosition") or "").strip()
                    if listed_position == "Substitute"
                    else listed_position
                )

                name = str(
                    player.get("knownName")
                    or " ".join(
                        part
                        for part in (
                            str(player.get("firstName") or "").strip(),
                            str(player.get("lastName") or "").strip(),
                        )
                        if part
                    )
                    or ""
                ).strip()

                player_context[pid] = {
                    "playerName": name,
                    "position": actual_position,
                    "substitute": (
                        "1" if listed_position == "Substitute" else "0"
                    ),
                    "venue": venue,
                }

    teams = {}

    if isinstance(match_payload, dict):
        for venue, key in (
            ("home", "homeTeam"),
            ("away", "awayTeam"),
        ):
            team = match_payload.get(key)
            if isinstance(team, dict):
                teams[venue] = {
                    "team": str(team.get("name") or "").strip(),
                    "team_id": str(team.get("id") or "").strip(),
                }

    rows: list[dict] = []

    for package, path in load_player_stats_packages(source_match_id):
        pid = str(package.get("source_player_id") or "").strip()

        resource = package.get("resource")
        payload = (
            resource.get("payload")
            if isinstance(resource, dict)
            else None
        )

        if not isinstance(payload, dict):
            continue

        stats = payload.get("stats")
        if not isinstance(stats, dict):
            continue

        row = dict(stats)

        # Preserve provider-native identity plus the compatibility identity
        # expected by the established Player-Match seam.
        row["matchId"] = source_match_id
        row["playerId"] = pid
        row["pl_code"] = pid
        row["season"] = season
        row["gameweek"] = str(
            fixture.get("gameweek")
            or fixture.get("event")
            or ""
        )

        context = player_context.get(pid, {})
        row.update(context)

        venue = str(context.get("venue") or "")
        row.update(teams.get(venue, {}))

        # The historical rich source calls this minutesPlayed.
        if (
            "minutesPlayed" not in row
            and row.get("minsPlayed") not in (None, "")
        ):
            row["minutesPlayed"] = row.get("minsPlayed")

        # Add only aliases already proven semantically equivalent.
        # Never erase or rename the native current field.
        for historical_name, current_name in (
            _PULSELIVE_PLAYER_MATCH_COMPATIBILITY_ALIASES.items()
        ):
            if (
                historical_name not in row
                and row.get(current_name) not in (None, "")
            ):
                row[historical_name] = row[current_name]

        # Governed key-pass compatibility.
        #
        # Same-player fixture -> season reconciliation strongly favours:
        #
        #   keyPass = totalAttAssist - goalAssist
        #
        # Derive only when totalAttAssist was actually emitted.
        # No general missing-value zero-fill is performed here.
        if (
            row.get("keyPass") in (None, "")
            and row.get("totalAttAssist") not in (None, "")
        ):
            try:
                attempted_assists = float(row["totalAttAssist"])
                goal_assists = float(row.get("goalAssist") or 0.0)
            except (TypeError, ValueError):
                pass
            else:
                row["keyPass"] = max(
                    0.0,
                    attempted_assists - goal_assists,
                )

        row["_pulselive_player_stats_path"] = str(path)
        row["_pulselive_player_stats_endpoint"] = str(
            resource.get("endpoint") or ""
        ) if isinstance(resource, dict) else ""
        row["_pulselive_player_stats_retrieved_at"] = str(
            resource.get("retrieved_at") or ""
        ) if isinstance(resource, dict) else ""

        rows.append(row)

    return tuple(rows)


def player_match_source_rows(season: str, fixture_id: str) -> tuple[dict, ...]:
    """Return complete native player-match rows for one canonical fixture."""
    if season == "2026-27":
        return _pulselive_player_match_source_rows(season, fixture_id)

    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    return tuple(fixture_player_match_rows(fixture))


@lru_cache(maxsize=4096)
def _fixture_pulselive_player_candidates(
    season: str,
    fixture_id: str,
) -> tuple[bool, dict[str, tuple[dict[str, object], ...]]]:
    """Index exact PulseLive ``playerId`` candidates through PM ``pl_code``.

    The Player-Match fixture relationship is already governed by
    ``player_match_source_rows``.  This index adds no name or numeric-namespace
    inference: it uses only exact, non-empty ``pl_code`` evidence and retains
    the established ``source_player_id()`` result as the target identity.
    """
    rows = player_match_source_rows(season, fixture_id)
    candidates: dict[str, dict[str, set[str]]] = {}

    for row in rows:
        pl_code = str(row.get("pl_code") or "").strip()
        player_match_id = source_player_id(row)
        if not pl_code or not player_match_id:
            continue

        player_id = str(row.get("playerId") or "").strip()
        namespace = (
            "players_match_stats.playerId"
            if player_id and player_id == player_match_id
            else "players_match_stats.pl_code"
        )
        candidates.setdefault(pl_code, {}).setdefault(player_match_id, set()).add(namespace)

    frozen: dict[str, tuple[dict[str, object], ...]] = {}
    for pl_code, identities in candidates.items():
        frozen[pl_code] = tuple(
            {
                "player_match_source_player_id": player_match_id,
                "player_match_source_player_id_namespace": (
                    next(iter(namespaces))
                    if len(namespaces) == 1
                    else "player_match_stats.source_player_id()"
                ),
                "source_fields": tuple(sorted(namespaces)),
            }
            for player_match_id, namespaces in sorted(identities.items())
        )
    return bool(rows), frozen


def resolve_pulselive_player_identity(
    season: str,
    fixture_id: str,
    pulselive_player_id: str | int | None,
) -> dict[str, object]:
    """Resolve one PulseLive player ID to the fixture's Player-Match identity.

    Route: PulseLive ``playerId`` -> exact Player-Match ``pl_code`` -> the
    existing ``source_player_id()`` result.  Missing and ambiguous evidence is
    returned without a promoted target identity.
    """
    source_id = str(pulselive_player_id or "").strip()
    source_context_available, by_pl_code = _fixture_pulselive_player_candidates(
        season,
        str(fixture_id),
    )
    candidates = by_pl_code.get(source_id, ()) if source_id else ()
    decision = evaluate_identity(
        "source_player_match_to_source_player_identity",
        source_context_available=source_context_available and bool(source_id),
        candidates=candidates,
    )
    result: dict[str, object] = {
        "season": season,
        "fixture_id": str(fixture_id),
        "pulselive_source_player_id": source_id or None,
        "pulselive_source_player_id_namespace": "pulselive_match.playerId",
        "identity_route": "PULSELIVE_PLAYER_ID_TO_PLAYER_MATCH_PL_CODE_TO_SOURCE_PLAYER_ID",
        "bridge_source_field": "players_match_stats.pl_code",
        "evidence_basis": (
            "Exact non-empty PulseLive playerId equality with Player-Match pl_code "
            "inside the verified canonical fixture relationship."
        ),
        "candidate_source_player_ids": [
            str(candidate["player_match_source_player_id"])
            for candidate in candidates
        ],
        "player_match_source_player_id": None,
        "player_match_source_player_id_namespace": None,
        **decision_dict(decision),
    }
    if decision.verified:
        result.update(candidates[0])
    return result


def player_match_source_rows_for_season(season: str) -> tuple[dict, ...]:
    """Return complete player-match records with canonical fixture context."""
    records: list[dict] = []
    for fixture in season_fixtures(season):
        try:
            rows = player_match_source_rows(season, fixture["fixture_id"])
        except ValueError:
            continue
        for row in rows:
            item = dict(row)
            item["frl_season"] = season
            item["frl_fixture_id"] = str(fixture["fixture_id"])
            item["frl_home_team_id"] = fixture.get("home_team_id", "")
            item["frl_away_team_id"] = fixture.get("away_team_id", "")
            records.append(item)
    return tuple(records)


@lru_cache(maxsize=16)
def player_match_source_fields(season: str) -> tuple[str, ...]:
    fields: set[str] = set()

    if season == "2026-27":
        for fixture in season_fixtures(season):
            try:
                rows = player_match_source_rows(
                    season,
                    fixture["fixture_id"],
                )
            except ValueError:
                continue

            for row in rows:
                fields.update(
                    key
                    for key in row
                    if not key.startswith("_")
                )

        return tuple(sorted(fields))

    root = Path(PL_ROOT)
    expected = f"{season}_players_match_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")

    for club_dir in sorted(root.iterdir()):
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "players_match_stats" / expected
        if not path.is_file():
            continue
        _, columns = _read_csv(path)
        fields.update(columns)
    return tuple(sorted(fields))


def player_match_records(season: str, fixture_id: str) -> tuple[dict, ...]:
    """Return player-match observations with verified fixture context.

    Player identity is not inferred from the observation itself. Consumers must
    resolve an FRL player identity separately before treating the observation as
    belonging to that identity.
    """
    resolved_fixture = resolve_source_match(season, fixture_id)
    rows = []
    for row in player_match_source_rows(season, fixture_id):
        item = dict(row)
        item["frl_source_player_id"] = source_player_id(row) or ""
        item["frl_participation_status"] = classify_participation(row)
        item["relationship_contract"] = "canonical_fixture_to_source_match"
        item["relationship_status"] = resolved_fixture["relationship_status"]
        rows.append(item)
    return tuple(rows)


@lru_cache(maxsize=16)
def player_season_source_rows(season: str) -> tuple[dict, ...]:
    """Return complete native players_stats rows for one season."""
    records: list[dict] = []
    root = Path(PL_ROOT)
    expected = f"{season}_players_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source root not found: {root}")

    for club_dir in sorted(root.iterdir()):
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "players_stats" / expected
        if not path.is_file():
            continue
        rows, _ = _read_csv(path)
        for row in rows:
            item = dict(row)
            item["_source_file"] = str(path)
            records.append(item)
    return tuple(records)


@lru_cache(maxsize=16)
def player_season_source_fields(season: str) -> tuple[str, ...]:
    rows = player_season_source_rows(season)
    fields: set[str] = set()
    for row in rows:
        fields.update(k for k in row if k != "_source_file")
    return tuple(sorted(fields))


def source_field_inventory(season: str) -> dict[str, tuple[str, ...]]:
    return {
        "fixture_team_match": team_match_source_fields(season),
        "player_match": player_match_source_fields(season),
        "player_season": player_season_source_fields(season),
    }


def resolve_fpl_player_identity(season: str, fpl_element: str) -> dict:
    """Return the verified FPL->FRL player identity decision for one season."""
    current_rows, _ = _read_csv(FPL_PLAYER_IDENTITY_FILE) if FPL_PLAYER_IDENTITY_FILE.is_file() else ([], [])
    current_matches = [
        row for row in current_rows
        if row.get("season") == season
        and str(row.get("fpl_element", "")).strip() == str(fpl_element).strip()
    ]
    if len(current_matches) == 1:
        row = dict(current_matches[0])
        status = str(row.get("identity_status") or "UNRESOLVED")
        usable = status in {"VERIFIED", "SOURCE_NATIVE_VERIFIED"}
        return {
            **row,
            "frl_player_source_id": row.get("player_match_source_player_id") or row.get("player_identity_key", ""),
            "relationship_contract": "fpl_player_to_frl_player_identity",
            "relationship_status": status,
            "candidate_count": int(row.get("candidate_count") or 0),
            "source_context_available": True,
            "contradiction": False,
            "verified": usable,
            "reason": row.get("evidence_basis", ""),
        }
    if len(current_matches) > 1:
        return {
            "season": season,
            "fpl_element": str(fpl_element),
            "relationship_contract": "fpl_player_to_frl_player_identity",
            "relationship_status": "AMBIGUOUS",
            "identity_status": "AMBIGUOUS",
            "candidate_count": len(current_matches),
            "source_context_available": True,
            "contradiction": False,
            "verified": False,
            "reason": "Multiple governed current-season FPL identity records exist.",
        }

    matches = [
        row for row in _player_identity_rows()
        if row.get("season") == season
        and str(row.get("fpl_element", "")).strip() == str(fpl_element).strip()
    ]
    decision = evaluate_identity(
        "fpl_player_to_frl_player_identity",
        source_context_available=bool(matches) or bool(_player_identity_rows()),
        candidates=matches,
    )
    if not decision.verified:
        return {
            "season": season,
            "fpl_element": str(fpl_element),
            **decision_dict(decision),
        }
    row = dict(matches[0])
    row.update(decision_dict(decision))
    row["frl_player_source_id"] = row.get("source_player_id", "")
    return row


def source_player_season_identity(season: str, source_player_id_value: str) -> dict:
    """Resolve a source player ID to exactly one player-season row."""
    candidates = [
        row for row in player_season_source_rows(season)
        if str(row.get("playerId", "")).strip() == str(source_player_id_value).strip()
    ]
    decision = evaluate_identity(
        "source_player_identity_to_player_season",
        source_context_available=True,
        candidates=candidates,
    )
    result = {
        "season": season,
        "source_player_id": str(source_player_id_value),
        **decision_dict(decision),
    }
    if decision.verified:
        result["player_season"] = dict(candidates[0])
    return result


def player_match_observation_status(
    season: str,
    fixture_id: str,
    source_player_id_value: str,
    *,
    player_identity_verified: bool = True,
) -> dict:
    """Classify a player-match observation without treating absence as identity failure."""
    resolve_source_match(season, fixture_id)
    rows = [
        row for row in player_match_source_rows(season, fixture_id)
        if str(source_player_id(row) or "").strip() == str(source_player_id_value).strip()
    ]
    status = classify_observation(
        identity_verified=player_identity_verified,
        fixture_verified=True,
        observation_present=bool(rows),
    )
    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_player_id": str(source_player_id_value),
        "relationship_contract": "player_identity_to_player_match_observations",
        "relationship_status": status,
        "observation_present": bool(rows),
    }


