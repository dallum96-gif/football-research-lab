$ErrorActionPreference = "Stop"

$Root = "C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"

$StateFile   = Join-Path $Root "features\historical_match_state_v2.csv"
$FixtureFile = Join-Path $Root "fixtures_master.csv"

if (-not (Test-Path $StateFile)) {
    throw "State file not found: $StateFile"
}

if (-not (Test-Path $FixtureFile)) {
    throw "Fixture master not found: $FixtureFile"
}

$State    = @(Import-Csv $StateFile)
$Fixtures = @(Import-Csv $FixtureFile)

$Failures = New-Object System.Collections.Generic.List[string]

# Build lookup:
# season|fixture_id -> fixture
$FixtureLookup = @{}

foreach ($Fixture in $Fixtures) {

    $Key = "$($Fixture.season)|$($Fixture.fixture_id)"

    if ($FixtureLookup.ContainsKey($Key)) {
        $Failures.Add("Duplicate fixture key in master: $Key")
        continue
    }

    $FixtureLookup[$Key] = $Fixture
}

function Test-SourceWindow {
    param(
        [Parameter(Mandatory=$true)]$Row,
        [Parameter(Mandatory=$true)][string]$TeamSide
    )

    $TargetKickoff = [datetime]$Row.kickoff_time

    $FixtureField = "${TeamSide}_last5_fixture_ids"
    $KickoffField = "${TeamSide}_last5_kickoffs"
    $MatchesField = "${TeamSide}_last5_matches"

    $FixtureString = [string]$Row.$FixtureField
    $KickoffString = [string]$Row.$KickoffField

    if ([string]::IsNullOrWhiteSpace($FixtureString)) {

        if ([int]$Row.$MatchesField -ne 0) {
            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "$TeamSide has no source fixtures but reports $($Row.$MatchesField) prior matches"
            )
        }

        return
    }

    $SourceIDs = @(
        $FixtureString -split "\|" |
            Where-Object { $_ -ne "" }
    )

    $SourceKickoffs = @(
        $KickoffString -split "\|" |
            Where-Object { $_ -ne "" }
    )

    if ($SourceIDs.Count -ne $SourceKickoffs.Count) {
        $Failures.Add(
            "$($Row.season) fixture $($Row.fixture_id): " +
            "$TeamSide source fixture count ($($SourceIDs.Count)) " +
            "does not equal source kickoff count ($($SourceKickoffs.Count))"
        )
    }

    if ($SourceIDs.Count -ne [int]$Row.$MatchesField) {
        $Failures.Add(
            "$($Row.season) fixture $($Row.fixture_id): " +
            "$TeamSide source count ($($SourceIDs.Count)) " +
            "does not equal reported prior-match count ($($Row.$MatchesField))"
        )
    }

    $DuplicateIDs = @(
        $SourceIDs |
            Group-Object |
            Where-Object { $_.Count -gt 1 }
    )

    if ($DuplicateIDs.Count -gt 0) {
        $Failures.Add(
            "$($Row.season) fixture $($Row.fixture_id): " +
            "$TeamSide last-5 window contains duplicate fixture IDs"
        )
    }

    for ($i = 0; $i -lt $SourceIDs.Count; $i++) {

        $SourceID = $SourceIDs[$i]
        $LookupKey = "$($Row.season)|$SourceID"

        if (-not $FixtureLookup.ContainsKey($LookupKey)) {
            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "$TeamSide source fixture $SourceID does not exist in fixture master"
            )
            continue
        }

        $SourceFixture = $FixtureLookup[$LookupKey]

        $SourceMasterKickoff = [datetime]$SourceFixture.kickoff_time
        $RecordedKickoff     = [datetime]$SourceKickoffs[$i]

        if ($RecordedKickoff -ne $SourceMasterKickoff) {
            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "$TeamSide source fixture $SourceID has provenance kickoff " +
                "$RecordedKickoff but master kickoff $SourceMasterKickoff"
            )
        }

        if ($SourceMasterKickoff -ge $TargetKickoff) {
            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "$TeamSide source fixture $SourceID occurs at $SourceMasterKickoff, " +
                "which is not before target kickoff $TargetKickoff"
            )
        }
    }
}

Write-Host ""
Write-Host "============================================="
Write-Host " RISK STRATEGY FRAMEWORK"
Write-Host " TEMPORAL PROVENANCE TEST"
Write-Host "============================================="
Write-Host ""

foreach ($Row in $State) {

    Test-SourceWindow -Row $Row -TeamSide "home"
    Test-SourceWindow -Row $Row -TeamSide "away"
}

if ($Failures.Count -eq 0) {

    Write-Host ""
    Write-Host "PASS  All historical windows have valid provenance." -ForegroundColor Green
    Write-Host "PASS  Every source fixture exists in the master." -ForegroundColor Green
    Write-Host "PASS  Every source kickoff matches the master." -ForegroundColor Green
    Write-Host "PASS  Every source fixture predates its target fixture." -ForegroundColor Green
    Write-Host "PASS  No duplicate source fixture IDs found." -ForegroundColor Green
    Write-Host ""

    exit 0
}

Write-Host ""
Write-Host "FAIL  Temporal provenance violations: $($Failures.Count)" -ForegroundColor Red
Write-Host ""

foreach ($Failure in $Failures) {
    Write-Host " - $Failure" -ForegroundColor Red
}

Write-Host ""

exit 1
