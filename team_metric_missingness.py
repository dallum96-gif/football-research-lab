from __future__ import annotations


BLANK_IS_MISSING = "BLANK_IS_MISSING"
BLANK_IS_STRUCTURAL_ZERO = "BLANK_IS_STRUCTURAL_ZERO"

# PR #40 / the 30 August 2026 missingness audits established this rule only
# for the preserved direct team-match representation and only for the audited
# Premier League seasons below. Do not extend it to another field, source
# representation or season without separate evidence and governance.
AUDITED_DIRECT_TEAM_MATCH_SEASONS = frozenset(
    {
        "2016-17",
        "2017-18",
        "2018-19",
        "2019-20",
        "2020-21",
        "2021-22",
        "2022-23",
        "2023-24",
        "2024-25",
        "2025-26",
    }
)

AUDITED_SPARSE_ZERO_METRICS = frozenset(
    {
        "Shots",
        "Shots on target",
        "Shots off target",
        "Blocked shots",
    }
)


def team_match_missingness_semantics(season: str, metric: str) -> str:
    """Return the governed blank-value semantics for one team-match metric.

    The default remains fail-closed: a blank is missing. The structural-zero
    exception is deliberately narrow and is supported by the preserved-source
    audits for the shot family over the audited decade.
    """
    if (
        season in AUDITED_DIRECT_TEAM_MATCH_SEASONS
        and metric in AUDITED_SPARSE_ZERO_METRICS
    ):
        return BLANK_IS_STRUCTURAL_ZERO
    return BLANK_IS_MISSING


def normalise_team_match_observation(
    season: str,
    metric: str,
    value: float | int | None,
) -> tuple[float | int | None, bool]:
    """Apply governed missingness semantics without changing source parsing.

    Returns ``(value, structural_zero_applied)``. Explicit numeric zero remains
    an ordinary observed value; only a source blank governed as sparse zero is
    marked as a structural zero.
    """
    semantics = team_match_missingness_semantics(season, metric)
    if value is None and semantics == BLANK_IS_STRUCTURAL_ZERO:
        return 0.0, True
    return value, False
