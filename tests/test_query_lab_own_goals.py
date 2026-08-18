import query_lab


def test_own_goals_metric_is_registered():
    assert query_lab.METRICS["own_goals"] == "own_goals"
