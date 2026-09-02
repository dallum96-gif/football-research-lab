from __future__ import annotations

from pathlib import Path

import pulselive_fixture_evidence


def test_dedicated_worktree_discovers_canonical_sibling_archive(
    monkeypatch,
    tmp_path: Path,
) -> None:
    feature_worktree = tmp_path / "frl-player-stats"
    feature_worktree.mkdir()
    canonical_archive = (
        tmp_path
        / "football-research-lab"
        / "data"
        / "raw"
        / "pulselive"
    )
    canonical_archive.mkdir(parents=True)

    monkeypatch.delenv(
        pulselive_fixture_evidence.ARCHIVE_ENV,
        raising=False,
    )
    monkeypatch.setattr(
        pulselive_fixture_evidence,
        "ROOT",
        feature_worktree,
    )

    assert pulselive_fixture_evidence.archive_root() == canonical_archive


def test_explicit_archive_root_remains_authoritative(
    monkeypatch,
    tmp_path: Path,
) -> None:
    explicit_archive = tmp_path / "explicit-pulselive"
    explicit_archive.mkdir()
    sibling_archive = (
        tmp_path
        / "football-research-lab"
        / "data"
        / "raw"
        / "pulselive"
    )
    sibling_archive.mkdir(parents=True)

    monkeypatch.setenv(
        pulselive_fixture_evidence.ARCHIVE_ENV,
        str(explicit_archive),
    )
    monkeypatch.setattr(
        pulselive_fixture_evidence,
        "ROOT",
        tmp_path / "frl-player-stats",
    )

    assert pulselive_fixture_evidence.archive_root() == explicit_archive
