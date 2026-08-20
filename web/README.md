# FRL Next.js foundation spike

This directory is the first reversible step of the FRL frontend migration.

## What this spike proves

- Next.js + React application structure.
- Current FRL warm-light colour system reproduced from `gui/theme.py`.
- Existing FRL typography hierarchy and restrained editorial styling as the visual target.
- A typed `ResearchResult<T>` contract.
- One Research Result driving both an interactive Plotly chart and an analytical table.
- Canonical fixture references carrying `(season, fixtureId)` rather than a bare fixture ID.
- A typed frontend/API boundary that explicitly keeps research logic in Python.

## What it does not do yet

- It does not replace Streamlit.
- It does not replace `query_api.py` or `query_lab.py`.
- It does not introduce a production FastAPI service yet.
- The demo data is intentionally static.

## Local development

Requirements: Node.js 20.9+.

```bash
cd web
npm install
npm run dev
```

Then open the local Next.js development URL shown by the command.

For production checks:

```bash
npm run typecheck
npm run build
```

The current package versions are intentionally pinned for this spike: Next.js 16.3.1, React 19.2.8, `react-plotly.js` 4.1.0 and Plotly.js 3.7.0.

## Next validation step

The foundation spike is not considered validated until the local environment proves:

1. the page renders;
2. the table and chart are driven by the same Research Result;
3. selecting a chart point changes the exact table/detail selection;
4. the current FRL palette and typography are visually faithful;
5. the project remains free/self-hostable;
6. the production adapter can be wired to the existing Python research/query seam without duplicating business logic.
