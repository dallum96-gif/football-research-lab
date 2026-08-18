from __future__ import annotations

import tempfile
from pathlib import Path

from tools.analytical_materialization import materialize


def test_analytical_materialisation_preserves_canonical_grains() -> None:
    with tempfile.TemporaryDirectory(prefix="frl-analytical-test-") as tmp:
        result = materialize(Path(tmp))
        assert result["fixtures"] > 0
        assert result["team_fixtures"] == result["fixtures"] * 2
        assert Path(result["fixture_output"]).exists()
        assert Path(result["team_fixture_output"]).exists()


def test_analytical_materialisation_is_additive_and_local() -> None:
    with tempfile.TemporaryDirectory(prefix="frl-analytical-test-") as tmp:
        output = Path(tmp)
        result = materialize(output)
        assert output.exists()
        assert Path(result["fixture_output"]).parent == output
        assert Path(result["team_fixture_output"]).parent == output
