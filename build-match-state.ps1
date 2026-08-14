$ErrorActionPreference = "Stop"

# ============================================================
# FOOTBALL RESEARCH LABORATORY
# Milestone 2 V1
# Historical Match-State Engine
#
# Purpose:
#   Reconstruct what was knowable about each team immediately
#   BEFORE every fixture, using results from earlier matches in
#   the same season only.
#
# Risk Strategy Framework:
#   - No current/future fixture is added to team history until
#     AFTER its feature row has been constructed.
#   - Unplayed fixtures do not alter team history.
#   - Latest source kickoff is recorded for leakage testing.
# ============================================================

$Root = "C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"

$FixtureMaster = Join-Path $Root "fixtures_master.csv"
$FeatureFolder = Join-Path $Root "features"
$OutputFile    = Join-Path $FeatureFolder "historical_match_state_v1.csv"

if (-not (Test-Path $FixtureMaster)) {
    throw "fixtures_master.csv was not found: $FixtureMaster"
}

if (-not (Test-Path $FeatureFolder)) {
    New-Item -ItemType Directory -Path $FeatureFolder | Out-Null
}

$Fixtures = @(Import-Csv $FixtureMaster)

if ($Fixtures.Count -eq 0) {
    throw "No fixtures were loaded."
}

# ------------------------------------------------------------
# Helper: return recent statistics from a team's prior matches
# ------------------------------------------------------------

function Get-RecentStats {
    param(
        [array]$History,
        [int]$Window = 5
    )

    $Recent = @(
        $History |
            Sort-Object @{Expression={[datetime]$_.kickoff_time}} -Descending |
            Select-Object -First $Window
    )

    $Matches = $Recent.Count

    if ($Matches -eq 0) {
        return [PSCustomObject]@{
            matches       = 0
            points        = 0
            goals_for     = 0
            goals_against = 0
            goal_diff     = 0
            form          = ""
            latest_kickoff = $null
        }
    }

    $Points = ($Recent | Measure-Object -Property points -Sum).Sum
    $GF     = ($Recent | Measure-Object -Property goals_for -Sum).Sum
    $GA     = ($Recent | Measure-Object -Property goals_against -Sum).Sum

    # Reverse so form reads oldest -> newest within the window.
    $Form = (
        $Recent |
            Sort-Object @{Expression={[datetime]$_.kickoff_time}} |
            ForEach-Object { $_.result }
    ) -join "-"

    $Latest = (
        $Recent |
            Sort-Object @{Expression={[datetime]$_.kickoff_time}} -Descending |
            Select-Object -First 1
    ).kickoff_time

    return [PSCustomObject]@{
        matches        = $Matches
        points         = [int]$Points
        goals_for      = [int]$GF
        goals_against  = [int]$GA
        goal_diff      = [int]($GF - $GA)
        form           = $Form
        latest_kickoff = $Latest
    }
}

# ------------------------------------------------------------
# Helper: convert score into result
# ------------------------------------------------------------

function Get-Result {
    param(
        [int]$GoalsFor,
        [int]$GoalsAgainst
    )

    if ($GoalsFor -gt $GoalsAgainst) {
        return "W"
    }

    if ($GoalsFor -eq $GoalsAgainst) {
        return "D"
    }

    return "L"
}

# ------------------------------------------------------------
# Sort chronologically.
# ------------------------------------------------------------

$Fixtures = @(
    $Fixtures |
        Sort-Object `
            @{Expression={[datetime]$_.kickoff_time}}, `
            @{Expression={$_.season}}, `
            @{Expression={[int]$_.fixture_id}}
)

# ------------------------------------------------------------
# Team history
#
# Key:
#   season|team_id
#
# Each value is a list of COMPLETED matches that have already
# occurred before the current fixture.
# ------------------------------------------------------------

$TeamHistory = @{}

$OutputRows = New-Object System.Collections.Generic.List[object]

$Processed = 0

foreach ($Fixture in $Fixtures) {

    $Processed++

    if (($Processed % 500) -eq 0) {
        Write-Host "Processed $Processed / $($Fixtures.Count)..."
    }

    $Season = [string]$Fixture.season
    $Kickoff = [datetime]$Fixture.kickoff_time

    $HomeTeam = [string]$Fixture.home_team_id
    $AwayTeam = [string]$Fixture.away_team_id

    $HomeKey = "$Season|$HomeTeam"
    $AwayKey = "$Season|$AwayTeam"

    if (-not $TeamHistory.ContainsKey($HomeKey)) {
        $TeamHistory[$HomeKey] = New-Object System.Collections.ArrayList
    }

    if (-not $TeamHistory.ContainsKey($AwayKey)) {
        $TeamHistory[$AwayKey] = New-Object System.Collections.ArrayList
    }

    # --------------------------------------------------------
    # IMPORTANT:
    # These histories contain ONLY matches occurring BEFORE
    # the current fixture.
    # --------------------------------------------------------

    $HomeHistory = @($TeamHistory[$HomeKey])
    $AwayHistory = @($TeamHistory[$AwayKey])

    $HomeOverall = Get-RecentStats -History $HomeHistory -Window 5
    $AwayOverall = Get-RecentStats -History $AwayHistory -Window 5

    $HomeHomeHistory = @(
        $HomeHistory |
            Where-Object { $_.was_home -eq $true }
    )

    $AwayAwayHistory = @(
        $AwayHistory |
            Where-Object { $_.was_home -eq $false }
    )

    $HomeHomeStats = Get-RecentStats -History $HomeHomeHistory -Window 5
    $AwayAwayStats  = Get-RecentStats -History $AwayAwayHistory  -Window 5

    # --------------------------------------------------------
    # Season-to-date totals
    # --------------------------------------------------------

    $HomeSeasonMatches = $HomeHistory.Count
    $AwaySeasonMatches = $AwayHistory.Count

    $HomeSeasonPoints = 0
    $AwaySeasonPoints = 0

    $HomeSeasonGF = 0
    $HomeSeasonGA = 0

    $AwaySeasonGF = 0
    $AwaySeasonGA = 0

    if ($HomeHistory.Count -gt 0) {
        $HomeSeasonPoints = [int](($HomeHistory | Measure-Object points -Sum).Sum)
        $HomeSeasonGF     = [int](($HomeHistory | Measure-Object goals_for -Sum).Sum)
        $HomeSeasonGA     = [int](($HomeHistory | Measure-Object goals_against -Sum).Sum)
    }

    if ($AwayHistory.Count -gt 0) {
        $AwaySeasonPoints = [int](($AwayHistory | Measure-Object points -Sum).Sum)
        $AwaySeasonGF     = [int](($AwayHistory | Measure-Object goals_for -Sum).Sum)
        $AwaySeasonGA     = [int](($AwayHistory | Measure-Object goals_against -Sum).Sum)
    }

    # --------------------------------------------------------
    # Rest days since each team's previous completed fixture.
    # --------------------------------------------------------

    $HomeRestDays = $null
    $AwayRestDays = $null

    if ($HomeOverall.latest_kickoff) {
        $HomeRestDays = ($Kickoff - [datetime]$HomeOverall.latest_kickoff).TotalDays
        $HomeRestDays = [math]::Round($HomeRestDays, 2)
    }

    if ($AwayOverall.latest_kickoff) {
        $AwayRestDays = ($Kickoff - [datetime]$AwayOverall.latest_kickoff).TotalDays
        $AwayRestDays = [math]::Round($AwayRestDays, 2)
    }

    # --------------------------------------------------------
    # Current fixture completion status.
    # --------------------------------------------------------

    $Completed = (
        -not [string]::IsNullOrWhiteSpace($Fixture.home_score) -and
        -not [string]::IsNullOrWhiteSpace($Fixture.away_score)
    )

    $OutputRows.Add(
        [PSCustomObject]@{
            season                     = $Season
            fixture_id                 = $Fixture.fixture_id
            fixture_code               = $Fixture.fixture_code
            kickoff_time               = $Fixture.kickoff_time
            gameweek                   = $Fixture.gameweek

            home_team_id               = $HomeTeam
            away_team_id               = $AwayTeam

            home_score                 = $Fixture.home_score
            away_score                 = $Fixture.away_score
            fixture_completed          = $Completed

            # ----------------------------------------------
            # Home overall pre-match state
            # ----------------------------------------------

            home_matches_prior         = $HomeSeasonMatches
            home_points_prior          = $HomeSeasonPoints
            home_goals_for_prior       = $HomeSeasonGF
            home_goals_against_prior   = $HomeSeasonGA
            home_goal_diff_prior       = $HomeSeasonGF - $HomeSeasonGA

            home_last5_matches         = $HomeOverall.matches
            home_last5_points          = $HomeOverall.points
            home_last5_goals_for       = $HomeOverall.goals_for
            home_last5_goals_against   = $HomeOverall.goals_against
            home_last5_goal_diff       = $HomeOverall.goal_diff
            home_last5_form            = $HomeOverall.form

            # ----------------------------------------------
            # Home-specific pre-match state
            # ----------------------------------------------

            home_last5_home_matches    = $HomeHomeStats.matches
            home_last5_home_points     = $HomeHomeStats.points
            home_last5_home_goals_for  = $HomeHomeStats.goals_for
            home_last5_home_goals_against = $HomeHomeStats.goals_against
            home_last5_home_goal_diff   = $HomeHomeStats.goal_diff
            home_last5_home_form       = $HomeHomeStats.form

            # ----------------------------------------------
            # Away overall pre-match state
            # ----------------------------------------------

            away_matches_prior         = $AwaySeasonMatches
            away_points_prior          = $AwaySeasonPoints
            away_goals_for_prior       = $AwaySeasonGF
            away_goals_against_prior   = $AwaySeasonGA
            away_goal_diff_prior       = $AwaySeasonGF - $AwaySeasonGA

            away_last5_matches         = $AwayOverall.matches
            away_last5_points          = $AwayOverall.points
            away_last5_goals_for       = $AwayOverall.goals_for
            away_last5_goals_against   = $AwayOverall.goals_against
            away_last5_goal_diff       = $AwayOverall.goal_diff
            away_last5_form            = $AwayOverall.form

            # ----------------------------------------------
            # Away-specific pre-match state
            # ----------------------------------------------

            away_last5_away_matches    = $AwayAwayStats.matches
            away_last5_away_points     = $AwayAwayStats.points
            away_last5_away_goals_for  = $AwayAwayStats.goals_for
            away_last5_away_goals_against = $AwayAwayStats.goals_against
            away_last5_away_goal_diff   = $AwayAwayStats.goal_diff
            away_last5_away_form       = $AwayAwayStats.form

            # ----------------------------------------------
            # Temporal provenance
            # ----------------------------------------------

            home_latest_prior_kickoff  = $HomeOverall.latest_kickoff
            away_latest_prior_kickoff  = $AwayOverall.latest_kickoff

            home_rest_days              = $HomeRestDays
            away_rest_days              = $AwayRestDays

            feature_as_of               = $Fixture.kickoff_time
        }
    ) | Out-Null

    # --------------------------------------------------------
    # ONLY AFTER constructing the current feature row do we
    # add the current fixture to team history.
    #
    # Unplayed fixtures are deliberately NOT added.
    # --------------------------------------------------------

    if ($Completed) {

        $HomeScore = [int]$Fixture.home_score
        $AwayScore = [int]$Fixture.away_score

        $HomeResult = Get-Result -GoalsFor $HomeScore -GoalsAgainst $AwayScore
        $AwayResult = Get-Result -GoalsFor $AwayScore -GoalsAgainst $HomeScore

        $HomePoints = 0
        $AwayPoints = 0

        if ($HomeResult -eq "W") {
            $HomePoints = 3
        }
        elseif ($HomeResult -eq "D") {
            $HomePoints = 1
            $AwayPoints = 1
        }
        else {
            $AwayPoints = 3
        }

        $HomeHistoryRecord = [PSCustomObject]@{
            kickoff_time = $Fixture.kickoff_time
            was_home     = $true
            goals_for    = $HomeScore
            goals_against = $AwayScore
            points       = $HomePoints
            result       = $HomeResult
            opponent_id  = $AwayTeam
            fixture_id   = $Fixture.fixture_id
        }

        $AwayHistoryRecord = [PSCustomObject]@{
            kickoff_time = $Fixture.kickoff_time
            was_home     = $false
            goals_for    = $AwayScore
            goals_against = $HomeScore
            points       = $AwayPoints
            result       = $AwayResult
            opponent_id  = $HomeTeam
            fixture_id   = $Fixture.fixture_id
        }

        [void]$TeamHistory[$HomeKey].Add($HomeHistoryRecord)
        [void]$TeamHistory[$AwayKey].Add($AwayHistoryRecord)
    }
}

# ------------------------------------------------------------
# Write output
# ------------------------------------------------------------

$OutputRows |
    Export-Csv $OutputFile -NoTypeInformation

Write-Host ""
Write-Host "============================================="
Write-Host " HISTORICAL MATCH-STATE BUILD COMPLETE"
Write-Host "============================================="
Write-Host "Rows written: $($OutputRows.Count)"
Write-Host "Output:"
Write-Host $OutputFile
Write-Host ""