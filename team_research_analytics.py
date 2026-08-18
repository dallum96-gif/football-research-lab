from __future__ import annotations

from datetime import datetime
from math import ceil
from typing import Any

import query_lab
from frl_analytical import ResearchResult, team_fixtures


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _rate(numerator: float, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 3)


def team_performance_profile(
    season: str,
    team: str,
    rolling_window: int = 5,
) -> ResearchResult:
    if rolling_window < 2:
        raise ValueError("rolling_window must be at least 2")

    source = team_fixtures(season=season, team=team, limit=100)
    completed = [
        row
        for row in source.rows
        if row.get("goals_for") is not None
        and row.get("goals_against") is not None
        and str(row.get("result", "")).upper() != "UNPLAYED"
    ]
    completed.sort(key=lambda row: (_parse_datetime(row["kickoff_time"]), int(row["fixture_id"])))

    enriched: list[dict[str, Any]] = []
    total_points = 0
    phase_size = max(1, ceil(len(completed) / 3))

    for index, row in enumerate(completed, start=1):
        result = str(row["result"]).upper()
        points = {"W": 3, "D": 1, "L": 0}.get(result, 0)
        total_points += points

        start = max(0, index - rolling_window)
        window = completed[start:index]
        window_points = sum(
            {"W": 3, "D": 1, "L": 0}.get(str(item["result"]).upper(), 0)
            for item in window
        )
        window_gf = sum(int(item["goals_for"]) for item in window)
        window_ga = sum(int(item["goals_against"]) for item in window)

        phase_index = min((index - 1) // phase_size, 2)
        phase = ("First third", "Middle third", "Final third")[phase_index]

        enriched.append(
            {
                **row,
                "sequence": index,
                "points": points,
                "cumulative_points": total_points,
                "cumulative_ppg": _rate(total_points, index),
                "rolling_ppg": _rate(window_points, len(window)),
                "rolling_goals_for_per_match": _rate(window_gf, len(window)),
                "rolling_goals_against_per_match": _rate(window_ga, len(window)),
                "phase": phase,
            }
        )

    def split_summary(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
        matches = len(rows)
        points = sum(int(row["points"]) for row in rows)
        gf = sum(int(row["goals_for"]) for row in rows)
        ga = sum(int(row["goals_against"]) for row in rows)
        wins = sum(str(row["result"]).upper() == "W" for row in rows)
        return {
            "label": label,
            "matches": matches,
            "wins": wins,
            "points": points,
            "ppg": _rate(points, matches),
            "goals_for": gf,
            "goals_against": ga,
            "goals_per_match": _rate(gf, matches),
            "goals_against_per_match": _rate(ga, matches),
            "goal_difference_per_match": _rate(gf - ga, matches),
            "win_rate": _rate(wins, matches),
        }

    venue_splits = [
        split_summary(
            [row for row in enriched if row.get("venue") == venue],
            venue.title(),
        )
        for venue in ("home", "away")
    ]

    phase_splits = [
        split_summary(
            [row for row in enriched if row.get("phase") == phase],
            phase,
        )
        for phase in ("First third", "Middle third", "Final third")
    ]

    overall = split_summary(enriched, "Overall")
    clean_sheets = sum(int(row["goals_against"]) == 0 for row in enriched)
    failed_to_score = sum(int(row["goals_for"]) == 0 for row in enriched)
    overall.update(
        {
            "clean_sheet_rate": _rate(clean_sheets, len(enriched)),
            "failed_to_score_rate": _rate(failed_to_score, len(enriched)),
        }
    )

    return ResearchResult(
        query_type="team_performance_profile",
        parameters={"season": season, "team": team, "rolling_window": rolling_window},
        columns=list(enriched[0].keys()) if enriched else [],
        rows=enriched,
        population={
            "season": season,
            "team": team,
            "completed_matches": len(enriched),
            "rolling_window": rolling_window,
            "phase_definition": "season split into three chronological thirds by completed fixture count",
            "overall": overall,
            "venue_splits": venue_splits,
            "phase_splits": phase_splits,
        },
        provenance=source.provenance,
        temporal_context={
            **source.temporal_context,
            "ordering": "kickoff_time then fixture_id",
        },
        limitations=(
            ["Profile metrics exclude unplayed fixtures."]
            if source.rows and len(enriched) != len(source.rows)
            else []
        ),
    )


def team_season_comparison(team: str, seasons: list[str]) -> ResearchResult:
    source = query_lab.team_compare(team=team, seasons=seasons)
    rows: list[dict[str, Any]] = []
    for row in source.get("seasons", []):
        played = int(row.get("played", 0) or 0)
        points = int(row.get("points", 0) or 0)
        gf = int(row.get("goals_for", 0) or 0)
        ga = int(row.get("goals_against", 0) or 0)
        gd = int(row.get("goal_difference", 0) or 0)
        rows.append(
            {
                **row,
                "points_per_match": _rate(points, played),
                "goals_for_per_match": _rate(gf, played),
                "goals_against_per_match": _rate(ga, played),
                "goal_difference_per_match": _rate(gd, played),
                "win_rate": _rate(int(row.get("wins", 0) or 0), played),
            }
        )

    def best(metric: str, reverse: bool = True) -> dict[str, Any] | None:
        populated = [row for row in rows if row.get(metric) is not None]
        if not populated:
            return None
        return max(populated, key=lambda row: row[metric]) if reverse else min(populated, key=lambda row: row[metric])

    return ResearchResult(
        query_type="team_season_comparison",
        parameters={"team": team, "seasons": list(seasons)},
        columns=list(rows[0].keys()) if rows else [],
        rows=rows,
        population={
            "requested_seasons": list(seasons),
            "returned_seasons": len(rows),
            "skipped_seasons": source.get("skipped_seasons", []),
            "signals": {
                "best_ppg": best("points_per_match"),
                "best_attack": best("goals_for_per_match"),
                "best_defence": best("goals_against_per_match", reverse=False),
                "best_goal_difference": best("goal_difference_per_match"),
            },
        },
        provenance={
            "fixture_source": source.get("fixture_source_file"),
            "identity_source": source.get("identity_source_file"),
            "corrections_source": source.get("corrections_file"),
            "query_version": source.get("query_version"),
        },
        temporal_context={"seasons": list(seasons), "comparison": "season_end_summary"},
        limitations=(
            ["Only verified seasons in the identity registry are included."]
            if source.get("skipped_seasons")
            else []
        ),
    )
