"""Universal Player Profile service over governed FRL evidence.

The page composition is universal; comparative templates remain position-
specific. MID V1 is the first governed comparison template and uses a single
Player-Season source representation, including source-native playing time, for
all six per-90 axes.
"""
from __future__ import annotations

from statistics import fmean

import player_analysis_kernel
import player_profile_biography_projection
import player_profile_context
import player_profile_identity
import player_profile_radar
import player_profile_source_projection
import player_research


def _text(value: object) -> str:
    return str(value or "").strip()


def _empty_comparison(position: str, season: str, player_code: str, limitation: str, cohort=None) -> dict:
    return {
        "available": False,
        "complete": False,
        "observed_axis_count": 0,
        "required_axis_count": 6 if position == "MID" else 0,
        "position": position,
        "season": season,
        "player_code": player_code,
        "axes": [],
        "summary": "",
        "cohort": cohort,
        "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
        "denominator_representation": "Player-Season timePlayed",
        "limitations": [limitation],
    }


def _midfielder_comparison(season: str, player: dict, identity: dict) -> dict:
    route_code = _text(player.get("player_code"))
    if _text(player.get("position")) != "MID":
        return _empty_comparison(
            _text(player.get("position")),
            season,
            route_code,
            "Player Profile comparison V1 is governed only for MID players; other positional templates require separate research and governance.",
        )

    policy = player_profile_radar.profile_minimum_minutes(season)
    minimum_minutes = int(policy["minimum_minutes"])
    seed_source_id = _text(identity.get("portrait_player_code"))
    source_rows = player_profile_source_projection.season_rows(season)
    seed_source = source_rows.get(seed_source_id)

    cohort_base = {
        "competition": "Premier League",
        "season": season,
        "position": "MID",
        **policy,
        "description": (
            "Premier League MID players with verified profile identity and at least "
            f"{minimum_minutes} Player-Season source minutes ({policy['qualification_share']:.0%} of currently available league minutes)."
        ),
    }

    if seed_source is None:
        return _empty_comparison(
            "MID", season, route_code,
            "No packaged Player-Season profile evidence is attached to this verified player identity.",
            {**cohort_base, "population_size": 0},
        )

    source_minutes = seed_source.get("source_minutes")
    if source_minutes is None or float(source_minutes) < minimum_minutes:
        return _empty_comparison(
            "MID", season, route_code,
            f"Player has {int(float(source_minutes or 0))} Player-Season source minutes and does not meet the {minimum_minutes}-minute Profile threshold.",
            {**cohort_base, "population_size": 0},
        )

    population: list[dict] = []
    unresolved_identity = 0
    missing_source = 0
    for candidate in player_research.season_players(season):
        if _text(candidate.get("position")) != "MID":
            continue
        candidate_identity = player_profile_identity.resolve_player_identity(season, candidate)
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
        population.append({
            "identity_key": candidate_identity.get("player_identity_key"),
            "route_code": _text(candidate.get("player_code")),
            "source_player_id": source_id,
            "source": source,
        })

    axes: list[dict] = []
    for definition in player_profile_source_projection.PROFILE_METRICS:
        entries = []
        for candidate in population:
            entries.append({
                "identity_key": candidate["identity_key"],
                "value": player_profile_source_projection.per_90(
                    candidate["source"], definition["source_key"]
                ),
            })
        player_analysis_kernel.rank_metric_entries(entries, True)
        selected = next(
            (
                entry for entry in entries
                if entry.get("identity_key") == identity.get("player_identity_key")
            ),
            None,
        )
        observed_values = [float(entry["value"]) for entry in entries if entry.get("value") is not None]
        if selected is None or selected.get("value") is None or selected.get("percentile") is None:
            axes.append({
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
                "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
                "denominator": "timePlayed",
            })
            continue

        average_value = fmean(observed_values)
        average_percentile = player_profile_radar._percentile_for_value(
            average_value, observed_values, True
        )
        axes.append({
            "key": definition["key"],
            "label": definition["label"],
            "metric_label": definition["metric_label"],
            "value": float(selected["value"]),
            "unit": definition["unit"],
            "percentile": float(selected["percentile"]),
            "average_value": round(average_value, 4),
            "average_percentile": average_percentile,
            "rank": selected.get("rank"),
            "out_of": int(selected.get("out_of") or 0),
            "observed_players": len(observed_values),
            "eligible_players": len(population),
            "availability": "AVAILABLE" if len(observed_values) == len(population) else "PARTIAL",
            "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
            "denominator": "timePlayed",
        })

    observed_axis_count = sum(axis["availability"] != "UNAVAILABLE" for axis in axes)
    partial = [axis for axis in axes if axis["availability"] == "PARTIAL"]
    unavailable = [axis for axis in axes if axis["availability"] == "UNAVAILABLE"]
    limitations = [
        "All Profile V1 axes use source-native Player-Season totals divided by the same Player-Season timePlayed denominator.",
        "The comparison cohort uses verified Player Profile identity and the FPL MID position classification, but qualification minutes come from the Player-Season source representation.",
        "Defensive event output is not possession-adjusted in Profile V1.",
    ]
    if unresolved_identity:
        limitations.append(
            f"{unresolved_identity} MID player records could not enter the comparison because a reusable verified player identity was unresolved."
        )
    if missing_source:
        limitations.append(
            f"{missing_source} identity-resolved MID player records had no packaged Player-Season profile row."
        )
    limitations.extend(
        f"{axis['label']} compares {axis['observed_players']} observed players from {axis['eligible_players']} eligible players because source coverage is partial."
        for axis in partial
    )
    limitations.extend(
        f"{axis['label']} is unavailable for this player-season and is not plotted as zero."
        for axis in unavailable
    )

    summary_player = dict(player)
    summary_player["minutes"] = source_minutes

    return {
        "available": observed_axis_count > 0,
        "complete": observed_axis_count == len(player_profile_source_projection.PROFILE_METRICS),
        "observed_axis_count": observed_axis_count,
        "required_axis_count": len(player_profile_source_projection.PROFILE_METRICS),
        "position": "MID",
        "season": season,
        "player_code": route_code,
        "axes": axes,
        "summary": player_profile_radar._summary(summary_player, axes),
        "cohort": {
            **cohort_base,
            "population_size": len(population),
            "identity_unresolved_records": unresolved_identity,
            "profile_source_missing_records": missing_source,
        },
        "analysis_version": "player-profile-universal-foundation-v1",
        "ranking_policy": player_analysis_kernel.COMPETITION_RANK,
        "percentile_policy": player_analysis_kernel.RANK_POSITION_PERCENTILE,
        "source_representation": "PLAYER_PROFILE_SOURCE_STATS_V1",
        "denominator_representation": "Player-Season timePlayed",
        "limitations": limitations,
    }


def build_player_profile(season: str, player_code: str) -> dict | None:
    player = player_research.player_detail(season, player_code)
    if player is None:
        return None

    identity = player_profile_identity.resolve_player_identity(season, player)
    context = player_profile_context.resolve_club_context(player, season)
    portrait_code = _text(identity.get("portrait_player_code"))
    biography = player_profile_biography_projection.resolve_biography(
        season,
        portrait_code,
        _text(player.get("player_name")),
        context.get("primary_club"),
    )
    seasons = list(player_profile_identity.profile_seasons(season, player_code))
    if not seasons:
        seasons = [{
            "season": season,
            "player_code": _text(player.get("player_code")),
            "player_name": _text(player.get("player_name")),
            "position": _text(player.get("position")),
            "clubs": list(player.get("clubs") or ()),
            "identity_status": _text(identity.get("identity_status")),
        }]

    comparison = _midfielder_comparison(season, player, identity)

    return {
        "milestone": "PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1",
        "profile": {
            "season": season,
            "player_code": _text(player.get("player_code")),
            "player_name": _text(player.get("player_name")),
            "position": _text(player.get("position")),
            "competition": "Premier League",
            "appearances": int(player.get("appearances") or 0),
            "starts": int(float(player.get("starts") or 0)),
            "minutes": int(float(player.get("minutes") or 0)),
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
            "profile_source_metadata": player_profile_source_projection.metadata(),
        },
        "limitations": [
            *list(identity.get("limitations") or ()),
            *list(context.get("limitations") or ()),
            *list(biography.get("limitations") or ()),
        ],
    }


__all__ = ["build_player_profile"]
