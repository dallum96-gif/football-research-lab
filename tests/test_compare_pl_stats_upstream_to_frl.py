from compare_pl_stats_upstream_to_frl import compare


def test_compare_exact_grain_and_field_name_only():
    upstream = {('team_match', 'possessionPercentage'), ('player_match', 'newMetric')}
    frl = {('team_match', 'possessionPercentage'), ('player_match', 'oldMetric')}
    rows = compare(upstream, frl)
    states = {(r['grain'], r['field_name']): r['state'] for r in rows}
    assert states[('team_match', 'possessionPercentage')] == 'BOTH'
    assert states[('player_match', 'newMetric')] == 'UPSTREAM_ONLY'
    assert states[('player_match', 'oldMetric')] == 'FRL_ONLY'


def test_same_field_different_grain_is_not_both():
    upstream = {('team_match', 'goals')}
    frl = {('player_match', 'goals')}
    rows = compare(upstream, frl)
    states = {(r['grain'], r['field_name']): r['state'] for r in rows}
    assert states[('team_match', 'goals')] == 'UPSTREAM_ONLY'
    assert states[('player_match', 'goals')] == 'FRL_ONLY'
