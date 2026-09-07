from __future__ import annotations

# Explicit provider-native meanings for the current PulseLive Team-Match residue.
# These definitions deliberately preserve the source concept rather than
# relabelling it into a different historical/canonical metric.
PULSELIVE_TEAM_STAT_MEANINGS = {
    "attBxCentre": "Scoring attempts recorded from the central area of the penalty box.",
    "attBxLeft": "Scoring attempts recorded from the left side of the penalty box.",
    "attBxRight": "Scoring attempts recorded from the right side of the penalty box.",
    "attCmissHigh": "Scoring attempts recorded as missing high through the centre.",
    "attCmissHighRight": "Scoring attempts recorded as missing high to the right.",
    "attCmissLeft": "Scoring attempts recorded as missing to the left.",
    "attCmissRight": "Scoring attempts recorded as missing to the right.",
    "attGoalLowCentre": "Goals recorded with a low-centre goalmouth placement.",
    "attGoalLowLeft": "Goals recorded with a low-left goalmouth placement.",
    "attGoalLowRight": "Goals recorded with a low-right goalmouth placement.",
    "attHdMiss": "Headed scoring attempts recorded as off target.",
    "attHdTarget": "Headed scoring attempts recorded as on target.",
    "attHdTotal": "Total headed scoring attempts recorded by the source.",
    "attIboxBlocked": "Scoring attempts from inside the penalty box recorded as blocked.",
    "attIboxGoal": "Goals scored from inside the penalty box.",
    "attIboxMiss": "Scoring attempts from inside the penalty box recorded as off target.",
    "attIboxTarget": "Scoring attempts from inside the penalty box recorded as on target.",
    "attLfGoal": "Goals scored with the left foot.",
    "attLfTarget": "Left-footed scoring attempts recorded as on target.",
    "attLfTotal": "Total left-footed scoring attempts recorded by the source.",
    "attMissHigh": "Scoring attempts recorded as missing high.",
    "attMissHighLeft": "Scoring attempts recorded as missing high to the left.",
    "attMissHighRight": "Scoring attempts recorded as missing high to the right.",
    "attMissLeft": "Scoring attempts recorded as missing to the left.",
    "attMissRight": "Scoring attempts recorded as missing to the right.",
    "attOboxBlocked": "Scoring attempts from outside the penalty box recorded as blocked.",
    "attOboxGoal": "Goals scored from outside the penalty box.",
    "attOboxMiss": "Scoring attempts from outside the penalty box recorded as off target.",
    "attOboxTarget": "Scoring attempts from outside the penalty box recorded as on target.",
    "attObxCentre": "Scoring attempts recorded from the central area outside the penalty box.",
    "attObxLeft": "Scoring attempts recorded from the left area outside the penalty box.",
    "attRfGoal": "Goals scored with the right foot.",
    "attRfTarget": "Right-footed scoring attempts recorded as on target.",
    "attRfTotal": "Total right-footed scoring attempts recorded by the source.",
    "attSvHighCentre": "On-target scoring attempts recorded as saved high in the centre of goal.",
    "attSvHighLeft": "On-target scoring attempts recorded as saved high to the left of goal.",
    "attSvHighRight": "On-target scoring attempts recorded as saved high to the right of goal.",
    "attSvLowCentre": "On-target scoring attempts recorded as saved low in the centre of goal.",
    "attSvLowLeft": "On-target scoring attempts recorded as saved low to the left of goal.",
    "attSvLowRight": "On-target scoring attempts recorded as saved low to the right of goal.",
    "cleanSheet": "Source clean-sheet value for the team in the fixture.",
    "goals": "Goals scored by the team in the fixture.",
    "goalsConceded": "Goals conceded by the team in the fixture.",
    "goalsConcededIbox": "Goals conceded from attempts inside the penalty box.",
}

PULSELIVE_TEAM_STAT_FIELDS = frozenset(PULSELIVE_TEAM_STAT_MEANINGS)

PULSELIVE_TEAM_CONTEXT_PATH_MEANINGS = {
    "resources.stats.payload[].stats.fastestPlayer": "Source-provided fastest-player reference for the team in the fixture; this is contextual evidence, not a scalar team-performance metric.",
    "resources.stats.payload[].stats.fastestPlayer.playerId": "Source player identifier attached to the fastest-player reference for the team in the fixture.",
    "resources.stats.payload[].side": "Source side label identifying which fixture team the Team-Match statistics belong to.",
}

__all__ = [
    "PULSELIVE_TEAM_CONTEXT_PATH_MEANINGS",
    "PULSELIVE_TEAM_STAT_FIELDS",
    "PULSELIVE_TEAM_STAT_MEANINGS",
]
