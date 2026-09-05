"""Machine-readable catalogue for the broad FRL source field universe.

This registry describes source-native fields without implying that every field
is canonical, derived, model-eligible, or UI-visible.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceFieldSpec:
    family: str
    source_field: str
    semantic_status: str = "retained"
    frl_field: str | None = None
    notes: str = ""


# Status vocabulary is deliberately small and conservative:
# retained   = preserve source value for future research
# exposed    = safe reusable FRL access exists
# derived    = FRL value should be calculated rather than copied
# restricted = requires additional semantic/licensing/identity review
# unknown    = discovered but not yet semantically assessed

COMMON_TEAM_FIELDS = {
    "matchId": "exposed",
    "gameweek": "exposed",
    "kickoff": "exposed",
    "team_id": "exposed",
    "team": "exposed",
    "venue": "exposed",
    "opponent": "exposed",
    "opponent_id": "exposed",
    "ground": "retained",
    "attendance": "retained",
    "halfTimeFor": "retained",
    "halfTimeAgainst": "retained",
    "goalsFor": "retained",
    "goalsAgainst": "retained",
    "result": "retained",
}

TEAM_CURATED_FIELDS = {
    "possessionPercentage": "exposed",
    "totalScoringAtt": "exposed",
    "ontargetScoringAtt": "exposed",
    "shotOffTarget": "exposed",
    "blockedScoringAtt": "exposed",
    "cornerTaken": "exposed",
    "totalPass": "exposed",
    "accuratePass": "exposed",
    "totalCross": "exposed",
    "totalTackle": "exposed",
    "wonTackle": "exposed",
    "interception": "exposed",
    "interceptionWon": "exposed",
    "totalClearance": "exposed",
    "effectiveClearance": "exposed",
    "fkFoulWon": "exposed",
    "fkFoulLost": "exposed",
    "totalOffside": "exposed",
    "totalYelCard": "exposed",
    "totalRedCard": "exposed",
    "saves": "exposed",
    "bigChanceCreated": "exposed",
    "bigChanceMissed": "exposed",
    "expectedGoals": "exposed",
    "expectedAssists": "exposed",
    "expectedGoalsOnTarget": "exposed",
}

# First controlled expansion from the September 2026 PulseLive capability
# industrialisation programme. These fields are decade-wide in the approved
# packaged team-match representation and were promoted only after combining:
# source-name clarity, external football-definition support where available,
# and empirical invariant checks for paired/subset relationships.
#
# See data/team_match_semantic_evidence_v1.json and
# data/audits/team_match_candidate_invariants/ for the review evidence.
# Deliberately excluded from this batch are ambiguous concepts such as
# totalContest/wonContest, challengeLost, effectiveHeadClearance and the
# cryptic shot-location/goal-mouth qualifier families.
TEAM_PROMOTION_BATCH_V1_FIELDS = {
    "accurateCrossNocorner": "exposed",
    "aerialLost": "exposed",
    "aerialWon": "exposed",
    "backwardPass": "exposed",
    "duelLost": "exposed",
    "duelWon": "exposed",
    "fwdPass": "exposed",
    "headClearance": "exposed",
    "longPassOwnToOpp": "exposed",
    "longPassOwnToOppSuccess": "exposed",
    "openPlayPass": "exposed",
    "successfulOpenPlayPass": "exposed",
    "totalCrossNocorner": "exposed",
}

# Second controlled expansion. These fields were promoted only after the V2
# evidence audit established complete decade-wide numeric observation (7,600
# team-match rows), non-negative values, direct Opta concept support, and
# zero-violation subset checks where a parent/child relationship was asserted.
#
# finalThirdEntries/penAreaEntries remain held because the V2 audit falsified
# the proposed nested-count relationship (35 violations), even though each
# source field may later prove independently usable.
#
# See data/team_match_semantic_evidence_v2.json and
# data/team_match_semantic_promotion_batch_v2.json.
TEAM_PROMOTION_BATCH_V2_FIELDS = {
    "ballRecovery": "exposed",
    "successfulFinalThirdPasses": "exposed",
    "totalChippedPass": "exposed",
    "totalFinalThirdPasses": "exposed",
    "touches": "exposed",
    "unsuccessfulTouch": "exposed",
}

# Third controlled expansion. These fields have sufficiently clear source
# semantics for reusable source-native research access, but the sparse-zero
# audit did NOT establish that their occasional source blanks encode zero.
# Therefore exposure deliberately preserves those blanks as missing under the
# standing team-match missingness contract. This is a coverage-aware exposure,
# not a structural-zero promotion.
#
# lostCorners remains excluded: the corrected opponent-route audit found 145
# disagreements in 7,438 observed comparisons and no independent blank-zero
# corroboration.
#
# See scripts/audit_team_match_sparse_zero_candidates.py and
# data/team_match_semantic_promotion_batch_v3.json.
TEAM_PROMOTION_BATCH_V3_FIELDS = {
    "blockedPass": "exposed",
    "goalKicks": "exposed",
    "touchesInOppBox": "exposed",
}

COMMON_PLAYER_MATCH_FIELDS = {
    "matchId": "exposed",
    "gameweek": "exposed",
    "team_id": "exposed",
    "team": "exposed",
    "venue": "exposed",
    "playerId": "exposed",
    "pl_code": "exposed",
    "playerName": "retained",
    "position": "retained",
    "substitute": "retained",
    "minutesPlayed": "exposed",
    "rating": "exposed",
    "goals": "exposed",
    "goalAssist": "exposed",
    "ownGoals": "exposed",
    "expectedGoals": "exposed",
    "expectedAssists": "exposed",
    "expectedGoalsOnTarget": "exposed",
}

PLAYER_MATCH_CURATED_FIELDS = {
    "totalPass": "exposed",
    "accuratePass": "exposed",
    "accurateOwnHalfPasses": "exposed",
    "accurateOppositionHalfPasses": "exposed",
    "totalLongBalls": "exposed",
    "accurateLongBalls": "exposed",
    "keyPass": "exposed",
    "bigChanceCreated": "exposed",
    "successfulDribbles": "exposed",
    "unsuccessfulDribbles": "exposed",
    "ballCarriesCount": "exposed",
    "progressiveBallCarriesCount": "exposed",
    "totalProgressiveBallCarriesDistance": "exposed",
    "totalProgression": "exposed",
    "touches": "exposed",
    "wonContest": "exposed",
    "wonTackle": "exposed",
    "duelWon": "exposed",
    "duelLost": "exposed",
    "aerialWon": "exposed",
    "aerialLost": "exposed",
}

PLAYER_SEASON_FIELDS = {
    "playerId": "exposed",
    "playerName": "retained",
    "position": "retained",
    "team_name": "retained",
    "team_id": "exposed",
    "season": "exposed",
    "gamesPlayed": "exposed",
    "starts": "exposed",
    "appearances": "exposed",
    "timePlayed": "exposed",
    "goals": "exposed",
    "goalAssists": "exposed",
    "expectedGoals": "exposed",
    "expectedAssists": "exposed",
    "successfulDribbles": "exposed",
    "interceptions": "exposed",
    "tacklesWon": "exposed",
    "touches": "exposed",
    # Conservative first promotion batch: decade-wide source-native fields
    # whose semantics are sufficiently explicit for reusable FRL access.
    "aerialDuels": "exposed",
    "aerialDuelsLost": "exposed",
    "aerialDuelsWon": "exposed",
    "blockedShots": "exposed",
    "expectedGoalsFreekick": "exposed",
    "expectedGoalsOnTarget": "exposed",
    "expectedGoalsOnTargetConceded": "exposed",
    "shotsBlockedInBox": "exposed",
    "shotsBlockedOutsideBox": "exposed",
    "shotsOnTargetIncGoals": "exposed",
}

SQUAD_FIELDS = {
    "playerId": "exposed",
    "displayName": "retained",
    "firstName": "retained",
    "lastName": "retained",
    "shirtNumber": "retained",
    "position": "retained",
    "preferredFoot": "exposed",
    "nationality": "exposed",
    "isoCode": "exposed",
    "birthDate": "exposed",
    "birthCountry": "exposed",
    "age": "retained",
    "height_cm": "exposed",
    "weight_kg": "exposed",
    "joinDate": "exposed",
    "onLoan": "exposed",
}


def _build_family(family: str, fields: dict[str, str]) -> tuple[SourceFieldSpec, ...]:
    return tuple(
        SourceFieldSpec(family=family, source_field=field, semantic_status=status)
        for field, status in sorted(fields.items())
    )


SOURCE_FIELD_REGISTRY = (
    _build_family(
        "team_match",
        COMMON_TEAM_FIELDS
        | TEAM_CURATED_FIELDS
        | TEAM_PROMOTION_BATCH_V1_FIELDS
        | TEAM_PROMOTION_BATCH_V2_FIELDS
        | TEAM_PROMOTION_BATCH_V3_FIELDS,
    )
    + _build_family("player_match", COMMON_PLAYER_MATCH_FIELDS | PLAYER_MATCH_CURATED_FIELDS)
    + _build_family("player_season", PLAYER_SEASON_FIELDS)
    + _build_family("squad", SQUAD_FIELDS)
)


def fields_for_family(family: str) -> tuple[SourceFieldSpec, ...]:
    return tuple(spec for spec in SOURCE_FIELD_REGISTRY if spec.family == family)


def field_inventory() -> dict[str, tuple[str, ...]]:
    return {
        family: tuple(spec.source_field for spec in fields_for_family(family))
        for family in {spec.family for spec in SOURCE_FIELD_REGISTRY}
    }
