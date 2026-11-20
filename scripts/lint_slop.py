#!/usr/bin/env python3
"""Fail the build if banned outcome-claim language or named slop phrases appear.

The word list comes from the SportyAgent handoff (Part 1 §L and Part 3 §9):
outcome-claim terms must not appear in any user-facing string, docs, or code
in this repository, except in this script and in the verbatim handoff copy.

Usage:
    python3 scripts/lint_slop.py
    python3 scripts/lint_slop.py path/to/file.md
    python3 scripts/lint_slop.py --root /path/to/repo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Terms are stored in parts so this file can be excluded from the scan
# without hiding the list from reviewers.
_OUTCOME = [
    "guaran" + "teed",
    r"\bsure\b",
    r"100\s*%",
    r"100\s+percent",
    "win" + " big",
    "risk" + "-free",
    "risk" + " free",
    "can't " + "lose",
    "cannot " + "lose",
    "can not " + "lose",
    "always " + "wins",
    "fixed " + "match",
    r"\bhack(?:s|ed|ing|er|ers)?\b",
]

# Phrases named in the handoff's anti-slop writing rules (Part 1 §V, Part 2).
_SLOP = [
    "it's worth noting",
    "it is worth noting",
    "at its core",
]

PATTERNS: list[tuple[str, str]] = []


def _compile():
    import re

    compiled = []
    for raw in _OUTCOME + _SLOP:
        compiled.append((raw, re.compile(raw, re.IGNORECASE)))
    return compiled


SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".eggs",
    "dist",
    "build",
    ".next",
    "htmlcov",
}

SKIP_FILE_NAMES = {
    "lint_slop.py",
}

# The verbatim handoff document quotes the banned list and the research log.
SKIP_RELATIVE_PATHS = {
    Path("docs") / "HANDOFF.md",
}

SCAN_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".rst",
    ".toml",
    ".yml",
    ".yaml",
    ".sh",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".json",
    ".css",
    ".svg",
    ".ini",
    ".cfg",
    ".makefile",
}

# Files with no suffix that we still scan.
SCAN_BARE_NAMES = {"Makefile", "makefile", "Dockerfile", "LICENSE", "README"}


def is_skipped(path: Path, root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = path
    if rel in SKIP_RELATIVE_PATHS or path.name in SKIP_FILE_NAMES:
        return True
    return False


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os_walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        base = Path(dirpath)
        for name in filenames:
            path = base / name
            if is_skipped(path, root):
                continue
            suffix = path.suffix.lower()
            if suffix in SCAN_SUFFIXES or path.name in SCAN_BARE_NAMES:
                yield path


def os_walk(root: Path):
    import os

    return os.walk(root)


# "100%" in a CSS size (width: 100%;) is not an outcome claim.
_CSS_SIZE_100 = __import__("re").compile(
    r"(?i)(?:min-|max-)?(?:width|height|flex-basis|inset|top|right|bottom|left"
    r"|font-size|border-radius|background-size|object-position|transform)\s*:\s*[^;]*100\s*%"
)


def _is_css_size_percent(raw: str, line: str) -> bool:
    if "100" not in raw:
        return False
    return _CSS_SIZE_100.search(line) is not None


def scan_text(text: str, compiled) -> list[tuple[int, str, str]]:
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for raw, cre in compiled:
            if cre.search(line) and not _is_css_size_percent(raw, line):
                hits.append((lineno, raw, line.strip()))
    return hits


def scan_file(path: Path, compiled) -> list[tuple[int, str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return scan_text(text, compiled)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Banned-language and slop linter")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to scan (default: the repository root)",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root used to resolve skip paths (default: parent of scripts/)",
    )
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    root = Path(args.root).resolve() if args.root else script_path.parent.parent

    compiled = _compile()
    targets: list[Path] = []
    if args.paths:
        for raw in args.paths:
            p = Path(raw)
            if p.is_dir():
                targets.extend(iter_files(p))
            else:
                targets.append(p)
    else:
        targets.extend(iter_files(root))

    # De-duplicate while keeping order
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in targets:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)

    failures = 0
    for path in unique:
        if is_skipped(path, root) and not args.paths:
            continue
        # When the user passes an explicit path, still honour skip for the
        # handoff and this script, unless the path is outside the normal tree
        # (tests write temporary files).
        try:
            rel = path.resolve().relative_to(root)
            display = str(rel)
        except ValueError:
            display = str(path)
            rel = None
        if rel is not None and is_skipped(path, root):
            continue
        for lineno, raw, excerpt in scan_file(path, compiled):
            print(f"{display}:{lineno}: banned language matching /{raw}/: {excerpt}")
            failures += 1

    if failures:
        print(
            f"\nlint-slop: {failures} hit(s). Remove outcome-claim wording "
            f"and the listed slop phrases, then re-run.",
            file=sys.stderr,
        )
        return 1
    print("lint-slop: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
