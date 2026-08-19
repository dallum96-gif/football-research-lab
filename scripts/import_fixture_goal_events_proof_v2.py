from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_identity_audit
import player_research
import query_lab
from match_stats import fixture_source_match

RAW = ROOT / "data" / "raw" / "fixture_goal_events_pulselive.csv"
OUT = ROOT / "data" / "fixture_goal_events.csv"

FIELDS = [
    "season", "fixture_id", "source_match_id", "source_pulse_fixture_id",
    "source_event_id", "source_event_type", "source_event_seconds",
    "source_event_time_label", "source_event_text", "source_scorer_name",
    "source_scorer_team", "source_scorer_id", "pulse_player_id",
    "archive_player_id", "identity_status", "fpl_element", "player_name",
    "side", "own_goal", "source_url", "retrieved_at_utc", "goal_count_match",
]


def norm(s):
    return " ".join(str(s or "").casefold().replace("_", " ").split())


def load(path):
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def player_bridge(season):
    fpl = {}
    for row in player_research._load_season_rows(season):
        name = player_research.display_player_name(row)
        club = player_research._row_club(row)
        element = player_research.seasonal_player_id(row)
        if not name or not club or not element:
            continue
        team = query_lab.resolve_team(season, club)
        key = (norm(name), str(team["persistent_team_code"]).strip())
        value = (str(element).strip(), name.strip())
        if key in fpl and fpl[key] != value:
            raise RuntimeError(f"Ambiguous FPL player identity: {season}/{key}")
        fpl[key] = value

    archive = defaultdict(set)
    for (name, team_code), values in player_identity_audit.source_player_index(season).items():
        for pid, display in values:
            archive[(name, str(team_code).strip())].add((pid, display))

    out = {}
    for key, fpl_value in fpl.items():
        vals = archive.get(key, set())
        if len(vals) == 1:
            pid, display = next(iter(vals))
            out[key] = (pid, fpl_value[0], fpl_value[1] or display)
    return out


def main():
    raw = load(RAW)
    print(f"RAW ROWS: {len(raw)}", flush=True)
    if not raw:
        raise RuntimeError("Raw PulseLive goal-event CSV is empty")

    seasons = sorted({r["season"].strip() for r in raw if r.get("season")})
    print(f"SEASONS: {', '.join(seasons)}", flush=True)

    identity_rows = query_lab.load_identity_registry()
    fixtures = load(Path(query_lab.FIXTURE_FILE))
    seasonal = [r for r in fixtures if r.get("season", "").strip() in seasons]
    print(f"CANONICAL FIXTURES IN TEST SEASONS: {len(seasonal)}", flush=True)

    targets = sorted({(r["season"].strip(), r["source_match_id"].strip()) for r in raw})
    print(f"SOURCE MATCH TARGETS: {len(targets)}", flush=True)

    resolved = {}
    for i, (season, source_id) in enumerate(targets, 1):
        print(f"FIXTURE {i}/{len(targets)}: {season}/{source_id}", flush=True)
        hits = []
        for fixture in seasonal:
            if fixture.get("season", "").strip() != season:
                continue
            hit = fixture_source_match(fixture, identity_rows)
            if hit and str(hit[0]).strip() == source_id:
                hits.append((fixture, hit))
        if len(hits) != 1:
            raise RuntimeError(f"Expected exactly one canonical fixture for {season}/{source_id}; found {len(hits)}")
        resolved[(season, source_id)] = hits[0]

    player_indexes = {season: player_bridge(season) for season in seasons}
    print("PLAYER IDENTITY: loaded", flush=True)

    out = []
    for row in raw:
        season = row["season"].strip()
        source_id = row["source_match_id"].strip()
        fixture, (_resolved_source_id, home, away) = resolved[(season, source_id)]
        scorer_name = row["source_scorer_name"].strip()
        team = query_lab.resolve_team(season, row["source_scorer_team"])
        team_code = str(team["persistent_team_code"]).strip()
        identity = player_indexes[season].get((norm(scorer_name), team_code))
        if not identity:
            raise RuntimeError(f"No verified player bridge: {season}/{source_id}/{row['source_scorer_id']}/{scorer_name}/{row['source_scorer_team']}")

        archive_player_id, element, player_name = identity
        home_code = str(home.get("team_id", "")).strip()
        away_code = str(away.get("team_id", "")).strip()
        scorer_side = "home" if team_code == home_code else "away" if team_code == away_code else ""
        if not scorer_side:
            raise RuntimeError(f"Scorer team does not match fixture sides: {scorer_name}/{row['source_scorer_team']}")

        own_goal = str(row.get("own_goal", "false")).casefold() == "true"
        scoring_side = ("away" if scorer_side == "home" else "home") if own_goal else scorer_side

        out.append({
            **row,
            "fixture_id": str(fixture["fixture_id"]),
            "pulse_player_id": row["source_scorer_id"],
            "archive_player_id": archive_player_id,
            "identity_status": "VERIFIED",
            "fpl_element": element,
            "player_name": player_name,
            "side": scoring_side,
        })

    temp = OUT.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    temp.replace(OUT)

    print("=" * 72, flush=True)
    print("FRL GOAL EVENT PROOF IMPORT", flush=True)
    print(f"RAW ROWS: {len(raw)}", flush=True)
    print(f"CANONICAL ROWS: {len(out)}", flush=True)
    print(f"OUTPUT: {OUT}", flush=True)
    print("ALL SCORERS VERIFIED THROUGH FRL TEAM + PLAYER IDENTITY RECONSTRUCTION", flush=True)


if __name__ == "__main__":
    main()
