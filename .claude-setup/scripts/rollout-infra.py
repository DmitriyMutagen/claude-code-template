#!/usr/bin/env python3
"""
Infrastructure rollout script.
Copies standard infra files from template-project to all target projects.
Never overwrites existing files.

Usage:
    python3 rollout-infra.py [--dry-run]
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE_ROOT = Path.home() / "Documents" / "template-project"

PROJECTS = [
    Path.home() / "Documents" / "marketai" / "marketai",
    Path.home() / "Documents" / "content_factory",
    Path.home() / "Documents" / "soulway-b2b",
    Path.home() / "Documents" / "агенты" / "wb_content_factory",
]

# Relative paths inside each project to copy from template
FILES_TO_COPY = [
    ".pre-commit-config.yaml",
    ".github/workflows/ci.yml",
    "tests/conftest.py",
    "tests/test_health.py",
]


def rollout(dry_run: bool = False) -> None:
    copied: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []
    precommit_installed: list[str] = []

    for project in PROJECTS:
        if not project.exists():
            errors.append(f"[SKIP] Project not found: {project}")
            continue

        project_got_precommit = False

        for rel_path in FILES_TO_COPY:
            src = TEMPLATE_ROOT / rel_path
            dst = project / rel_path

            if not src.exists():
                errors.append(f"[ERROR] Template missing: {src}")
                continue

            if dst.exists():
                skipped.append(f"  {project.name}/{rel_path} (already exists)")
                continue

            if dry_run:
                copied.append(f"  {project.name}/{rel_path} [WOULD COPY]")
                if rel_path == ".pre-commit-config.yaml":
                    project_got_precommit = True
                continue

            # Create parent dirs
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(f"  {project.name}/{rel_path}")

            if rel_path == ".pre-commit-config.yaml":
                project_got_precommit = True

        # Run pre-commit install if we just copied .pre-commit-config.yaml
        if project_got_precommit:
            if dry_run:
                precommit_installed.append(f"  {project.name} [WOULD RUN pre-commit install]")
            else:
                try:
                    result = subprocess.run(
                        ["pre-commit", "install"],
                        cwd=str(project),
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        precommit_installed.append(f"  {project.name} (ok)")
                    else:
                        precommit_installed.append(
                            f"  {project.name} (failed: {result.stderr.strip()})"
                        )
                except FileNotFoundError:
                    precommit_installed.append(
                        f"  {project.name} (pre-commit not installed on system)"
                    )
                except subprocess.TimeoutExpired:
                    precommit_installed.append(f"  {project.name} (timeout)")

    # Report
    mode = "[DRY RUN] " if dry_run else ""
    print(f"\n{'='*60}")
    print(f" {mode}Infrastructure Rollout Report")
    print(f"{'='*60}")
    print(f"\nTemplate: {TEMPLATE_ROOT}")
    print(f"Projects: {len(PROJECTS)}")

    if copied:
        print(f"\nCopied ({len(copied)}):")
        for line in copied:
            print(line)
    else:
        print("\nNothing to copy -- all files already in place.")

    if skipped:
        print(f"\nSkipped ({len(skipped)}):")
        for line in skipped:
            print(line)

    if precommit_installed:
        print(f"\npre-commit install:")
        for line in precommit_installed:
            print(line)

    if errors:
        print(f"\nErrors/Warnings ({len(errors)}):")
        for line in errors:
            print(line)

    print()


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    rollout(dry_run=dry_run)


if __name__ == "__main__":
    main()
