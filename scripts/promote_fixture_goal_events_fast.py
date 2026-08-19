from __future__ import annotations

import csv
import os
import sys
import tempfile
import unicodedata
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_research
import query_lab
from match_stats import fixture_source_match
import player_identity_audit

RAW = ROOT / "data" / "raw" / "fixture_goal_events_pulselive.csv"
OUT = ROOT / "data" / "fixture_goal_events.csv"

FIELDS = [
    "season","fixture_id","source_match_id","source_pulse_fixture_id",
    "source_event_id","source_event_type","source_event_seconds",
    "source_event_time_label","source_event_text","source_scorer_name",
    "source_scorer_team","source_scorer_id","pulse_player_id",
    "archive_player_id","identity_status","fpl_element","player_name",
    "side","own_goal","source_url","retrieved_at_utc","goal_count_match",
]


def norm(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def load_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def atomic_write(rows):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".fixture_goal_events.", suffix=".tmp", dir=OUT.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, OUT)
    except Exception:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise


def build_fpl_index(seasons):
    index = defaultdict(set)
    for season in seasons:
        for row in player_research._load_season_rows(season):
            name = norm(player_research.display_player_name(row))
            club = player_research._row_club(row)
            if not name or not club:
                continue
            team = query_lab.resolve_team(season, club)
            element = str(row.get("element") or player_research.seasonal_player_id(row) or "").strip()
            display = player_research.display_player_name(row)
            if element:
                index[(season, name, str(team["persistent_team_code"]).strip())].add((element, display))
    return index


def build_source_index(seasons):
    out = {}
    for season in seasons:
        out[season] = player_identity_audit.source_player_index(season)
    return out


def resolve_target_fixtures(raw, identity_rows):
    targets = {(r["season"].strip(), r["source_match_id"].strip()) for r in raw if r.get("season") and r.get("source_match_id")}
    fixtures = { (r["season"], str(r["fixture_id"])): r for r in query_lab.load_csv(query_lab.FIXTURE_FILE)[0] }
    result = {}
    for season, source_id in sorted(targets):
        found = []
        for fixture in fixtures.values():
            if fixture["season"] != season:
                continue
            resolved = fixture_source_match(fixture, identity_rows)
            if resolved and str(resolved[0]).strip() == source_id:
                found.append((fixture, resolved))
        if len(found) != 1:
            raise RuntimeError(f"Canonical fixture reconstruction failed for {season}/{source_id}: found {len(found)}")
        result[(season, source_id)] = found[0]
    return result


def main():
    raw = load_rows(RAW)
    print(f"RAW ROWS: {len(raw)}")
    seasons = sorted({r["season"].strip() for r in raw if r.get("season")})
    print(f"SEASONS: {', '.join(seasons)}")

    identity_rows = query_lab.load_identity_registry()
    print("TEAM IDENTITY: loaded")
    fixture_map = resolve_target_fixtures(raw, identity_rows)
    print(f"FIXTURE RECONSTRUCTION: {len(fixture_map)} source matches")

    fpl_index = build_fpl_index(seasons)
    source_index = build_source_index(seasons)
    print("PLAYER IDENTITY: loaded via FRL team reconstruction")

    canonical = []
    unresolved = []

    for row in raw:
        season = row["season"].strip()
        source_id = row["source_match_id"].strip()
        pulse_id = row["source_scorer_id"].strip()
        scorer_name = row["source_scorer_name"].strip()
        scorer_team = row["source_scorer_team"].strip()

        fixture, (resolved_source_id, home, away) = fixture_map[(season, source_id)]
        team = query_lab.resolve_team(season, scorer_team)
        persistent = str(team["persistent_team_code"]).strip()
        key = (season, norm(scorer_name), persistent)
        fpl_values = fpl_index.get(key, set())
        src_values = source_index[season].get((norm(scorer_name), persistent), set())

        if len(fpl_values) != 1 or len(src_values) != 1:
            unresolved.append(f"{season}/{source_id}:{pulse_id}/{scorer_name}/{scorer_team}")
            continue

        element, player_name = next(iter(fpl_values))
        archive_player_id, _ = next(iter(src_values))
        home_code = str(home.get("team_id") or "").strip()
        away_code = str(away.get("team_id") or "").strip()
        scorer_side = "home" if persistent == home_code else "away" if persistent == away_code else ""
        if not scorer_side:
            raise RuntimeError(f"Player team {persistent} is not either fixture side for {season}/{fixture['fixture_id']}")
        own_goal = str(row.get("own_goal") or "false").casefold() == "true"
        scoring_side = ("away" if scorer_side == "home" else "home") if own_goal else scorer_side

        canonical.append({
            **row,
            "fixture_id": str(fixture["fixture_id"]),
            "pulse_player_id": pulse_id,
            "archive_player_id": archive_player_id,
            "identity_status": "VERIFIED",
            "fpl_element": element,
            "player_name": player_name,
            "side": scoring_side,
        })

    if unresolved:
        raise RuntimeError("Refusing canonical promotion: unresolved rows: " + "; ".join(unresolved[:10]))

    atomic_write(canonical)
    print("=" * 72)
    print("FRL GOAL EVENT PROMOTION")
    print(f"RAW ROWS:       {len(raw)}")
    print(f"CANONICAL ROWS: {len(canonical)}")
    print(f"OUTPUT:         {OUT}")
    print(f"VALIDATED:      {datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}")


if __name__ == "__main__":
    main()
