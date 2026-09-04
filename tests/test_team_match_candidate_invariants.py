from __future__ import annotations

from scripts.audit_team_match_candidate_invariants import evaluate_invariants


def test_subset_invariant_passes_when_child_never_exceeds_parent():
    rules = ({
        'rule_id': 'won_lte_total',
        'child_field': 'wonContest',
        'parent_field': 'totalContest',
        'rationale': 'subset',
    },)
    rows = [
        {'frl_fixture_id': '1', 'wonContest': '3', 'totalContest': '5'},
        {'frl_fixture_id': '2', 'wonContest': '0', 'totalContest': '0'},
        {'frl_fixture_id': '3', 'wonContest': '', 'totalContest': '2'},
    ]

    result = evaluate_invariants(rows, season='2024-25', rules=rules)[0]

    assert result['rows_compared'] == 2
    assert result['violations'] == 0
    assert result['status'] == 'EMPIRICALLY_CONSISTENT_NO_VIOLATIONS'


def test_subset_invariant_reports_violation_without_rewriting_data():
    rules = ({
        'rule_id': 'won_lte_total',
        'child_field': 'wonContest',
        'parent_field': 'totalContest',
        'rationale': 'subset',
    },)
    rows = [
        {'frl_fixture_id': '9', 'team': 'Example', 'wonContest': '6', 'totalContest': '5'},
    ]

    result = evaluate_invariants(rows, season='2024-25', rules=rules)[0]

    assert result['violations'] == 1
    assert result['max_child_minus_parent'] == 1.0
    assert result['status'] == 'REVIEW_VIOLATIONS'
    assert result['example_violations'][0]['fixture_id'] == '9'


def test_missing_pair_produces_no_comparable_observations():
    rules = ({
        'rule_id': 'success_lte_total',
        'child_field': 'success',
        'parent_field': 'total',
        'rationale': 'subset',
    },)
    rows = [{'success': '', 'total': '4'}, {'success': '2', 'total': ''}]

    result = evaluate_invariants(rows, season='2024-25', rules=rules)[0]

    assert result['rows_compared'] == 0
    assert result['status'] == 'NO_COMPARABLE_OBSERVATIONS'
