from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "frl_documentation_state_v1.json"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def changed_files(base_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def path_matches(changed: str, configured: str) -> bool:
    configured = configured.replace("\\", "/")
    if configured.endswith("/"):
        return changed.startswith(configured)
    return changed == configured


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FRL standing-document synchronisation.")
    parser.add_argument(
        "--base-ref",
        help="Optional Git base ref/SHA used to detect architecture-sensitive changes in this branch.",
    )
    args = parser.parse_args()

    errors: list[str] = []

    if not MANIFEST.is_file():
        print(f"DOCUMENTATION SYNC - FAILED\nMissing manifest: {MANIFEST.relative_to(ROOT)}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    living = manifest.get("living_documents", [])
    orientation = manifest.get("orientation_documents", [])
    durable = manifest.get("durable_contracts_checked_at_checkpoint", [])
    current_refs = manifest.get("current_reference_documents", [])
    required_files = set(living + orientation + durable + current_refs)
    required_files.add("data/frl_documentation_state_v1.json")

    for relative in sorted(required_files):
        if not (ROOT / relative).is_file():
            fail(f"Required repository-memory file is missing: {relative}", errors)

    marker = manifest.get("required_sync_marker")
    if marker:
        for relative in living + orientation:
            path = ROOT / relative
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if marker not in text:
                fail(f"{relative} does not reference the documentation-sync contract ({marker}).", errors)

    forbidden = manifest.get("forbidden_current_claims", [])
    for relative in living + orientation:
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for phrase in forbidden:
            if phrase in text:
                fail(f"Known obsolete current-state claim found in {relative}: {phrase!r}", errors)

    if args.base_ref:
        changed = changed_files(args.base_ref)
        sensitive = manifest.get("architecture_sensitive_paths", [])
        sensitive_changed = sorted(
            path
            for path in changed
            if any(path_matches(path, configured) for configured in sensitive)
        )
        checkpoint_files = set(manifest.get("checkpoint_files", []))
        checkpoint_changed = sorted(changed & checkpoint_files)

        if sensitive_changed and not checkpoint_changed:
            fail(
                "Architecture-sensitive files changed without refreshing a current-state checkpoint. "
                f"Sensitive changes: {sensitive_changed}; expected one of: {sorted(checkpoint_files)}",
                errors,
            )

    if errors:
        print("DOCUMENTATION SYNC - FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("DOCUMENTATION SYNC - PASSED")
    print(f"Checkpoint: {manifest.get('checkpoint_id')} ({manifest.get('checkpoint_date')})")
    print(f"Active frontend: {manifest.get('active_frontend')}")
    print(f"Active product phase: {manifest.get('active_product_phase')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
