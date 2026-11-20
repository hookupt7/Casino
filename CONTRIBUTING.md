# Contributing to SportyAgent

Thanks for wanting to help. This project only works if the numbers stay honest and the copy stays calm, so the bar is a bit stricter than a typical weekend repo.

## Before you start

1. Read the [README](README.md), especially **What it is not**, **Hard constraints**, and **Honest limits**.
2. Skim [docs/ROADMAP.md](docs/ROADMAP.md). Phase 1 (the live RTP and accumulator page) and Phase 2 (the analyst) are the product. Almost everything else waits.
3. If you are changing architecture or transport, read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). The fixtures feed signature is not something to reconstruct. Drive a real browser, or do not make the call.

Please also follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Set up

You need Python 3.11 or newer.

```bash
git clone https://github.com/hookupt7/Casino.git
cd Casino
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make lint-slop
make test
```

`./start.sh` installs the same extras and serves the Phase 0 page at `http://127.0.0.1:3000`. It will refuse to bind a public interface.

## What a good change looks like

- Maths and published tables are tested. If you touch `payout_multiplier` or a later model, add a case with a known answer.
- User-facing claims cite a source URL and a timestamp, or they do not ship.
- New network I/O lives in the harvest or API layers, not in a random module.
- Dependencies are justified in the pull request. Prefer the standard library. A new package needs a sentence on why an existing option is not enough.
- Credentials, cookies, and API keys are never logged, committed, or sent off the machine.

## What will be rejected

- Outcome-claim wording. The linter fails the build on a list that includes "guaran" + "teed" and the other terms from the handoff. Do not try to sneak the same claim past it with a synonym.
- Cloud-hosted multi-tenant designs, credential collection, or anything that asks a user to paste a SportyBet password into a server you run.
- Virtuals or crash-game "pattern" models. Those games are treated as random.
- A Discord bot, a mobile app, or placement code ahead of the phases that own them.

## Banned language

Run `make lint-slop` (or `python3 scripts/lint_slop.py`) before you open a pull request. CI runs the same check.

The linter flags outcome-claim wording and the slop phrases listed in `scripts/lint_slop.py`. The verbatim research document at `docs/HANDOFF.md` is excluded because it quotes the banned list and the raw research notes. Do not copy those phrases into new docs or UI copy.

Write in plain sentences of mixed length. Lead with the fact, not a mission statement.

## Pull requests

Use the pull request template. Link an issue when there is one. Keep the diff focused: one problem, one PR, tests and linter green.

Preferred issue types, besides ordinary bugs and features:

- **Endpoint changed** — a SportyBet path or contract moved.
- **Model was wrong** — a verdict or probability did not match the result. Being wrong is expected; hiding it is not.

## Review axes

Reviewers will look at, in roughly this order:

1. Does any copy promise an outcome?
2. Is every new claim sourced?
3. Is the maths tested?
4. Could this leak a credential, a session, or a key?
5. Is the change in the right module?
6. Does it pull the work away from Phase 1 or 2?

## Commit style

Short imperative subject, body when the why is not obvious. Example: `Add AnyWin payout multiplier table from factsCenter config`.
