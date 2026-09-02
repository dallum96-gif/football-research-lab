import player_analysis_kernel


def test_raw_and_per90_variants_share_one_player_metric_concept():
    goals = player_analysis_kernel.DEFINITIONS_BY_KEY["goals"]
    goals_per_90 = player_analysis_kernel.DEFINITIONS_BY_KEY["goals_per_90"]

    assert goals.concept_key == "goals"
    assert goals_per_90.concept_key == "goals"
    assert goals.normalization == player_analysis_kernel.RAW
    assert goals_per_90.normalization == player_analysis_kernel.PER_90
    assert player_analysis_kernel.NORMALIZATIONS_BY_CONCEPT["goals"] == (
        player_analysis_kernel.RAW,
        player_analysis_kernel.PER_90,
    )


def test_rate_metric_is_not_misrepresented_as_per90():
    pass_completion = player_analysis_kernel.DEFINITIONS_BY_KEY["pass_completion"]

    assert pass_completion.concept_key == "pass_completion"
    assert pass_completion.normalization == player_analysis_kernel.RATE
    assert pass_completion.per_90 is False
    assert player_analysis_kernel.NORMALIZATIONS_BY_CONCEPT["pass_completion"] == (
        player_analysis_kernel.RATE,
    )


def test_public_metric_definition_exposes_supported_normalizations():
    goals_per_90 = player_analysis_kernel.DEFINITIONS_BY_KEY["goals_per_90"]
    payload = player_analysis_kernel.definition_payload(goals_per_90)

    assert payload["concept_key"] == "goals"
    assert payload["normalization"] == player_analysis_kernel.PER_90
    assert payload["supported_normalizations"] == [
        player_analysis_kernel.RAW,
        player_analysis_kernel.PER_90,
    ]
