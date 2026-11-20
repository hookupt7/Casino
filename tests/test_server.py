from pathlib import Path

import pytest

from sportyagent.api.server import bind_host, web_dir


def test_web_page_exists_and_cites_the_accumulator_finding():
    page = web_dir() / "index.html"
    text = page.read_text(encoding="utf-8")
    assert "0.15" in text
    assert "factsCenter/betType/config" in text


def test_bind_host_refuses_public_interfaces():
    assert bind_host("127.0.0.1") == "127.0.0.1"
    assert bind_host("localhost") == "127.0.0.1"
    with pytest.raises(ValueError):
        bind_host("0.0.0.0")
    with pytest.raises(ValueError):
        bind_host("::")


def test_repo_layout_has_the_phase_zero_entry_points():
    root = Path(__file__).resolve().parents[1]
    assert (root / "start.sh").is_file()
    assert (root / "Makefile").is_file()
    assert (root / "docs" / "HANDOFF.md").is_file()
