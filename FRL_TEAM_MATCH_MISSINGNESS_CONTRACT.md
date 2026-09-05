# Football Research Laboratory — Team-Match Missingness Contract

**Status:** Governed field-level analytical contract  
**Date:** 30 August 2026  
**Latest evidence review:** 5 September 2026

## Purpose

This contract governs how FRL interprets blank values from the preserved direct team-match statistics representation when constructing analytical team-match and team-season observations.

It supplements `FRL_SOURCE_ROUTING_CONTRACT.md`. Source parsing remains source-faithful: a blank cell is parsed as `None`. Any analytical interpretation of that blank happens later and must be explicitly governed here or by a successor field-level contract.

## Core rule

> **A source blank is missing by default. It may become a structural zero only when the football concept, source representation and audited period provide specific evidence that blank encodes zero occurrences.**

Never generalise a sparse-zero rule merely because another count field uses sparse encoding.

## Current governed scope

For the preserved direct `events_stats` / packaged team-match representation, the following fields are governed as sparse-zero counts for Premier League seasons **2016-17 through 2025-26**:

| FRL metric | Source field | Blank semantics |
| --- | --- | --- |
| Shots | `totalScoringAtt` | structural zero |
| Shots on target | `ontargetScoringAtt` | structural zero |
| Shots off target | `shotOffTarget` | structural zero |
| Blocked shots | `blockedScoringAtt` | structural zero |

An explicit numeric `0` remains an ordinary observed zero. A structural zero is specifically a blank source observation interpreted as zero under this governed rule.

## Evidence basis

The 30 August 2026 preserved-source audits established:

- total shots had only two blank team-side observations across the audited decade; independent player-match totals resolved both to zero;
- the historical shot partition `total shots = on target + off target + blocked` was exact on every fully observed team-side from 2016-17 through 2024-25;
- for shots on target, 152 blank observations were inferable from the other shot fields: 151 resolved to zero and none resolved positively; the remaining non-zero residual was a 2025-26 source-classification anomaly;
- for shots off target, all 113 inferable blanks resolved to zero;
- for blocked shots, 464 of 465 inferable blanks resolved to zero and none resolved positively; the remaining negative residual was another source-classification anomaly;
- the 2025-26 partition exceptions remain source anomalies and are not rewritten to force the historical identity.

The diagnostic automation remains read-only. This contract is the explicit governance step that promotes the audited shot-family blank semantics into analytical use.

## September 2026 sparse-zero review

A second read-only audit reviewed four high-value team-match fields whose packaged representation has occasional blanks and no observed numeric zeros:

- `blockedPass` — 5 blanks across 7,600 team-match rows;
- `touchesInOppBox` — 2 blanks;
- `goalKicks` — 21 blanks;
- `lostCorners` — 160 blanks.

The audit deliberately sought **independent corroboration** rather than inferring zero from sparse encoding.

### Player-match corroboration

No exact same-field player-match route exists for any of the four candidates across the audited decade. Therefore none of their blank observations can be independently resolved to zero through exact player-match summation.

### Opponent-route review for `lostCorners`

The corrected opponent comparison keys fixtures by **season + fixture**, preventing same-numbered fixtures from different seasons being combined.

For observed `lostCorners` values against the opponent's `cornerTaken`:

- 7,438 team-side comparisons were available;
- 7,293 were exact matches;
- 145 were mismatches;
- all 160 `lostCorners` blanks paired with opponent `cornerTaken` blanks;
- no blank `lostCorners` observation was independently corroborated as zero.

Therefore `lostCorners` must not be treated as a proven synonym for opponent corners taken/conceded, and its blanks must not be promoted to structural zero.

### Governance decision

**No new structural-zero fields were approved by the 5 September review.**

For `blockedPass`, `touchesInOppBox`, `goalKicks` and `lostCorners`, a blank continues to mean **missing** in the preserved direct team-match representation unless future independent evidence justifies a narrower field-level exception.

This decision is separate from semantic exposure. A source-native field may be judged safe for coverage-aware research access while its occasional blanks remain genuinely missing.

Evidence is produced by:

`scripts/audit_team_match_sparse_zero_candidates.py`

## Fields that remain missing when blank

This contract does **not** approve sparse-zero interpretation for other fields.

In particular, blanks remain missing/unavailable unless separately governed for:

- possession;
- expected goals, expected assists and expected goals on target;
- saves;
- offsides;
- big chances;
- passing, defensive, discipline and goalkeeper counts not listed in the governed structural-zero table above;
- `blockedPass`, `touchesInOppBox`, `goalKicks` and `lostCorners`;
- any future field merely because it is numeric or count-like.

The known Tottenham Hotspur v Everton possession gap on 13 September 2020 remains missing.

## Period and representation boundary

The current sparse-zero approval is deliberately bounded to:

- the preserved direct team-match representation used by `team_research_stats`;
- Premier League seasons 2016-17 through 2025-26;
- descriptive team-match/team-season analytical use.

Do not automatically apply the rule to:

- 2026-27 or later seasons;
- player-match or player-season representations;
- alternative PulseLive snapshots;
- another competition;
- historical as-of claims where information-availability semantics differ.

Those contexts require their own evidence or an explicit extension of this contract.

## Aggregation requirements

For every governed metric, aggregation should preserve at least:

- eligible matches;
- source-observed matches;
- structural-zero matches;
- governed observed matches;
- genuinely missing matches;
- observed total;
- per-observed-match value;
- missingness semantics;
- coverage status.

For a governed sparse-zero metric, a structural-zero match belongs to the observed analytical population and contributes `0` to the total and denominator.

For a genuinely missing metric such as xG, the missing match does not belong to the observed denominator.

## Comparability

Derived ratios and rankings must use the governed observation population.

This means, for example, that a blank shots-on-target cell governed as structural zero can legitimately participate as `0` in shots-on-target per match and in shot-accuracy population alignment. A missing xG observation cannot be treated the same way.

Coverage-aware source-native fields with occasional genuine blanks must use only their observed population unless a derived comparison explicitly requires complete/comparable populations.

## Source preservation

Do not change generic source parsing so that blank becomes zero globally.

Preferred flow:

```text
source blank
    ↓
source-faithful parse as None
    ↓
field + representation + period missingness policy
    ↓
missing OR structural zero
    ↓
metric observation / population
```

This preserves the difference between what the source stored and what FRL has governed the observation to mean.

## Testing

The governed implementation must test at least:

- explicit zero remains observed zero;
- approved shot-family blank becomes structural zero in an audited season;
- structural zero enters the per-match denominator;
- source-observed and structural-zero counts remain distinguishable;
- shot-derived populations become comparable where the governed zero completes them;
- xG blank remains missing and coverage-aware;
- `blockedPass`, `touchesInOppBox`, `goalKicks` and `lostCorners` blanks remain missing after the September review;
- the sparse-zero rule does not leak into an unaudited future season.

## Final principle

> **Missingness is football semantics, not parser convenience: preserve the blank, govern its meaning, and only then aggregate it.**
