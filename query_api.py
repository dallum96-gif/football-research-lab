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
    by_local_id = {}
    by_persistent_code = {}
    aliases = {}

    for row in rows:
        if row.get("season") != season:
            continue

        local_id = str(row.get("local_team_id", "")).strip()
        persistent_code = str(row.get("persistent_team_code", "")).strip()
        canonical = str(row.get("canonical_name", "")).replace("_", " ").strip()
        source_name = str(row.get("source_name", "")).replace("_", " ").strip()

        if not local_id or not canonical:
            continue

        record = {
            "local_team_id": local_id,
            "persistent_team_code": persistent_code,
            "team": canonical,
        }
        by_local_id[local_id] = record
        if persistent_code:
            by_persistent_code[persistent_code] = record

        aliases[canonical.casefold()] = local_id
        if source_name:
            aliases[source_name.casefold()] = local_id

    return by_local_id, by_persistent_code, aliases


def _resolve_team_id(season, search):
    if search is None:
        return None

    requested = str(search).strip().casefold()
    by_local_id, by_persistent_code, aliases = _team_lookup(season)

    if requested in aliases:
        return aliases[requested]

    if requested.isdigit():
        if requested in by_local_id:
            return requested
        if requested in by_persistent_code:
            return by_persistent_code[requested]["local_team_id"]

    for local_id, record in by_local_id.items():
        if requested == record["team"].casefold() or requested in record["team"].casefold():
            return local_id

    try:
        resolved = query_lab.resolve_team(season, search)
        local_id = str(resolved.get("local_team_id", "")).strip()
        if local_id in by_local_id:
            return local_id
    except Exception as exc:
        raise ValueError(f"No team matching '{search}' found in {season}.") from exc

    raise ValueError(f"No team matching '{search}' found in {season}.")


def _fixture_result(team_id, home_id, away_id, home_score, away_score):
    if home_score in (None, "") or away_score in (None, ""):
        return "UNPLAYED"

    home_score = int(home_score)
    away_score = int(away_score)

    if team_id == home_id:
        return "W" if home_score > away_score else "D" if home_score == away_score else "L"

    return "W" if away_score > home_score else "D" if away_score == home_score else "L"


def league_table(season):
    by_local_id, _, _ = _team_lookup(season)
    fixtures = [row for row in _load_csv(FIXTURE_FILE) if row.get("season") == season]

    stats = {
        local_id: {
            "team": record["team"],
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
        }
        for local_id, record in by_local_id.items()
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

    by_local_id, _, _ = _team_lookup(season)
    team_id = _resolve_team_id(season, team)
    opponent_id = _resolve_team_id(season, opponent)

    rows = [row for row in _load_csv(FIXTURE_FILE) if row.get("season") == season]
    results = []

    for row in rows:
        home_id = str(row.get("home_team_id", "")).strip()
        away_id = str(row.get("away_team_id", "")).strip()

        if home_id not in by_local_id or away_id not in by_local_id:
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

        current_result = (
            _fixture_result(
                team_id,
                home_id,
                away_id,
                row.get("home_score"),
                row.get("away_score"),
            )
            if team_id
            else None
        )

        if result and current_result != result:
            continue

        output = dict(row)
        output["home_team_name"] = by_local_id[home_id]["team"]
        output["away_team_name"] = by_local_id[away_id]["team"]
        results.append(output)

    results.sort(
        key=lambda item: (
            str(item.get("kickoff_time", "")),
            int(item.get("fixture_id", 0)),
        )
    )

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
        "results": results[:limit],
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
