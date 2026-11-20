# Changelog

All notable changes to SportyAgent are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and version numbers follow [SemVer](https://semver.org/).

## [Unreleased]

Nothing yet beyond the initial skeleton.

## [0.1.0] — 2026-11-20

Phase 0. The repository is usable as a clone-and-run tree, but the live RTP page is not in this version.

### Added

- Repo layout: `core/` (Python package `sportyagent`), `web/`, `mcp/`, `docs/`
- `start.sh` serves the Phase 0 page on `http://127.0.0.1:3000` and refuses a public bind
- Published AnyWin accumulator payout table (`payout_multiplier`) from `/api/ng/factsCenter/betType/config`, verified 19–20 November 2026
- Static local page that leads with the 0.15× finding
- Banned-language linter (`scripts/lint_slop.py`, `make lint-slop`) and pytest coverage
- GitHub Actions CI on Python 3.11 and 3.13, running the linter and the tests
- MIT licence, contributor documents, issue and pull request templates
- Verbatim research handoff at `docs/HANDOFF.md`, plus architecture and roadmap distillations
