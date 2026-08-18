# FRL Branch Health Audit — 17 August 2026

## Finding

The development branch `design/player-filter-tiles` and `main` had diverged from the shared project baseline `1fbac1dfbc99bbbdd51776848fa0449aec54c2d1`.

The initial comparison reported:

- development branch: 262 commits ahead
- development branch: 11 commits behind

The 11 `main`-only commits were not independent external work. They were recent Football Research Laboratory changes that had been written directly to `main` during development, including documentation, recovery notes, player-match work and an older Team workspace implementation.

## Why this mattered

The direct-to-main writes violated the intended project branch model:

```text
main = stable / trusted integration line
feature / redesign branch = development work
```

It also created a risk that an older or superseded implementation on `main` could later be merged back over newer development work.

## Repair

Before moving the `main` ref, the previous `main` tip was preserved as:

`safety/main-accidental-work-2026-08-17`

That safety branch points to:

`3bbe55e8cf8250e8f4e06d921bab19cbe20948f1`

The `main` ref was then restored to the clean shared baseline:

`1fbac1dfbc99bbbdd51776848fa0449aec54c2d1`

No historical commit objects were deleted.

The active development branch remains intact and now contains the intended current redesign work plus the strengthened session protocol.

## Current topology

```text
main
  ↓
1fbac1d  ← clean shared baseline
  ↓
263 development commits
  ↓
design/player-filter-tiles
```

The current relationship is:

- `main`: 0 behind / 0 ahead of the clean baseline
- `design/player-filter-tiles`: 263 commits ahead / 0 behind `main`

This is an intentional long-lived development branch state, not an accidental divergence.

## Future integration rule

A development branch should not be promoted to `main` by moving the `main` ref directly.

When the project is ready for integration:

1. validate the complete relevant research/data/GUI gates;
2. inspect the branch-to-main diff;
3. review which work is intended to become trusted project state;
4. integrate through an explicit pull request/release decision;
5. verify the resulting `main` state;
6. only then continue development from the new baseline.

## Prevention

`SESSION_START_PROTOCOL.md` now explicitly requires:

- branch comparison before substantive work;
- inspection of main-only commits when a branch is behind;
- explicit branch parameters on GitHub writes;
- no direct development writes to `main`;
- a named safety branch before destructive ref movement.

The project Master Prompt should carry the same rule.

## Important interpretation

A large ahead count is not automatically a health failure. A long-lived feature/design branch may legitimately contain substantial work.

The dangerous state is **unexplained divergence**, especially when `main` contains accidental development work or when nobody knows which line represents the intended trusted project state.
