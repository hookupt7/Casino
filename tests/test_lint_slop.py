"""The banned-language linter must fail the build when a banned term is used."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINTER = REPO / "scripts" / "lint_slop.py"


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINTER), *args],
        cwd=cwd or REPO,
        text=True,
        capture_output=True,
        check=False,
    )


def test_repository_is_clean():
    result = _run("--root", str(REPO))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "lint-slop: clean" in result.stdout


def test_linter_fails_on_the_word_the_handoff_calls_out(tmp_path: Path):
    # Construct the term at runtime so this test file itself stays clean.
    banned = "guaran" + "teed"
    sample = tmp_path / "claim.txt"
    sample.write_text(f"This outcome is {banned}.\n", encoding="utf-8")

    result = _run("--root", str(REPO), str(sample))
    assert result.returncode == 1
    assert banned in result.stdout.lower() or "guaran" in result.stdout


def test_linter_fails_on_a_clean_then_dirty_pair(tmp_path: Path):
    clean = tmp_path / "ok.md"
    clean.write_text("A 50-leg slip is paid at 0.15 of the advertised odds.\n")
    dirty = tmp_path / "bad.md"
    dirty.write_text("Buy this risk" + "-free tip.\n")

    ok = _run("--root", str(REPO), str(clean))
    assert ok.returncode == 0, ok.stdout + ok.stderr

    bad = _run("--root", str(REPO), str(dirty))
    assert bad.returncode == 1
    assert "risk" in bad.stdout


def test_css_width_percent_is_allowed_but_a_claim_is_not(tmp_path: Path):
    css = tmp_path / "ok.css"
    css.write_text("main { width: 100%; max-width: 100%; }\n")
    ok = _run("--root", str(REPO), str(css))
    assert ok.returncode == 0, ok.stdout + ok.stderr

    claim = tmp_path / "claim.txt"
    claim.write_text("This method is 100" + "% " + "accurate.\n")
    bad = _run("--root", str(REPO), str(claim))
    assert bad.returncode == 1
