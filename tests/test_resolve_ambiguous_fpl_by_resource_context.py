from resolve_ambiguous_fpl_by_resource_context import grain_from_evidence, resolve


def test_bootstrap_events_use_frl_event_grain():
    assert grain_from_evidence("bootstrap-static", "events[].id") == "event"


def test_exact_resource_path_resolves_single_grain():
    rows = [{
        "field_name": "fixtures[].id",
        "candidate_grains": "fixture;player;player_match",
        "candidate_resources": "fixtures;element-summary",
        "evidence_paths": "fixtures:fixtures[].id",
        "review_status": "OPEN",
        "resolution": "",
        "evidence_required": "",
    }]
    out = resolve(rows)
    assert out[0]["resolution_status"] == "STRUCTURALLY_RESOLVED"
    assert out[0]["resolved_grain"] == "fixture"


def test_multiple_resource_contexts_remain_fail_closed():
    rows = [{
        "field_name": "id",
        "candidate_grains": "event;fixture",
        "candidate_resources": "bootstrap-static;fixtures",
        "evidence_paths": "bootstrap-static:events[].id | fixtures:fixtures[].id",
        "review_status": "OPEN",
        "resolution": "",
        "evidence_required": "",
    }]
    out = resolve(rows)
    assert out[0]["resolution_status"] == "AMBIGUOUS_RESOURCE_CONTEXT"
    assert out[0]["resolved_grain"] == "UNMAPPED_REVIEW"
