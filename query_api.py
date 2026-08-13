from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_lab


def league_table(season):
    return query_lab.league_table(
        season=season
    )


def team_summary(
    season,
    team,
):
    return query_lab.team_summary(
        season=season,
        team=team,
    )


def team_compare(
    team,
    seasons,
):
    return query_lab.team_compare(
        team=team,
        seasons=seasons,
    )


def fixtures(
    season=None,
    team=None,
    opponent=None,
    venue=None,
    result=None,
    limit=100,
):
    return query_lab.query_fixtures(
        season=season,
        team=team,
        opponent=opponent,
        venue=venue,
        result=result,
        limit=limit,
    )



def head_to_head(
    team,
    opponent,
    seasons,
):
    return query_lab.head_to_head(
        team=team,
        opponent=opponent,
        seasons=seasons,
    )


def team_form(
    season,
    team=None,
    team_id=None,
):
    return query_lab.team_form(
        season=season,
        team=team,
        team_id=team_id,
    )


def top_players(
    season,
    metric="goals",
    limit=10,
):
    return query_lab.top_players(
        season=season,
        metric=metric,
        limit=limit,
    )


def player_total(
    season,
    player,
    metric="goals",
):
    return query_lab.player_total(
        season=season,
        player_search=player,
        metric=metric,
    )


def list_seasons():
    rows = query_lab.load_identity_registry()

    return sorted(
        {
            row["season"]
            for row in rows
        }
    )


def list_metrics():
    return dict(
        query_lab.METRICS
    )


def dispatch(
    query,
    **kwargs,
):
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
            f"Unknown query '{query}'. "
            f"Available: "
            f"{', '.join(sorted(queries))}"
        )

    return queries[query](**kwargs)


def main():
    payload = json.loads(
        sys.stdin.read()
    )

    query = payload.get(
        "query"
    )

    if not query:
        raise ValueError(
            "Request must contain 'query'."
        )

    kwargs = payload.get(
        "params",
        {}
    )

    result = dispatch(
        query,
        **kwargs
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "type": type(exc).__name__,
                },
                indent=2,
            )
        )
        raise SystemExit(1)
