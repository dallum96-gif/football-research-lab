import relationship_contracts as rc


def test_required_relationship_contracts_exist():
    expected = {
        "canonical_fixture_to_source_match",
        "canonical_team_season_to_source_team",
        "fpl_player_to_frl_player_identity",
        "source_player_match_to_source_player_identity",
        "source_player_identity_to_player_season",
        "player_identity_to_player_match_observations",
        "source_field_to_season_availability",
    }
    assert {contract.name for contract in rc.RELATIONSHIP_CONTRACTS} == expected


def test_identity_classification_fails_closed():
    assert rc.classify_identity_status(
        source_context_available=False,
        candidate_count=1,
    ) == "UNAVAILABLE"
    assert rc.classify_identity_status(
        source_context_available=True,
        candidate_count=0,
    ) == "UNRESOLVED"
    assert rc.classify_identity_status(
        source_context_available=True,
        candidate_count=1,
    ) == "VERIFIED"
    assert rc.classify_identity_status(
        source_context_available=True,
        candidate_count=2,
    ) == "AMBIGUOUS"
    assert rc.classify_identity_status(
        source_context_available=True,
        candidate_count=1,
        contradiction=True,
    ) == "CONTRADICTORY"


def test_fpl_contract_forbids_element_continuity_and_name_only_inference():
    contract = rc.get_relationship_contract("fpl_player_to_frl_player_identity")
    assert "name-only matching" in contract.forbidden_inference
    assert "FPL element treated as longitudinal without proof" in contract.forbidden_inference
    assert "cross-season code continuity treated as proof by itself" in contract.forbidden_inference
    assert contract.absent_means == "UNAVAILABLE"
