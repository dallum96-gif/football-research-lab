from __future__ import annotations

import csv
import json
from io import StringIO

from canonical_variable_catalogue import canonical_variables
from variable_capability_inventory import (
    CAPABILITY_AREAS,
    INVENTORY_VERSION,
    ORIGIN_KINDS,
    PRODUCT_USES,
    build_inventory,
    outputs_are_current,
    render_inventory_csv,
    render_inventory_json,
    render_summary_json,
)


def _by_id(inventory: dict) -> dict[str, dict]:
    return {row["record_id"]: row for row in inventory["variables"]}


def test_inventory_schema_and_catalogue_census_are_complete():
    inventory = build_inventory()
    variables = inventory["variables"]
    required = set(inventory["schema"]["variable_record_required_fields"])

    assert inventory["inventory_version"] == INVENTORY_VERSION
    assert inventory["generator"]["deterministic"] is True
    assert inventory["scope"]["not_a_coverage_audit"] is True
    assert len(inventory["families"]) == len(CAPABILITY_AREAS)
    assert {row["canonical_family_name"] for row in inventory["families"]} == set(CAPABILITY_AREAS)
    assert len({row["record_id"] for row in variables}) == len(variables)
    assert all(required <= set(row) for row in variables)
    assert all(row["canonical_name"] for row in variables)
    assert all(row["origin_kind"] in ORIGIN_KINDS for row in variables)
    assert all(set(row["capability_areas"]) <= set(CAPABILITY_AREAS) for row in variables)
    assert all(set(row["likely_product_uses"]) <= set(PRODUCT_USES) for row in variables)

    catalogue_records = [row for row in variables if row["record_id"].startswith("catalogue:")]
    assert len(catalogue_records) == len(canonical_variables()) == 1414
    assert inventory["summary"]["canonical_catalogue_variable_count"] == 1414
    assert inventory["summary"]["ura_discoverable_capability_count"] == 688


def test_inventory_generation_is_byte_reproducible_and_tracked_outputs_are_current():
    first = build_inventory()
    second = build_inventory()

    assert render_inventory_json(first) == render_inventory_json(second)
    assert render_inventory_csv(first) == render_inventory_csv(second)
    assert render_summary_json(first) == render_summary_json(second)
    assert outputs_are_current()

    parsed_json = json.loads(render_inventory_json(first))
    parsed_csv = list(csv.DictReader(StringIO(render_inventory_csv(first))))
    assert parsed_json["summary"]["variable_record_count"] == len(parsed_csv)


def test_representative_source_and_derived_families_preserve_governance():
    inventory = build_inventory()
    rows = _by_id(inventory)

    team_match = rows["catalogue:FRL_LOCAL_CSV:team_match:team_match:possessionPercentage"]
    assert team_match["canonical_name"] == "possessionPercentage"
    assert team_match["capability_family"] == "team_match"
    assert team_match["source"]["native_fields"] == ["possessionPercentage"]
    assert team_match["coverage"]["season_count"] == 10
    assert team_match["source_rights"]["status"] == "REVIEW REQUIRED"

    fpl = rows["catalogue:fpl:element:sample_payload:history[].total_points"]
    assert fpl["canonical_name"] == "history[].total_points"
    assert fpl["capability_family"] == "player_match"
    assert fpl["coverage"]["status"] == "DISCOVERY_SAMPLE_ONLY"
    assert fpl["governance"]["ura_exposure"] == "URA_DISCOVERABLE"

    pulselive_event = rows[
        "catalogue:pulselive:match:sample_payload:resources.events.payload.homeTeam.goals[].playerId"
    ]
    assert pulselive_event["capability_family"] == "events"
    assert pulselive_event["grain"]["name"] == "fixture-event"
    assert pulselive_event["source_rights"]["status"] == (
        "REVIEW REQUIRED / DO NOT ASSUME REDISTRIBUTION RIGHTS"
    )

    derived = rows["ura_derived:player_match:passCompletionPct"]
    assert derived["origin_kind"] == "DERIVED"
    assert derived["source"]["native_fields"] == ["accuratePass", "totalPass"]
    assert derived["transformation"]["kind"] == "EXPLICIT_FORMULA"
    assert derived["coverage"]["status"] == "INHERITS_INPUT_COVERAGE"


def test_representative_context_league_model_and_market_limits_are_explicit():
    rows = _by_id(build_inventory())

    historical = rows["historical_state_v2:home_rest_days"]
    assert "historical_as_of" in historical["capability_areas"]
    assert historical["temporal_as_of"]["state_semantics"] == "PRE_MATCH_AS_OF_FIXTURE_KICKOFF"
    assert historical["coverage"]["population"] == 3800

    canonical_fixture = rows["canonical_fixture:fixtures_master_corrected.csv:fixture_id"]
    assert canonical_fixture["capability_family"] == "fixture"
    assert canonical_fixture["coverage"]["season_count"] == len(canonical_fixture["coverage"]["seasons_observed"])
    assert "2026-27" in canonical_fixture["coverage"]["seasons_observed"]

    league = rows["league_table:teams[].position"]
    assert league["capability_family"] == "league_season"
    assert league["origin_kind"] == "DERIVED"

    model = rows["poisson_v0_1:probabilities.home_win"]
    assert model["origin_kind"] == "MODEL_OUTPUT"
    assert model["coverage"]["status"] == "FIXED_MODEL_SCOPE"

    market = rows["market_comparison:bookmaker_odds.home_win"]
    assert market["origin_kind"] == "MARKET_INPUT"
    assert market["coverage"]["status"] == "NOT_PRESERVED"
    assert market["temporal_as_of"]["information_available_as_of"] == "NOT_PERSISTED"

    review = rows["catalogue:fpl:bootstrap-static.json:sample_payload:chips"]
    assert review["football_meaning"]["status"] == "REVIEW_REQUIRED"
    assert "review" in inventory_unknown_policy().casefold()


def inventory_unknown_policy() -> str:
    return build_inventory()["schema"]["unknown_policy"]
