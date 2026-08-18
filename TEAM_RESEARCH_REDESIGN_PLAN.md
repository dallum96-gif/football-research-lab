# Team Research redesign

Team Research is being redesigned as a research workspace rather than a dashboard.

## Profile questions
- How good was the team?
- How did performance evolve through the season?
- Where was the team strong or weak?
- What changed between phases of the season?
- What evidence supports the conclusions?

## Stats questions
- How does this season compare with other seasons for the same team?
- Which seasons were strongest or weakest by points, PPG, goals, goals conceded and goal difference?
- Where are sustained changes visible across seasons?

The presentation should preserve the FRL GUI contract, use canonical analytical outputs, keep provenance visible, and avoid decorative charts without analytical purpose.

The redesign should initially reuse verified fixture-level data and existing team summary/form/compare research APIs. New derived metrics should be added to the analytical layer only when their definitions and provenance are explicit.
