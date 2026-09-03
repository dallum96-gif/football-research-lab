"""Materialise one pinned, living FPL season through governed FRL seams.

The input must be an already-preserved or isolated checkout of the approved
Premier-League-Stats distribution.  This command never contacts a football
API.  It preserves the source release before constructing canonical fixture,
team-identity, FPL player-fixture and release-capability artefacts.

The materialisation is deliberately replace-by-season and deterministic:
historical rows remain byte-for-byte equivalent after CSV serialisation, while
the selected living season is regenerated from its pinned release.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UPSTREAM_URL = "https://github.com/imadeddine-belkat/Premier-League-Stats.git"
RIGHTS_CLASSIFICATION = "REVIEW_REQUIRED"

CANONICAL_FIELDS = (
    "season",
    "fixture_id",
    "fixture_code",
    "kickoff_time",
    "gameweek",
    "home_team_id",
    "away_team_id",
    "home_score",
    "away_score",
)
TEAM_FIELDS = (
    "team_season_id",
    "season",
    "club_id",
    "canonical_name",
    "persistent_team_code",
    "local_team_id",
    "source_name",
    "mapping_status",
    "mapping_source",
)
TEAM_PROVENANCE_FIELDS = ("season", "method", "source", "notes")
IDENTITY_FIELDS = (
    "season",
    "fpl_element",
    "fpl_player_code",
    "fpl_team_code",
    "player_identity_key",
    "player_match_source_player_id",
    "identity_status",
    "identity_route",
    "candidate_count",
    "evidence_seasons",
    "evidence_basis",
    "source_release_sha",
    "source_path",
    "source_sha256",
)


class MaterialisationError(ValueError):
    """Raised when pinned evidence cannot be materialised safely."""


def _read_csv_bytes(payload: bytes, *, label: str) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = payload.decode(encoding)
        except UnicodeDecodeError:
            continue
        reader = csv.DictReader(io.StringIO(text, newline=""))
        rows = list(reader)
        return rows, tuple(reader.fieldnames or ())
    raise MaterialisationError(f"Could not decode CSV: {label}")


def _read_csv(path: Path) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    return _read_csv_bytes(path.read_bytes(), label=str(path))


def _git_bytes(worktree: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(worktree), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        raise MaterialisationError(
            f"Pinned Git evidence lookup failed in {worktree}: {detail or exc}"
        ) from exc
    return result.stdout


def _git_repo_root(path: Path) -> Path:
    output = _git_bytes(path, "rev-parse", "--show-toplevel").decode("utf-8", errors="strict").strip()
    if not output:
        raise MaterialisationError(f"Could not resolve Git repository root from {path}")
    return Path(output).resolve()


def _git_relative_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise MaterialisationError(f"Source path {path} is outside Git repository {repo_root}") from exc


def _git_blob_bytes(repo_root: Path, commit: str, relative_path: str) -> bytes:
    return _git_bytes(repo_root, "show", f"{commit}:{relative_path}")


def _pinned_file_bytes(path: Path, *, repo_root: Path, source_commit: str) -> tuple[bytes, str]:
    """Read one source artefact from the immutable Git object, never the worktree."""
    relative_path = _git_relative_path(repo_root, path)
    return _git_blob_bytes(repo_root, source_commit, relative_path), relative_path


def _pinned_csv(
    path: Path,
    *,
    repo_root: Path,
    source_commit: str,
) -> tuple[list[dict[str, str]], tuple[str, ...], bytes]:
    payload, relative_path = _pinned_file_bytes(
        path, repo_root=repo_root, source_commit=source_commit
    )
    rows, fields = _read_csv_bytes(
        payload, label=f"{source_commit}:{relative_path}"
    )
    return rows, fields, payload


def _verify_pinned_paths(
    paths: dict[str, Path],
    *,
    repo_root: Path,
    source_commit: str,
) -> None:
    for path in paths.values():
        _pinned_file_bytes(path, repo_root=repo_root, source_commit=source_commit)


def _csv_bytes(rows: Iterable[dict[str, object]], fields: Iterable[str], *, bom: bool = False) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=tuple(fields),
        extrasaction="ignore",
        lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    encoding = "utf-8-sig" if bom else "utf-8"
    return buffer.getvalue().encode(encoding)


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_or_check(path: Path, payload: bytes, *, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_bytes() != payload:
            raise MaterialisationError(f"Generated artefact is stale: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _normalise_score(value: str, *, completed: bool) -> str:
    text = str(value or "").strip()
    if not completed:
        return ""
    if not text:
        raise MaterialisationError("Completed fixture has a missing score.")
    try:
        number = float(text)
    except ValueError as exc:
        raise MaterialisationError(f"Invalid completed score: {value!r}") from exc
    if not number.is_integer() or number < 0:
        raise MaterialisationError(f"Invalid completed score: {value!r}")
    return str(int(number))


def fixture_state(row: dict[str, str]) -> str:
    finished = str(row.get("finished", "")).strip().casefold() == "true"
    started = str(row.get("started", "")).strip().casefold() == "true"
    home_score = str(row.get("team_h_score", "")).strip()
    away_score = str(row.get("team_a_score", "")).strip()
    if finished and home_score and away_score:
        return "COMPLETED"
    if not started and not home_score and not away_score:
        return "SCHEDULED"
    if started and not finished:
        return "IN_PROGRESS"
    return "UNRESOLVED"


def _canonical_name(source_name: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", source_name)).strip("_")


def _season_source_paths(source_root: Path, season: str) -> dict[str, Path]:
    return {
        "fixtures": source_root / "fixtures" / f"{season}_all_fixtures.csv",
        "players": source_root / "_merged" / "players" / f"{season}_all_players_gw.csv",
        "players_index": source_root / "_index" / "_players_index.json",
        "teams_index": source_root / "_index" / "_teams_index.json",
    }


def _source_metadata(
    paths: dict[str, Path],
    source_root: Path,
    *,
    repo_root: Path,
    source_commit: str,
) -> dict[str, dict[str, object]]:
    metadata: dict[str, dict[str, object]] = {}
    for key, path in paths.items():
        payload, relative_path = _pinned_file_bytes(
            path, repo_root=repo_root, source_commit=source_commit
        )
        digest = hashlib.sha256(payload).hexdigest()
        metadata[key] = {
            "path": path.relative_to(source_root).as_posix(),
            "sha256": digest,
            "bytes": len(payload),
            "git_path": relative_path,
            "git_object_sha256": digest,
            "read_mode": "PINNED_GIT_OBJECT",
        }
    return metadata


def _team_entries_bytes(payload: bytes, season: str, *, label: str) -> dict[str, dict[str, str]]:
    try:
        index = json.loads(payload.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MaterialisationError(f"Could not decode teams index: {label}") from exc
    entries: dict[str, dict[str, str]] = {}
    for persistent_code, seasons in index.items():
        if not isinstance(seasons, dict) or season not in seasons:
            continue
        item = seasons[season]
        local_id = str(item.get("id", "")).strip()
        if not local_id or local_id in entries:
            raise MaterialisationError(f"Invalid or duplicate {season} FPL team ID: {local_id!r}")
        entries[local_id] = {
            "persistent_team_code": str(persistent_code),
            "local_team_id": local_id,
            "source_name": str(item.get("name", "")).strip(),
            "short_name": str(item.get("short_name", "")).strip(),
        }
    if len(entries) != 20:
        raise MaterialisationError(f"Expected 20 {season} teams; found {len(entries)}")
    return entries


def build_canonical_fixtures(
    source_rows: list[dict[str, str]],
    *,
    season: str,
    teams_by_local_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    seen_ids: set[str] = set()
    seen_codes: set[str] = set()
    rows: list[dict[str, str]] = []
    for source in source_rows:
        fixture_id = str(source.get("id", "")).strip()
        fixture_code = str(source.get("code", "")).strip()
        home_id = str(source.get("team_h", "")).strip()
        away_id = str(source.get("team_a", "")).strip()
        if not fixture_id or fixture_id in seen_ids:
            raise MaterialisationError(f"Missing or duplicate source fixture ID: {fixture_id!r}")
        if not fixture_code or fixture_code in seen_codes:
            raise MaterialisationError(f"Missing or duplicate source fixture code: {fixture_code!r}")
        if home_id == away_id or home_id not in teams_by_local_id or away_id not in teams_by_local_id:
            raise MaterialisationError(f"Unresolved team relationship for source fixture {fixture_id}")
        state = fixture_state(source)
        if state == "UNRESOLVED":
            raise MaterialisationError(f"Unresolved fixture state for source fixture {fixture_id}")
        completed = state == "COMPLETED"
        rows.append(
            {
                "season": season,
                "fixture_id": fixture_id,
                "fixture_code": fixture_code,
                "kickoff_time": str(source.get("kickoff_time", "")).strip(),
                "gameweek": str(source.get("event", "")).strip(),
                "home_team_id": home_id,
                "away_team_id": away_id,
                "home_score": _normalise_score(source.get("team_h_score", ""), completed=completed),
                "away_score": _normalise_score(source.get("team_a_score", ""), completed=completed),
            }
        )
        seen_ids.add(fixture_id)
        seen_codes.add(fixture_code)
    rows.sort(key=lambda item: int(item["fixture_id"]))
    return rows


def build_team_seasons(
    existing_rows: list[dict[str, str]],
    *,
    season: str,
    teams_by_local_id: dict[str, dict[str, str]],
    source_commit: str,
) -> list[dict[str, str]]:
    names_by_code: dict[str, set[str]] = defaultdict(set)
    for row in existing_rows:
        if row.get("season") == season:
            continue
        code = str(row.get("persistent_team_code", "")).strip()
        name = str(row.get("canonical_name", "")).strip()
        if code and name:
            names_by_code[code].add(name)

    result: list[dict[str, str]] = []
    for item in teams_by_local_id.values():
        code = item["persistent_team_code"]
        known_names = names_by_code.get(code, set())
        if len(known_names) > 1:
            raise MaterialisationError(f"Ambiguous canonical team name for persistent code {code}")
        canonical_name = next(iter(known_names), _canonical_name(item["source_name"]))
        if not canonical_name:
            raise MaterialisationError(f"Missing canonical team name for persistent code {code}")
        result.append(
            {
                "team_season_id": f"{season}:{code}",
                "season": season,
                "club_id": code,
                "canonical_name": canonical_name,
                "persistent_team_code": code,
                "local_team_id": item["local_team_id"],
                "source_name": item["source_name"],
                "mapping_status": "VERIFIED",
                "mapping_source": f"Pinned FPL teams index @ {source_commit}",
            }
        )
    return sorted(result, key=lambda row: int(row["local_team_id"]))


def _player_match_bridge(
    player_match_root: Path,
    *,
    source_commit: str,
    repo_root: Path | None = None,
) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, object]]:
    """Build the historical identity bridge from immutable Git objects only.

    The caller may point at a dirty working tree.  File discovery and CSV bytes
    are both read from ``source_commit`` so untracked or modified files cannot
    change the bridge.
    """
    repo_root = (repo_root or _git_repo_root(player_match_root)).resolve()
    prefix = _git_relative_path(repo_root, player_match_root).rstrip("/")
    listed = _git_bytes(
        repo_root,
        "ls-tree",
        "-r",
        "--name-only",
        source_commit,
        "--",
        prefix,
    ).decode("utf-8", errors="strict").splitlines()
    paths = [
        path
        for path in listed
        if "/players_match_stats/" in path
        and re.search(r"\d{4}-\d{2}_players_match_stats\.csv$", path)
    ]

    candidates: dict[str, set[str]] = defaultdict(set)
    seasons: dict[str, set[str]] = defaultdict(set)
    fingerprints: list[str] = []
    for relative_path in sorted(paths):
        match = re.search(r"(?P<season>\d{4}-\d{2})_players_match_stats\.csv$", relative_path)
        if not match:
            continue
        season = match.group("season")
        payload = _git_blob_bytes(repo_root, source_commit, relative_path)
        rows, _ = _read_csv_bytes(
            payload,
            label=f"{source_commit}:{relative_path}",
        )
        fingerprints.append(
            f"{relative_path}:{hashlib.sha256(payload).hexdigest()}"
        )
        for row in rows:
            code = str(row.get("pl_code", "")).strip()
            source_player_id = str(
                row.get("playerId") or row.get("pl_code") or ""
            ).strip()
            if code and source_player_id:
                candidates[code].add(source_player_id)
                seasons[code].add(season)

    digest = hashlib.sha256("\n".join(fingerprints).encode("utf-8")).hexdigest()
    return candidates, seasons, {
        "source_family": "players_match_stats",
        "source_release_sha": source_commit,
        "read_mode": "PINNED_GIT_OBJECTS",
        "canonical_file_count": len(paths),
        "evidence_set_sha256": digest,
        "mapping_rule": "exact non-empty FPL player_code == players_match_stats.pl_code",
        "ambiguous_pl_codes": sum(1 for values in candidates.values() if len(values) > 1),
    }


def build_player_identities(
    player_rows: list[dict[str, str]],
    *,
    season: str,
    bridge_candidates: dict[str, set[str]],
    bridge_seasons: dict[str, set[str]],
    registered_source_player_ids: set[str],
    source_commit: str,
    source_path: str,
    source_sha256: str,
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    seen_elements: dict[str, int] = {}
    for row in player_rows:
        element = str(row.get("element", "")).strip()
        player_code = str(row.get("player_code", "")).strip()
        team_code = str(row.get("team_code", "")).strip()
        if not element or not player_code:
            raise MaterialisationError(f"Missing FPL player identity: {element!r}")
        if element in seen_elements:
            existing = result[seen_elements[element]]
            if existing["fpl_player_code"] != player_code:
                raise MaterialisationError(
                    f"Inconsistent FPL player identity for element {element!r}: "
                    f"{existing['fpl_player_code']!r} != {player_code!r}"
                )
            if team_code:
                existing["fpl_team_code"] = team_code
            continue
        candidates = bridge_candidates.get(player_code, set())
        evidence_seasons = bridge_seasons.get(player_code, set())
        if len(candidates) > 1:
            status = "AMBIGUOUS"
            route = "REVIEW_REQUIRED_FPL_PLAYER_CODE_TO_PLAYER_MATCH_PL_CODE"
            identity_key = ""
            source_player_id = ""
            basis = "Exact player_code/pl_code evidence maps to multiple Player-Match identities; no identity promoted."
        elif len(candidates) == 1:
            source_player_id = next(iter(candidates))
            if source_player_id in registered_source_player_ids:
                status = "VERIFIED"
                route = "FPL_PLAYER_CODE_TO_PLAYER_MATCH_PL_CODE_TO_REGISTERED_SOURCE_PLAYER_ID"
            else:
                status = "SOURCE_NATIVE_VERIFIED"
                route = "FPL_PLAYER_CODE_TO_PLAYER_MATCH_PL_CODE_TO_SOURCE_NATIVE_PLAYER"
            identity_key = f"player_match:{source_player_id}"
            basis = "Exact FPL player_code equality with an unambiguous historical Player-Match pl_code relationship."
        else:
            status = "SOURCE_NATIVE_VERIFIED"
            route = "SOURCE_NATIVE_FPL_PLAYER_CODE"
            identity_key = f"fpl_player:{player_code}"
            source_player_id = ""
            basis = "Stable source-native FPL player_code preserved without a cross-source identity claim."
        result.append(
            {
                "season": season,
                "fpl_element": element,
                "fpl_player_code": player_code,
                "fpl_team_code": team_code,
                "player_identity_key": identity_key,
                "player_match_source_player_id": source_player_id,
                "identity_status": status,
                "identity_route": route,
                "candidate_count": str(len(candidates)),
                "evidence_seasons": "|".join(sorted(evidence_seasons)),
                "evidence_basis": basis,
                "source_release_sha": source_commit,
                "source_path": source_path,
                "source_sha256": source_sha256,
            }
        )
        seen_elements[element] = len(result) - 1
    return sorted(result, key=lambda row: int(row["fpl_element"]))


def _fixture_evidence_rows(
    source_rows: list[dict[str, str]],
    canonical_rows: list[dict[str, str]],
    *,
    season: str,
    source_commit: str,
    source_repository: str,
    source_path: str,
    source_sha256: str,
    retrieved_at: str,
) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    canonical_by_code = {row["fixture_code"]: row for row in canonical_rows}
    prefix = (
        "frl_season",
        "frl_fixture_id",
        "frl_fpl_fixture_key",
        "frl_fixture_relationship_status",
        "frl_fixture_state",
        "source_release_sha",
        "source_repository",
        "source_path",
        "source_sha256",
        "source_retrieved_at",
    )
    source_fields = tuple(source_rows[0]) if source_rows else ()
    output: list[dict[str, str]] = []
    for row in source_rows:
        canonical = canonical_by_code.get(str(row.get("code", "")).strip())
        if canonical is None:
            raise MaterialisationError(f"FPL fixture code is unresolved: {row.get('code')}")
        item = {
            "frl_season": season,
            "frl_fixture_id": canonical["fixture_id"],
            "frl_fpl_fixture_key": str(row.get("id", "")).strip(),
            "frl_fixture_relationship_status": "VERIFIED",
            "frl_fixture_state": fixture_state(row),
            "source_release_sha": source_commit,
            "source_repository": source_repository,
            "source_path": source_path,
            "source_sha256": source_sha256,
            "source_retrieved_at": retrieved_at,
        }
        item.update({f"source_{field}": row.get(field, "") for field in source_fields})
        output.append(item)
    return output, prefix + tuple(f"source_{field}" for field in source_fields)


def _player_evidence_rows(
    source_rows: list[dict[str, str]],
    canonical_rows: list[dict[str, str]],
    identity_rows: list[dict[str, str]],
    teams_by_local_id: dict[str, dict[str, str]],
    *,
    season: str,
    source_commit: str,
    source_repository: str,
    source_path: str,
    source_sha256: str,
    retrieved_at: str,
) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    fixture_by_code = {row["fixture_code"]: row for row in canonical_rows}
    identity_by_element = {row["fpl_element"]: row for row in identity_rows}
    persistent_by_local = {
        local_id: item["persistent_team_code"] for local_id, item in teams_by_local_id.items()
    }
    prefix = (
        "frl_season",
        "frl_fixture_id",
        "frl_fpl_fixture_key",
        "frl_fpl_player_key",
        "frl_fpl_gameweek",
        "frl_player_identity_key",
        "frl_player_identity_status",
        "frl_player_identity_route",
        "frl_team_id",
        "frl_opponent_team_id",
        "frl_was_home",
        "frl_fixture_relationship_status",
        "frl_team_relationship_status",
        "frl_observation_status",
        "frl_participation_status",
        "source_release_sha",
        "source_repository",
        "source_path",
        "source_sha256",
        "source_retrieved_at",
    )
    source_fields = tuple(source_rows[0]) if source_rows else ()
    output: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in source_rows:
        fixture_code = str(row.get("fixture_code", "")).strip()
        element = str(row.get("element", "")).strip()
        key = (element, fixture_code)
        if key in seen:
            raise MaterialisationError(f"Duplicate FPL player-fixture grain: {key}")
        fixture = fixture_by_code.get(fixture_code)
        identity = identity_by_element.get(element)
        if fixture is None or identity is None:
            raise MaterialisationError(f"Unresolved FPL player-fixture relationship: {key}")
        home_code = persistent_by_local[fixture["home_team_id"]]
        away_code = persistent_by_local[fixture["away_team_id"]]
        team_code = str(row.get("team_code", "")).strip()
        if team_code == home_code:
            was_home, opponent, team_status = "true", away_code, "VERIFIED"
        elif team_code == away_code:
            was_home, opponent, team_status = "false", home_code, "VERIFIED"
        else:
            was_home, opponent, team_status = "", "", "REVIEW_REQUIRED"
        minutes = str(row.get("minutes", "")).strip()
        if minutes == "":
            observation_status = "MISSING_OBSERVATION"
            participation_status = "UNKNOWN"
        elif float(minutes) == 0:
            observation_status = "OBSERVED"
            participation_status = "REGISTERED_ZERO_MINUTES"
        else:
            observation_status = "OBSERVED"
            participation_status = "STARTED" if str(row.get("starts", "")).strip() == "1" else "SUBSTITUTE_APPEARANCE"
        item = {
            "frl_season": season,
            "frl_fixture_id": fixture["fixture_id"],
            "frl_fpl_fixture_key": str(fixture["fixture_id"]),
            "frl_fpl_player_key": element,
            "frl_fpl_gameweek": fixture["gameweek"],
            "frl_player_identity_key": identity["player_identity_key"],
            "frl_player_identity_status": identity["identity_status"],
            "frl_player_identity_route": identity["identity_route"],
            "frl_team_id": team_code,
            "frl_opponent_team_id": opponent,
            "frl_was_home": was_home,
            "frl_fixture_relationship_status": "VERIFIED",
            "frl_team_relationship_status": team_status,
            "frl_observation_status": observation_status,
            "frl_participation_status": participation_status,
            "source_release_sha": source_commit,
            "source_repository": source_repository,
            "source_path": source_path,
            "source_sha256": source_sha256,
            "source_retrieved_at": retrieved_at,
        }
        item.update({f"source_{field}": row.get(field, "") for field in source_fields})
        output.append(item)
        seen.add(key)
    output.sort(key=lambda item: (int(item["frl_fixture_id"]), int(item["frl_fpl_player_key"])))
    return output, prefix + tuple(f"source_{field}" for field in source_fields)


def _schema_profile(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[str, dict[str, object]]:
    profile: dict[str, dict[str, object]] = {}
    for field in fields:
        values = [str(row.get(field, "")).strip() for row in rows]
        nonempty = [value for value in values if value]
        inferred = "EMPTY"
        if nonempty:
            try:
                [int(value) for value in nonempty]
                inferred = "INT"
            except ValueError:
                try:
                    [float(value) for value in nonempty]
                    inferred = "FLOAT"
                except ValueError:
                    inferred = "STRING"
        profile[field] = {
            "inferred_type": inferred,
            "blank_count": len(values) - len(nonempty),
            "distinct_nonblank": len(set(nonempty)),
        }
    return profile


def _capability_register(
    *,
    season: str,
    source_commit: str,
    retrieved_at: str,
    canonical_rows: list[dict[str, str]],
    player_rows: list[dict[str, str]],
    identity_rows: list[dict[str, str]],
) -> dict[str, object]:
    completed = sum(row["home_score"] != "" and row["away_score"] != "" for row in canonical_rows)
    scheduled = len(canonical_rows) - completed
    identity_counts = Counter(row["identity_status"] for row in identity_rows)
    identity_route_counts = Counter(row["identity_route"] for row in identity_rows)

    def capability(
        name: str,
        *,
        present: bool,
        connected: bool,
        identity: bool | None,
        derivable: bool,
        governed: bool,
        comparable: bool,
        product: bool,
        review: bool,
        unavailable: bool,
        grain: str,
        coverage: str,
        representation: str,
        note: str,
    ) -> dict[str, object]:
        return {
            "capability": name,
            "required_grain": grain,
            "source_representation": representation,
            "coverage": coverage,
            "states": {
                "SOURCE_PRESENT": present,
                "CONNECTED": connected,
                "IDENTITY_RESOLVED": identity,
                "DERIVABLE": derivable,
                "GOVERNED": governed,
                "COMPARABLE": comparable,
                "PRODUCT_READY": product,
                "REVIEW_REQUIRED": review,
                "UNAVAILABLE": unavailable,
            },
            "note": note,
        }

    fpl_note = "Source-native FPL player-fixture evidence is product-readable; equivalence with historical Opta-derived player-match variables is not asserted."
    capabilities = [
        capability("canonical_fixtures", present=True, connected=True, identity=True, derivable=False, governed=True, comparable=True, product=True, review=False, unavailable=False, grain="fixture", coverage=f"{len(canonical_rows)}/{len(canonical_rows)}", representation="canonical fixture + pinned FPL fixture source", note="Scheduled and completed fixtures remain distinct."),
        capability("results_scores", present=completed > 0, connected=True, identity=True, derivable=False, governed=True, comparable=True, product=True, review=False, unavailable=False, grain="fixture", coverage=f"{completed}/{len(canonical_rows)} completed", representation="canonical fixture result", note="Missing scheduled scores remain missing, never zero."),
        capability("scheduled_fixtures", present=scheduled > 0, connected=True, identity=True, derivable=False, governed=True, comparable=True, product=True, review=False, unavailable=False, grain="fixture", coverage=f"{scheduled}/{len(canonical_rows)} scheduled", representation="canonical fixture schedule", note="Living schedule remains mutable across releases."),
        capability("team_identity", present=True, connected=True, identity=True, derivable=False, governed=True, comparable=True, product=True, review=False, unavailable=False, grain="team-season", coverage="20/20 teams", representation="FPL teams index to persistent FRL team", note="Season-local team ID remains separate from persistent team code."),
        capability(
            "player_identity",
            present=True,
            connected=True,
            identity=identity_counts.get("VERIFIED", 0) == len(identity_rows),
            derivable=False,
            governed=True,
            comparable=False,
            product=True,
            review=identity_counts.get("VERIFIED", 0) != len(identity_rows),
            unavailable=False,
            grain="player-season",
            coverage=(
                f"{len(identity_rows)}/{len(identity_rows)} source identities; "
                f"{identity_counts.get('VERIFIED', 0)} cross-source verified; "
                f"{identity_route_counts.get('FPL_PLAYER_CODE_TO_PLAYER_MATCH_PL_CODE_TO_SOURCE_NATIVE_PLAYER', 0)} "
                "source-native linked; "
                f"{identity_route_counts.get('SOURCE_NATIVE_FPL_PLAYER_CODE', 0)} FPL-only source-native"
            ),
            representation="FPL element + player_code relationship",
            note=(
                "Every FPL identity remains source-usable, but canonical cross-source "
                "player identity is incomplete until every source identity is VERIFIED."
            ),
        ),
    ]
    for name, fields in (
        ("participation_minutes", ("minutes",)),
        ("starts", ("starts",)),
        ("goals", ("goals_scored",)),
        ("assists", ("assists",)),
        ("expected_goals", ("expected_goals",)),
        ("expected_assists", ("expected_assists",)),
        ("expected_goal_involvements", ("expected_goal_involvements",)),
        ("defensive_actions", ("defensive_contribution", "tackles", "recoveries", "clearances_blocks_interceptions")),
        ("goalkeeper_metrics", ("saves", "penalties_saved", "expected_goals_conceded")),
        ("discipline", ("yellow_cards", "red_cards")),
        ("fpl_bonus_bps", ("bonus", "bps")),
        ("fpl_ict", ("influence", "creativity", "threat", "ict_index")),
    ):
        available = all(field in player_rows[0] for field in fields) if player_rows else False
        capabilities.append(capability(name, present=available, connected=available, identity=True if available else None, derivable=False, governed=available, comparable=False, product=available, review=available, unavailable=not available, grain="FPL player × fixture", coverage=f"{len(player_rows)}/{len(player_rows)} source rows" if available else "0", representation="FPL player-fixture", note=fpl_note if available else "Field family is absent from the pinned FPL representation."))
    for name, grain, note in (
        ("shooting", "player-match/team-match", "No source-native shot-count fields exist in the pinned FPL player-fixture schema."),
        ("passing", "player-match/team-match", "Creativity is not silently relabelled as passing evidence."),
        ("chance_creation", "player-match/team-match", "FPL xA/creativity exist, but direct chance/key-pass equivalence is not established."),
        ("possession", "team-match", "No team-match possession representation extends into the pinned release."),
        ("duels", "player-match/team-match", "No governed duel representation extends into the pinned release."),
        ("team_match_statistics", "team-match", "Historical pl_stats events_stats does not extend into 2026/27."),
        ("opta_player_match_statistics", "player-match", "Historical Opta-derived players_match_stats does not extend into 2026/27; FPL remains separate."),
        ("detailed_events", "event", "No rich event feed is present in the pinned release."),
        ("lineups_formations", "fixture-lineup", "No lineup or formation source is present in the pinned release."),
        ("odds_markets", "fixture-market", "No odds/market source is present in the pinned release."),
    ):
        review = name == "chance_creation"
        capabilities.append(capability(name, present=False, connected=False, identity=None, derivable=False, governed=False, comparable=False, product=False, review=review, unavailable=True, grain=grain, coverage="0", representation="UNAVAILABLE", note=note))
    capabilities.append(capability("league_table_standings", present=True, connected=True, identity=True, derivable=True, governed=True, comparable=True, product=True, review=False, unavailable=False, grain="team-season as of release", coverage=f"{completed} completed fixtures", representation="derived from canonical completed results", note="A current table is partial-season state, not a completed-season comparison."))

    totals = Counter()
    for item in capabilities:
        for state, value in item["states"].items():
            if value is True:
                totals[state] += 1
    return {
        "schema_version": "FRL_2026_27_CAPABILITY_GAP_REGISTER_V1",
        "season": season,
        "source_release_sha": source_commit,
        "information_available_as_of": retrieved_at,
        "scope": "Capabilities proved by the currently pinned 2026/27 source release, not the football-data universe.",
        "capability_count": len(capabilities),
        "state_totals": dict(sorted(totals.items())),
        "capabilities": capabilities,
    }


def materialise(args: argparse.Namespace) -> dict[str, object]:
    source_root = Path(args.source_root).resolve()
    source_repo_root = Path(args.source_repo_root).resolve()
    output_root = Path(args.output_root).resolve()
    season = args.season
    paths = _season_source_paths(source_root, season)
    source_metadata = _source_metadata(
        paths,
        source_root,
        repo_root=source_repo_root,
        source_commit=args.source_commit,
    )
    fixture_rows, fixture_fields, fixture_payload = _pinned_csv(
        paths["fixtures"], repo_root=source_repo_root, source_commit=args.source_commit
    )
    player_rows, player_fields, player_payload = _pinned_csv(
        paths["players"], repo_root=source_repo_root, source_commit=args.source_commit
    )
    teams_payload, teams_git_path = _pinned_file_bytes(
        paths["teams_index"], repo_root=source_repo_root, source_commit=args.source_commit
    )
    teams_by_local = _team_entries_bytes(
        teams_payload, season, label=f"{args.source_commit}:{teams_git_path}"
    )

    predecessor = args.predecessor_season
    predecessor_paths = _season_source_paths(source_root, predecessor)
    _verify_pinned_paths(
        {
            "fixtures": predecessor_paths["fixtures"],
            "players": predecessor_paths["players"],
        },
        repo_root=source_repo_root,
        source_commit=args.source_commit,
    )
    previous_fixture_rows, previous_fixture_fields, _ = _pinned_csv(
        predecessor_paths["fixtures"],
        repo_root=source_repo_root,
        source_commit=args.source_commit,
    )
    previous_player_rows, previous_player_fields, _ = _pinned_csv(
        predecessor_paths["players"],
        repo_root=source_repo_root,
        source_commit=args.source_commit,
    )
    if fixture_fields != previous_fixture_fields or player_fields != previous_player_fields:
        raise MaterialisationError("Pinned season schema differs from its declared predecessor.")

    existing_fixtures, existing_fixture_fields = _read_csv(output_root / "fixtures_master_corrected.csv")
    existing_teams, existing_team_fields = _read_csv(output_root / "identity" / "team_seasons.csv")
    existing_provenance, existing_provenance_fields = _read_csv(output_root / "identity" / "team_seasons_provenance.csv")
    registry_rows, _ = _read_csv(output_root / "player_identity_registry.csv")
    if existing_fixture_fields != CANONICAL_FIELDS or existing_team_fields != TEAM_FIELDS or existing_provenance_fields != TEAM_PROVENANCE_FIELDS:
        raise MaterialisationError("Existing FRL canonical artefact schema does not match the governed contract.")

    canonical = build_canonical_fixtures(fixture_rows, season=season, teams_by_local_id=teams_by_local)
    team_rows = build_team_seasons(existing_teams, season=season, teams_by_local_id=teams_by_local, source_commit=args.source_commit)
    bridge, bridge_seasons, bridge_meta = _player_match_bridge(
        Path(args.player_match_root).resolve(),
        source_commit=args.source_commit,
        repo_root=source_repo_root,
    )
    identity_rows = build_player_identities(
        player_rows,
        season=season,
        bridge_candidates=bridge,
        bridge_seasons=bridge_seasons,
        registered_source_player_ids={str(row.get("source_player_id", "")).strip() for row in registry_rows},
        source_commit=args.source_commit,
        source_path=str(source_metadata["players"]["path"]),
        source_sha256=str(source_metadata["players"]["sha256"]),
    )
    fixture_evidence, fixture_evidence_fields = _fixture_evidence_rows(
        fixture_rows, canonical, season=season, source_commit=args.source_commit,
        source_repository=args.source_repository, source_path=str(source_metadata["fixtures"]["path"]),
        source_sha256=str(source_metadata["fixtures"]["sha256"]), retrieved_at=args.retrieved_at,
    )
    player_evidence, player_evidence_fields = _player_evidence_rows(
        player_rows, canonical, identity_rows, teams_by_local, season=season,
        source_commit=args.source_commit, source_repository=args.source_repository,
        source_path=str(source_metadata["players"]["path"]), source_sha256=str(source_metadata["players"]["sha256"]),
        retrieved_at=args.retrieved_at,
    )

    complete_fixtures = [row for row in existing_fixtures if row.get("season") != season] + canonical
    complete_teams = [row for row in existing_teams if row.get("season") != season] + team_rows
    complete_provenance = [row for row in existing_provenance if row.get("season") != season] + [{
        "season": season,
        "method": "pinned_fpl_fixture_and_team_index",
        "source": f"Premier-League-Stats@{args.source_commit}",
        "notes": "Persistent team code and season-local FPL team ID preserved from the pinned teams index; canonical fixtures use source fixture id/code.",
    }]

    release_dir = output_root / "data" / "season_releases" / season / "releases" / args.source_commit
    preserved_paths = {
        key: release_dir / "source" / Path(str(meta["path"])).name
        for key, meta in source_metadata.items()
    }
    pinned_payloads = {
        key: _pinned_file_bytes(
            paths[key], repo_root=source_repo_root, source_commit=args.source_commit
        )[0]
        for key in paths
    }
    for key, destination in preserved_paths.items():
        _write_or_check(destination, pinned_payloads[key], check=args.check)

    manifest = {
        "schema_version": "FRL_INCREMENTAL_SEASON_RELEASE_MANIFEST_V1",
        "season": season,
        "source_repository": args.source_repository,
        "source_commit": args.source_commit,
        "source_commit_date": args.source_commit_date,
        "source_commit_message": args.source_commit_message,
        "retrieved_at": args.retrieved_at,
        "rights_classification": RIGHTS_CLASSIFICATION,
        "source_provider_attribution": "Official FPL API evidence redistributed through Premier-League-Stats",
        "source_artifacts": source_metadata,
        "preserved_artifacts": {key: destination.relative_to(output_root).as_posix() for key, destination in preserved_paths.items()},
        "predecessor_schema_comparison": {
            "season": predecessor,
            "fixture_fields_equal": fixture_fields == previous_fixture_fields,
            "player_fields_equal": player_fields == previous_player_fields,
            "added_fixture_fields": sorted(set(fixture_fields) - set(previous_fixture_fields)),
            "removed_fixture_fields": sorted(set(previous_fixture_fields) - set(fixture_fields)),
            "added_player_fields": sorted(set(player_fields) - set(previous_player_fields)),
            "removed_player_fields": sorted(set(previous_player_fields) - set(player_fields)),
            "fixture_field_profiles": {predecessor: _schema_profile(previous_fixture_rows, previous_fixture_fields), season: _schema_profile(fixture_rows, fixture_fields)},
            "player_field_profiles": {predecessor: _schema_profile(previous_player_rows, previous_player_fields), season: _schema_profile(player_rows, player_fields)},
        },
        "player_match_identity_bridge": bridge_meta,
        "materialisation_counts": {
            "source_fixtures": len(fixture_rows),
            "canonical_fixtures": len(canonical),
            "completed_fixtures": sum(row["home_score"] != "" for row in canonical),
            "scheduled_fixtures": sum(row["home_score"] == "" for row in canonical),
            "team_seasons": len(team_rows),
            "source_player_fixture_rows": len(player_rows),
            "materialised_player_fixture_rows": len(player_evidence),
            "zero_minute_rows": sum(row["frl_participation_status"] == "REGISTERED_ZERO_MINUTES" for row in player_evidence),
            "player_identity_statuses": dict(sorted(Counter(row["identity_status"] for row in identity_rows).items())),
            "duplicate_player_fixture_rows": 0,
            "unresolved_fixture_rows": 0,
        },
    }
    gap_register = _capability_register(
        season=season, source_commit=args.source_commit, retrieved_at=args.retrieved_at,
        canonical_rows=canonical, player_rows=player_rows, identity_rows=identity_rows,
    )

    outputs: dict[Path, bytes] = {
        output_root / "fixtures_master_corrected.csv": _csv_bytes(complete_fixtures, CANONICAL_FIELDS),
        output_root / "identity" / "team_seasons.csv": _csv_bytes(complete_teams, TEAM_FIELDS),
        output_root / "identity" / "team_seasons_provenance.csv": _csv_bytes(complete_provenance, TEAM_PROVENANCE_FIELDS),
        output_root / "_merged" / "players" / f"{season}_all_players_gw.csv": player_payload,
        output_root / "data" / "fpl_fixture_evidence.csv": _csv_bytes(fixture_evidence, fixture_evidence_fields),
        output_root / "data" / "fpl_player_gw_evidence.csv": _csv_bytes(player_evidence, player_evidence_fields),
        output_root / "data" / "fpl_player_identity_relationships.csv": _csv_bytes(identity_rows, IDENTITY_FIELDS),
        release_dir / "source_manifest.json": _json_bytes(manifest),
        output_root / "data" / "season_releases" / season / "current_release.json": _json_bytes(manifest),
        output_root / "data" / "season_releases" / season / "capability_gap_register.json": _json_bytes(gap_register),
    }
    for path, payload in outputs.items():
        _write_or_check(path, payload, check=args.check)
    return {"manifest": manifest, "gap_register": gap_register}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, help="Checkout's fpl_scraper/fpl_stats directory used only to locate source paths")
    parser.add_argument("--source-repo-root", required=True, help="Git repository root containing the pinned source commit")
    parser.add_argument("--player-match-root", required=True, help="Approved preserved pl_stats directory")
    parser.add_argument("--output-root", default=str(ROOT))
    parser.add_argument("--season", default="2026-27")
    parser.add_argument("--predecessor-season", default="2025-26")
    parser.add_argument("--source-repository", default=DEFAULT_UPSTREAM_URL)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-commit-date", required=True)
    parser.add_argument("--source-commit-message", required=True)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.retrieved_at:
        current_manifest = Path(args.output_root) / "data" / "season_releases" / args.season / "current_release.json"
        if args.check and current_manifest.is_file():
            args.retrieved_at = json.loads(current_manifest.read_text(encoding="utf-8"))["retrieved_at"]
        else:
            args.retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return args


def main(argv: list[str] | None = None) -> int:
    try:
        result = materialise(_parse_args(argv))
    except MaterialisationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    counts = result["manifest"]["materialisation_counts"]
    print(json.dumps(counts, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
