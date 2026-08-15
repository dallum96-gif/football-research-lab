from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_lab

FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
IDENTITY_FILE = ROOT / "identity" / "team_seasons.csv"
QUERY_VERSION = "0.4.1"


def _load_csv(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                return list(reader)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def _team_lookup(season):
    rows = _load_csv(IDENTITY_FILE)
    lookup = {}
    aliases = {}
    local_ids = {}
    for row in rows:
        if row.get("season") != season:
            continue
        club_id = str(row.get("club_id", "")).strip()
        canonical = str(row.get("canonical_name", "")).replace("_", " ").strip()
        if not club_id or not canonical:
            continue
        lookup[club_id] = canonical
        aliases[canonical.casefold()] = club_id
        aliases[str(row.get("source_name", "")).replace("_", " ").strip().casefold()] = club_id
        local_ids[club_id] = str(row.get("local_team_id", "")).strip()
    return lookup, aliases, local_ids


def _resolve_team_id(season, search):
    if search is None:
        return None
    requested = str(search).strip().casefold()
    lookup, aliases, local_ids = _team_lookup(season)
    if requested in aliases:
        return aliases[requested]
    if requested.isdigit() and requested in lookup:
        return requested
    for club_id, canonical in lookup.items():
        if requested == canonical.casefold() or requested in canonical.casefold():
            return club_id
    try:
        resolved = query_lab.resolve_team(season, search)
        return str(resolved["persistent_team_code"])
    except Exception as exc:
        raise ValueError(f"No team matching '{search}' found in {season}.") from exc


def _fixture_result(team_id, home_id, away_id, home_score, away_score):
    if home_score in (None, "") or away_score in (None, ""):
        return "UNPLAYED"
    home_score = int(home_score)
    away_score = int(away_score)
    if team_id == home_id:
        return "W" if home_score > away_score else "D" if home_score == away_score else "L"
    return "W" if away_score > home_score else "D" if away_score == home_score else "L"


def league_table(season):
    teams_by_id, _, _ = _team_lookup(season)
    fixtures = [row for row in _load_csv(FIXTURE_FILE) if row.get("season") == season]

    stats = {
        club_id: {
            "team": team_name,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
        }
        for club_id, team_name in teams_by_id.items()
    }

    for row in fixtures:
        home_id = str(row.get("home_team_id", "")).strip()
        away_id = str(row.get("away_team_id", "")).strip()
        if home_id not in stats or away_id not in stats:
            raise ValueError(
                f"Fixture identity missing for {season}: "
                f"{home_id} vs {away_id} (fixture {row.get('fixture_id')})."
            )
        if row.get("home_score") in (None, "") or row.get("away_score") in (None, ""):
            continue
        home_score = int(row["home_score"])
        away_score = int(row["away_score"])

        home = stats[home_id]
        away = stats[away_id]
        home["played"] += 1
        away["played"] += 1
        home["goals_for"] += home_score
        home["goals_against"] += away_score
        away["goals_for"] += away_score
        away["goals_against"] += home_score

        if home_score > away_score:
            home["wins"] += 1
            away["losses"] += 1
            home["points"] += 3
        elif away_score > home_score:
            away["wins"] += 1
            home["losses"] += 1
            away["points"] += 3
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    rows = []
    for item in stats.values():
        item["goal_difference"] = item["goals_for"] - item["goals_against"]
        rows.append(item)

    rows.sort(
        key=lambda item: (
            -item["points"],
            -item["goal_difference"],
            -item["goals_for"],
            item["team"].casefold(),
        )
    )

    for position, item in enumerate(rows, start=1):
        item["position"] = position

    return {
        "query_type": "league_table",
        "query_version": QUERY_VERSION,
        "season": season,
        "source_file": str(FIXTURE_FILE),
        "source_rows": len(fixtures),
        "teams": rows,
    }


def fixtures(
    season=None,
    team=None,
    opponent=None,
    venue=None,
    result=None,
    limit=100,
):
    if not season:
        raise ValueError("Season is required for fixture queries.")

    teams_by_id, _, _ = _team_lookup(season)
    team_id = _resolve_team_id(season, team)
    opponent_id = _resolve_team_id(season, opponent)

    rows = [row for row in _load_csv(FIXTURE_FILE) if row.get("season") == season]
    results = []

    for row in rows:
        home_id = str(row.get("home_team_id", "")).strip()
        away_id = str(row.get("away_team_id", "")).strip()
        if home_id not in teams_by_id or away_id not in teams_by_id:
            raise ValueError(
                f"Fixture identity missing for {season}: "
                f"{home_id} vs {away_id} (fixture {row.get('fixture_id')})."
            )
        if team_id and team_id not in (home_id, away_id):
            continue
        if opponent_id and opponent_id not in (home_id, away_id):
            continue
        if opponent_id and team_id and opponent_id == team_id:
            continue

        current_venue = None
        if team_id:
            current_venue = "home" if home_id == team_id else "away"
            if venue and venue != current_venue:
                continue

        current_result = _fixture_result(
            team_id,
            home_id,
            away_id,
            row.get("home_score"),
            row.get("away_score"),
        ) if team_id else None
        if result and current_result != result:
            continue

        output = dict(row)
        output["home_team_name"] = teams_by_id[home_id]
        output["away_team_name"] = teams_by_id[away_id]
        results.append(output)

    results.sort(key=lambda item: (str(item.get("kickoff_time", "")), int(item.get("fixture_id", 0))))

    selected = results[:limit]
    return {
        "query_type": "fixtures",
        "query_version": QUERY_VERSION,
        "season": season,
        "filters": {
            "team_id": team_id,
            "opponent_id": opponent_id,
            "venue": venue,
            "result": result,
        },
        "total_matches": len(results),
        "results": selected,
        "source_file": str(FIXTURE_FILE),
    }


def team_summary(season, team):
    return query_lab.team_summary(season=season, team=team)


def team_compare(team, seasons):
    return query_lab.team_compare(team=team, seasons=seasons)


def head_to_head(team, opponent, seasons):
    return query_lab.head_to_head(team=team, opponent=opponent, seasons=seasons)


def team_form(season, team=None, team_id=None):
    return query_lab.team_form(season=season, team=team, team_id=team_id)


def top_players(season, metric="goals", limit=10):
    return query_lab.top_players(season=season, metric=metric, limit=limit)


def player_total(season, player, metric="goals"):
    return query_lab.player_total(season=season, player_search=player, metric=metric)


def fixture_detail(season, fixture_id):
    return query_lab.fixture_detail(season=season, fixture_id=fixture_id)


def list_seasons():
    rows = query_lab.load_identity_registry()
    return sorted({row["season"] for row in rows})


def list_metrics():
    return dict(query_lab.METRICS)


def dispatch(query, **kwargs):
    queries = {
        "league-table": league_table,
        "team-summary": team_summary,
        "team-compare": team_compare,
        "fixtures": fixtures,
        "head-to-head": head_to_head,
        "team-form": team_form,
        "top-players": top_players,
        "player-total": player_total,
    }
    if query not in queries:
        raise ValueError(
            f"Unknown query '{query}'. Available: {', '.join(sorted(queries))}"
        )
    return queries[query](**kwargs)


def main():
    import json
    payload = json.loads(sys.stdin.read())
    query = payload.get("query")
    if not query:
        raise ValueError("Request must contain 'query'.")
    result = dispatch(query, **payload.get("params", {}))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc), "type": type(exc).__name__}, indent=2))
        raise SystemExit(1)
