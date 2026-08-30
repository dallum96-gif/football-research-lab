from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "api" / "frl_api.py"

IMPORT_OLD = "import query_api\nimport team_research_stats\n"
IMPORT_NEW = "import query_api\nimport team_research_stats\nimport team_analysis_kernel\n"

START = '''@app.get(
    "/api/v1/team-stats/{season}/{persistent_team_code}/overview",
    response_model=TeamStatsOverviewResult,
)
def get_team_stats_overview(
'''
END = "\n\n\ndef _ordinal(value: int) -> str:\n"

NEW_ENDPOINT = '''@app.get(
    "/api/v1/team-stats/{season}/{persistent_team_code}/overview",
    response_model=TeamStatsOverviewResult,
)
def get_team_stats_overview(
    season: str,
    persistent_team_code: str,
) -> TeamStatsOverviewResult:
    requested_code = persistent_team_code.strip()

    try:
        options = get_teams(season)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Team Stats context failed safely.",
        ) from exc

    selected = next(
        (
            option
            for option in options
            if option.persistent_team_code == requested_code
        ),
        None,
    )

    if selected is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Team {persistent_team_code} "
                f"is unavailable in {season}."
            ),
        )

    try:
        analysis = team_analysis_kernel.team_overview_analysis(
            season,
            requested_code,
        )

        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Governed Team Stats are unavailable for "
                    f"{selected.display_name} in {season}."
                ),
            )

        stats = team_research_stats.team_season_stats(
            season,
            requested_code,
        )

        if stats.get("status") != "AVAILABLE":
            raise HTTPException(
                status_code=404,
                detail=(
                    "Governed Team Stats are unavailable for "
                    f"{selected.display_name} in {season}."
                ),
            )

        match_rows = list(
            team_research_stats.team_match_stats(
                season,
                requested_code,
            )
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Team Stats Overview failed safely.",
        ) from exc

    metrics = [
        TeamStatsMetric(
            key=str(metric["key"]),
            label=str(metric["label"]),
            value=round(float(metric["value"]), 3),
            unit=str(metric["unit"]),
            rank=int(metric["rank"]),
            out_of=int(metric["out_of"]),
            percentile=float(metric["percentile"]),
            higher_is_better=bool(metric["higher_is_better"]),
        )
        for metric in analysis["metrics"]
        if metric.get("value") is not None
        and metric.get("rank") is not None
        and metric.get("percentile") is not None
    ]

    match_rows.sort(
        key=lambda row: (
            str(row.get("kickoff_time") or ""),
            str(row.get("fixture_id") or ""),
        )
    )

    trend: list[TeamStatsTrendPoint] = []

    for row in match_rows:
        gf = row.get("goals_for")
        ga = row.get("goals_against")
        points = 0

        if gf is not None and ga is not None:
            if float(gf) > float(ga):
                points = 3
            elif float(gf) == float(ga):
                points = 1

        trend.append(
            TeamStatsTrendPoint(
                fixture_id=str(row.get("fixture_id") or ""),
                kickoff_time=(
                    str(row.get("kickoff_time"))
                    if row.get("kickoff_time")
                    else None
                ),
                home=bool(row.get("home")),
                points=points,
                goals_for=(float(gf) if gf is not None else None),
                goals_against=(float(ga) if ga is not None else None),
                shots=(
                    float(row["Shots"])
                    if row.get("Shots") is not None
                    else None
                ),
                shots_on_target=(
                    float(row["Shots on target"])
                    if row.get("Shots on target") is not None
                    else None
                ),
                possession=(
                    float(row["Possession"])
                    if row.get("Possession") is not None
                    else None
                ),
            )
        )

    home_rows = [row for row in match_rows if row.get("home")]
    away_rows = [row for row in match_rows if not row.get("home")]

    xg = analysis.get("expected_goals") or {}
    expected_goals = xg.get("value")
    xg_overperformance = xg.get("xg_overperformance")

    limitations = [
        (
            "League ranks and percentiles are projections of the shared "
            "governed Team Stats season analysis result."
        ),
        (
            "Percentile is descriptive league context, not predictive "
            "evidence."
        ),
    ]

    if expected_goals is None:
        limitations.append(
            "Expected-goals evidence is omitted where no governed "
            "season representation is available."
        )
    elif not xg.get("coverage_complete"):
        limitations.append(
            "Expected-goals evidence is partial: "
            f"{xg.get('observed_matches', 0)} of "
            f"{xg.get('eligible_matches', 0)} team fixtures are observed. "
            "xG overperformance remains withheld until the season population "
            "is complete."
        )

    return TeamStatsOverviewResult(
        persistent_team_code=requested_code,
        display_name=selected.display_name,
        season=season,
        matches=int(stats.get("matches", 0)),
        metrics=metrics,
        pass_accuracy=(
            round(float(stats["pass_accuracy"]), 4)
            if stats.get("pass_accuracy") is not None
            else None
        ),
        clean_sheet_rate=(
            round(float(stats["clean_sheet_rate"]), 4)
            if stats.get("clean_sheet_rate") is not None
            else None
        ),
        failed_to_score_rate=(
            round(float(stats["failed_to_score_rate"]), 4)
            if stats.get("failed_to_score_rate") is not None
            else None
        ),
        expected_goals_per_match=(
            round(float(expected_goals), 3)
            if expected_goals is not None
            else None
        ),
        xg_overperformance=(
            round(float(xg_overperformance), 3)
            if xg_overperformance is not None
            else None
        ),
        splits=[
            _team_stats_split("Home", home_rows),
            _team_stats_split("Away", away_rows),
        ],
        trend=trend,
        provenance=ResearchProvenance(
            source=(
                "team_analysis_kernel + team_research_stats + governed "
                "expected-metric routing"
            ),
            transformation_version="team-stats-overview-kernel-v1",
        ),
        limitations=limitations,
    )
'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    if IMPORT_NEW not in text:
        if IMPORT_OLD not in text:
            raise SystemExit("Expected Team Stats import marker not found")
        text = text.replace(IMPORT_OLD, IMPORT_NEW, 1)

    start = text.find(START)
    if start < 0:
        raise SystemExit("Team Stats Overview endpoint start marker not found")

    end = text.find(END, start)
    if end < 0:
        raise SystemExit("Team Stats Overview endpoint end marker not found")

    current = text[start:end]
    if "team_analysis_kernel.team_overview_analysis" in current:
        print("Team Stats Overview already uses the analytical kernel.")
        return 0

    text = text[:start] + NEW_ENDPOINT + text[end:]
    TARGET.write_text(text, encoding="utf-8", newline="")
    print("Applied Team Stats Overview analytical-kernel patch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
