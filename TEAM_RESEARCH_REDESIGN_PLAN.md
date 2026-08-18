# Team Research redesign

Team Research is a research workspace, not a dashboard. The page should help an analyst answer what the team was like, how its performance changed, where strengths and weaknesses appeared, and how a season compares with other seasons.

## Profile
- Season identity and concise performance snapshot.
- Performance trajectory through the season, with analytically meaningful rolling measures rather than a decorative goals line.
- Fixture-level scoring and defensive profile.
- Home/away context when the underlying data supports it.
- First/middle/final phase comparison when definitions are explicit.
- Recent fixtures as evidence, not just navigation decoration.

## Stats
- Genuine multi-season comparison for a selected club.
- Comparable metrics such as points, points per match, goals for/against per match and goal difference.
- Clear best/worst/changed-season signals where supported by the data.
- Comparisons should preserve season identity, provenance and limitations.

## Design constraints
- Preserve the FRL GUI contract and existing design system.
- Use canonical analytical outputs rather than UI-specific re-computation.
- Keep visualisations purposeful: every chart should answer a research question.
- Prefer compact editorial presentation over dashboard card grids.
- Do not add derived metrics to the UI without an explicit analytical definition and evidence path.
