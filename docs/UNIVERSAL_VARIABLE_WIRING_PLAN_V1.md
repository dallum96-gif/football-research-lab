# FRL Universal Variable Wiring Plan V1

**Status:** Implementation contract / execution checkpoint

## Objective

Wire the universal variable resolver to the existing FRL retrieval mechanisms so that validated variables are reachable from their canonical graph contexts without GUI-specific source joins.

## Required behaviour

- Fixture-scoped requests resolve fixture-owned variables.
- Team–Fixture requests resolve team-match variables through the verified team/fixture identity path.
- Player–Fixture requests resolve player-match variables through the verified player/fixture identity path.
- Player–Season and Team–Season requests resolve through their canonical season grains where supported.
- Event variables remain at event grain and retain their fixture/team/player route where the source provides it.
- GUI consumers request canonical variable names and contexts only.
- Resolver failures remain fail-closed.

## Non-goals

- Do not create a universal mega-table.
- Do not duplicate canonical observations onto presentation entities merely for convenience.
- Do not invent player/fixture joins from display names or coincidental IDs.
- Do not replace existing trusted query/source mechanisms.
- Do not mark a variable `GUI_ACCESSIBLE` unless a tested resolver pathway exists for the relevant context.

## Implementation order

1. Inventory existing source-family/query handlers by canonical relationship/grain.
2. Register handler families with the universal resolver.
3. Map canonical variables to handler families and derivations.
4. Test fixture → team → player traversal for representative variables.
5. Test failure semantics and provenance.
6. Only then widen the registry from the initial display variables toward the complete validated canonical universe.

The end-state is:

```text
canonical variable
      ↓
canonical grain / relationship
      ↓
verified identity bridge
      ↓
existing query/source handler
      ↓
universal resolver
      ↓
fixture / team / player / research consumer
```
