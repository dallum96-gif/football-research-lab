# FRL Universal Variable Runtime Wiring V2

**Status:** Additive runtime expansion

The universal resolver now treats the empirical source-field layer as the runtime discovery surface. A variable does not need an individual Python handler: once a field is present in the requested season and source family, the existing generic research-field query seam resolves it.

This preserves the distinction between:

- discovered source field;
- semantically catalogued field;
- canonical FRL alias / derived metric;
- GUI display choice.

All source-native resolution remains season-aware and fails closed when the requested field is absent.

## Runtime rule

```text
requested variable
      ↓
canonical alias / source-field lookup
      ↓
requested context selects family
      ↓
empirical season field availability
      ↓
existing research_field_query
      ↓
source-family adapter + verified relationship bridge
      ↓
structured result + provenance
```

This makes the consumer interface broad without silently promoting every source field into a canonical FRL concept.
