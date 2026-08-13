# Form & Streaks — Initial Design

## Purpose

Build a provenance-aware backend query that describes a team's recent Premier League form and streaks without hard-coding a single GUI representation.

## First milestone

Given a season and team, return recent completed fixtures in chronological order plus derived indicators for configurable windows.

Initial indicators:

- last 3 results
- last 5 results
- points from last 3 / 5
- goals for / against from last 3 / 5
- goal difference from last 3 / 5
- current win streak
- current unbeaten streak
- current loss streak
- current clean-sheet streak
- current scoring streak

## Data principles

The underlying fixtures remain the source data. Form and streaks are derived views, not permanent stored facts.

Only completed fixtures contribute to form and streak calculations. Missing or incomplete fixture data must be surfaced rather than silently interpreted as a result.

Team identity must use the existing persistent identity system.

## Testing principle

Test invariants across multiple teams, seasons, windows and edge cases rather than relying on one example.

The GUI should not be built until the backend query contract is stable and tested.
