import source_field_review_queue as queue


def test_uncatalogued_core_fields_are_prioritised(monkeypatch):
    monkeypatch.setattr(
        queue,
        "build_catalog",
        lambda: (
            {
                "family": "team_match",
                "source_field": "coreMetric",
                "registry_status": "UNCATALOGUED",
                "first_seen_season": "2016-17",
                "last_seen_season": "2025-26",
                "seasons_present": 10,
                "seasons_total": 10,
                "coverage_class": "CORE_DECADE",
            },
            {
                "family": "player_match",
                "source_field": "rareMetric",
                "registry_status": "UNCATALOGUED",
                "first_seen_season": "2025-26",
                "last_seen_season": "2025-26",
                "seasons_present": 1,
                "seasons_total": 10,
                "coverage_class": "SINGLE_SEASON",
            },
        ),
    )
    rows = queue.build_review_queue()
    assert rows[0]["source_field"] == "coreMetric"
    assert rows[0]["review_priority"][0] == 0
    assert rows[1]["review_priority"][0] == 3


def test_curated_fields_are_not_queued(monkeypatch):
    monkeypatch.setattr(
        queue,
        "build_catalog",
        lambda: (
            {
                "family": "team_match",
                "source_field": "alreadyExposed",
                "registry_status": "exposed",
                "first_seen_season": "2016-17",
                "last_seen_season": "2025-26",
                "seasons_present": 10,
                "seasons_total": 10,
                "coverage_class": "CORE_DECADE",
            },
        ),
    )
    assert queue.build_review_queue() == ()
