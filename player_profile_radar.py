"""Position-aware comparative profile summary for Player Profile.

This is intentionally a small descriptive seam over the existing governed
player-analysis kernel. It does not create a second ranking universe.

The V1 template is MID-only. Other positional templates should be researched
and governed separately rather than mechanically reusing midfielder metrics.
"""
from __future__ import annotations

from collections import Counter
from math import ceil
from statistics import fmean

import player_analysis_kernel
import player_research
import query_lab


MIDFIELD_PROFILE_TEMPLATE = (
    ("xg_per_90", "Goal threat"),
    ("xa_per_90", "Chance creation"),
    (
        "accurate_opposition_half_passes_per_90",
        "Advanced passing",
    ),
    (
        "progressive_carries_per_90",
        "Carrying",
    ),
    (
        "recoveries_per_90",
        "Recoveries",
    ),
    (
        "tackles_won_per_90",
        "Ball winning",
    ),
)




PROFILE_MINUTE_SHARE = 0.33


def profile_minimum_minutes(season: str) -> dict:
    """33% of the maximum league minutes available so far."""
    rows, _columns = query_lab.load_csv(
        query_lab.FIXTURE_FILE
    )

    matches_by_team: Counter[str] = Counter()

    for row in rows:
        if str(row.get("season") or "") != season:
            continue

        home_score = str(
            row.get("home_score") or ""
        ).strip()

        away_score = str(
            row.get("away_score") or ""
        ).strip()

        if home_score == "" or away_score == "":
            continue

        matches_by_team[
            str(row.get("home_team_id") or "")
        ] += 1

        matches_by_team[
            str(row.get("away_team_id") or "")
        ] += 1

    maximum_matches = (
        max(matches_by_team.values())
        if matches_by_team
        else 0
    )

    possible_minutes = maximum_matches * 90

    minimum_minutes = (
        max(
            1,
            ceil(
                possible_minutes
                * PROFILE_MINUTE_SHARE
            ),
        )
        if possible_minutes
        else 1
    )

    return {
        "maximum_matches_played":
            maximum_matches,
        "possible_minutes":
            possible_minutes,
        "qualification_share":
            PROFILE_MINUTE_SHARE,
        "minimum_minutes":
            minimum_minutes,
    }


def _qualified_population(
    season: str,
    position: str,
    minimum_minutes: int,
) -> list[dict]:
    return [
        player
        for player
        in player_research.season_players(season)
        if (
            str(player.get("position") or "")
            == position
            and float(
                player.get("minutes") or 0
            )
            >= minimum_minutes
        )
    ]


def _percentile_for_value(
    value: float,
    population_values: list[float],
    higher_is_better: bool,
) -> float:
    total = len(population_values)

    if total <= 1:
        return 100.0 if total == 1 else 0.0

    better = sum(
        1
        for candidate in population_values
        if (
            candidate > value
            if higher_is_better
            else candidate < value
        )
    )

    rank = better + 1

    return round(
        100.0
        * (total - rank)
        / (total - 1),
        1,
    )


def _summary(
    player: dict,
    axes: list[dict],
) -> str:
    minutes = int(float(player.get("minutes") or 0))

    observed_axes = [
        axis
        for axis in axes
        if (
            axis.get("percentile") is not None
            and axis.get("average_percentile") is not None
        )
    ]

    if not observed_axes:
        return ""

    ranked = sorted(
        observed_axes,
        key=lambda axis: (
            float(axis["percentile"])
            - float(axis["average_percentile"])
        ),
        reverse=True,
    )

    clearly_above = [
        axis
        for axis in ranked
        if (
            float(axis["percentile"])
            - float(axis["average_percentile"])
        ) >= 10.0
    ]

    if len(clearly_above) >= 2:
        first = clearly_above[0]["label"].lower()
        second = clearly_above[1]["label"].lower()

        return (
            f"Through {minutes} Premier League minutes, "
            "his early-season profile sits furthest above "
            "the qualified midfielder average for "
            f"{first} and {second}."
        )

    if len(clearly_above) == 1:
        first = clearly_above[0]["label"].lower()

        return (
            f"Through {minutes} Premier League minutes, "
            "his clearest above-average marker in the "
            f"current midfielder cohort is {first}."
        )

    return (
        f"Through {minutes} Premier League minutes, "
        "his observed profile sits broadly around "
        "the qualified midfielder average."
    )


def build_player_profile_radar(
    season: str,
    player_code: str,
) -> dict | None:
    player = player_research.player_detail(
        season,
        player_code,
    )

    if player is None:
        return None

    position = str(
        player.get("position") or ""
    )

    if position != "MID":
        return {
            "available": False,
            "position": position,
            "season": season,
            "player_code": str(player_code),
            "axes": [],
            "summary": "",
            "cohort": None,
            "limitations": [
                "Player Profile radar V1 is governed only for MID players."
            ],
        }

    policy = profile_minimum_minutes(
        season
    )

    minimum_minutes = int(
        policy["minimum_minutes"]
    )

    player_minutes = float(
        player.get("minutes") or 0
    )

    if player_minutes < minimum_minutes:
        return {
            "available": False,
            "position": position,
            "season": season,
            "player_code": str(player_code),
            "axes": [],
            "summary": "",
            "cohort": {
                "competition":
                    "Premier League",
                "season": season,
                "position": position,
                **policy,
                "population_size": 0,
                "description": (
                    "Premier League MID players "
                    f"with at least {minimum_minutes} "
                    "recorded minutes."
                ),
            },
            "limitations": [
                (
                    f"Player has {int(player_minutes)} "
                    "minutes and does not meet the "
                    f"{minimum_minutes}-minute Profile "
                    "comparison threshold."
                )
            ],
        }

    population = _qualified_population(
        season,
        position,
        minimum_minutes,
    )

    axes: list[dict] = []

    for key, display_label in (
        MIDFIELD_PROFILE_TEMPLATE
    ):
        definition = (
            player_analysis_kernel
            .DEFINITIONS_BY_KEY[key]
        )

        entries: list[dict] = []

        for candidate in population:
            value = (
                player_analysis_kernel
                .metric_value(
                    candidate,
                    definition,
                )
            )

            entries.append(
                {
                    "player_code": str(
                        candidate.get(
                            "player_code"
                        )
                        or ""
                    ),
                    "value": value,
                }
            )

        player_analysis_kernel.rank_metric_entries(
            entries,
            definition.higher_is_better,
        )

        selected = next(
            (
                entry
                for entry in entries
                if entry["player_code"]
                == str(player_code)
            ),
            None,
        )

        observed_values = [
            float(entry["value"])
            for entry in entries
            if entry.get("value") is not None
        ]

        if (
            selected is None
            or selected.get("value") is None
            or selected.get("percentile") is None
            or not observed_values
        ):
            axes.append(
                {
                    "key": key,
                    "label": display_label,
                    "metric_label":
                        definition.label,
                    "value": None,
                    "unit": definition.unit,
                    "percentile": None,
                    "average_value": None,
                    "average_percentile": None,
                    "rank": None,
                    "out_of": len(observed_values),
                    "observed_players":
                        len(observed_values),
                    "eligible_players":
                        len(population),
                    "availability": "UNAVAILABLE",
                }
            )
            continue

        average_value = fmean(
            observed_values
        )

        average_percentile = (
            _percentile_for_value(
                average_value,
                observed_values,
                definition.higher_is_better,
            )
        )

        axes.append(
            {
                "key": key,
                "label": display_label,
                "metric_label":
                    definition.label,
                "value": float(
                    selected["value"]
                ),
                "unit": definition.unit,
                "percentile": float(
                    selected["percentile"]
                ),
                "average_value":
                    round(
                        average_value,
                        4,
                    ),
                "average_percentile":
                    average_percentile,
                "rank":
                    selected.get("rank"),
                "out_of": int(
                    selected.get(
                        "out_of"
                    )
                    or 0
                ),
                "observed_players":
                    len(observed_values),
                "eligible_players":
                    len(population),
                "availability": (
                    "AVAILABLE"
                    if len(observed_values)
                    == len(population)
                    else "PARTIAL"
                ),
            }
        )

    observed_axis_count = sum(
        axis["availability"] != "UNAVAILABLE"
        for axis in axes
    )

    complete = (
        observed_axis_count
        == len(MIDFIELD_PROFILE_TEMPLATE)
    )

    partial_axes = [
        axis
        for axis in axes
        if axis["availability"] == "PARTIAL"
    ]

    unavailable_axes = [
        axis
        for axis in axes
        if axis["availability"] == "UNAVAILABLE"
    ]

    coverage_limitations = [
        (
            f"{axis['label']} compares {axis['observed_players']} "
            f"observed players from {axis['eligible_players']} eligible "
            "players because source coverage is partial."
        )
        for axis in partial_axes
    ] + [
        (
            f"{axis['label']} is unavailable for this player-season and "
            "is not plotted as zero."
        )
        for axis in unavailable_axes
    ]

    return {
        "available": observed_axis_count > 0,
        "complete": complete,
        "observed_axis_count": observed_axis_count,
        "required_axis_count": len(MIDFIELD_PROFILE_TEMPLATE),
        "position": position,
        "season": season,
        "player_code": str(player_code),
        "axes": axes,
        "summary": _summary(player, axes),
        "cohort": {
            "competition":
                "Premier League",
            "season": season,
            "position": position,
            **policy,
            "population_size":
                len(population),
            "description": (
                "Premier League MID players "
                f"with at least {minimum_minutes} "
                "recorded minutes "
                f"({PROFILE_MINUTE_SHARE:.0%} "
                "of currently available league minutes)."
            ),
        },
        "analysis_version":
            player_analysis_kernel
            .ANALYSIS_VERSION,
        "ranking_policy":
            player_analysis_kernel
            .COMPETITION_RANK,
        "percentile_policy":
            player_analysis_kernel
            .RANK_POSITION_PERCENTILE,
        "limitations": [
            (
                "All six dimensions use per-90 "
                "output within the qualified "
                "same-position cohort."
            ),
            (
                "Profile comparison eligibility "
                f"requires at least "
                f"{PROFILE_MINUTE_SHARE:.0%} "
                "of currently available league minutes."
            ),
            (
                "The average overlay represents "
                "the qualified cohort mean raw output "
                "for each metric, mapped onto the "
                "same percentile scale."
            ),
            (
                "Defensive event output is not "
                "possession-adjusted in Profile V1."
            ),
            *coverage_limitations,
        ],
    }

__all__ = [
    "MIDFIELD_PROFILE_TEMPLATE",
    "build_player_profile_radar",
]
