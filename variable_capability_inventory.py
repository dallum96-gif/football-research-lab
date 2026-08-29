"""Deterministic FRL Variable Capability Inventory generator.

The inventory is an additive metadata view over governed FRL registries and
existing research/model seams.  It does not acquire evidence, alter source
data, or promote a discovered source field into an approved semantic contract.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from canonical_route_registry import load_routes, route_key, validate_route_registry
from canonical_variable_catalogue import canonical_variables
from fpl_variable_access import fpl_catalogue
from research_access import discover
from variable_resolver import ALIASES


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
INVENTORY_JSON = DATA_DIR / "frl_variable_capability_inventory_v1.json"
INVENTORY_CSV = DATA_DIR / "frl_variable_capability_inventory_v1.csv"
SUMMARY_JSON = DATA_DIR / "frl_variable_capability_summary_v1.json"

SCHEMA_VERSION = "1.0.0"
INVENTORY_VERSION = "FRL_VARIABLE_CAPABILITY_INVENTORY_V1"
GENERATOR_VERSION = "1.0.0"

CORE_SEASONS = (
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
)

CAPABILITY_AREAS = (
    "fixture",
    "events",
    "team_match",
    "team_season",
    "player_match",
    "player_season",
    "league_season",
    "context",
    "odds_markets",
    "derived_metrics",
    "models",
    "historical_as_of",
    "infrastructure",
)

ORIGIN_KINDS = (
    "SOURCE",
    "DERIVED",
    "MODEL_OUTPUT",
    "MARKET_INPUT",
    "INFRASTRUCTURE",
)

ASSESSMENT_STATUSES = (
    "ESTABLISHED",
    "CONDITIONAL",
    "NOT_APPLICABLE",
    "UNKNOWN",
    "REVIEW_REQUIRED",
)

PRODUCT_USES = (
    "Fixture",
    "Team Profile",
    "Team Stats",
    "Player Profile",
    "Player Stats",
    "League Stats",
    "Head-to-Head",
    "Prediction Lab",
    "modelling-only",
    "infrastructure-only",
)


FAMILY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "fixture": {
        "football_meaning": "Identity, schedule, participants, score and match-centre evidence for one canonical fixture.",
        "primary_grain": "fixture",
        "aggregation": "Fixture observations are not intrinsically aggregatable; individual numeric facets may feed governed higher-grain derivations.",
        "temporal": "Fixture event time, correction history and source retrieval time must remain distinguishable.",
        "limitations": ["Optional enrichment is not equivalent to canonical fixture existence."],
        "product_uses": ["Fixture", "Team Profile", "Head-to-Head"],
    },
    "events": {
        "football_meaning": "Chronological goals, cards, substitutions or commentary associated with one fixture.",
        "primary_grain": "fixture-event",
        "aggregation": "Event counts may be aggregated only after event type, identity and source completeness are established.",
        "temporal": "Event time belongs to the match timeline; retrieval time is separate and does not prove when information first became available.",
        "limitations": ["PulseLive and FPL event structures are not automatically interchangeable."],
        "product_uses": ["Fixture", "Player Profile", "Head-to-Head"],
    },
    "team_match": {
        "football_meaning": "One team's measured performance in one fixture.",
        "primary_grain": "team-match",
        "aggregation": "Many count fields are summable, while percentages, rates and provider-specific definitions require explicit aggregation rules.",
        "temporal": "A completed-match observation is historical state; information-availability time is not established by the value alone.",
        "limitations": ["The historical events_stats source is team-match aggregate evidence, not a chronological event stream."],
        "product_uses": ["Fixture", "Team Profile", "Team Stats", "League Stats", "Head-to-Head", "Prediction Lab"],
    },
    "team_season": {
        "football_meaning": "A team's season-level totals, rates, record or standing components derived from fixture evidence.",
        "primary_grain": "team-season",
        "aggregation": "Season totals are comparable only with schedule completeness, competition and denominator caveats made explicit.",
        "temporal": "Season-end values differ from season-to-date values and require an explicit as-of cut-off.",
        "limitations": ["The current URA has no separate atomic team-season source family; existing rows are derived through governed fixture queries."],
        "product_uses": ["Team Profile", "Team Stats", "League Stats", "Head-to-Head", "Prediction Lab"],
    },
    "player_match": {
        "football_meaning": "One player's participation or measured performance in one fixture or FPL gameweek observation.",
        "primary_grain": "player-match",
        "aggregation": "Counts may be aggregated with verified player/fixture identity; rates and position-sensitive metrics need denominators and comparability review.",
        "temporal": "Completed-match evidence is historical state; FPL gameweek snapshots and match observations retain distinct source semantics.",
        "limitations": ["Source player identifiers require the governed identity and relationship routes."],
        "product_uses": ["Fixture", "Player Profile", "Player Stats", "Head-to-Head", "Prediction Lab"],
    },
    "player_season": {
        "football_meaning": "A player's source-supplied or governed season aggregate.",
        "primary_grain": "player-season",
        "aggregation": "Source totals should not be re-summed across overlapping grains; cross-season and cross-position comparisons remain conditional.",
        "temporal": "A season total needs an explicit season-end or season-to-date interpretation.",
        "limitations": ["Some player-season fields are retained but not yet semantically approved for reusable exposure."],
        "product_uses": ["Player Profile", "Player Stats", "League Stats", "Head-to-Head", "Prediction Lab"],
    },
    "league_season": {
        "football_meaning": "League-wide standings, scoring environment, rankings and distributions for one season.",
        "primary_grain": "league-season",
        "aggregation": "League summaries are derived from a declared fixture population and must expose completeness and season scope.",
        "temporal": "Season-end and as-of league views are distinct; current league-table code is based on completed fixtures in the requested season.",
        "limitations": ["No generic league-wide variable family is currently exposed by URA."],
        "product_uses": ["Team Profile", "Team Stats", "League Stats", "Head-to-Head", "Prediction Lab"],
    },
    "context": {
        "football_meaning": "Identity, venue, gameweek, score state, availability, profile and situational context used to interpret football observations.",
        "primary_grain": "explicit-source-context",
        "aggregation": "Identifiers and labels are not measures; contextual categories require declared grouping semantics.",
        "temporal": "Context may describe event time, a snapshot, or pre-match state; those meanings must not be collapsed.",
        "limitations": ["Many raw configuration/profile fields remain semantically unclassified."],
        "product_uses": ["Fixture", "Team Profile", "Player Profile", "Team Stats", "Player Stats", "League Stats", "Head-to-Head", "Prediction Lab"],
    },
    "odds_markets": {
        "football_meaning": "Explicit bookmaker price inputs and market-derived probabilities or edges.",
        "primary_grain": "odds-market-observation",
        "aggregation": "Market values require bookmaker, market, selection and observation-time identity; the current calculator does not preserve such a history.",
        "temporal": "Prediction time and market observation time are essential and are not persisted by the current user-input calculator.",
        "limitations": ["FRL currently has no governed historical odds dataset."],
        "product_uses": ["Prediction Lab", "modelling-only"],
    },
    "derived_metrics": {
        "football_meaning": "An FRL calculation whose source inputs and formula are explicitly identified.",
        "primary_grain": "inherits-input-grain",
        "aggregation": "A derived metric inherits the comparability and coverage limits of every input and must be recomputed at the intended grain.",
        "temporal": "A derivation is only as-of safe as its latest input and construction order.",
        "limitations": ["Derived status does not create missing source evidence or remove source-rights dependencies."],
        "product_uses": ["Team Stats", "Player Stats", "League Stats", "Head-to-Head", "Prediction Lab", "modelling-only"],
    },
    "models": {
        "football_meaning": "Outputs of an explicit predictive model, kept separate from observed football evidence.",
        "primary_grain": "model-output",
        "aggregation": "Model outputs are comparable only within a declared model version, target population and prediction-time information set.",
        "temporal": "Inputs knowable at prediction time must be distinguished from later outcomes; current Poisson V0.1 has fixed source/target seasons.",
        "limitations": ["Poisson V0.1 is a bounded current model, not a universal calibrated historical forecast archive."],
        "product_uses": ["Prediction Lab", "modelling-only"],
    },
    "historical_as_of": {
        "football_meaning": "Historical state constructed using only evidence available before a declared fixture or date cut-off.",
        "primary_grain": "fixture-pre-match-state",
        "aggregation": "Historical features may be compared when construction version, lookback window and as-of cut-off match.",
        "temporal": "The V2 match-state artifact records feature_as_of and prior-fixture provenance; outcome columns are labels, not pre-match inputs.",
        "limitations": ["URA request-time information availability remains distinct and is not inferred from ordinary historical observations."],
        "product_uses": ["Team Stats", "League Stats", "Head-to-Head", "Prediction Lab", "modelling-only"],
    },
    "infrastructure": {
        "football_meaning": "Acquisition, transport, registry or provenance metadata retained to operate and audit FRL, not football performance evidence.",
        "primary_grain": "infrastructure-record",
        "aggregation": "Not applicable as a football statistic.",
        "temporal": "Retrieval and capture timestamps are provenance times, not match-event or information-availability semantics.",
        "limitations": ["Must not be surfaced as a football variable merely because it appears in a raw payload."],
        "product_uses": ["infrastructure-only"],
    },
}


FIELD_MEANINGS = {
    "season": "FRL season identity.",
    "fixture_id": "Canonical fixture identifier within an FRL season.",
    "fixture_code": "Source fixture code retained when supplied.",
    "kickoff_time": "Canonical fixture kickoff timestamp.",
    "gameweek": "Competition gameweek associated with the observation.",
    "home_team_id": "Canonical season-local home-team identifier.",
    "away_team_id": "Canonical season-local away-team identifier.",
    "home_score": "Home-team goals recorded for the fixture.",
    "away_score": "Away-team goals recorded for the fixture.",
    "possessionPercentage": "Share of recorded possession attributed to the team in the fixture.",
    "totalScoringAtt": "Total scoring attempts recorded by the source.",
    "ontargetScoringAtt": "Scoring attempts recorded as on target.",
    "accuratePass": "Passes recorded as accurate by the source.",
    "totalPass": "Passes recorded by the source.",
    "minutesPlayed": "Minutes of player participation recorded for the fixture.",
    "goals": "Goals credited to the player by the source.",
    "goalAssist": "Goal assists credited to the player by the source.",
    "expectedGoals": "Expected-goals value supplied by the source; provider methodology is not defined by FRL.",
    "expectedAssists": "Expected-assists value supplied by the source; provider methodology is not defined by FRL.",
    "played": "Completed league fixtures counted for the team.",
    "wins": "Completed league fixtures won by the team.",
    "draws": "Completed league fixtures drawn by the team.",
    "losses": "Completed league fixtures lost by the team.",
    "goals_for": "Goals scored by the team in the declared population.",
    "goals_against": "Goals conceded by the team in the declared population.",
    "goal_difference": "Goals for minus goals against in the declared population.",
    "points": "League points derived from completed fixture results.",
    "position": "League position after points, goal difference and goals-for ordering.",
}


PROVENANCE_FILES = (
    "data/frl_canonical_variable_dictionary_v1.csv",
    "data/frl_canonical_variable_routes_v1.csv",
    "data/fpl_canonical_variable_registry_v1.csv",
    "fixtures_master_corrected.csv",
    "features/historical_match_state_v2.csv",
    "canonical_variable_catalogue.py",
    "canonical_route_registry.py",
    "fpl_variable_access.py",
    "research_access.py",
    "variable_resolver.py",
    "source_field_registry.py",
    "query_lab.py",
    "poisson_model.py",
    "kelly_analysis.py",
    "FRL_SOURCE_RIGHTS_REGISTER.md",
)


CSV_COLUMNS = (
    "record_id",
    "canonical_name",
    "capability_family",
    "capability_areas",
    "football_meaning_status",
    "football_meaning",
    "grain",
    "grain_status",
    "origin_kind",
    "source_family",
    "source_surface",
    "source_resource",
    "source_native_fields",
    "transformation_kind",
    "transformation_status",
    "transformation_route",
    "coverage_status",
    "coverage_summary",
    "seasons_observed",
    "season_count",
    "population",
    "aggregation_status",
    "aggregation_summary",
    "temporal_state",
    "information_available_as_of",
    "major_limitations",
    "likely_product_uses",
    "rights_status",
    "acquisition_classification",
    "semantic_status",
    "ura_exposure",
    "route_status",
    "attachment_verified",
)


def _read_csv(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def _csv_profile(path: Path) -> dict[str, Any]:
    rows = _read_csv(path)
    seasons = sorted(
        {
            str(row.get("season") or row.get("frl_season") or "").strip()
            for row in rows
            if str(row.get("season") or row.get("frl_season") or "").strip()
        }
    )
    fields = tuple(rows[0].keys()) if rows else ()
    if not fields:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            fields = tuple(next(csv.reader(handle), ()))
    return {"rows": rows, "row_count": len(rows), "seasons": seasons, "fields": fields}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rights(source_surface: str) -> dict[str, str]:
    if source_surface in {"FRL_LOCAL_CSV", "FPL_GAMEWEEK_ARCHIVE"}:
        return {
            "status": "REVIEW REQUIRED",
            "acquisition_classification": "Downloaded/local GitHub-hosted Imadeddine source; underlying PL/FPL-origin data rights remain under review.",
            "governance_source": "FRL_SOURCE_RIGHTS_REGISTER.md",
        }
    if source_surface == "fpl":
        return {
            "status": "REVIEW REQUIRED",
            "acquisition_classification": "FPL-origin payload evidence; public availability does not establish unrestricted reuse.",
            "governance_source": "FRL_SOURCE_RIGHTS_REGISTER.md",
        }
    if source_surface == "pulselive":
        return {
            "status": "REVIEW REQUIRED / DO NOT ASSUME REDISTRIBUTION RIGHTS",
            "acquisition_classification": "Direct Premier League / PulseLive snapshot acquisition preserved locally.",
            "governance_source": "FRL_SOURCE_RIGHTS_REGISTER.md",
        }
    if source_surface in {"FRL_CANONICAL", "FRL_DERIVED", "FRL_MODEL", "local_json"}:
        return {
            "status": "INHERITS SOURCE DEPENDENCIES",
            "acquisition_classification": "FRL-constructed artifact; upstream lineage and rights obligations remain attached.",
            "governance_source": "FRL_SOURCE_RIGHTS_REGISTER.md",
        }
    if source_surface == "USER_INPUT":
        return {
            "status": "NOT_APPLICABLE_TO_PERSISTED_SOURCE",
            "acquisition_classification": "Ephemeral user input; no historical market source is acquired or preserved.",
            "governance_source": "FRL_SOURCE_RIGHTS_REGISTER.md",
        }
    return {
        "status": "UNKNOWN",
        "acquisition_classification": "Source-rights classification is not established.",
        "governance_source": "FRL_SOURCE_RIGHTS_REGISTER.md",
    }


def _source_family(source_surface: str) -> str:
    return {
        "FRL_LOCAL_CSV": "IMadeddine historical Premier League statistics",
        "FPL_GAMEWEEK_ARCHIVE": "IMadeddine historical FPL gameweek archive",
        "fpl": "Fantasy Premier League payload",
        "pulselive": "Premier League / PulseLive match centre",
        "local_json": "FRL acquisition manifest",
        "FRL_CANONICAL": "FRL canonical fixture layer",
        "FRL_DERIVED": "FRL governed derivation",
        "FRL_MODEL": "FRL Poisson V0.1",
        "USER_INPUT": "User-supplied market observation",
    }.get(source_surface, "UNKNOWN")


def _is_infrastructure(row: dict[str, str]) -> bool:
    surface = row.get("source_surface", "")
    field = row.get("field_name", "")
    if surface == "local_json":
        return True
    if surface != "pulselive":
        return False
    return (
        ".headers" in field
        or field.endswith(".endpoint")
        or ".params" in field
        or field.endswith(".status_code")
        or field in {"retrieved_at", "source", "source_match_id", "resources"}
    )


def _fpl_family_and_grain(field: str, resource: str) -> tuple[str, str, list[str]]:
    if resource == "event":
        return "player_match", "player-gameweek-live", ["player_match", "events"]
    if field.startswith("history_past[]"):
        return "player_season", "player-season", ["player_season"]
    if field.startswith("history[]"):
        return "player_match", "player-fixture-gameweek", ["player_match"]
    if field.startswith("fixtures[]"):
        return "fixture", "player-fixture-forecast", ["fixture", "context"]
    if field.startswith("elements[]"):
        return "player_season", "player-snapshot", ["player_season", "context"]
    if field.startswith("teams[]"):
        return "team_season", "team-snapshot", ["team_season", "context"]
    return "context", "fpl-configuration-snapshot", ["context"]


def _catalogue_family_and_grain(row: dict[str, str]) -> tuple[str, str, list[str]]:
    surface = row.get("source_surface", "")
    resource = row.get("resource", "")
    field = row.get("field_name", "")
    if _is_infrastructure(row):
        return "infrastructure", "acquisition-metadata", ["infrastructure"]
    if surface == "FRL_LOCAL_CSV":
        if resource == "squad":
            return "context", "player-season-profile", ["context", "player_season"]
        family = resource if resource in {"team_match", "player_match", "player_season"} else "context"
        return family, resource.replace("_", "-"), [family]
    if surface == "fpl":
        return _fpl_family_and_grain(field, resource)
    if surface == "pulselive":
        if field.startswith("resources.events"):
            grain = "fixture-event" if any(token in field for token in ("cards[]", "goals[]", "subs[]")) else "fixture-event-collection"
            return "events", grain, ["events", "fixture"]
        if field.startswith("resources.commentary"):
            grain = "fixture-commentary-entry" if "payload.data[]" in field else "fixture-commentary"
            return "events", grain, ["events", "fixture"]
        if field.startswith("resources.stats"):
            return "team_match", "team-match", ["team_match", "fixture"]
        if field.startswith("resources.lineups"):
            if ".players[]" in field:
                grain = "fixture-lineup-player"
            elif ".managers[]" in field:
                grain = "fixture-lineup-manager"
            else:
                grain = "fixture-team-lineup"
            return "fixture", grain, ["fixture", "context"]
        return "fixture", "fixture", ["fixture", "context"]
    return "infrastructure", "unknown", ["infrastructure"]


def _meaning(row: dict[str, str], family: str) -> dict[str, str]:
    field = row.get("field_name", "")
    leaf = re.sub(r"\[\]", "", field).split(".")[-1]
    if family == "infrastructure":
        return {"status": "ESTABLISHED", "text": "Acquisition or provenance metadata; not football performance evidence."}
    if field in FIELD_MEANINGS:
        return {"status": "ESTABLISHED", "text": FIELD_MEANINGS[field]}
    if leaf in FIELD_MEANINGS:
        return {"status": "ESTABLISHED", "text": FIELD_MEANINGS[leaf]}
    category = row.get("navigation_subcategory") or row.get("navigation_category") or "unclassified football evidence"
    return {
        "status": "REVIEW_REQUIRED",
        "text": f"Source-native field '{field}' associated with {category}; its exact provider definition has not been separately approved by FRL.",
    }


def _catalogue_coverage(row: dict[str, str]) -> dict[str, Any]:
    surface = row.get("source_surface", "")
    notes = row.get("notes", "")
    if surface == "FRL_LOCAL_CSV":
        match = re.search(r"coverage=([^;]+); seasons=(\d+)/(\d+)", notes)
        if match:
            label, count, total = match.groups()
            count_i = int(count)
            return {
                "status": "DECLARED_FULL" if count_i == int(total) else "DECLARED_PARTIAL",
                "summary": f"Canonical catalogue declares {label}: field present in {count}/{total} core seasons.",
                "seasons_observed": list(CORE_SEASONS) if count_i == len(CORE_SEASONS) else [],
                "season_count": count_i,
                "population": None,
                "basis": ["data/frl_canonical_variable_dictionary_v1.csv"],
            }
        return {
            "status": "UNKNOWN",
            "summary": "No season coverage declaration is present in the canonical catalogue.",
            "seasons_observed": [],
            "season_count": None,
            "population": None,
            "basis": ["data/frl_canonical_variable_dictionary_v1.csv"],
        }
    if surface in {"fpl", "pulselive"}:
        return {
            "status": "DISCOVERY_SAMPLE_ONLY",
            "summary": "Observed in governed raw discovery payloads; this is not a season or fixture coverage claim.",
            "seasons_observed": [],
            "season_count": None,
            "population": None,
            "basis": [notes] if notes else [],
        }
    return {
        "status": "PROVENANCE_ONLY",
        "summary": "Capture metadata is present but does not establish football evidence coverage.",
        "seasons_observed": [],
        "season_count": None,
        "population": None,
        "basis": [notes] if notes else [],
    }


def _aggregation(row: dict[str, str], family: str) -> dict[str, str]:
    field_type = row.get("field_type", "unknown")
    field = row.get("field_name", "").casefold()
    if family == "infrastructure" or field_type in {"object", "NoneType"}:
        return {"status": "NOT_APPLICABLE", "summary": "Not an atomic football measure suitable for aggregation."}
    if any(token in field for token in ("id", "name", "position", "formation", "kickoff", "timestamp", "period", "type", "status")):
        return {"status": "NOT_APPLICABLE", "summary": "Identity or contextual evidence; group/filter rather than sum."}
    if family in {"team_match", "player_match", "player_season", "team_season"}:
        return {"status": "CONDITIONAL", "summary": FAMILY_DEFINITIONS[family]["aggregation"]}
    if family in {"fixture", "events", "context"}:
        return {"status": "REVIEW_REQUIRED", "summary": FAMILY_DEFINITIONS[family]["aggregation"]}
    return {"status": "UNKNOWN", "summary": "Aggregation and cross-source comparability have not been established."}


def _temporal(source_surface: str, family: str) -> dict[str, Any]:
    if source_surface == "pulselive":
        state = "MATCH_EVENT_OR_RETRIEVAL_STATE"
        note = "PulseLive match/event time and snapshot retrieval time remain distinct."
    elif source_surface == "fpl":
        state = "FPL_SNAPSHOT_OR_GAMEWEEK_STATE"
        note = "FPL snapshot/gameweek state is source-native; first information-availability time is not established."
    elif family == "player_season":
        state = "SEASON_AGGREGATE_STATE"
        note = "Season-end versus season-to-date interpretation must be established by the query context."
    elif family in {"team_match", "player_match", "events", "fixture"}:
        state = "MATCH_OBSERVATION_STATE"
        note = "The observation belongs to a fixture; that alone does not establish when the information entered FRL."
    else:
        state = "SOURCE_CONTEXT_STATE"
        note = "Temporal semantics require source-specific review."
    return {
        "status": "CONDITIONAL",
        "state_semantics": state,
        "information_available_as_of": "UNKNOWN",
        "historical_state_and_information_availability_distinct": True,
        "summary": note,
    }


def _product_uses(family: str, origin_kind: str) -> list[str]:
    if origin_kind == "INFRASTRUCTURE":
        return ["infrastructure-only"]
    return list(FAMILY_DEFINITIONS[family]["product_uses"])


def _route_for(row: dict[str, str], route: dict[str, str] | None, ura_exposure: str) -> dict[str, Any]:
    if route:
        steps = [
            route.get(key, "")
            for key in ("player_route", "fixture_route", "team_route")
            if route.get(key, "")
        ]
        if not steps:
            steps = [route.get("route_status", "")]
        return {
            "kind": "SOURCE_NATIVE_WITH_DECLARED_ROUTE",
            "status": route.get("attachment_verified") or "UNKNOWN",
            "route": steps,
        }
    if row.get("source_surface") == "fpl" and ura_exposure == "URA_DISCOVERABLE":
        return {
            "kind": "SOURCE_NATIVE_FPL_ACCESS",
            "status": "UNMAPPED_REVIEW",
            "route": ["authoritative FPL variable registry", "fpl_variable_access.py", "Universal Research Access"],
        }
    return {
        "kind": "SOURCE_NATIVE_PRESERVED",
        "status": "REVIEW_REQUIRED",
        "route": ["canonical variable catalogue"],
    }


def _base_limitations(row: dict[str, str], meaning_status: str, route: dict[str, str] | None) -> list[str]:
    limits: list[str] = []
    if meaning_status != "ESTABLISHED":
        limits.append("Exact football semantics remain REVIEW_REQUIRED; the source-native name is preserved without reinterpretation.")
    if row.get("source_surface") in {"fpl", "pulselive"}:
        limits.append("Discovery in sample payloads does not establish historical coverage or current materialisation.")
    if route and route.get("attachment_verified") == "NOT_YET_PROVEN":
        limits.append("The declared canonical attachment route is NOT_YET_PROVEN in the route registry.")
    if row.get("canonical_attachment") == "UNMAPPED_REVIEW":
        limits.append("Canonical attachment remains UNMAPPED_REVIEW.")
    return limits


def _record(
    *,
    record_id: str,
    canonical_name: str,
    family: str,
    areas: Iterable[str],
    meaning: dict[str, str],
    grain: str,
    grain_status: str,
    origin_kind: str,
    source_surface: str,
    source_resource: str,
    source_native_fields: Iterable[str],
    transformation: dict[str, Any],
    coverage: dict[str, Any],
    aggregation: dict[str, str],
    temporal: dict[str, Any],
    limitations: Iterable[str],
    governance: dict[str, Any],
    product_uses: Iterable[str] | None = None,
) -> dict[str, Any]:
    area_list = list(dict.fromkeys(areas))
    for area in area_list:
        if area not in CAPABILITY_AREAS:
            raise ValueError(f"Unknown capability area: {area}")
    if family not in CAPABILITY_AREAS:
        raise ValueError(f"Unknown capability family: {family}")
    if origin_kind not in ORIGIN_KINDS:
        raise ValueError(f"Unknown origin kind: {origin_kind}")
    if meaning.get("status") not in ASSESSMENT_STATUSES:
        raise ValueError(f"Unknown meaning status: {meaning.get('status')}")
    uses = list(dict.fromkeys(product_uses or _product_uses(family, origin_kind)))
    for use in uses:
        if use not in PRODUCT_USES:
            raise ValueError(f"Unknown product use: {use}")
    return {
        "record_id": record_id,
        "canonical_name": canonical_name,
        "capability_family": family,
        "capability_areas": area_list,
        "football_meaning": meaning,
        "grain": {"name": grain, "status": grain_status},
        "origin_kind": origin_kind,
        "source": {
            "family": _source_family(source_surface),
            "surface": source_surface,
            "resource": source_resource,
            "native_fields": list(source_native_fields),
        },
        "transformation": transformation,
        "coverage": coverage,
        "aggregation_comparability": aggregation,
        "temporal_as_of": temporal,
        "major_limitations": list(dict.fromkeys(limitations)),
        "likely_product_uses": uses,
        "source_rights": _rights(source_surface),
        "governance": governance,
    }


def _catalogue_records(root: Path) -> list[dict[str, Any]]:
    del root  # authoritative registry modules are rooted beside this generator
    routes = {route_key(row): row for row in load_routes()}
    ura_results = discover()["results"]
    ura_keys = {(item["family"], item["variable"]) for item in ura_results}
    fpl_rows = {
        (row.get("source_surface", ""), row.get("resource", ""), row.get("grain", ""), row.get("field_name", "")): row
        for row in _read_csv(DATA_DIR / "fpl_canonical_variable_registry_v1.csv")
    }
    alias_by_family_name = {(definition.family, name): definition for name, definition in ALIASES.items()}
    records: list[dict[str, Any]] = []
    for row in canonical_variables():
        key = (
            row.get("source_surface", ""),
            row.get("resource", ""),
            row.get("grain", ""),
            row.get("field_name", ""),
        )
        family, grain, areas = _catalogue_family_and_grain(row)
        if row.get("source_surface") == "FRL_LOCAL_CSV":
            ura_family = "squad" if row.get("resource") == "squad" else row.get("resource", "")
        elif row.get("source_surface") == "fpl":
            ura_family = "fpl"
        else:
            ura_family = ""
        is_discoverable = (ura_family, row.get("field_name", "")) in ura_keys
        alias = alias_by_family_name.get((ura_family, row.get("field_name", "")))
        ura_exposure = "URA_RUNTIME_EXPOSED" if alias is not None else ("URA_DISCOVERABLE" if is_discoverable else "NOT_EXPOSED_BY_URA")
        meaning = _meaning(row, family)
        route = routes.get(key)
        fpl_governance = fpl_rows.get(key, {})
        origin_kind = "INFRASTRUCTURE" if family == "infrastructure" else "SOURCE"
        governance = {
            "catalogue": "FRL canonical variable catalogue",
            "semantic_status": row.get("semantic_status") or "UNKNOWN",
            "navigation_category": row.get("navigation_category") or "UNKNOWN",
            "navigation_subcategory": row.get("navigation_subcategory") or "UNKNOWN",
            "canonical_attachment": row.get("canonical_attachment") or "UNKNOWN",
            "relationship_kind": row.get("relationship_kind") or "UNKNOWN",
            "identity_contract": row.get("identity_contract") or "UNKNOWN",
            "source_identity_required": str(row.get("source_identity_required", "")).upper() == "TRUE",
            "ura_exposure": ura_exposure,
            "fpl_research_exposed": fpl_governance.get("research_exposed") or "NOT_APPLICABLE",
            "route_status": route.get("route_status") if route else "NO_DECLARED_ROUTE",
            "attachment_verified": route.get("attachment_verified") if route else "NO_DECLARED_ROUTE",
        }
        if alias and alias.definition:
            governance["resolver_definition"] = alias.definition
        records.append(
            _record(
                record_id="catalogue:" + ":".join(key),
                canonical_name=row.get("field_name", ""),
                family=family,
                areas=areas,
                meaning=meaning,
                grain=grain,
                grain_status="ESTABLISHED" if row.get("grain") != "sample_payload" else "CONDITIONAL",
                origin_kind=origin_kind,
                source_surface=row.get("source_surface", "UNKNOWN"),
                source_resource=row.get("resource", "UNKNOWN"),
                source_native_fields=[row.get("field_name", "")],
                transformation=_route_for(row, route, ura_exposure),
                coverage=_catalogue_coverage(row),
                aggregation=_aggregation(row, family),
                temporal=_temporal(row.get("source_surface", ""), family),
                limitations=_base_limitations(row, meaning["status"], route),
                governance=governance,
            )
        )
    return records


def _artifact_coverage(profile: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "status": "MATERIALISED",
        "summary": f"Tracked artifact contains {profile['row_count']} rows across {len(profile['seasons'])} seasons.",
        "seasons_observed": list(profile["seasons"]),
        "season_count": len(profile["seasons"]),
        "population": profile["row_count"],
        "basis": [source],
    }


def _canonical_fixture_records(root: Path) -> list[dict[str, Any]]:
    source = root / "fixtures_master_corrected.csv"
    profile = _csv_profile(source)
    records = []
    for field in profile["fields"]:
        meaning = {
            "status": "ESTABLISHED" if field in FIELD_MEANINGS else "REVIEW_REQUIRED",
            "text": FIELD_MEANINGS.get(field, f"Canonical fixture field '{field}'; exact consumer meaning requires review."),
        }
        records.append(
            _record(
                record_id=f"canonical_fixture:fixtures_master_corrected.csv:{field}",
                canonical_name=field,
                family="fixture",
                areas=["fixture", "context"],
                meaning=meaning,
                grain="fixture",
                grain_status="ESTABLISHED",
                origin_kind="SOURCE",
                source_surface="FRL_CANONICAL",
                source_resource="fixtures_master_corrected.csv",
                source_native_fields=[field],
                transformation={
                    "kind": "CANONICAL_CONSTRUCTION",
                    "status": "GOVERNED",
                    "route": ["source fixture evidence", "identity/team_seasons.csv", "fixture corrections", "fixtures_master_corrected.csv"],
                },
                coverage=_artifact_coverage(profile, "fixtures_master_corrected.csv"),
                aggregation={"status": "NOT_APPLICABLE", "summary": "Canonical fixture identity/context is not itself a statistic."},
                temporal={
                    "status": "ESTABLISHED",
                    "state_semantics": "CANONICAL_FIXTURE_EVENT_TIME_WITH_CORRECTION_PROVENANCE",
                    "information_available_as_of": "UNKNOWN",
                    "historical_state_and_information_availability_distinct": True,
                    "summary": "Canonical scheduled/event state preserves governed correction history; first information availability is not inferred.",
                },
                limitations=["Canonical fixture fields establish fixture identity/state, not optional rich evidence coverage."],
                governance={
                    "catalogue": "fixtures_master_corrected.csv",
                    "semantic_status": "CANONICAL",
                    "ura_exposure": "OTHER_GOVERNED_QUERY_SEAM",
                    "route_status": "CANONICAL_FIXTURE_ROUTE",
                    "attachment_verified": "GOVERNED",
                },
            )
        )
    return records


def _historical_feature_meaning(field: str) -> dict[str, str]:
    if field == "feature_as_of":
        return {"status": "ESTABLISHED", "text": "Cut-off timestamp at which the pre-match feature row is constructed."}
    if field.endswith("_rest_days"):
        return {"status": "ESTABLISHED", "text": "Days between the current kickoff and the team's latest prior completed fixture."}
    if field.endswith("_latest_prior_kickoff"):
        return {"status": "ESTABLISHED", "text": "Kickoff timestamp of the latest completed fixture included in prior history."}
    if "last5" in field:
        return {"status": "ESTABLISHED", "text": "Five-match-window pre-fixture team state; home/away qualifiers are preserved in the field name."}
    if field.endswith("_prior"):
        return {"status": "ESTABLISHED", "text": "Season-to-date team state calculated from completed fixtures before the current fixture."}
    if field in FIELD_MEANINGS:
        return {"status": "ESTABLISHED", "text": FIELD_MEANINGS[field]}
    if field in {"fixture_completed"}:
        return {"status": "ESTABLISHED", "text": "Outcome-label flag describing whether the current fixture is completed; not a pre-match predictor."}
    return {"status": "REVIEW_REQUIRED", "text": f"Field '{field}' in the governed historical match-state V2 artifact; exact usage requires review."}


def _historical_feature_records(root: Path) -> list[dict[str, Any]]:
    source = root / "features" / "historical_match_state_v2.csv"
    profile = _csv_profile(source)
    records = []
    label_fields = {"home_score", "away_score", "fixture_completed"}
    passthrough = {"season", "fixture_id", "fixture_code", "kickoff_time", "gameweek", "home_team_id", "away_team_id"}
    for field in profile["fields"]:
        areas = ["context", "historical_as_of"]
        if field not in passthrough and field not in label_fields:
            areas.append("derived_metrics")
        limits = ["Construction version is V2 and must not be silently conflated with historical_match_state_v1.csv."]
        uses = ["Team Stats", "Head-to-Head", "Prediction Lab", "modelling-only"]
        if field in label_fields:
            limits.append("Current-fixture outcome evidence is a target/label and must not be used as a pre-match input.")
            uses = ["modelling-only"]
        records.append(
            _record(
                record_id=f"historical_state_v2:{field}",
                canonical_name=field,
                family="context",
                areas=areas,
                meaning=_historical_feature_meaning(field),
                grain="fixture-pre-match-state",
                grain_status="ESTABLISHED",
                origin_kind="DERIVED",
                source_surface="FRL_DERIVED",
                source_resource="features/historical_match_state_v2.csv",
                source_native_fields=[field],
                transformation={
                    "kind": "TEMPORAL_DERIVATION",
                    "status": "GOVERNED",
                    "route": ["fixtures_master_corrected.csv", "chronological completed-fixture history", "historical_match_state_v2.csv"],
                },
                coverage=_artifact_coverage(profile, "features/historical_match_state_v2.csv"),
                aggregation={"status": "CONDITIONAL", "summary": "Comparable only with the same V2 lookback, venue and as-of construction semantics."},
                temporal={
                    "status": "ESTABLISHED",
                    "state_semantics": "PRE_MATCH_AS_OF_FIXTURE_KICKOFF" if field not in label_fields else "POST_MATCH_OUTCOME_LABEL",
                    "information_available_as_of": "FEATURE_AS_OF_FOR_DECLARED_INPUTS",
                    "historical_state_and_information_availability_distinct": True,
                    "summary": "Prior features are constructed before the current fixture enters team history; outcome labels remain explicitly separate.",
                },
                limitations=limits,
                governance={
                    "catalogue": "historical_match_state_v2.csv header",
                    "semantic_status": "DERIVED",
                    "ura_exposure": "MODELLING_ARTIFACT_NOT_URA",
                    "route_status": "TEMPORAL_CONSTRUCTION",
                    "attachment_verified": "GOVERNED_BY_TEMPORAL_TESTS",
                },
                product_uses=uses,
            )
        )
    return records


def _historical_player_field_coverage(root: Path, field: str) -> dict[str, Any]:
    seasons: list[str] = []
    for path in sorted((root / "_merged" / "players").glob("*_all_players_gw.csv")):
        fields: list[str] = []
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                with path.open("r", encoding=encoding, newline="") as handle:
                    fields = next(csv.reader(handle), [])
                break
            except UnicodeDecodeError:
                continue
        if field in fields:
            seasons.append(path.name.removesuffix("_all_players_gw.csv"))
    return {
        "status": "DECLARED_FULL" if tuple(seasons) == CORE_SEASONS else ("DECLARED_PARTIAL" if seasons else "MATERIALISATION_MISSING"),
        "summary": f"Historical player/gameweek files expose '{field}' in {len(seasons)}/{len(CORE_SEASONS)} core seasons.",
        "seasons_observed": seasons,
        "season_count": len(seasons),
        "population": None,
        "basis": ["_merged/players/*_all_players_gw.csv headers"],
    }


def _resolver_records(root: Path, existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing_names = {(record["source"]["surface"], record["canonical_name"]) for record in existing}
    records: list[dict[str, Any]] = []
    for name, definition in sorted(ALIASES.items()):
        if definition.derived_from:
            records.append(
                _record(
                    record_id=f"ura_derived:{definition.family}:{name}",
                    canonical_name=name,
                    family="derived_metrics",
                    areas=["derived_metrics", definition.family],
                    meaning={"status": "ESTABLISHED", "text": definition.definition or definition.label},
                    grain=definition.family.replace("_", "-"),
                    grain_status="ESTABLISHED",
                    origin_kind="DERIVED",
                    source_surface="FRL_DERIVED",
                    source_resource="variable_resolver.py",
                    source_native_fields=list(definition.derived_from),
                    transformation={
                        "kind": "EXPLICIT_FORMULA",
                        "status": "URA_RUNTIME_EXPOSED",
                        "route": [f"{definition.derived_from[0]} / {definition.derived_from[1]} * 100", "variable_resolver.resolve_variable"],
                    },
                    coverage={
                        "status": "INHERITS_INPUT_COVERAGE",
                        "summary": "Available only where both source inputs are present and the denominator is non-zero.",
                        "seasons_observed": [],
                        "season_count": None,
                        "population": None,
                        "basis": list(definition.derived_from),
                    },
                    aggregation={"status": "CONDITIONAL", "summary": "Recompute from aggregated numerator and denominator; do not average row percentages."},
                    temporal={
                        "status": "CONDITIONAL",
                        "state_semantics": "INHERITS_INPUT_MATCH_STATE",
                        "information_available_as_of": "INHERITS_LATEST_INPUT",
                        "historical_state_and_information_availability_distinct": True,
                        "summary": "The derived percentage inherits both input fields' temporal and provenance limits.",
                    },
                    limitations=["Returns unavailable when the denominator is zero/missing or either source input is absent."],
                    governance={
                        "catalogue": "variable_resolver.ALIASES",
                        "semantic_status": "DERIVED",
                        "ura_exposure": "URA_RUNTIME_EXPOSED",
                        "route_status": "EXPLICIT_FORMULA",
                        "attachment_verified": "EXISTING_IDENTITY_ROUTE",
                    },
                    product_uses=["Player Profile", "Player Stats", "Head-to-Head", "Prediction Lab"],
                )
            )
        elif name == "dribbles" and ("fpl", name) not in existing_names:
            records.append(
                _record(
                    record_id="ura_alias:fpl:dribbles",
                    canonical_name=name,
                    family="player_match",
                    areas=["player_match"],
                    meaning={"status": "ESTABLISHED", "text": definition.definition or definition.label},
                    grain="player-fixture-gameweek",
                    grain_status="ESTABLISHED",
                    origin_kind="SOURCE",
                    source_surface="FPL_GAMEWEEK_ARCHIVE",
                    source_resource="_merged/players/*_all_players_gw.csv",
                    source_native_fields=[definition.source_field or name],
                    transformation={
                        "kind": "SOURCE_NATIVE_FPL_ACCESS",
                        "status": "URA_RUNTIME_EXPOSED",
                        "route": ["historical_player_fixture_values", "variable_resolver.resolve_variable", "Universal Research Access"],
                    },
                    coverage=_historical_player_field_coverage(root, definition.source_field or name),
                    aggregation={"status": "CONDITIONAL", "summary": "Source-native player-fixture count; cross-season source comparability remains under review."},
                    temporal=_temporal("fpl", "player_match"),
                    limitations=["FPL source semantics remain distinct from similarly named Player-Match statistics."],
                    governance={
                        "catalogue": "variable_resolver.ALIASES",
                        "semantic_status": "exposed",
                        "ura_exposure": "URA_RUNTIME_EXPOSED",
                        "route_status": "HISTORICAL_FPL_PLAYER_FIXTURE_ROUTE",
                        "attachment_verified": "SOURCE_FIXTURE_FIELD",
                    },
                    product_uses=["Fixture", "Player Profile", "Player Stats", "Head-to-Head"],
                )
            )
    return records


def _league_records(root: Path) -> list[dict[str, Any]]:
    fixture_profile = _csv_profile(root / "fixtures_master_corrected.csv")
    specs = {
        "team": ("team_season", "Team name resolved through the verified season identity registry."),
        "played": ("team_season", FIELD_MEANINGS["played"]),
        "wins": ("team_season", FIELD_MEANINGS["wins"]),
        "draws": ("team_season", FIELD_MEANINGS["draws"]),
        "losses": ("team_season", FIELD_MEANINGS["losses"]),
        "goals_for": ("team_season", FIELD_MEANINGS["goals_for"]),
        "goals_against": ("team_season", FIELD_MEANINGS["goals_against"]),
        "goal_difference": ("team_season", FIELD_MEANINGS["goal_difference"]),
        "points": ("team_season", FIELD_MEANINGS["points"]),
        "position": ("league_season", FIELD_MEANINGS["position"]),
    }
    records = []
    for field, (family, meaning) in specs.items():
        areas = [family, "league_season"] if family != "league_season" else ["league_season", "team_season"]
        records.append(
            _record(
                record_id=f"league_table:teams[].{field}",
                canonical_name=field,
                family=family,
                areas=areas + ["derived_metrics"],
                meaning={"status": "ESTABLISHED", "text": meaning},
                grain="team-league-season",
                grain_status="ESTABLISHED",
                origin_kind="DERIVED",
                source_surface="FRL_DERIVED",
                source_resource="query_lab.league_table",
                source_native_fields=["home_score", "away_score", "home_team_id", "away_team_id"],
                transformation={
                    "kind": "FIXTURE_RESULT_AGGREGATION",
                    "status": "GOVERNED_QUERY_SEAM",
                    "route": ["fixtures_master_corrected.csv", "verified team identity", "query_lab.league_table"],
                },
                coverage=_artifact_coverage(fixture_profile, "fixtures_master_corrected.csv"),
                aggregation={"status": "CONDITIONAL", "summary": "Derived over completed fixtures; the response exposes incomplete seasons explicitly."},
                temporal={
                    "status": "CONDITIONAL",
                    "state_semantics": "REQUESTED_SEASON_COMPLETED_FIXTURES",
                    "information_available_as_of": "NOT_PARAMETERISED",
                    "historical_state_and_information_availability_distinct": True,
                    "summary": "Current query is season-scoped but has no independent historical information-availability parameter.",
                },
                limitations=["Season completeness and competition scope must accompany comparisons."],
                governance={
                    "catalogue": "query_lab.league_table return contract",
                    "semantic_status": "DERIVED",
                    "ura_exposure": "OTHER_GOVERNED_QUERY_SEAM",
                    "route_status": "FIXTURE_RESULT_AGGREGATION",
                    "attachment_verified": "VERIFIED_TEAM_IDENTITY",
                },
            )
        )
    return records


MODEL_OUTPUTS = {
    "expected_goals.home": "Expected home goals produced by Poisson V0.1.",
    "expected_goals.away": "Expected away goals produced by Poisson V0.1.",
    "probabilities.home_win": "Poisson V0.1 probability of a home win.",
    "probabilities.draw": "Poisson V0.1 probability of a draw.",
    "probabilities.away_win": "Poisson V0.1 probability of an away win.",
    "probabilities.over_2_5": "Poisson V0.1 probability that total goals are at least three.",
    "probabilities.btts": "Poisson V0.1 probability that both teams score.",
    "fair_odds.home_win": "Reciprocal of the Poisson V0.1 home-win probability.",
    "fair_odds.draw": "Reciprocal of the Poisson V0.1 draw probability.",
    "fair_odds.away_win": "Reciprocal of the Poisson V0.1 away-win probability.",
    "most_likely_score.home": "Home goals in the highest-probability score cell in the truncated model grid.",
    "most_likely_score.away": "Away goals in the highest-probability score cell in the truncated model grid.",
    "most_likely_score.probability": "Probability of the highest-probability score cell in the truncated model grid.",
}


def _model_records() -> list[dict[str, Any]]:
    records = []
    for field, meaning in MODEL_OUTPUTS.items():
        areas = ["models"] + (["odds_markets"] if field.startswith("fair_odds") else [])
        records.append(
            _record(
                record_id=f"poisson_v0_1:{field}",
                canonical_name=field,
                family="models",
                areas=areas,
                meaning={"status": "ESTABLISHED", "text": meaning},
                grain="model-fixture-output",
                grain_status="ESTABLISHED",
                origin_kind="MODEL_OUTPUT",
                source_surface="FRL_MODEL",
                source_resource="poisson_model.poisson_prediction",
                source_native_fields=[field],
                transformation={
                    "kind": "POISSON_V0_1",
                    "status": "MODEL_OUTPUT",
                    "route": ["2025-26 canonical completed fixture scores", "home/away strength", "truncated independent Poisson score grid (0-8)", field],
                },
                coverage={
                    "status": "FIXED_MODEL_SCOPE",
                    "summary": "Poisson V0.1 uses source season 2025-26 for target season 2026-27 and a fixed declared team universe.",
                    "seasons_observed": ["2025-26"],
                    "season_count": 1,
                    "population": None,
                    "basis": ["poisson_model.py"],
                },
                aggregation={"status": "CONDITIONAL", "summary": "Comparable only within Poisson V0.1, its fixed team universe and the same prediction-time inputs."},
                temporal={
                    "status": "CONDITIONAL",
                    "state_semantics": "MODEL_SOURCE_2025_26_TARGET_2026_27",
                    "information_available_as_of": "MODEL_RUN_TIME_NOT_PERSISTED",
                    "historical_state_and_information_availability_distinct": True,
                    "summary": "The source and target seasons are explicit; no historical prediction archive or run timestamp is persisted by the model output contract.",
                },
                limitations=["Not calibrated as a universal historical model.", "Promoted-team priors include explicit hard-coded EFL inputs.", "Score grid is truncated at eight goals per team."],
                governance={
                    "catalogue": "poisson_model.poisson_prediction return contract",
                    "semantic_status": "MODEL_OUTPUT",
                    "ura_exposure": "MODEL_SEAM_NOT_URA",
                    "route_status": "POISSON_V0_1",
                    "attachment_verified": "FIXED_MODEL_SCOPE",
                },
            )
        )
    return records


MARKET_OUTPUTS = {
    "bookmaker_odds.home_win": ("MARKET_INPUT", "Decimal home-win price entered by the user."),
    "bookmaker_odds.draw": ("MARKET_INPUT", "Decimal draw price entered by the user."),
    "bookmaker_odds.away_win": ("MARKET_INPUT", "Decimal away-win price entered by the user."),
    "raw_implied_probability.home_win": ("DERIVED", "Reciprocal of the entered home-win decimal price before margin removal."),
    "raw_implied_probability.draw": ("DERIVED", "Reciprocal of the entered draw decimal price before margin removal."),
    "raw_implied_probability.away_win": ("DERIVED", "Reciprocal of the entered away-win decimal price before margin removal."),
    "overround": ("DERIVED", "Sum of raw implied 1X2 probabilities."),
    "market_probability.home_win": ("DERIVED", "Home-win implied probability normalised by the 1X2 overround."),
    "market_probability.draw": ("DERIVED", "Draw implied probability normalised by the 1X2 overround."),
    "market_probability.away_win": ("DERIVED", "Away-win implied probability normalised by the 1X2 overround."),
    "probability_edge.home_win": ("DERIVED", "Model home-win probability minus normalised market probability."),
    "probability_edge.draw": ("DERIVED", "Model draw probability minus normalised market probability."),
    "probability_edge.away_win": ("DERIVED", "Model away-win probability minus normalised market probability."),
    "expected_value.home_win": ("DERIVED", "Model probability multiplied by entered home-win odds, minus one."),
    "expected_value.draw": ("DERIVED", "Model probability multiplied by entered draw odds, minus one."),
    "expected_value.away_win": ("DERIVED", "Model probability multiplied by entered away-win odds, minus one."),
}


def _market_records() -> list[dict[str, Any]]:
    records = []
    for field, (origin, meaning) in MARKET_OUTPUTS.items():
        surface = "USER_INPUT" if origin == "MARKET_INPUT" else "FRL_DERIVED"
        records.append(
            _record(
                record_id=f"market_comparison:{field}",
                canonical_name=field,
                family="odds_markets",
                areas=["odds_markets"] + ([] if origin == "MARKET_INPUT" else ["derived_metrics"]),
                meaning={"status": "ESTABLISHED", "text": meaning},
                grain="ephemeral-fixture-market-comparison",
                grain_status="CONDITIONAL",
                origin_kind=origin,
                source_surface=surface,
                source_resource="poisson_model.compare_bookmaker_odds",
                source_native_fields=[field],
                transformation={
                    "kind": "USER_INPUT" if origin == "MARKET_INPUT" else "EXPLICIT_MARKET_CALCULATION",
                    "status": "EPHEMERAL_NOT_PRESERVED",
                    "route": ["user-entered 1X2 decimal odds", "poisson_model.compare_bookmaker_odds", field],
                },
                coverage={
                    "status": "NOT_PRESERVED",
                    "summary": "Calculated from ad hoc user input; FRL has no governed historical odds observation store.",
                    "seasons_observed": [],
                    "season_count": 0,
                    "population": 0,
                    "basis": ["poisson_model.compare_bookmaker_odds"],
                },
                aggregation={"status": "NOT_APPLICABLE", "summary": "No cross-observation aggregation is valid without bookmaker, market and observation-time identity."},
                temporal={
                    "status": "REVIEW_REQUIRED",
                    "state_semantics": "EPHEMERAL_USER_INPUT",
                    "information_available_as_of": "NOT_PERSISTED",
                    "historical_state_and_information_availability_distinct": True,
                    "summary": "The current calculator does not preserve market observation time or prediction run time.",
                },
                limitations=["Not a historical market dataset.", "Bookmaker, market and observation timestamp are not captured by the current function signature."],
                governance={
                    "catalogue": "poisson_model.compare_bookmaker_odds return contract",
                    "semantic_status": origin,
                    "ura_exposure": "DECISION_LAYER_NOT_URA",
                    "route_status": "EPHEMERAL_CALCULATOR",
                    "attachment_verified": "NOT_PERSISTED",
                },
                product_uses=["Prediction Lab", "modelling-only"],
            )
        )
    return records


def _family_records(variable_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for name in CAPABILITY_AREAS:
        definition = FAMILY_DEFINITIONS[name]
        members = [record for record in variable_records if name in record["capability_areas"]]
        source_counts = Counter(record["source"]["family"] for record in members)
        records.append(
            {
                "record_type": "family",
                "canonical_family_name": name,
                "football_meaning": definition["football_meaning"],
                "primary_grain": definition["primary_grain"],
                "aggregation_comparability": definition["aggregation"],
                "temporal_as_of_semantics": definition["temporal"],
                "major_limitations": definition["limitations"],
                "likely_product_uses": definition["product_uses"],
                "variable_record_count": len(members),
                "source_family_counts": dict(sorted(source_counts.items())),
            }
        )
    return records


def _summary(variable_records: list[dict[str, Any]], family_records: list[dict[str, Any]]) -> dict[str, Any]:
    def counts(path: tuple[str, ...]) -> dict[str, int]:
        values = []
        for record in variable_records:
            value: Any = record
            for key in path:
                value = value[key]
            values.append(str(value))
        return dict(sorted(Counter(values).items()))

    area_counts = Counter()
    for record in variable_records:
        area_counts.update(record["capability_areas"])
    catalogue_count = sum(record["record_id"].startswith("catalogue:") for record in variable_records)
    review_count = sum(
        record["football_meaning"]["status"] in {"UNKNOWN", "REVIEW_REQUIRED"}
        for record in variable_records
    )
    return {
        "inventory_version": INVENTORY_VERSION,
        "family_count": len(family_records),
        "variable_record_count": len(variable_records),
        "canonical_catalogue_variable_count": catalogue_count,
        "supplemental_existing_capability_count": len(variable_records) - catalogue_count,
        "ura_discoverable_capability_count": discover()["count"],
        "meaning_unknown_or_review_count": review_count,
        "by_primary_family": counts(("capability_family",)),
        "by_capability_area": dict(sorted(area_counts.items())),
        "by_grain": counts(("grain", "name")),
        "by_origin_kind": counts(("origin_kind",)),
        "by_source_family": counts(("source", "family")),
        "by_coverage_status": counts(("coverage", "status")),
        "by_meaning_status": counts(("football_meaning", "status")),
        "by_rights_status": counts(("source_rights", "status")),
        "interpretation_notes": [
            "Variable records are capabilities, not a claim that every value is materialised for every fixture/season.",
            "Capability-area counts overlap because one variable may serve more than one governed area.",
            "DISCOVERY_SAMPLE_ONLY is not historical coverage.",
            "UNKNOWN and REVIEW_REQUIRED are intentional fail-closed metadata values.",
        ],
    }


def _schema() -> dict[str, Any]:
    return {
        "variable_record_required_fields": [
            "record_id",
            "canonical_name",
            "capability_family",
            "capability_areas",
            "football_meaning",
            "grain",
            "origin_kind",
            "source",
            "transformation",
            "coverage",
            "aggregation_comparability",
            "temporal_as_of",
            "major_limitations",
            "likely_product_uses",
            "source_rights",
            "governance",
        ],
        "capability_areas": list(CAPABILITY_AREAS),
        "origin_kinds": list(ORIGIN_KINDS),
        "assessment_statuses": list(ASSESSMENT_STATUSES),
        "product_uses": list(PRODUCT_USES),
        "unknown_policy": "Use UNKNOWN when evidence is absent and REVIEW_REQUIRED when evidence exists but its definition, route, comparability or rights status is not safely approved.",
    }


def build_inventory(root: Path = ROOT) -> dict[str, Any]:
    """Build the complete deterministic inventory in memory."""
    validate_route_registry()
    records = _catalogue_records(root)
    records.extend(_canonical_fixture_records(root))
    records.extend(_historical_feature_records(root))
    records.extend(_resolver_records(root, records))
    records.extend(_league_records(root))
    records.extend(_model_records())
    records.extend(_market_records())
    records.sort(key=lambda record: record["record_id"])

    ids = [record["record_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Variable capability inventory contains duplicate record_id values")

    families = _family_records(records)
    provenance_files = []
    for relative in PROVENANCE_FILES:
        path = root / relative
        provenance_files.append(
            {
                "path": relative,
                "sha256": _sha256(path),
            }
        )

    summary = _summary(records, families)
    return {
        "schema_version": SCHEMA_VERSION,
        "inventory_version": INVENTORY_VERSION,
        "generator": {
            "module": "variable_capability_inventory.py",
            "version": GENERATOR_VERSION,
            "deterministic": True,
            "runtime_timestamp_omitted_for_reproducibility": True,
        },
        "scope": {
            "statement": "Governed capability metadata derived from existing FRL registries, artifacts and implemented research/model seams.",
            "not_a_coverage_audit": True,
            "not_a_new_ingestion": True,
            "no_semantic_promotion_by_inference": True,
        },
        "schema": _schema(),
        "provenance": {
            "source_files": provenance_files,
            "ura_access_version": discover()["access_version"],
            "rights_register": "FRL_SOURCE_RIGHTS_REGISTER.md",
        },
        "summary": summary,
        "families": families,
        "variables": records,
    }


def render_inventory_json(inventory: dict[str, Any]) -> str:
    return json.dumps(inventory, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_summary_json(inventory: dict[str, Any]) -> str:
    return json.dumps(inventory["summary"], indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _json_cell(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    coverage = record["coverage"]
    governance = record["governance"]
    return {
        "record_id": record["record_id"],
        "canonical_name": record["canonical_name"],
        "capability_family": record["capability_family"],
        "capability_areas": _json_cell(record["capability_areas"]),
        "football_meaning_status": record["football_meaning"]["status"],
        "football_meaning": record["football_meaning"]["text"],
        "grain": record["grain"]["name"],
        "grain_status": record["grain"]["status"],
        "origin_kind": record["origin_kind"],
        "source_family": record["source"]["family"],
        "source_surface": record["source"]["surface"],
        "source_resource": record["source"]["resource"],
        "source_native_fields": _json_cell(record["source"]["native_fields"]),
        "transformation_kind": record["transformation"]["kind"],
        "transformation_status": record["transformation"]["status"],
        "transformation_route": _json_cell(record["transformation"]["route"]),
        "coverage_status": coverage["status"],
        "coverage_summary": coverage["summary"],
        "seasons_observed": _json_cell(coverage["seasons_observed"]),
        "season_count": coverage["season_count"],
        "population": coverage["population"],
        "aggregation_status": record["aggregation_comparability"]["status"],
        "aggregation_summary": record["aggregation_comparability"]["summary"],
        "temporal_state": record["temporal_as_of"]["state_semantics"],
        "information_available_as_of": record["temporal_as_of"]["information_available_as_of"],
        "major_limitations": _json_cell(record["major_limitations"]),
        "likely_product_uses": _json_cell(record["likely_product_uses"]),
        "rights_status": record["source_rights"]["status"],
        "acquisition_classification": record["source_rights"]["acquisition_classification"],
        "semantic_status": governance.get("semantic_status", "UNKNOWN"),
        "ura_exposure": governance.get("ura_exposure", "UNKNOWN"),
        "route_status": governance.get("route_status", "UNKNOWN"),
        "attachment_verified": governance.get("attachment_verified", "UNKNOWN"),
    }


def render_inventory_csv(inventory: dict[str, Any]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for record in inventory["variables"]:
        writer.writerow(_flatten_record(record))
    return output.getvalue()


def generated_outputs(root: Path = ROOT) -> dict[Path, str]:
    inventory = build_inventory(root)
    return {
        root / "data" / INVENTORY_JSON.name: render_inventory_json(inventory),
        root / "data" / INVENTORY_CSV.name: render_inventory_csv(inventory),
        root / "data" / SUMMARY_JSON.name: render_summary_json(inventory),
    }


def write_inventory(root: Path = ROOT, output_dir: Path | None = None) -> dict[str, Any]:
    inventory = build_inventory(root)
    destination = output_dir or (root / "data")
    destination.mkdir(parents=True, exist_ok=True)
    outputs = {
        destination / INVENTORY_JSON.name: render_inventory_json(inventory),
        destination / INVENTORY_CSV.name: render_inventory_csv(inventory),
        destination / SUMMARY_JSON.name: render_summary_json(inventory),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="")
    return inventory


def outputs_are_current(root: Path = ROOT) -> bool:
    return all(path.is_file() and path.read_text(encoding="utf-8") == content for path, content in generated_outputs(root).items())


__all__ = [
    "CAPABILITY_AREAS",
    "CSV_COLUMNS",
    "INVENTORY_VERSION",
    "ORIGIN_KINDS",
    "PRODUCT_USES",
    "SCHEMA_VERSION",
    "build_inventory",
    "generated_outputs",
    "outputs_are_current",
    "render_inventory_csv",
    "render_inventory_json",
    "render_summary_json",
    "write_inventory",
]
