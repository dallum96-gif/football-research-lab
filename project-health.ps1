$ErrorActionPreference = "Stop"

# ============================================================
# FOOTBALL RESEARCH LABORATORY
# Risk Strategy Framework V1
# Project Health Check
# ============================================================

$Root = "C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"

$PlayerFolder  = Join-Path $Root "_merged\players"
$FixtureMaster = Join-Path $Root "fixtures_master.csv"

$Failures = New-Object System.Collections.Generic.List[string]
$Warnings = New-Object System.Collections.Generic.List[string]

function Pass($Message) {
    Write-Host "PASS  $Message" -ForegroundColor Green
}

function Fail($Message) {
    Write-Host "FAIL  $Message" -ForegroundColor Red
    $Failures.Add($Message)
}

function Warn($Message) {
    Write-Host "WARN  $Message" -ForegroundColor Yellow
    $Warnings.Add($Message)
}

Write-Host ""
Write-Host "============================================="
Write-Host " FOOTBALL RESEARCH LABORATORY"
Write-Host " RISK STRATEGY FRAMEWORK V1"
Write-Host " PROJECT HEALTH CHECK"
Write-Host "============================================="
Write-Host ""

# ------------------------------------------------------------
# 1. SOURCE FILES
# ------------------------------------------------------------

Write-Host "[1] SOURCE FILES"

$PlayerFiles = Get-ChildItem $PlayerFolder `
    -Filter "*_all_players_gw.csv" `
    -File |
    Sort-Object Name

if ($PlayerFiles.Count -eq 10) {
    Pass "10 historical player files found"
}
else {
    Fail "Expected 10 historical player files; found $($PlayerFiles.Count)"
}

$ExpectedSeasons = @(
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26"
)

$FoundSeasons = $PlayerFiles.BaseName |
    ForEach-Object {
        $_ -replace "_all_players_gw$", ""
    }

foreach ($Season in $ExpectedSeasons) {
    if ($FoundSeasons -contains $Season) {
        Pass "Player data present: $Season"
    }
    else {
        Fail "Missing player data: $Season"
    }
}

# ------------------------------------------------------------
# 2. MASTER FIXTURE FILE
# ------------------------------------------------------------

Write-Host ""
Write-Host "[2] FIXTURE MASTER"

if (-not (Test-Path $FixtureMaster)) {

    Fail "fixtures_master.csv does not exist"

}
else {

    $Fixtures = @(Import-Csv $FixtureMaster)

    if ($Fixtures.Count -eq 3800) {
        Pass "Fixture count = 3,800"
    }
    else {
        Fail "Expected 3,800 fixtures; found $($Fixtures.Count)"
    }

    # --------------------------------------------------------
    # 3. SEASON INTEGRITY
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "[3] SEASON INTEGRITY"

    $SeasonGroups = $Fixtures |
        Group-Object season

    foreach ($Season in $ExpectedSeasons) {

        $Group = $SeasonGroups |
            Where-Object { $_.Name -eq $Season }

        if ($null -eq $Group) {

            Fail "No fixtures found for $Season"

        }
        elseif ($Group.Count -eq 380) {

            Pass "$Season = 380 fixtures"

        }
        else {

            Fail "$Season = $($Group.Count) fixtures; expected 380"

        }
    }

    # --------------------------------------------------------
    # 4. DUPLICATE CHECKS
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "[4] DUPLICATE CHECKS"

    $DuplicateFixtures = $Fixtures |
        Group-Object season, fixture_id |
        Where-Object { $_.Count -gt 1 }

    if ($DuplicateFixtures.Count -eq 0) {

        Pass "No duplicate season + fixture IDs"

    }
    else {

        Fail "$($DuplicateFixtures.Count) duplicate season + fixture ID groups"

    }

    # --------------------------------------------------------
    # 5. REQUIRED FIELDS
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "[5] REQUIRED FIELDS"

    $MissingHome = @(
        $Fixtures |
            Where-Object {
                [string]::IsNullOrWhiteSpace($_.home_team_id)
            }
    )

    $MissingAway = @(
        $Fixtures |
            Where-Object {
                [string]::IsNullOrWhiteSpace($_.away_team_id)
            }
    )

    $MissingKickoff = @(
        $Fixtures |
            Where-Object {
                [string]::IsNullOrWhiteSpace($_.kickoff_time)
            }
    )

    if ($MissingHome.Count -eq 0) {
        Pass "No missing home team IDs"
    }
    else {
        Fail "$($MissingHome.Count) fixtures missing home team ID"
    }

    if ($MissingAway.Count -eq 0) {
        Pass "No missing away team IDs"
    }
    else {
        Fail "$($MissingAway.Count) fixtures missing away team ID"
    }

    if ($MissingKickoff.Count -eq 0) {
        Pass "No missing kickoff times"
    }
    else {
        Fail "$($MissingKickoff.Count) fixtures missing kickoff time"
    }

    # --------------------------------------------------------
    # 6. SCORE / COMPLETION SEMANTICS
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "[6] SCORE / COMPLETION INTEGRITY"

    # A fixture with scores is treated as completed.
    # A fixture with missing scores is currently treated as
    # uncompleted and flagged for review rather than failed.
    #
    # Later we will add explicit fixture_status to the
    # canonical schema and make this check more precise.

    $MissingScores = @(
        $Fixtures |
            Where-Object {
                [string]::IsNullOrWhiteSpace($_.home_score) -or
                [string]::IsNullOrWhiteSpace($_.away_score)
            }
    )

    if ($MissingScores.Count -eq 0) {

        Pass "All fixtures contain scores"

    }
    else {

        Warn "$($MissingScores.Count) fixtures have no score; treated as uncompleted pending explicit fixture status"

        foreach ($Fixture in $MissingScores) {

            Write-Host (
                "      $($Fixture.season) fixture $($Fixture.fixture_id) " +
                "($($Fixture.home_team_id) vs $($Fixture.away_team_id), " +
                "$($Fixture.kickoff_time))"
            )
        }
    }

    # --------------------------------------------------------
    # 7. TEAM INTEGRITY
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "[7] TEAM INTEGRITY"

    $InvalidSameTeam = @(
        $Fixtures |
            Where-Object {
                $_.home_team_id -eq $_.away_team_id
            }
    )

    if ($InvalidSameTeam.Count -eq 0) {

        Pass "No fixtures with identical home and away teams"

    }
    else {

        Fail "$($InvalidSameTeam.Count) fixtures have the same home and away team"

    }

    # --------------------------------------------------------
    # 8. DATE INTEGRITY
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "[8] DATE INTEGRITY"

    $InvalidDates = @()

    foreach ($Fixture in $Fixtures) {

        try {

            $null = [datetime]$Fixture.kickoff_time

        }
        catch {

            $InvalidDates += $Fixture

        }
    }

    if ($InvalidDates.Count -eq 0) {

        Pass "All kickoff times are valid datetimes"

    }
    else {

        Fail "$($InvalidDates.Count) fixtures have invalid kickoff times"

    }

    # --------------------------------------------------------
    # 9. PLAYER / FIXTURE RELATIONSHIP
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "[9] PLAYER / FIXTURE RELATIONSHIP"

    $Player2025 = $PlayerFiles |
        Where-Object {
            $_.Name -eq "2025-26_all_players_gw.csv"
        }

    if ($Player2025) {

        $PlayerRows = @(Import-Csv $Player2025.FullName)

        $PlayerFixtureCodes = @(
            $PlayerRows.fixture_code |
                Where-Object { $_ } |
                Sort-Object -Unique
        )

        if ($PlayerFixtureCodes.Count -eq 380) {

            Pass "2025-26 player data contains 380 unique fixture codes"

        }
        else {

            Fail "2025-26 player data contains $($PlayerFixtureCodes.Count) unique fixture codes; expected 380"

        }

        $ModernFixtureCodes = @(
            $Fixtures |
                Where-Object {
                    $_.season -eq "2025-26" -and
                    $_.fixture_code
                } |
                Select-Object -ExpandProperty fixture_code |
                Sort-Object -Unique
        )

        if ($ModernFixtureCodes.Count -eq 380) {

            Pass "2025-26 master contains 380 unique fixture codes"

        }
        else {

            Fail "2025-26 master contains $($ModernFixtureCodes.Count) unique fixture codes; expected 380"

        }

        $MissingFromMaster = @(
            $PlayerFixtureCodes |
                Where-Object {
                    $_ -notin $ModernFixtureCodes
                }
        )

        if ($MissingFromMaster.Count -eq 0) {

            Pass "All 2025-26 player fixture codes resolve to the master fixture table"

        }
        else {

            Fail "$($MissingFromMaster.Count) 2025-26 player fixture codes do not resolve"

        }

    }
    else {

        Fail "2025-26 player file could not be located"

    }
}

# ------------------------------------------------------------
# FINAL STATUS
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================================="
Write-Host " FINAL STATUS"
Write-Host "============================================="

if ($Failures.Count -eq 0) {

    if ($Warnings.Count -eq 0) {

        Write-Host ""
        Write-Host "GREEN LIGHT - PROJECT HEALTH CHECK PASSED" -ForegroundColor Green
        Write-Host ""

    }
    else {

        Write-Host ""
        Write-Host "GREEN LIGHT - PASSED WITH WARNINGS" -ForegroundColor Green
        Write-Host ""
        Write-Host "Warnings:"
        
        foreach ($Warning in $Warnings) {
            Write-Host " - $Warning" -ForegroundColor Yellow
        }

        Write-Host ""
    }

    exit 0

}
else {

    Write-Host ""
    Write-Host "RED LIGHT - PROJECT HEALTH CHECK FAILED" -ForegroundColor Red
    Write-Host ""

    Write-Host "Failures:"

    foreach ($Failure in $Failures) {
        Write-Host " - $Failure" -ForegroundColor Red
    }

    if ($Warnings.Count -gt 0) {

        Write-Host ""
        Write-Host "Warnings:"

        foreach ($Warning in $Warnings) {
            Write-Host " - $Warning" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    exit 1
}