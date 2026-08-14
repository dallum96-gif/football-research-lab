$ErrorActionPreference = "Stop"

$Root = "C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"

$StateFile = Join-Path $Root "features\historical_match_state_v1.csv"

if (-not (Test-Path $StateFile)) {
    throw "Historical match-state file not found: $StateFile"
}

$Rows = @(Import-Csv $StateFile)

$Failures = New-Object System.Collections.Generic.List[string]

Write-Host ""
Write-Host "============================================="
Write-Host " RISK STRATEGY FRAMEWORK"
Write-Host " TEMPORAL INTEGRITY TEST"
Write-Host "============================================="
Write-Host ""

foreach ($Row in $Rows) {

    $Kickoff = [datetime]$Row.kickoff_time

    if (-not [string]::IsNullOrWhiteSpace($Row.home_latest_prior_kickoff)) {

        $HomePrior = [datetime]$Row.home_latest_prior_kickoff

        if ($HomePrior -ge $Kickoff) {

            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "home prior kickoff $HomePrior is not before target kickoff $Kickoff"
            )
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($Row.away_latest_prior_kickoff)) {

        $AwayPrior = [datetime]$Row.away_latest_prior_kickoff

        if ($AwayPrior -ge $Kickoff) {

            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "away prior kickoff $AwayPrior is not before target kickoff $Kickoff"
            )
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($Row.home_rest_days)) {

        if ([double]$Row.home_rest_days -lt 0) {

            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "negative home rest days"
            )
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($Row.away_rest_days)) {

        if ([double]$Row.away_rest_days -lt 0) {

            $Failures.Add(
                "$($Row.season) fixture $($Row.fixture_id): " +
                "negative away rest days"
            )
        }
    }
}

if ($Failures.Count -eq 0) {

    Write-Host ""
    Write-Host "PASS  No temporal integrity violations found." -ForegroundColor Green
    Write-Host "PASS  All prior-kickoff values precede target kickoff." -ForegroundColor Green
    Write-Host "PASS  No negative rest periods found." -ForegroundColor Green
    Write-Host ""

    exit 0
}

Write-Host ""
Write-Host "FAIL  Temporal integrity violations: $($Failures.Count)" -ForegroundColor Red
Write-Host ""

foreach ($Failure in $Failures) {
    Write-Host " - $Failure" -ForegroundColor Red
}

Write-Host ""

exit 1
