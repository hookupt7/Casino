# Roadmap

Phases land as tagged releases. A project that ships several times looks alive; a project that sits on one giant drop does not. Phase 1 is the launch. Phase 2 is enough for people to keep using the tool. Everything after that is a reward for finishing those two.

This is a distillation of the handoff (Part 1 §§C, W, X and Part 2). The verbatim plan, including the longer feature list, is in [HANDOFF.md](HANDOFF.md).

## Phases

| Phase | What ships | Login | AI key | Status |
| --- | --- | --- | --- | --- |
| 0 | Repo skeleton, `start.sh`, CI, banned-language linter, static page | no | no | **done (this tree)** |
| 1 | Live RTP + accumulator page | no | no | next |
| 2 | Analyst: fixtures, models, critic, NO-BET gate | no | yes (user's key) | planned |
| 3 | Journal, bankroll, ruin simulator, calibration | no | no | planned |
| 4 | MCP server, six read-only tools | no | optional | planned |
| 5 | Browser-driven placement, guarded | yes | yes | only if review passes |

Release tags in the original plan: v0.1 skeleton, v0.2 RTP page, v0.3 analyst, v0.4 accounting, v0.5 MCP. This repository treats the table above as the source of truth if a later paragraph in the handoff disagrees.

### Phase 0 — skeleton

The first thing anyone does is `git clone && ./start.sh`. That path already works. CI runs the linter and the tests. The static page leads with the 0.15× accumulator finding and cites the endpoint. The published AnyWin `oddsKeys` table is in `sportyagent.sim.accumulator`.

### Phase 1 — the page that makes it real

Pull `getOddsBoostLobRtpRatio` live and render the boost-to-RTP table beside an accumulator decay calculator. No login, no accounts, no AI. It works the second someone opens it.

One number dominates each screen. The 1.25× row looks different from the 1.00× row without a label explaining why. No hero section, no gradient buttons, no stock photograph. Tabular figures, dark by default, mobile first. Cite the endpoint at the bottom of the screen. If the endpoint fails, show an honest error, not a blank or a stale silent number.

### Phase 2 — the analyst

Fixture list, market list, and an evidence-backed research loop. Poisson and Elo models alongside an LLM analyst, a critic pass whose job is to argue against the pick, and a NO-BET gate that fires on thin evidence. Bring-your-own-key only in this phase.

The agent may conclude that there is not enough evidence to bet. That is a successful run.

### Phase 3 — accounting

Journal, bankroll, ruin simulator, calibration dashboard. This is where the app starts telling users things they may not want to hear, which is the point.

### Phase 4 — MCP server

Six tools, read-only at first: `list_fixtures`, `get_market_prices`, `research_match`, `check_rtp`, `get_bankroll`, `log_bet`. Write access for placement is out of scope for the first MCP release.

### Phase 5 — placement, only if it survives review

Browser-driven, with an expiry-bound loss cap, explicit confirmation, and an audit log. If the caps and the log are not airtight, ship without placement and say so in the README. Automated access may breach the operator's terms and can get an account closed.

## First issues, once the tracker is open

These come from the original plan and are still the right order after the skeleton:

1. Keep `./start.sh` booting a working page on a clean clone (already true for Phase 0; must stay true as the web app grows).
2. Consent gate and legal screens, blocking on first run, before later features.
3. SportyBet read client through a real browser session (no forged fixtures-feed signature).
4. Poisson / Dixon-Coles model, tested on a known season.
5. Elo model, tested against known values.
6. LLM analyst tool loop: every claim has a URL; runs inside a token budget.
7. Ensemble / synthesizer, weighted by recent Brier scores.
8. NO-BET gate: edge threshold, data completeness, stake caps.
9. Journal and bankroll.
10. Calibration dashboard.

## What we will not build

- A cloud-hosted multi-tenant version
- Credential collection of any kind
- Copy that promises a certain outcome
- Virtuals or crash-game "pattern" models
- A Discord bot before the web app works
- A mobile app before the MCP server
- Hosting the tool inside a user's AI, which would break the loss cap, the vault, and the audit log

## Scope risk

The handoff contains a long feature list. That list is a backlog, not a promise for the next month. If a change does not help Phase 1 or Phase 2, it waits.
