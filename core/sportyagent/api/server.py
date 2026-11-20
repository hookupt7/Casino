"""A tiny localhost static server for Phase 0.

Binds 127.0.0.1 only. ``next start`` (Phase 1) defaults to 0.0.0.0;
start.sh and this module both refuse that.
"""

from __future__ import annotations

import argparse
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3000


def repo_root() -> Path:
    # core/sportyagent/api/server.py → repo root is parents[3]
    return Path(__file__).resolve().parents[3]


def web_dir() -> Path:
    path = repo_root() / "web"
    if not (path / "index.html").is_file():
        raise FileNotFoundError(f"missing Phase 0 page at {path / 'index.html'}")
    return path


class LocalPageHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(web_dir()), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def bind_host(host: str) -> str:
    if host not in ALLOWED_HOSTS:
        raise ValueError(
            f"refusing to bind {host!r}; SportyAgent listens on 127.0.0.1 only"
        )
    # "localhost" can resolve to ::1; use the loopback address explicitly.
    return "127.0.0.1"


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    address = (bind_host(host), port)
    directory = str(web_dir())

    class Handler(LocalPageHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    httpd = ThreadingHTTPServer(address, Handler)
    print(
        f"SportyAgent Phase 0 — open http://127.0.0.1:{port}",
        flush=True,
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    finally:
        httpd.server_close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Serve the SportyAgent Phase 0 page")
    parser.add_argument("--host", default=os.environ.get("HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", DEFAULT_PORT)))
    args = parser.parse_args(argv)
    serve(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
