.PHONY: audit test lint-slop

PYTHON ?= python3

lint-slop:
	$(PYTHON) scripts/lint_slop.py

test:
	$(PYTHON) -m pytest

audit: lint-slop
	@echo "Phase 0 audit runs the banned-language linter."
	@echo "Later phases add dependency audit, lockfile drift, secret scan,"
	@echo "vault export guard, redaction tests, permission checks, licence scan,"
	@echo "audit-chain integrity, and SBOM diff."
