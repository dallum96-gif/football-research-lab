from fixture_goal_events import fixture_goal_events


def test_missing_source_match_id_is_unavailable():
    result = fixture_goal_events(None)

    assert result["status"] == "UNAVAILABLE"
    assert result["goals"] == []


def test_invalid_source_match_id_is_unavailable():
    result = fixture_goal_events("not-an-id")

    assert result["status"] == "UNAVAILABLE"
    assert result["source_match_id"] == "not-an-id"


def test_goal_normalisation_shape(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "incidents": [
                    {
                        "incidentType": "goal",
                        "incidentClass": "regular",
                        "time": 25,
                        "isHome": True,
                        "player": {"id": 123, "name": "Kai Havertz"},
                    },
                    {
                        "incidentType": "goal",
                        "incidentClass": "ownGoal",
                        "time": 82,
                        "isHome": False,
                        "playerName": "Own Goal",
                        "player": {"id": 456, "name": "Defender"},
                    },
                    {"incidentType": "card", "time": 40},
                ]

    monkeypatch.setattr("fixture_goal_events.requests.get", lambda *args, **kwargs: Response())
    fixture_goal_events.cache_clear()

    result = fixture_goal_events("855174")

    assert result["status"] == "AVAILABLE"
    assert len(result["goals"]) == 2
    assert result["goals"][0]["player"] == "Kai Havertz"
    assert result["goals"][0]["minute"] == 25
    assert result["goals"][0]["is_home"] is True
    assert result["goals"][0]["own_goal"] is False
    assert result["goals"][1]["minute"] == 82
    assert result["goals"][1]["own_goal"] is True
