from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


DIRECT_TEAM_MATCH = "DIRECT_TEAM_MATCH"
PLAYER_MATCH_DERIVED_TEAM_MATCH = "PLAYER_MATCH_DERIVED_TEAM_MATCH"
NO_GOVERNED_SEASON_ROUTE = "NO_GOVERNED_SEASON_ROUTE"

SINGLE_SEASON_DESCRIPTIVE = "SINGLE_SEASON_DESCRIPTIVE"
CROSS_SEASON_COMPARISON = "CROSS_SEASON_COMPARISON"

COMPLETE = "COMPLETE"
NEAR_COMPLETE = "NEAR_COMPLETE"
PARTIAL = "PARTIAL"
COVERAGE_GAP = "COVERAGE_GAP"

EXPECTED_GOALS = "Expected goals"
EXPECTED_ASSISTS = "Expected assists"
EXPECTED_GOALS_ON_TARGET = "Expected goals on target"

EXPECTED_METRICS = (
    EXPECTED_GOALS,
    EXPECTED_ASSISTS,
    EXPECTED_GOALS_ON_TARGET,
)

AUDITED_SEASONS = tuple(
    f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2026)
)
PLAYER_EXPECTED_METRIC_SEASONS = (
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
)

# Fixture counts below are the governed evidence checkpoint produced by the
# preserved-source audits merged on 30 August 2026. They describe availability
# of each representation; they do not assert that the representations are
# numerically identical or silently interchangeable.
REPRESENTATION_FIXTURE_COVERAGE = {
    EXPECTED_GOALS: {
        "2016-17": {DIRECT_TEAM_MATCH: 0, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2017-18": {DIRECT_TEAM_MATCH: 0, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2018-19": {DIRECT_TEAM_MATCH: 1, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2019-20": {DIRECT_TEAM_MATCH: 3, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2020-21": {DIRECT_TEAM_MATCH: 5, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2021-22": {DIRECT_TEAM_MATCH: 3, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2022-23": {DIRECT_TEAM_MATCH: 2, PLAYER_MATCH_DERIVED_TEAM_MATCH: 380},
        "2023-24": {DIRECT_TEAM_MATCH: 2, PLAYER_MATCH_DERIVED_TEAM_MATCH: 379},
        "2024-25": {DIRECT_TEAM_MATCH: 170, PLAYER_MATCH_DERIVED_TEAM_MATCH: 380},
        "2025-26": {DIRECT_TEAM_MATCH: 380, PLAYER_MATCH_DERIVED_TEAM_MATCH: 380},
    },
    EXPECTED_ASSISTS: {
        "2016-17": {DIRECT_TEAM_MATCH: 0, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2017-18": {DIRECT_TEAM_MATCH: 0, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2018-19": {DIRECT_TEAM_MATCH: 1, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2019-20": {DIRECT_TEAM_MATCH: 3, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2020-21": {DIRECT_TEAM_MATCH: 5, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2021-22": {DIRECT_TEAM_MATCH: 3, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2022-23": {DIRECT_TEAM_MATCH: 2, PLAYER_MATCH_DERIVED_TEAM_MATCH: 380},
        "2023-24": {DIRECT_TEAM_MATCH: 2, PLAYER_MATCH_DERIVED_TEAM_MATCH: 380},
        "2024-25": {DIRECT_TEAM_MATCH: 170, PLAYER_MATCH_DERIVED_TEAM_MATCH: 380},
        "2025-26": {DIRECT_TEAM_MATCH: 380, PLAYER_MATCH_DERIVED_TEAM_MATCH: 380},
    },
    EXPECTED_GOALS_ON_TARGET: {
        "2016-17": {DIRECT_TEAM_MATCH: 0, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2017-18": {DIRECT_TEAM_MATCH: 0, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2018-19": {DIRECT_TEAM_MATCH: 1, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2019-20": {DIRECT_TEAM_MATCH: 3, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2020-21": {DIRECT_TEAM_MATCH: 5, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2021-22": {DIRECT_TEAM_MATCH: 2, PLAYER_MATCH_DERIVED_TEAM_MATCH: 0},
        "2022-23": {DIRECT_TEAM_MATCH: 1, PLAYER_MATCH_DERIVED_TEAM_MATCH: 374},
        "2023-24": {DIRECT_TEAM_MATCH: 2, PLAYER_MATCH_DERIVED_TEAM_MATCH: 336},
        "2024-25": {DIRECT_TEAM_MATCH: 169, PLAYER_MATCH_DERIVED_TEAM_MATCH: 334},
        "2025-26": {DIRECT_TEAM_MATCH: 379, PLAYER_MATCH_DERIVED_TEAM_MATCH: 321},
    },
}


@dataclass(frozen=True)
class ExpectedMetricRouteDecision:
    metric: str
    purpose: str
    seasons: tuple[str, ...]
    representation: str
    observed_fixtures: int
    eligible_fixtures: int
    coverage_status: str
    representation_mixing_allowed: bool
    provenance_required: bool
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def _validate_metric(metric: str) -> None:
    if metric not in EXPECTED_METRICS:
        raise ValueError(f"Unsupported expected metric: {metric}")


def _validate_season(season: str) -> None:
    if season not in AUDITED_SEASONS:
        raise ValueError(
            f"Expected-metric routing is not governed for season {season}"
        )


def _coverage_status(observed: int, eligible: int) -> str:
    if observed <= 0:
        return COVERAGE_GAP
    if observed == eligible:
        return COMPLETE
    if observed / eligible >= 0.95:
        return NEAR_COMPLETE
    return PARTIAL


def single_season_route(metric: str, season: str) -> ExpectedMetricRouteDecision:
    """Return the governed preferred representation for one season.

    Sparse pre-2022 direct observations remain preserved evidence, but they are
    not promoted into a season-level analytical route because they cannot
    support a legitimate league/team-season population.
    """
    _validate_metric(metric)
    _validate_season(season)
    eligible = 380
    coverage = REPRESENTATION_FIXTURE_COVERAGE[metric][season]

    if season not in PLAYER_EXPECTED_METRIC_SEASONS:
        return ExpectedMetricRouteDecision(
            metric=metric,
            purpose=SINGLE_SEASON_DESCRIPTIVE,
            seasons=(season,),
            representation=NO_GOVERNED_SEASON_ROUTE,
            observed_fixtures=max(coverage.values()),
            eligible_fixtures=eligible,
            coverage_status=COVERAGE_GAP,
            representation_mixing_allowed=False,
            provenance_required=True,
            note=(
                "Preserve isolated direct observations as evidence, but do not "
                "present them as a season-level expected-metric population."
            ),
        )

    # A complete source-native direct team-match representation is preferred
    # for a single-season descriptive view. Otherwise use the governed
    # player-match-derived representation when it materially improves coverage.
    direct = coverage[DIRECT_TEAM_MATCH]
    player = coverage[PLAYER_MATCH_DERIVED_TEAM_MATCH]
    if direct == eligible:
        representation = DIRECT_TEAM_MATCH
        observed = direct
        note = (
            "Complete source-native team-match representation preferred for "
            "single-season descriptive analysis; keep player-derived evidence "
            "distinct for cross-season consistency or corroboration."
        )
    elif player > direct:
        representation = PLAYER_MATCH_DERIVED_TEAM_MATCH
        observed = player
        note = (
            "Player-match-derived team representation provides the strongest "
            "governed season coverage. Do not fill its residual gaps from the "
            "direct representation."
        )
    else:
        representation = DIRECT_TEAM_MATCH
        observed = direct
        note = (
            "Direct team-match representation provides the strongest governed "
            "season coverage. Do not fill residual gaps from another representation."
        )

    return ExpectedMetricRouteDecision(
        metric=metric,
        purpose=SINGLE_SEASON_DESCRIPTIVE,
        seasons=(season,),
        representation=representation,
        observed_fixtures=observed,
        eligible_fixtures=eligible,
        coverage_status=_coverage_status(observed, eligible),
        representation_mixing_allowed=False,
        provenance_required=True,
        note=note,
    )


def cross_season_route(
    metric: str,
    seasons: Iterable[str],
) -> ExpectedMetricRouteDecision:
    """Return one consistent representation for a cross-season comparison.

    Cross-season analysis must not switch representation season by season merely
    to maximise fill-rate. For the audited 2022-23..2025-26 window, the
    player-match-derived representation is the only governed consistent route.
    """
    _validate_metric(metric)
    ordered = tuple(dict.fromkeys(seasons))
    if not ordered:
        raise ValueError("At least one season is required")
    for season in ordered:
        _validate_season(season)

    eligible = 380 * len(ordered)
    if any(season not in PLAYER_EXPECTED_METRIC_SEASONS for season in ordered):
        observed = sum(
            REPRESENTATION_FIXTURE_COVERAGE[metric][season][
                PLAYER_MATCH_DERIVED_TEAM_MATCH
            ]
            for season in ordered
        )
        return ExpectedMetricRouteDecision(
            metric=metric,
            purpose=CROSS_SEASON_COMPARISON,
            seasons=ordered,
            representation=NO_GOVERNED_SEASON_ROUTE,
            observed_fixtures=observed,
            eligible_fixtures=eligible,
            coverage_status=COVERAGE_GAP,
            representation_mixing_allowed=False,
            provenance_required=True,
            note=(
                "No single governed expected-metric representation spans the "
                "requested pre-2022 and post-2022 seasons. Do not manufacture a "
                "continuous series by mixing sparse direct and player-derived values."
            ),
        )

    observed = sum(
        REPRESENTATION_FIXTURE_COVERAGE[metric][season][
            PLAYER_MATCH_DERIVED_TEAM_MATCH
        ]
        for season in ordered
    )
    status = _coverage_status(observed, eligible)
    note = (
        "Use one player-match-derived representation consistently across the "
        "requested seasons. Direct team-match values may corroborate the route "
        "but must not be substituted into missing player-derived fixtures."
    )
    if metric == EXPECTED_GOALS_ON_TARGET and status != COMPLETE:
        note += (
            " xGOT remains materially partial; analyses must expose that coverage "
            "rather than treating the requested period as complete."
        )

    return ExpectedMetricRouteDecision(
        metric=metric,
        purpose=CROSS_SEASON_COMPARISON,
        seasons=ordered,
        representation=PLAYER_MATCH_DERIVED_TEAM_MATCH,
        observed_fixtures=observed,
        eligible_fixtures=eligible,
        coverage_status=status,
        representation_mixing_allowed=False,
        provenance_required=True,
        note=note,
    )


__all__ = [
    "AUDITED_SEASONS",
    "COMPLETE",
    "COVERAGE_GAP",
    "CROSS_SEASON_COMPARISON",
    "DIRECT_TEAM_MATCH",
    "EXPECTED_ASSISTS",
    "EXPECTED_GOALS",
    "EXPECTED_GOALS_ON_TARGET",
    "EXPECTED_METRICS",
    "ExpectedMetricRouteDecision",
    "NEAR_COMPLETE",
    "NO_GOVERNED_SEASON_ROUTE",
    "PARTIAL",
    "PLAYER_MATCH_DERIVED_TEAM_MATCH",
    "REPRESENTATION_FIXTURE_COVERAGE",
    "SINGLE_SEASON_DESCRIPTIVE",
    "cross_season_route",
    "single_season_route",
]
