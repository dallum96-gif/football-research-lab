from fixture_goal_events import _normalise_event


def test_normalise_regular_goal():
    event = _normalise_event(
        {
            "type": "goal",
            "time": "61'00",
            "player": {"name": {"display": "Bukayo Saka"}},
            "isHome": True,
        },
        "3",
        "4",
    )

    assert event == {
        "minute": 61,
        "seconds_remainder": None,
        "player": "Bukayo Saka",
        "side": "home",
        "own_goal": False,
        "goal_type": "goal",
    }


def test_normalise_penalty_and_own_goal():
    penalty = _normalise_event(
        {
            "type": "penalty goal",
            "seconds": 420,
            "scorer": {"name": "Thierry Henry"},
            "isHome": False,
        },
        "3",
        "4",
    )
    own_goal = _normalise_event(
        {
            "type": "own goal",
            "time": "12'00",
            "playerName": "William Gallas",
            "isHome": True,
        },
        "3",
        "4",
    )

    assert penalty["minute"] == 7
    assert penalty["player"] == "Thierry Henry"
    assert penalty["side"] == "away"
    assert own_goal["own_goal"] is True


def test_non_goal_event_is_ignored():
    assert _normalise_event(
        {
            "type": "yellow card",
            "time": "33'00",
            "playerName": "Martin Odegaard",
            "isHome": True,
        },
        "3",
        "4",
    ) is None
