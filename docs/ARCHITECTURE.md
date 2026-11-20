# Architecture

SportyAgent is one product with a shared Python core and a few thin surfaces. The expensive work — harvesters, models, the NO-BET gate, the evidence ledger — happens once. Everything a user clicks or a client calls is a shell around that core.

This note is a distillation of the research handoff (Parts 1, 2, 8 and 9). The verbatim source is [HANDOFF.md](HANDOFF.md). Where the earlier drafts disagree, the six-phase plan and the `core/` + `web/` + `mcp/` layout in the README win.

## Surfaces

| Surface | Role | Who runs it | Ships |
| --- | --- | --- | --- |
| Core | Python: harvesters, models, gate, ledger, simulators | the repo | v0.1 (skeleton now) |
| API | Local wrapper over the core, loopback by default | the user | v0.1 |
| Web app | Next.js 15 in Phase 1; Phase 0 is a static page served by `./start.sh` | the user's browser | Phase 1 |
| MCP server | TypeScript, same API, six read-only tools | Claude, Cursor, or any MCP client | Phase 4 |
| Desktop | A later shell around the web app, if at all | the user | v1, maybe |
| Hosted inside a user's AI | refused | — | — |

"Tell your AI to host it" is refused for a practical reason. If a third-party model hosts the tool, that model also holds the API key and the session. A loss cap, a self-exclusion, and an audit log become suggestions. The safety rules only hold if this process owns the runtime.

The default AI mode is the user's own key, stored in a local vault, never sent to a SportyAgent server. A local model (Ollama) is an option. A project-supplied key, if it ever exists, has to be capped and metered; a research loop can burn tens of thousands of tokens per match.

## Process model

One command: `./start.sh`. In Phase 0 that command creates a virtualenv, installs the package, and serves `web/index.html` on `127.0.0.1:3000`. It will not bind `0.0.0.0`.

Phase 1 keeps that entry point and switches the page to Next.js 15 (App Router, TypeScript, Tailwind) talking to a FastAPI wrapper around the core, with SQLite for local state. The bind address stays loopback unless the user later chooses a tighter, documented exception.

Credentials never leave the machine. There is no multi-tenant cloud deployment in this design.

## Core modules

The import name is `sportyagent`, living under `core/`:

- `harvest/` — public endpoint collectors and parsers. All network I/O for SportyBet belongs here, or in the API layer that calls it.
- `models/` — Poisson, Elo, ensemble, and the LLM analyst. Sports fixtures only.
- `gate/` — edge threshold, evidence floor, stake caps. "Do not bet" is a successful result.
- `ledger/` — evidence records (claim, confidence, graded source, limitations, coverage, timestamp) and a hash-chained audit log.
- `sim/` — accumulator decay, ruin, crash-game distributions. Phase 0 already ships the published AnyWin `oddsKeys` table as `payout_multiplier`.
- `api/` — the local server.

RNG, live-dealer, virtuals and crash games are never predicted. They get risk mathematics, or a plain statement that there is nothing to model. A prediction leaking out for those classes is a bug, and a test should catch it.

The identity of the system is the evidence record. The loop is:

```
target → unknowns → hypotheses → evidence[] → verdict → (optional) bet → journal
```

Every arrow is stored. Settled verdicts are re-scored (Brier, log loss, closing-line value where a price was captured) so the app can publish its own calibration and be caught when it is wrong.

## Transport decisions that are already settled

A few platform facts change the shape of the code. They were verified against the live site on 19–20 November 2026 and should not be re-derived as folklore.

- **The fixtures feed needs a signature the page computes.** A replica call with session cookies still returns `19000 Invalid`. All such reads go through a real browser session. That is the design, not a temporary workaround. Do not try to reconstruct the signature.
- **Bet placement is encrypted.** The order body is processed inside the site's bundle. The server replies `REQUEST_DECRYPT_FAILED` to anything it cannot decrypt. Decision: drive the page, or do not place. Placement is Phase 5, and only if the caps and the audit log are airtight.
- **The games lobby needs the header `x-platform: WAP`.** Without it, the request fails with HTTP 500.
- **Two response contracts exist.** Older namespaces return `{bizCode, innerMsg, message, data}`; newer ones return `{errorCode, errorName, causeMsg}`. Parsers have to handle both.
- **Base markets carry `probability` fields that sum to 1.0000.** Those are de-vigged figures. The margin lives in `odds` (typical overround 7–9%) and in product rules such as the accumulator `oddsKeys` and the boost-to-RTP table.

The three figures the UI must lead with, each fetched, timestamped, and linked to its endpoint once Phase 1 ships:

- about 8% typical base-market overround
- 0.15× payout multiplier at 50 legs
- 0.00–0.50 RTP band at a 1.25× odds boost

If an endpoint changes, the page should say so rather than show a stale number without comment. That is also why the repo has an "endpoint changed" issue template.

## Security notes that affect the layout

See [SECURITY.md](../SECURITY.md) for reporting and for the honest limits. In short: bind loopback explicitly; header tokens rather than cookies; Host and Origin checks; a vault that does not write secrets in the clear; a hash-chained audit log with the head hash stored outside the database.

`make audit` is the hook for the later ten-part suite. Phase 0 runs the banned-language linter only.

## What this file is not

It is not a licence to implement placement, a scraper-at-scale, or a hosted tips service. The backlog and the stop-list are in [ROADMAP.md](ROADMAP.md).
