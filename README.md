# SportyAgent

[![CI](https://github.com/hookupt7/Casino/actions/workflows/ci.yml/badge.svg)](https://github.com/hookupt7/Casino/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A 50-leg accumulator on SportyBet is paid at **0.15** of the advertised odds. That factor is not buried in a PDF. It is published at `/api/ng/factsCenter/betType/config`, and it falls from **0.95** at two or three legs down to **0.15** at 47 and above.

This repository, named Casino on GitHub, is the public home of **SportyAgent**: an open-source tool that puts that number on one local page, next to the operator's own boost-to-RTP table and the fact that every one of the 21 lobby games returns `rtp: null`. It does not pick winners. It makes the cost of a slip visible.

Research behind these figures was checked against the live site on 19–20 November 2026. Phase 0, which is what this commit ships, is the repo skeleton, a working `./start.sh`, CI, and that static page. Live fetch lands in Phase 1.

## Contents

- [Creator](#creator)
- [What it is](#what-it-is)
- [What it is not](#what-it-is-not)
- [Hard constraints](#hard-constraints)
- [Honest limits](#honest-limits)
- [Quickstart](#quickstart)
- [Roadmap](#roadmap)
- [Project structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Responsible gambling](#responsible-gambling)
- [License](#license)

## Creator

Created by Oanks. TikTok: [@oanksswag](https://www.tiktok.com/@oanksswag)

## What it is

A research tool for SportyBet (Nigeria) that you run on your own machine. Clone it, run one command, open `http://127.0.0.1:3000`.

Three findings, all public and unauthenticated, sit at the centre of the product:

- **Accumulator decay.** `/api/ng/factsCenter/betType/config` publishes the payout multiplier as legs grow: 0.95 at 2–3 legs, 0.15 at 47+. Flexi declares `flexiAverageWeightedMinEffectiveRtp: 0.8`.
- **Boost-to-RTP table.** `/api/ng/marketing/v1/activities/oddsBoost/getOddsBoostLobRtpRatio` maps a 1.25× “odds boost” to an RTP band of **0.00–0.50**. A boosted selection can pay nothing.
- **Unpublished game RTP.** All 21 lobby games return `rtp: null`. Base market overround on ordinary sports markets runs 7–9%. The `probability` fields on those markets sum to 1.0000; they are de-vigged figures supplied with the feed, and the margin sits on top in `odds`.

Later phases add a research agent that is allowed to say “no bet,” a journal that scores its own calibration, and an optional MCP server. The agent only recommends when the evidence is strong enough. “I don’t know” is a valid verdict.

Even a competent forecaster loses regularly. Any edge is small, measured in fractions of a percent, and only visible over hundreds of bets.

## What it is not

- A tipster channel, a signal group, or a “prediction” product that pretends the next result is known.
- Affiliated with SportyBet or Super Group. This is an independent, unofficial tool.
- A hosted multi-tenant service. There is no cloud account to sign up for, and we will not build one.
- A credential collector. Login details never leave your machine, and they are not requested in Phase 0 or Phase 1 at all.
- A model of virtuals, Aviator, instant games, or live-dealer tables. Those are treated as random or as house-edge displays, never as puzzles to be solved.
- Financial, legal, or gambling advice. You can lose the entire stake on any bet.

## Hard constraints

These are non-negotiable, in the app and in this repo:

1. Never claim a certain outcome, anywhere, in any string.
2. Never place a bet without either an explicit human confirmation or an expiry-bound loss cap. Placement itself is Phase 5, and only if it survives review.
3. Every claim in user-facing output traces to an evidence record with a source URL and a timestamp.
4. Games classified as RNG or live-dealer are never predicted; they get risk mathematics only.
5. Credentials never leave the user's machine.

A CI linter (`make lint-slop`) fails the build if banned outcome-claim wording lands in the tree. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Honest limits

- No tool can tell you what will happen in a match. Anyone who says otherwise is selling you something.
- The bookmaker's margin means the average bettor loses. The only long-run defence is betting rarely, small, and only with a measured edge.
- Virtuals, Aviator and instant games are certified random. There is nothing to research. This app will tell you that every time you open those pages.
- Automated access may breach SportyBet's terms of use and can get an account closed, with winnings voided. That risk will be stated in the consent screen if placement ever ships, not buried in a file nobody opens.
- If gambling stops being fun, stop. Use the operator's own limits and self-exclusion, and the support resources below.

## Quickstart

You need Python 3.11 or newer.

```bash
git clone https://github.com/hookupt7/Casino.git
cd Casino
./start.sh
```

Then open [http://127.0.0.1:3000](http://127.0.0.1:3000). The process binds loopback only; it will refuse `0.0.0.0`.

To run the checks without serving the page:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make lint-slop
make test
```

`make audit` runs the linter today. The rest of the audit suite (dependency audit, secret scan, vault export guard, and so on) lands with later phases.

## Roadmap

| Phase | What ships | Login | AI key | Status |
| --- | --- | --- | --- | --- |
| 0 | Repo skeleton, `start.sh`, CI, banned-language linter, static page | no | no | **this commit** |
| 1 | Live RTP + accumulator page | no | no | next |
| 2 | Analyst: fixtures, models, critic, NO-BET gate | no | yes (your key) | planned |
| 3 | Journal, bankroll, ruin simulator, calibration | no | no | planned |
| 4 | MCP server, six read-only tools | no | optional | planned |
| 5 | Browser-driven placement, guarded | yes | yes | only if review passes |

Phase 1 is the launch. It needs no account, no key, and no server of ours. Details, and the list of things we will not build, are in [docs/ROADMAP.md](docs/ROADMAP.md).

## Project structure

```
Casino/
├── start.sh                 one command, reaches a working page
├── Makefile                 audit, test, lint-slop
├── scripts/lint_slop.py     fails the build on banned wording
├── core/                    python (import name: sportyagent)
│   └── sportyagent/
│       ├── harvest/         sportyharvest, odds analyser, game catalogue
│       ├── models/          poisson, elo, ensemble, llm analyst
│       ├── gate/            edge threshold, evidence floor, stake caps
│       ├── ledger/          hash-chained evidence + audit log
│       ├── sim/             ruin simulator, accumulator decay
│       └── api/             local server (FastAPI later)
├── web/                     Phase 0 static page; Next.js 15 in Phase 1
├── mcp/                     TypeScript MCP server (Phase 4)
├── docs/                    research, architecture, roadmap
└── tests/
```

## Documentation

- [docs/HANDOFF.md](docs/HANDOFF.md) — the complete original research and planning document, copied verbatim
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the pieces fit, and the transport decisions that already exist
- [docs/ROADMAP.md](docs/ROADMAP.md) — phases, first issues, and the out-of-scope list
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to propose a change
- [SECURITY.md](SECURITY.md) — threat model and how to report a vulnerability
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Contributor Covenant

## Contributing

Pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before you open one, and run `make lint-slop` and `make test`. By participating you also agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Responsible gambling

This tool is for adults (18+) who already choose to look at a betting product, and who want the costs of that product in the open. It will not help you “get even.”

If you want to stop, start with the operator's own tools. SportyBet exposes self-exclusion and self-imposed betting limits in its account API; those are the first controls to use.

Verified Nigerian resources (checked 20 November 2026):

- [Gamble Alert](https://gamblealert.org/) — independent nonprofit. 24/7 helpline +234 916 295 7989. Toll-free +234 705 889 0073 and +234 705 889 0074.
- [SafePlay](https://safeplay.ng/) — Lagos State Lotteries and Gaming Authority (LSLGA) self-exclusion registry. Free, NIN-verified, covers LSLGA-licensed operators including SportyBet. It does not cover unlicensed or offshore sites.

If you are outside Lagos or Nigeria, use the support and self-exclusion routes in your own jurisdiction.

## License

[MIT](LICENSE). Copyright 2026 Oanks.

The original handoff proposed AGPL-3.0. This public repository ships under MIT as the licence on the project. The research notes in `docs/HANDOFF.md` still mention AGPL in places; that is a record of the earlier plan, not the licence of this tree.
