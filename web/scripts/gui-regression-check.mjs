import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd());
const explorerPath = path.join(root, "src", "components", "FixtureExplorer.tsx");
const cssPath = path.join(root, "src", "app", "globals.css");

function read(file) {
  if (!fs.existsSync(file)) {
    throw new Error(`Missing required file: ${path.relative(root, file)}`);
  }
  return fs.readFileSync(file, "utf8");
}

function assert(name, condition, detail) {
  if (!condition) throw new Error(`${name}: ${detail}`);
  console.log(`PASS  ${name}`);
}

const explorer = read(explorerPath);
const css = read(cssPath);

assert(
  "Team heading remains the context control",
  explorer.includes('className={`frl-team-title-button${teamMenuOpen ? " is-open" : ""}`}') &&
    explorer.includes('className="frl-title"'),
  "FixtureExplorer no longer contains the approved team-heading interaction."
);

assert(
  "Season remains a heading-level selector",
  explorer.includes('className="frl-context-control frl-context-control-season"') &&
    explorer.includes('aria-label="Season"'),
  "Season selector has been removed or moved out of the approved heading pattern."
);

assert(
  "Explore section remains present",
  explorer.includes('aria-label="Fixture exploration"') &&
    explorer.includes("Explore fixtures"),
  "The dedicated fixture exploration section is missing."
);

assert(
  "Core fixture filters remain present",
  ["Opponent", "Venue", "Result"].every((label) => explorer.includes(`aria-label=\"${label}\"`)),
  "One or more existing fixture filters has disappeared."
);

assert(
  "Multi-season viewing control exists",
  explorer.includes('aria-label="Fixture view"') &&
    explorer.includes('value="multi">Multiple seasons</option>'),
  "The single-season/multi-season exploration control is missing."
);

assert(
  "Multi-season period controls exist",
  explorer.includes('aria-label="From season"') &&
    explorer.includes('aria-label="To season"') &&
    explorer.includes('next.set("from",') &&
    explorer.includes('next.set("to",'),
  "Multi-season range selection is missing or not URL-backed."
);

assert(
  "Multi-season identity matching is persistent-code based",
  explorer.includes("persistent_team_code") &&
    explorer.includes("option.persistent_team_code === selectedPersistentTeamCode"),
  "Cross-season team selection must use verified persistent identity rather than display-name guessing."
);

assert(
  "Unavailable seasons fail closed",
  explorer.includes("excludedSeasons") &&
    explorer.includes("No verified team identity is present"),
  "The multi-season view must explicitly exclude unverified seasons rather than infer them."
);

assert(
  "Fixture navigation stays same-tab",
  explorer.includes('href={`/fixtures/${row.season}/${row.fixtureId}`}') &&
    !explorer.includes('target="_blank"'),
  "Fixture links must remain normal same-tab Next.js links."
);

assert(
  "Selectors remain integrated rather than boxed",
  css.includes(".frl-context-control select") &&
    css.includes("border:0") &&
    css.includes("background:transparent"),
  "The shared selector treatment has reverted to generic boxed inputs."
);

assert(
  "FRL visual tokens remain intact",
  ["--frl-bg: #f5f1e8", "--frl-accent: #e85d3f", "--frl-secondary: #9aaa42", "--frl-sidebar: #1b1b18"].every((token) => css.includes(token)),
  "One or more authoritative FRL visual tokens has changed unexpectedly."
);

assert(
  "No accidental Streamlit-style selector markup",
  !explorer.includes("stSelectbox") && !explorer.includes("stMultiSelect"),
  "Streamlit-specific selector markup has leaked into the Next.js frontend."
);

console.log("GUI REGRESSION CHECK: PASS");
