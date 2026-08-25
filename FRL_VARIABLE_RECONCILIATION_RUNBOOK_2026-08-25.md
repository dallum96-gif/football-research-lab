# FRL Variable Reconciliation — Local Runbook

The repository now contains the reconciliation contract and utility. The actual 477 baseline and broader source-universe manifest are not currently available as a single tracked repository input, so the final authoritative count must be generated from the local/source audit workspace rather than guessed.

## 1. Locate the two inventories

The inputs should be the most authoritative versions of:

- the existing mapped baseline (historically described as 477);
- the broader source-universe inventory (historically described as 1,414).

Do not manually type either count into the output.

## 2. Run

```powershell
python .\reconcile_variable_universe.py `
  --baseline "<PATH_TO_477_BASELINE>.csv" `
  --universe "<PATH_TO_BROAD_UNIVERSE>.csv" `
  --output ".\audit\variable_universe_reconciliation_2026-08-25.csv"
```

JSON inventories are also accepted.

## 3. Interpret

The output distinguishes:

- `MAPPED_VALIDATED`
- `MAPPED_VALIDATION_PENDING`
- `SOURCE_NATIVE_UNMAPPED`
- `ALIAS_OF_EXISTING`
- `DERIVED_VARIABLE`
- `DUPLICATE_SOURCE_FACET`
- `SEMANTICALLY_AMBIGUOUS`
- `TEMPORALLY_UNSAFE`
- `IDENTITY_UNRESOLVED`
- `OUT_OF_CANONICAL_BOUNDARY`
- `NOT_A_VARIABLE_METADATA`

The current utility automatically handles exact source-family + field + grain matches. It does **not** infer semantic equivalence from similar names.

## 4. Count the result

The authoritative headline should be generated from the reconciliation output, for example:

```text
Total reconciled source-variable facets: N
Canonical variables: N
Mapped + validated: N
Validation pending: N
Source-native unmapped: N
Aliases: N
Derived variables: N
Unresolved / unsafe: N
GUI-accessible: N
Resolver-accessible: N
```

Only after review should this count replace the legacy 477 / working 1,414 labels in project status documentation.

## 5. Verification

Run the normal FRL 26/26 research-test baseline and:

```powershell
.\project-health.ps1
```

The health gate should remain GREEN LIGHT. The known 2019–20 incomplete fixture warning should not be converted into fabricated data.
