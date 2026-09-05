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

TEAM_PROMOTION_BATCH_V2_FIELDS = {
    "ballRecovery": "exposed",
    "successfulFinalThirdPasses": "exposed",
    "totalChippedPass": "exposed",
    "totalFinalThirdPasses": "exposed",
    "touches": "exposed",
    "unsuccessfulTouch": "exposed",
}

TEAM_PROMOTION_BATCH_V3_FIELDS = {
    "blockedPass": "exposed",
    "goalKicks": "exposed",
    "touchesInOppBox": "exposed",
}

TEAM_PROMOTION_BATCH_V4_FIELDS = {
    "accurateChippedPass": "exposed",
    "accurateCross": "exposed",
    "accurateFlickOn": "exposed",
    "accurateGoalKicks": "exposed",
    "accurateKeeperThrows": "exposed",
    "accurateLaunches": "exposed",
    "accurateLayoffs": "exposed",
    "accurateLongBalls": "exposed",
    "blockedCross": "exposed",
    "keeperThrows": "exposed",
    "lostCorners": "exposed",
    "totalFlickOn": "exposed",
    "totalLaunches": "exposed",
    "totalLayoffs": "exposed",
    "totalLongBalls": "exposed",
    "wonCorners": "exposed",
}

# Bulk exact-field semantic resolution. See V5 evidence/manifest.
TEAM_PROMOTION_BATCH_V5_FIELDS = {
    "accurateBackZonePass": "exposed",
    "accurateCornersIntobox": "exposed",
    "accurateFwdZonePass": "exposed",
    "accurateKeeperSweeper": "exposed",
    "accuratePullBack": "exposed",
    "accurateThroughBall": "exposed",
    "accurateThrows": "exposed",
    "attAssistOpenplay": "exposed",
    "attAssistSetplay": "exposed",
    "attemptsConcededIbox": "exposed",
    "attemptsConcededObox": "exposed",
    "bigChanceScored": "exposed",
    "challengeLost": "exposed",
    "crosses18yard": "exposed",
    "crosses18yardplus": "exposed",
    "divingSave": "exposed",
    "effectiveBlockedCross": "exposed",
    "effectiveHeadClearance": "exposed",
    "errorLeadToGoal": "exposed",
    "errorLeadToShot": "exposed",
    "finalThirdEntries": "exposed",
    "fouledFinalThird": "exposed",
    "freekickCross": "exposed",
    "hitWoodwork": "exposed",
    "interceptionsInBox": "exposed",
    "leftsidePass": "exposed",
    "outfielderBlock": "exposed",
    "overrun": "exposed",
    "passesLeft": "exposed",
    "passesRight": "exposed",
    "penAreaEntries": "exposed",
    "possLostAll": "exposed",
    "possWonAtt3rd": "exposed",
    "possWonDef3rd": "exposed",
    "possWonMid3rd": "exposed",
    "rightsidePass": "exposed",
    "savedIbox": "exposed",
    "savedObox": "exposed",
    "subsMade": "exposed",
    "totalBackZonePass": "exposed",
    "totalContest": "exposed",
    "totalCornersIntobox": "exposed",
    "totalFwdZonePass": "exposed",
    "totalHighClaim": "exposed",
    "totalKeeperSweeper": "exposed",
    "totalPullBack": "exposed",
    "totalThroughBall": "exposed",
    "totalThrows": "exposed",
    "wonContest": "exposed",
}

# Second bulk exact-field pass. See V6 evidence/manifest.
TEAM_PROMOTION_BATCH_V6_FIELDS = {
    "accurateFreekickCross": "exposed",
    "attCorner": "exposed",
    "attFastbreak": "exposed",
    "attFreekickGoal": "exposed",
    "attFreekickMiss": "exposed",
    "attFreekickTarget": "exposed",
    "attFreekickTotal": "exposed",
    "attObxdLeft": "exposed",
    "attObxdRight": "exposed",
    "attOneOnOne": "exposed",
    "attOpenplay": "exposed",
    "attPenGoal": "exposed",
    "attPenMiss": "exposed",
    "attPenPost": "exposed",
    "attPenTarget": "exposed",
    "attPostHigh": "exposed",
    "attPostLeft": "exposed",
    "attPostRight": "exposed",
    "attSetpiece": "exposed",
    "attemptedTackleFoul": "exposed",
    "clearanceOffLine": "exposed",
    "contentiousDecision": "exposed",
    "defenderGoals": "exposed",
    "dispossessed": "exposed",
    "forwardGoals": "exposed",
    "foulThrowIn": "exposed",
    "goalAssist": "exposed",
    "goalAssistDeadball": "exposed",
    "goalAssistIntentional": "exposed",
    "goalAssistOpenplay": "exposed",
    "goalAssistSetplay": "exposed",
    "goalFastbreak": "exposed",
    "goalsOpenplay": "exposed",
    "goodHighClaim": "exposed",
    "handBall": "exposed",
    "midfielderGoals": "exposed",
    "offtargetAttAssist": "exposed",
    "ontargetAttAssist": "exposed",
    "ownGoals": "exposed",
    "penGoalsConceded": "exposed",
    "penaltyConceded": "exposed",
    "penaltyFaced": "exposed",
    "penaltySave": "exposed",
    "penaltyWon": "exposed",
    "possLostCtrl": "exposed",
    "postScoringAtt": "exposed",
    "punches": "exposed",
    "rescindedRedCard": "exposed",
    "secondYellow": "exposed",
    "shieldBallOop": "exposed",
    "shotFastbreak": "exposed",
    "sixYardBlock": "exposed",
    "totalAttAssist": "exposed",
    "totalFastbreak": "exposed",
}

# Post-V6 residue resolution. These exact fields have direct legacy definitions
# or an existing governed FRL direct-field label. Blanks remain missing.
# See data/team_match_semantic_evidence_v7.json and
# data/team_match_semantic_promotion_batch_v7.json.
TEAM_PROMOTION_BATCH_V7_FIELDS = {
    "attFreekickPost": "exposed",
    "attIboxOwnGoal": "exposed",
    "attLgCentre": "exposed",
    "attLgLeft": "exposed",
    "attLgRight": "exposed",
    "attemptsIbox": "exposed",
    "attemptsObox": "exposed",
    "ptsDroppedWinningPos": "exposed",
    "ptsGainedLosingPos": "exposed",
    "winningGoal": "exposed",
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
        | TEAM_PROMOTION_BATCH_V3_FIELDS
        | TEAM_PROMOTION_BATCH_V4_FIELDS
        | TEAM_PROMOTION_BATCH_V5_FIELDS
        | TEAM_PROMOTION_BATCH_V6_FIELDS
        | TEAM_PROMOTION_BATCH_V7_FIELDS,
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
