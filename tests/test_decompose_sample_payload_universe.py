from decompose_sample_payload_universe import infer_context


def test_specific_grain_is_preserved():
    grain, basis = infer_context("totalShots", "team_match", "team_match", "")
    assert grain == "team_match"
    assert "pre-existing" in basis


def test_unknown_sample_payload_fails_closed():
    grain, _ = infer_context("mystery.value", "raw_upstream", "sample_payload", "")
    assert grain == "UNMAPPED_REVIEW"


def test_player_match_context_can_be_derived():
    grain, _ = infer_context("player_match.totalShots", "match", "sample_payload", "")
    assert grain == "player_match"


def test_fixture_context_can_be_derived():
    grain, _ = infer_context("fixture.homeTeam", "match", "sample_payload", "")
    assert grain == "fixture"
