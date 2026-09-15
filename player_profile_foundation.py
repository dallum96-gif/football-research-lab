"""Universal Player Profile service over governed FRL evidence.

The page composition is universal and the comparative template is position-
specific. GKP, DEF, MID and FWD each use a six-axis profile built from the same
pinned Player-Season representation used for Profile participation.

Every current player may have a Profile, but comparative claims are governed by
sample state. Qualified players enter the benchmark population; provisional
players are compared against that qualified population without entering it; and
players without comparable Player-Season minutes remain explicitly
INSUFFICIENT_SAMPLE rather than receiving fabricated ranks or zeros.
"""
from __future__ import annotations

from functools import lru_cache
from statistics import fmean

import player_analysis_kernel
import player_profile_biography_projection
import player_profile_context
import player_profile_identity
import player_profile_radar
import player_profile_source_projection
import player_research


_POSITION_PLURAL = {
    "GKP": "goalkeepers",
    "DEF": "defenders",
    "MID": "midfielders",
    "FWD": "forwards",
}

_SAMPLE_QUALIFIED = "QUALIFIED"
_SAMPLE_PROVISIONAL = "PROVISIONAL"
_SAMPLE_INSUFFICIENT = "INSUFFICIENT_SAMPLE"


def _text(value: object) -> str:
    return str(value or "").strip()


def _sample_progress(sample_minutes: int, qualification_minutes: int) -> float:
    if qualification_minutes <= 0:
        return 0.0
    return round(min(1.0, max(0.0, sample_minutes / qualification_minutes)), 3)


def _empty_comparison(
    position: str,
    season: str,
    player_code: str,
    limitation: str,
    cohort=None,
    *,
    sample_minutes: int = 0,
    qualification_minutes: int = 0,
    sample_message: str | None = None,
) -> dict:
    definitions = player_profile_source_projection.profile_metrics_for_position(position)
    return {
        "available": False,
        "complete": False,
        "observed_axis_count": 0,
        "required_axis_count": len(definitions),
        "position": position,
        "season": season,
        "player_code": player_code,
        "axes": [],
        "summary": "",
        "cohort": cohort,
        "sample_status": _SAMPLE_INSUFFICIENT,
        "sample_minutes": sample_minutes,
        "qualification_minutes": qualification_minutes,
        "qualification_progress": _sample_progress(sample_minutes, qualification_minutes),
        "comparison_mode": "NONE",
        "formal_rank_available": False,
        "sample_message": sample_message or limitation,
        "analysis_version": "player-profile-universal-rollout-v1",
        "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
        "denominator_representation": "Player-Season source-native denominators",
        "template_key": f"{position}_PROFILE_V1" if definitions else None,
        "limitations": [limitation],
    }


def _summary(
    player: dict,
    axes: list[dict],
    position: str,
    sample_status: str,
    qualification_minutes: int,
) -> str:
    minutes = int(float(player.get("minutes") or 0))
    cohort = _POSITION_PLURAL.get(position, "same-position players")

    if sample_status == _SAMPLE_PROVISIONAL:
        return (
            f"Through {minutes} Premier League minutes, his statistical profile is provisional "
            f"against the qualified {cohort} benchmark. FRL's current qualification threshold "
            f"is {qualification_minutes} minutes, so formal ranks are withheld until he qualifies."
        )

    observed = [
        axis
        for axis in axes
        if axis.get("percentile") is not None
        and axis.get("average_percentile") is not None
    ]
    if not observed:
        return ""
    ranked = sorted(
        observed,
        key=lambda axis: float(axis["percentile"])
        - float(axis["average_percentile"]),
        reverse=True,
    )
    clearly_above = [
        axis
        for axis in ranked
        if float(axis["percentile"])
        - float(axis["average_percentile"])
        >= 10.0
    ]
    if len(clearly_above) >= 2:
        first = clearly_above[0]["label"].lower()
        second = clearly_above[1]["label"].lower()
        return (
            f"Through {minutes} Premier League minutes, his early-season profile sits "
            f"furthest above the qualified {cohort} average for {first} and {second}."
        )
    if len(clearly_above) == 1:
        first = clearly_above[0]["label"].lower()
        return (
            f"Through {minutes} Premier League minutes, his clearest above-average marker "
            f"in the current {cohort} cohort is {first}."
        )
    return (
        f"Through {minutes} Premier League minutes, his observed profile sits broadly "
        f"around the qualified {cohort} average."
    )


@lru_cache(maxsize=32)
def _qualified_population_snapshot(
    season: str,
    position: str,
    minimum_minutes: int,
) -> tuple[tuple[dict, ...], int, int]:
    """Build the benchmark once per season/position/threshold.

    Only players meeting the governed minute threshold can enter this population.
    This is deliberately separate from whether the player currently being viewed
    is qualified or provisional.
    """
    source_rows = player_profile_source_projection.season_rows(season)
    population: list[dict] = []
    unresolved_identity = 0
    missing_source = 0

    for candidate in player_research.season_players(season):
        if _text(candidate.get("position")).upper() != position:
            continue
        candidate_identity = player_profile_identity.resolve_player_identity(
            season, candidate
        )
        source_id = _text(candidate_identity.get("portrait_player_code"))
        if not source_id:
            unresolved_identity += 1
            continue
        source = source_rows.get(source_id)
        if source is None:
            missing_source += 1
            continue
        minutes = source.get("source_minutes")
        if minutes is None or float(minutes) < minimum_minutes:
            continue
        population.append(
            {
                "identity_key": candidate_identity.get("player_identity_key"),
                "route_code": _text(candidate.get("player_code")),
                "source_player_id": source_id,
                "source": source,
            }
        )

    return tuple(population), unresolved_identity, missing_source


def _position_comparison(season: str, player: dict, identity: dict) -> dict:
    route_code = _text(player.get("player_code"))
    position = _text(player.get("position")).upper()
    definitions = player_profile_source_projection.profile_metrics_for_position(position)
    if not definitions:
        return _empty_comparison(
            position,
            season,
            route_code,
            "No governed Player Profile comparison template exists for this position classification.",
        )

    policy = player_profile_radar.profile_minimum_minutes(season)
    minimum_minutes = int(policy["minimum_minutes"])
    seed_source_id = _text(identity.get("portrait_player_code"))
    source_rows = player_profile_source_projection.season_rows(season)
    seed_source = source_rows.get(seed_source_id)
    cohort_label = _POSITION_PLURAL.get(position, f"{position} players")

    cohort_base = {
        "competition": "Premier League",
        "season": season,
        "position": position,
        **policy,
        "description": (
            f"Premier League {position} players with verified profile identity and at least "
            f"{minimum_minutes} Player-Season source minutes "
            f"({policy['qualification_share']:.0%} of currently available league minutes)."
        ),
    }

    population_snapshot, unresolved_identity, missing_source = (
        _qualified_population_snapshot(season, position, minimum_minutes)
    )
    population = list(population_snapshot)
    cohort = {
        **cohort_base,
        "population_size": len(population),
        "identity_unresolved_records": unresolved_identity,
        "profile_source_missing_records": missing_source,
        "label": cohort_label,
    }

    if seed_source is None:
        return _empty_comparison(
            position,
            season,
            route_code,
            "No packaged Player-Season profile evidence is attached to this verified player identity.",
            cohort,
            qualification_minutes=minimum_minutes,
            sample_message=(
                "Statistical profile pending comparable Player-Season evidence. "
                f"The current qualification threshold is {minimum_minutes} minutes."
            ),
        )

    source_minutes = seed_source.get("source_minutes")
    sample_minutes = int(float(source_minutes or 0))
    if source_minutes is None or float(source_minutes) <= 0:
        return _empty_comparison(
            position,
            season,
            route_code,
            "Comparable Player-Season minutes are unavailable for this player-season.",
            cohort,
            sample_minutes=sample_minutes,
            qualification_minutes=minimum_minutes,
            sample_message=(
                "Statistical profile pending Premier League Player-Season minutes. "
                f"The current qualification threshold is {minimum_minutes} minutes."
            ),
        )

    qualified = float(source_minutes) >= minimum_minutes
    sample_status = _SAMPLE_QUALIFIED if qualified else _SAMPLE_PROVISIONAL
    comparison_mode = "RANKED" if qualified else "INDICATIVE"

    axes: list[dict] = []
    for definition in definitions:
        entries = [
            {
                "identity_key": candidate["identity_key"],
                "value": player_profile_source_projection.metric_value(
                    candidate["source"], definition
                ),
            }
            for candidate in population
        ]
        higher_is_better = bool(definition.get("higher_is_better", True))
        player_analysis_kernel.rank_metric_entries(entries, higher_is_better)
        observed_values = [
            float(entry["value"])
            for entry in entries
            if entry.get("value") is not None
        ]
        player_value = player_profile_source_projection.metric_value(
            seed_source, definition
        )
        selected = next(
            (
                entry
                for entry in entries
                if entry.get("identity_key") == identity.get("player_identity_key")
            ),
            None,
        )

        if player_value is None or not observed_values:
            axes.append(
                {
                    "key": definition["key"],
                    "label": definition["label"],
                    "metric_label": definition["metric_label"],
                    "value": None,
                    "unit": definition["unit"],
                    "percentile": None,
                    "average_value": None,
                    "average_percentile": None,
                    "rank": None,
                    "out_of": len(observed_values),
                    "observed_players": len(observed_values),
                    "eligible_players": len(population),
                    "availability": "UNAVAILABLE",
                    "comparison_status": comparison_mode,
                    "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
                    "denominator": definition["denominator"],
                }
            )
            continue

        if qualified:
            if selected is None or selected.get("percentile") is None:
                axes.append(
                    {
                        "key": definition["key"],
                        "label": definition["label"],
                        "metric_label": definition["metric_label"],
                        "value": None,
                        "unit": definition["unit"],
                        "percentile": None,
                        "average_value": None,
                        "average_percentile": None,
                        "rank": None,
                        "out_of": len(observed_values),
                        "observed_players": len(observed_values),
                        "eligible_players": len(population),
                        "availability": "UNAVAILABLE",
                        "comparison_status": comparison_mode,
                        "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
                        "denominator": definition["denominator"],
                    }
                )
                continue
            percentile = float(selected["percentile"])
            rank = selected.get("rank")
            out_of = int(selected.get("out_of") or 0)
        else:
            percentile = player_profile_radar._percentile_for_value(
                float(player_value), observed_values, higher_is_better
            )
            rank = None
            out_of = len(observed_values)

        average_value = fmean(observed_values)
        average_percentile = player_profile_radar._percentile_for_value(
            average_value, observed_values, higher_is_better
        )
        axes.append(
            {
                "key": definition["key"],
                "label": definition["label"],
                "metric_label": definition["metric_label"],
                "value": float(player_value),
                "unit": definition["unit"],
                "percentile": float(percentile),
                "average_value": round(average_value, 4),
                "average_percentile": average_percentile,
                "rank": rank,
                "out_of": out_of,
                "observed_players": len(observed_values),
                "eligible_players": len(population),
                "availability": (
                    "AVAILABLE"
                    if len(observed_values) == len(population)
                    else "PARTIAL"
                ),
                "comparison_status": comparison_mode,
                "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
                "denominator": definition["denominator"],
            }
        )

    observed_axis_count = sum(
        axis["availability"] != "UNAVAILABLE" for axis in axes
    )
    partial = [axis for axis in axes if axis["availability"] == "PARTIAL"]
    unavailable = [
        axis for axis in axes if axis["availability"] == "UNAVAILABLE"
    ]
    limitations = [
        "All Profile positional axes use fields from one pinned Player-Season source representation.",
        "Per-90 axes use that same row's timePlayed; ratio axes use only same-row source-native denominators.",
        (
            f"The comparison cohort uses verified Player Profile identity and the FPL {position} "
            "position classification, while qualification minutes come from the Player-Season "
            "source representation."
        ),
    ]
    if sample_status == _SAMPLE_PROVISIONAL:
        limitations.append(
            f"This player has {sample_minutes} comparable Player-Season minutes, below the "
            f"{minimum_minutes}-minute qualification threshold. The displayed percentiles are "
            "indicative placements against the qualified cohort; the player does not enter that "
            "cohort and formal ranks are withheld."
        )
    if position in {"DEF", "GKP"}:
        limitations.append(
            "Defensive and goalkeeper volume axes are descriptive profile measures and are not "
            "possession-, shot-volume- or team-context adjusted in V1."
        )
    if unresolved_identity:
        limitations.append(
            f"{unresolved_identity} {position} player records could not enter the comparison "
            "because a reusable verified player identity was unresolved."
        )
    if missing_source:
        limitations.append(
            f"{missing_source} identity-resolved {position} player records had no packaged "
            "Player-Season profile row."
        )
    limitations.extend(
        f"{axis['label']} compares {axis['observed_players']} observed players from "
        f"{axis['eligible_players']} eligible players because source coverage is partial."
        for axis in partial
    )
    limitations.extend(
        f"{axis['label']} is unavailable for this player-season and is not plotted as zero."
        for axis in unavailable
    )

    summary_player = dict(player)
    summary_player["minutes"] = source_minutes
    sample_message = (
        f"Qualified profile: {sample_minutes} Player-Season minutes meet the current "
        f"{minimum_minutes}-minute threshold."
        if qualified
        else (
            f"Provisional profile: {sample_minutes} Player-Season minutes are below the current "
            f"{minimum_minutes}-minute threshold. Percentiles are indicative against the "
            "qualified cohort and formal ranks are withheld."
        )
    )

    return {
        "available": observed_axis_count > 0,
        "complete": observed_axis_count == len(definitions),
        "observed_axis_count": observed_axis_count,
        "required_axis_count": len(definitions),
        "position": position,
        "season": season,
        "player_code": route_code,
        "axes": axes,
        "summary": _summary(
            summary_player,
            axes,
            position,
            sample_status,
            minimum_minutes,
        ),
        "cohort": cohort,
        "sample_status": sample_status,
        "sample_minutes": sample_minutes,
        "qualification_minutes": minimum_minutes,
        "qualification_progress": _sample_progress(
            sample_minutes, minimum_minutes
        ),
        "comparison_mode": comparison_mode,
        "formal_rank_available": qualified,
        "sample_message": sample_message,
        "analysis_version": "player-profile-universal-rollout-v1",
        "ranking_policy": (
            player_analysis_kernel.COMPETITION_RANK
            if qualified
            else "RANK_WITHHELD_PROVISIONAL_SAMPLE"
        ),
        "percentile_policy": (
            player_analysis_kernel.RANK_POSITION_PERCENTILE
            if qualified
            else "INDICATIVE_PERCENTILE_VS_QUALIFIED_COHORT"
        ),
        "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
        "denominator_representation": "Player-Season source-native denominators",
        "template_key": f"{position}_PROFILE_V1",
        "limitations": limitations,
    }


def build_player_profile(season: str, player_code: str) -> dict | None:
    player = player_research.player_detail(season, player_code)
    if player is None:
        return None
    identity = player_profile_identity.resolve_player_identity(season, player)
    context = player_profile_context.resolve_club_context(player, season)
    portrait_code = _text(identity.get("portrait_player_code"))
    source_row = player_profile_source_projection.season_rows(season).get(portrait_code)
    source_participation = player_profile_source_projection.complete_participation(source_row)
    if source_participation is not None:
        participation = source_participation
        participation_representation = "PLAYER_PROFILE_SOURCE_STATS_V1"
    else:
        participation = {
            "appearances": int(player.get("appearances") or 0),
            "starts": int(float(player.get("starts") or 0)),
            "minutes": int(float(player.get("minutes") or 0)),
        }
        participation_representation = "FPL_PLAYER_FIXTURE_AGGREGATE_FALLBACK"
    biography = player_profile_biography_projection.resolve_biography(
        season,
        portrait_code,
        _text(player.get("player_name")),
        context.get("primary_club"),
    )
    seasons = list(player_profile_identity.profile_seasons(season, player_code))
    if not seasons:
        seasons = [
            {
                "season": season,
                "player_code": _text(player.get("player_code")),
                "player_name": _text(player.get("player_name")),
                "position": _text(player.get("position")),
                "clubs": list(player.get("clubs") or ()),
                "identity_status": _text(identity.get("identity_status")),
            }
        ]
    comparison = _position_comparison(season, player, identity)
    return {
        "milestone": "PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1",
        "profile": {
            "season": season,
            "player_code": _text(player.get("player_code")),
            "player_name": _text(player.get("player_name")),
            "position": _text(player.get("position")),
            "competition": "Premier League",
            **participation,
            "participation_representation": participation_representation,
            "clubs": list(context.get("clubs") or ()),
            "primary_club": context.get("primary_club"),
            "club_context_status": context.get("status"),
            "portrait_player_code": identity.get("portrait_player_code"),
            "player_identity_key": identity.get("player_identity_key"),
            "identity_status": identity.get("identity_status"),
            "biography": biography,
        },
        "seasons": seasons,
        "comparison": comparison,
        "evidence": {
            "identity": identity,
            "club_context": context,
            "player_source": dict(player.get("_evidence") or {}),
            "profile_source_player_id": portrait_code or None,
            "profile_source_participation": source_participation,
            "profile_source_metadata": player_profile_source_projection.metadata(),
        },
        "limitations": [
            *list(identity.get("limitations") or ()),
            *list(context.get("limitations") or ()),
            *list(biography.get("limitations") or ()),
            *(
                [
                    "Player Profile participation falls back to the governed FPL player-fixture aggregate because complete Player-Season participation fields are unavailable for this player-season."
                ]
                if source_participation is None
                else []
            ),
        ],
    }


__all__ = ["build_player_profile"]