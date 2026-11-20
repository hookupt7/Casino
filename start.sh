#!/usr/bin/env bash
# One command: install the local package and serve the Phase 0 page.
# Binds 127.0.0.1 only. Credentials are not collected.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "SportyAgent needs python3 (3.11 or newer) on PATH." >&2
  exit 1
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-3000}"
if [[ "$HOST" != "127.0.0.1" && "$HOST" != "localhost" ]]; then
  echo "Refusing to bind $HOST. SportyAgent listens on 127.0.0.1 only." >&2
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "Creating a virtualenv in .venv"
  "$PYTHON" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q -U pip
python -m pip install -q -e ".[dev]"

echo
echo "SportyAgent  Phase 0"
echo "Open  http://127.0.0.1:${PORT}"
echo "Stop with Ctrl+C"
echo
exec python -m sportyagent.api --host 127.0.0.1 --port "$PORT"
