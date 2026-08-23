import source_field_semantic_priority as priority


def test_priority_prefers_core_research_fields(monkeypatch):
    monkeypatch.setattr(
        priority,
        "build_review_queue",
        lambda: [
            {
                "family": "player_match",
                "source_field": "progressiveBallCarriesCount",
                "coverage_class": "CORE_DECADE",
                "seasons_present": 10,
                "registry_status": "UNCATALOGUED",
            },
            {
                "family": "squad",
                "source_field": "shirtNumber",
                "coverage_class": "SINGLE_SEASON",
                "seasons_present": 1,
                "registry_status": "UNCATALOGUED",
            },
        ],
    )
    rows = priority.build_priority_queue()
    assert rows[0]["source_field"] == "progressiveBallCarriesCount"
    assert rows[0]["review_priority_score"] > rows[1]["review_priority_score"]


def test_negative_polarity_does_not_get_positive_success_signal():
    score, reasons = priority._score({
        "family": "player_match",
        "source_field": "unsuccessfulCrossesOpenPlay",
        "coverage_class": "CORE_DECADE",
        "seasons_present": 10,
        "registry_status": "UNCATALOGUED",
    })
    assert "research-relevant name: cross" in "; ".join(reasons)
    assert "successful" not in "; ".join(reasons)
    assert "negative outcome/reverse-polarity term" in reasons
