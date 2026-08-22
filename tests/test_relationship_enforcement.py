from relationship_enforcement import (
    classify_observation,
    evaluate_identity,
    field_available,
    require_verified,
)


def test_verified_identity_requires_exactly_one_candidate():
    decision = evaluate_identity(
        "canonical_fixture_to_source_match",
        source_context_available=True,
        candidates=({"source_match_id": "2645195"},),
    )
    assert decision.status == "VERIFIED"
    assert decision.verified is True


def test_ambiguous_identity_fails_closed():
    decision = evaluate_identity(
        "fpl_player_to_frl_player_identity",
        source_context_available=True,
        candidates=({"id": "1"}, {"id": "2"}),
    )
    assert decision.status == "AMBIGUOUS"
    try:
        require_verified(decision)
    except ValueError as exc:
        assert "AMBIGUOUS" in str(exc)
    else:
        raise AssertionError("Ambiguous identity must not be promoted")


def test_unavailable_source_is_not_unresolved():
    decision = evaluate_identity(
        "fpl_player_to_frl_player_identity",
        source_context_available=False,
        candidates=(),
    )
    assert decision.status == "UNAVAILABLE"


def test_observation_absence_is_not_identity_failure():
    assert classify_observation(
        identity_verified=True,
        fixture_verified=True,
        observation_present=False,
    ) == "UNAVAILABLE"


def test_field_availability_is_season_local():
    assert field_available("expectedGoals", ("expectedGoals",))
    assert not field_available("expectedGoals", ("goals",))
