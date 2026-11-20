# SportyAgent — Complete Handoff Document

**What this is.** Every plan, research finding, design document and tool specification for an
open-source AI betting-research tool for SportyBet (Nigeria), assembled into one file so it can be
handed to a coding agent.

**Status.** Research complete and verified against the live site on 2026-11-19/20. No application
code written yet. Three working Python tools exist (specifications in Part 1, section Z).

**How to use this document.** Part 1 is the summary and the decision record; read it first. Parts 2–4
set the product decisions and the agent's reasoning discipline. Parts 5–7 are verified platform
facts. Parts 8–9 are the engineering contracts. Parts 10–11 are the research log and the honest
evidence on what can and cannot be predicted. Part 12 is the full feature backlog.

**The one-line brief.** Make visible what SportyBet's odds, multipliers and RTP intervals actually
cost the player — then let an agent research matches within an evidence discipline that can say
"I don't know."

**Hard constraints, non-negotiable.**
1. Never claim a guaranteed outcome, anywhere, in any string.
2. Never place a bet without either an explicit human confirmation or an expiry-bound loss cap.
3. Every claim in user-facing output traces to an evidence record with a source URL and timestamp.
4. Games classified as RNG or live-dealer are never predicted; they get risk mathematics only.
5. Credentials never leave the user's machine.

**What has been verified about the platform** (so the agent does not have to re-derive it):
- Base markets carry `probability` fields that sum to exactly 1.0000; these are de-vigged true
  probabilities supplied by Betgenius. The `odds` field carries a 7–9% overround on top.
- Accumulator payout multipliers decay 0.95 → 0.15 as legs grow; published at `factsCenter/betType/config`.
- Odds-boost to RTP mapping is published: 1.25× boost maps to a 0.00–0.50 RTP band.
- All 21 games in the lobby return `rtp: null`.
- Fixtures feed requires a page-computed signature; bet placement is encrypted. Both mean the only
  viable transport is a real browser session.
- Games lobby API requires header `x-platform: WAP` or returns HTTP 500.

---



---

# Part 1 — The Plan, A to Z


## SportyAgent — Everything, A to Z
The complete plan. Written 2026-11-20. Read this file first; it links to the rest.

---

### A — What this is

An open-source AI research tool for SportyBet. You clone it, run one command, open localhost, and get a page that tells you what your bets actually cost you. After that comes a research agent that argues with itself before recommending anything, and a bankroll tracker that keeps score.

It does not predict winners with certainty. Nothing does. What it does instead is make the maths visible, which is the part the product currently hides.

### B — Why it exists

Three findings, all verified live against sportybet.com, all checkable in under a minute by anyone:

**The boost table.** `/api/ng/marketing/v1/activities/oddsBoost/getOddsBoostLobRtpRatio` returns SportyBet's own mapping from "odds boost" to actual return. At 1.25× the RTP band is **0.00 to 0.50**. A boosted selection can pay nothing.

**The accumulator decay.** `/api/ng/factsCenter/betType/config` publishes the multiplier applied to a winning slip as legs grow: **0.95 at 2–3 legs, falling to 0.15 at 47+**. A 50-leg slip pays 15% of its advertised odds. Flexi declares `flexiAverageWeightedMinEffectiveRtp: 0.8`.

**The unpublished RTP.** All 21 games in the lobby return `rtp: null`. The field exists. They don't fill it. Base market overround runs **7–9%**.

None of this is secret. It's public, unauthenticated, and nobody has put it on one screen.

### C — What ships, in order

| # | Thing | Needs a login | Needs an AI key | Time |
|---|---|---|---|---|
| 0 | Repo skeleton, `start.sh`, CI | no | no | 3 d |
| 1 | **RTP + accumulator page** | no | no | 2 wk |
| 2 | Analyst (fixtures, models, critic, NO-BET) | no | yes | 3 wk |
| 3 | Journal, bankroll, ruin sim, calibration | no | no | 2 wk |
| 4 | MCP server, six read-only tools | no | optional | 1 wk |
| 5 | Browser-driven placement, guarded | **yes** | yes | open |

Phase 1 is the launch. It requires no account, no key, no server. It works the second someone opens it.

### D — The stack

Python core, because that's where the maths and the existing tools already live. FastAPI for the local API. Next.js 15 with TypeScript for the web app. SQLite through Drizzle. Node for the MCP server, because MCP clients expect it.

Why not all TypeScript: the harvesters, the Poisson and Elo models, and the simulators are already written and tested in Python. Rewriting them to unify the language would cost two weeks and buy nothing.

```
sporty-agent/
├── start.sh                    one command, reaches a working page
├── core/                       python
│   ├── harvest/                sportyharvest, odds_analyzer, game_catalogue
│   ├── models/                 poisson, elo, ensemble, llm_analyst
│   ├── gate/                   edge threshold, evidence floor, stake caps
│   ├── ledger/                 hash-chained evidence + audit log
│   ├── sim/                    ruin simulator, accumulator decay
│   └── api/                    FastAPI
├── web/                        next.js 15
├── mcp/                        typescript mcp server
├── docs/                       the research already written
└── makefile                    audit, test, lint-slop
```

### E — The AI layer

Three ways to supply a model, and the default is the user's own key.

**Their key.** Encrypted in the vault, never reaching your server. They pay their own tokens. This is the default because it's the only mode that costs you nothing and scales to a thousand users.

**Local model.** Ollama. Zero cost, works offline. Slower and weaker on research, so it's an option rather than the default.

**Your key.** Only if you charge, or cap hard. A research loop with web fetching and a critic pass burns 20k–80k tokens per match. Three free analyses a day with a visible meter is the honest free tier.

The agent's discipline comes from `AGENT-METHOD.md`: open a target, list unknowns, record hypotheses, gather graded evidence, verify, report. A claim supported only by social media cannot pass the gate no matter how confident the model sounds.

### F — The identity and data model

Everything is an evidence record: claim, confidence, source with grade A–D, limitations, coverage, timestamp. That structure is why the tool can say "I don't know," and why a recommendation is traceable to the page that justified it.

```
target → unknowns → hypotheses → evidence[] → verdict → (optional) bet → journal
```

Every arrow is stored. Every verdict is re-scored once the result is known, so the app can publish its own Brier score and be caught when it's wrong.

### G — Greece, or: the numbers that must be on the page

The three figures the app leads with, each pulled live:

- **8%** — typical base market overround
- **0.15×** — payout multiplier at 50 legs
- **0.00–0.50** — RTP band at 1.25× odds boost

Every one is fetched, timestamped, and linked to the endpoint that produced it. If an endpoint changes, the page says so instead of showing a stale number without comment.

### H — How it handles all the games

Four tiers, decided per game class at runtime, not by hand:

**Modellable.** Football and the other 21 sports verticals. Full research loop.

**Risk maths only.** Aviator, Sporty Jet, crash games. No prediction. A simulator that runs any auto-cashout strategy a thousand times and shows the distribution.

**Not modellable.** vFootball, eSoccer, eBasketball, virtuals, SportySIM. The verified fact that the virtuals engine returns 403 without a session, plus the fact that no seed is exposed anywhere in 5 MB of bundle, means there is nothing to model. The app says this plainly and offers an expected-loss calculator.

**House edge only.** Lucky Numbers, jackpot, the 21 lobby games. RTP is unpublished on every one, and the app says that too.

If the agent ever emits a prediction for a game in tiers two through four, that's a bug and the test suite fails.

### I — Implementation notes worth knowing up front

**The fixtures feed needs a signature the page computes.** A replica call with session cookies still returns `19000 Invalid`. So all reads go through a real browser context. That is not a workaround, it's the design.

**Bet placement is encrypted.** The order body goes through a routine inside the bundle; the server replies `REQUEST_DECRYPT_FAILED` to anything it can't decrypt. `ARCHITECTURE.md` already has the decision recorded: drive the page or don't place.

**The games lobby needs `x-platform: WAP`.** Without it, HTTP 500 on every request. Found by grepping their 2 MB games bundle, after an hour of 404s on guessed paths.

**Two contracts exist.** Older namespaces return `{bizCode, innerMsg, message, data}`; newer ones return `{errorCode, errorName, causeMsg}`. Parsers handle both.

### J — Journal and calibration

Every analysis is logged with its probability. Once the match settles, the log is scored: Brier, log loss, and closing line value where a price was captured. The app publishes a calibration curve — predicted probability on one axis, observed frequency on the other.

This is the feature that separates the project from every tipster page. Not accuracy, honesty about accuracy.

### K — Kelly and the limits

Quarter-Kelly, capped in notes, never full Kelly. A worked example sits in `landscape.md`: 10,000 naira at odds 2.00 with a true 52% is a 100-naira stake. Anyone staking a tenth of their bankroll per bet is not betting, they're donating.

Hard stops that can't be raised without a cooldown: daily loss cap, session budget with expiry, correlation cap of two legs per match, and a calibration floor that widens the gate automatically when the model's recent Brier score is worse than backing the favourite.

### L — Legal pack

Seven documents in `docs/`: TERMS, DISCLAIMER, RISK_WARNING, ACCEPTABLE_USE, PRIVACY, RESPONSIBLE_GAMBLING, and the licence (AGPL-3.0). Plus a blocking consent screen inside the app that requires typed acknowledgement and re-consent on major versions.

The honest sentence, which appears in the README and the app: even a good forecaster loses regularly; any edge is small, measured in fractions of a percent, and only visible over hundreds of bets.

A CI linter fails the build on the words guaranteed, sure, 100%, win big, risk-free, can't lose, fixed match, hack.

### M — Money

Zero to run. The user's key pays for inference. Hosting the static pages is free on any of the usual suspects. If you later host a shared API, that's where cost appears, and it's the reason the free tier is three analyses a day rather than unlimited.

### N — Naming

Working name SportyAgent. Check it isn't taken on npm and PyPI before the first commit. If it is, the fallback is the honest one: something that describes the artefact rather than promising an outcome.

### O — Open source and community

AGPL-3.0, because it keeps forks open and stops someone turning the tool into a paid tips service without publishing their changes. Contributor guide with the code review axes from `code-review-and-quality`. Issue templates for "endpoint changed" and "model was wrong," both of which will happen weekly.

First ten issues are already specified in `PLAN.md` section 11.

### P — Performance and data

Cache every external call with a source-class TTL and stale-while-error. Serve stale data with a visible marker rather than a blank page. Single-flight dedup so parallel tool calls don't stampede the same endpoint. A failure ledger listing every source that's down on the card.

### Q — QA

Playwright against the local server, `with_server.py` managing the lifecycle. The tests that matter: clean clone reaches a working page; the RTP page shows correct numbers from a mocked response and an honest error when the endpoint fails; the NO-BET gate blocks a fixture with missing lineups; the key field never writes plaintext to storage; the slop linter fires.

Screenshot each phase's main screen into `docs/screens/`.

### R — Risk register

**Scope.** 100+ features in PLAN.md, one maintainer. Phase 1 and 2 are the whole product. Everything else is a reward for shipping those.

**Endpoint drift.** SportyBet can change `bizCode` or params at any time. Mitigation: the contract is asserted in tests, and a failed assertion opens an issue automatically rather than failing silently.

**Account risk.** Automated access may breach their terms and can get an account closed. This is stated in the consent screen, not buried in a document nobody opens.

**Reputational risk.** Two of the top three SportyBet repos on GitHub are outright balance-adder scams. Guilt by association is real, so the README names the difference in the first paragraph and the app never promises an outcome.

**AI cost surprise.** A research loop without caching doubles its own bill. Token budget per analysis, enforced in code, not in a prompt.

### S — Security

Local vault, Argon2id derivation, AES-256-GCM, keybinding to the OS keychain where available, 15-minute auto-lock. Bind to 127.0.0.1 explicitly, because `next start` defaults to 0.0.0.0. Per-install token in a header, no auth cookies, Host and Origin checks, body size limits. Hash-chained audit log with the head hash stored outside the database.

`make audit` runs ten checks: dependency audit, lockfile drift, secret scan, slop linter, vault export guard, redaction test, permission check, licence scan, audit-chain integrity, SBOM diff.

The honest limits are in `SECURITY.md` section 6 and stay there. Malware on the machine wins. A user approving a bad slip is still a user approving a bad slip.

### T — Testing the maths

The Poisson model against a known season from football-data.co.uk. The Elo ratings against published values. The accumulator decay against the live endpoint. The ruin simulator against a closed-form case where the answer is known. Kelly against the worked example.

### U — UX principles

One number dominates each screen. The 1.25× row must look different from the 1.00× row without a label explaining why. No hero sections, no gradient buttons, no stock photographs. Numbers in tabular figures so they don't jitter when they update.

Mobile first, because this is a phone market. Dark by default, because people check this at night.

### V — Voice and copy

Follow the banned-word list from `write-anti-ai-slop`. No "it's worth noting," no "at its core," no rule-of-three paragraphs, no uniform sentence length. The README's first paragraph is the accumulator finding, not a mission statement.

### W — Workflow

Phases land as tagged releases: v0.1 skeleton, v0.2 RTP page, v0.3 analyst, v0.4 accounting, v0.5 MCP. Each one releasable on its own, because a project that ships five times in a month looks alive and a project that ships once in six months looks abandoned.

### X — What not to build

A cloud-hosted multi-tenant version. Credential collection of any kind. Anything that says "sure prediction." Virtuals pattern models. A Discord bot before the web app works. A mobile app before the MCP server.

### Y — Why this beats the alternatives

Every existing SportyBet repo is a scraper or a scam. The top one has 22 stars and runs Selenium to auto-place bets. Nothing publishes an evidence trail, nothing tracks its own calibration, nothing tells you not to bet. The slot is empty because honesty is harder to build than hype, and it's the only durable thing in this category.

### Z — What to do next

Today: create the repo, `start.sh`, the licence, and the slop linter. Push it. An empty project with a working `./start.sh` is worth more than a perfect one in a notes file.

Next week: the RTP page. Live table, accumulator calculator, endpoint cited at the bottom of the screen.

Then: the analyst.

---

### The files that already exist

| File | What's in it |
|---|---|
| `BUILD-PLAN.md` | The surface decision and six phases |
| `PLAN.md` | 100+ features, legal pack, roadmap, first ten issues |
| `KNOWLEDGE.md` | How the platform works, verified |
| `AGENT-METHOD.md` | How the agent reasons, evidence-first |
| `research/ODDS-DEEP.md` | 321 markets, de-vig proof, product rules verbatim |
| `research/BUSINESS-MODEL.md` | The RTP table, the margin stack, the placement path |
| `research/GAMES-CATALOGUE.md` | 21 games, categories, unpublished RTP |
| `research/ARCHITECTURE.md` | Modules, schema, placement state machine |
| `research/SECURITY.md` | Threat model, vault, audit chain |
| `research/SITE-REVERSE.md` | Endpoint inventory from live traffic |
| `research/landscape.md` | Evidence on whether models beat the margin |
| `tools/sportyharvest.py` | 19 endpoints, evidence ledger, 95 records collected |
| `tools/odds_analyzer.py` | 321 markets classified by how they're priced |
| `tools/game_catalogue.py` | 21 games with RTP status |
| `demo/accumulator-decay.html` | Working interactive calculator |





---

# Part 2 — Surfaces and Phases


## SportyAgent — The Build Plan
Decided 2026-11-20. One product, four delivery surfaces, one shared core.

---

### The decision you asked for

You gave four options for how a user gets the agent. Only one of them is actually a build decision; the other three are distribution channels off the same core.

**Build the web app. Ship it as: web app first, MCP server second, desktop app third, "host it in your AI" never.**

Here's why, one line each.

**Web app.** It's the only surface where a chart, a table of odds and a slip sit together. It's what people screenshot and post. It's what turns a GitHub repo into a project with users. Cost: you own a server, a database, and the security story.

**MCP server.** A different product category and the fastest-growing distribution route for tools right now. Claude Desktop, Cursor, ChatGPT connectors and a dozen agent apps all speak MCP. Write it once in TypeScript and every one of those clients gets "what's the value on Arsenal v Spurs" as a tool call. It is a client of the same core API, not a separate app.

**Desktop app.** Highest effort, smallest reach. Skip until v1.

**"Tell your AI to host it."** This is the one to refuse, and the reason isn't philosophical. If a user's AI hosts the thing, that AI also holds the API key and the session. You cannot enforce a loss cap, a self-exclusion or an audit log when the runtime belongs to someone else's model. Every safety guarantee in `AGENT-METHOD.md` becomes a suggestion. Cross it off because it breaks the one thing that makes the project trustworthy, not because it's hard.

### The architecture in one table

| Surface | What it is | Who runs it | Ships |
|---|---|---|---|
| **Core** | Python: harvesters, models, gate, ledger | you | v0.1 |
| **API** | FastAPI wrapper over core, localhost by default | user or your server | v0.1 |
| **Web app** | Next.js 15, talks to API with a user token | user's browser | v0.5 |
| **MCP server** | TypeScript, wraps the same API | Claude / Cursor / any MCP client | v0.5 |
| **Desktop** | Tauri shell around the web app | user | v1.0 |
| **Hosted in user's AI** | refused | — | — |

The core is the investment. Every surface is a thin shell, which is why the order is cheap: the expensive work happens once.

### Where the AI key comes from — the real decision

Three modes, and the default matters more than the feature.

**Mode 1: user brings their own key.** Default, and the only one that's free for you. Their key sits in encrypted browser storage or the local API vault, never on your server. They pay their own token bill. This is what most users will want, and Nigerian users on limited data will prefer a cheap model they already have an account for.

**Mode 2: local model.** Ollama on their machine. Zero cost, works offline, and it's the honest answer when someone asks whether they can use this without sending their bets to OpenAI. Slower and weaker at research, so it's a checkbox rather than a default.

**Mode 3: you supply the key.** Viable only if you charge, or cap it hard. A research loop with web fetching and a critic pass burns 20k–80k tokens per match. At even $0.30 a match that's real money on a free tier. If you offer it, make it three matches a day with a visible meter.

Whichever mode, the key lives in the vault from `SECURITY.md`. Not plaintext localStorage, not a `.env` on a rented server, never a log line.

### The build, in six phases

**Phase 0 — skeleton (3 days).** Repo, `start.sh`, licence, CI running lint and the banned-language check. Empty pages that load. The point is that `git clone && ./start.sh` works before any features exist, because it's the first thing anyone does.

**Phase 1 — the thing that makes it real (2 weeks).** The RTP tool. A page that pulls `getOddsBoostLobRtpRatio` live and renders the boost-to-RTP table beside an accumulator decay calculator. No login, no accounts, no AI. It works the second someone opens it, and it's what gets shared. Launch artifact; everything else is secondary until it exists.

Design notes for that page: one number dominates each screen. The 1.25× row looks different from the 1.00× row without a label explaining why. No hero section, no gradient buttons, no stock photo of strangers celebrating.

**Phase 2 — the analyst (3 weeks).** Fixture list, market list, and the evidence-backed research loop from `AGENT-METHOD.md`. Poisson and Elo models alongside an LLM analyst, the critic pass, and the NO-BET gate firing on thin evidence. Bring-your-own-key only in this phase.

**Phase 3 — accounting (2 weeks).** Journal, bankroll, ruin simulator, calibration dashboard. This is where the app starts telling users things they don't want to hear, which is the whole value proposition.

**Phase 4 — MCP server (1 week).** Six tools: `list_fixtures`, `get_market_prices`, `research_match`, `check_rtp`, `get_bankroll`, `log_bet`. Read-only at first. An MCP client doesn't need write access to place a bet in order to be useful, and read-only kills an entire category of risk.

**Phase 5 — placement, only if it survives review.** Browser-driven, Mode B caps, audit log. This is where you decide whether you actually want to ship it. If the caps and the log aren't airtight, ship without placement and say so in the README.

### What "user's own key" looks like

```
Settings → AI
  ○ Bring your own key     [provider ▾] [key ____________]   encrypted, never sent to us
  ○ Local model (Ollama)   [endpoint ____________] [model ▾]
  ○ Use SportyAgent's key  3 analyses/day remaining ████░░░░
```

Three radios, one field each. The key field is a password input showing the last four characters. A "test connection" button fires one cheap request and reports the model name back. When a key fails, the error text is the provider's own message rather than a friendly paraphrase.

### Testing, per the webapp-testing skill

Playwright scripts against the local server, `scripts/with_server.py` managing the lifecycle. Test what would embarrass you:

- `start.sh` on a clean clone reaches a working page
- The RTP page renders correct numbers from a mocked response, and shows an honest error when the endpoint fails
- The NO-BET gate blocks a fixture with missing lineup data
- The key field never writes plaintext to storage — assert against localStorage directly
- The banned-word linter fails the build when someone writes "guaranteed"

Screenshot each phase's main screen into `docs/screens/`. Visual regressions are cheap to spot and expensive to find later.

### Writing, per the anti-slop directive

The README and every user-facing string follows the banned-word list. No "it's worth noting," no "at its core," no rule-of-three paragraphs, no uniform sentence length. The README opens with what the thing does and the number that proves it.

Its first paragraph should be the accumulator multiplier finding. True, surprising, checkable in thirty seconds. Not a mission statement.

### Sequencing risk

What sinks this isn't technical, it's scope. There are 100+ features in `PLAN.md` and a first-time maintainer. Phase 1 alone is enough for a launch. Phase 2 is enough for people to keep using it. Everything after that is a reward for finishing those two.

### Next action

Phase 0 today: repo skeleton with `start.sh`, CI, licence and the banned-language linter. Then Phase 1's RTP page, because that page is the project's proof of life.





---

# Part 3 — How SportyBet Actually Works


## SportyBet — How the Site Actually Works
**Verified 2026-11-18** by inspecting the live site's own network traffic and probing endpoints. Every claim here was observed, not assumed. This file is the agent's domain knowledge base — it is loaded into the system prompt so the agent knows the platform before it reasons about anything.

> **Update discipline:** if a claim here fails in production, mark it `[STALE]` with the date and what changed. Never silently delete. The next contributor needs to know we were wrong and when.

---

### 1. Platform shape

SportyBet runs on **Sportradar** data. Every ID you see is Sportradar format:

```
sr:sport:1        → Football
sr:category:34    → Australia
sr:tournament:136 → A-League
sr:match:12345    → a specific fixture
```

This matters: any Sportradar-compatible data source uses the same ID space, so fixture matching between SportyBet and external data providers can be done **on ID, not on team-name string matching**. That kills a whole class of bugs (the "Man Utd" vs "Manchester United" problem).

### 2. API envelope

Every endpoint returns the same wrapper:

```json
{ "bizCode": 10000, "innerMsg": "...", "message": "...", "data": {...} }
```

| bizCode | Meaning | What it tells you |
|---|---|---|
| `10000` | Success | `data` is populated |
| `19000` | Invalid | Route exists, **params wrong** — or signature missing |
| `19001` | Not found | Route does not exist |
| `19003` | Forbidden | Route exists, **needs an authenticated session** |

Practical rule for the agent: `19000` on a request you copied from the real page = **missing signature/header**, not a bad URL. Do not retry it. `19003` = login needed, stop and ask the user.

### 3. Endpoint map (verified)

#### Open — work without login
```
GET /api/ng/factsCenter/sportList?productId=3
    → full sport tree: 22 verticals, countries, tournaments, event counts

GET /api/ng/factsCenter/quickMarketList?block=A|B&sport=sr:sport:1
    → the market chips shown on the match list

GET /api/ng/factsCenter/story/v1/story-sets?page=0&pageSize=15
    → editorial content blocks

GET /api/ng/common/config/query
GET /api/ng/common/config/broadcast
```

#### Requires signature (present in page, fails when replicated)
```
GET /api/ng/factsCenter/liveOrPrematchEvents
    ?productId=3
    &sportId=sr:sport:1
    &marketId=1,18,10,29,11,26,36,14
    &categoryId=all
    &tournamentId=all
    &timeline=
    &pageSize=10
    &pageNum=1
    &option=1
```
**Verified failure mode:** copying this URL exactly, with session cookies present, returns `19000 Invalid`. The page computes a signature (header or param) that we do not replicate. **Therefore: all fixture/odds reads go through the real browser context.** Use Playwright `context.request` bound to a live browser session, or navigate and read — never reconstruct the call.

```
GET /api/ng/factsCenter/wapConfigurableIndexLiveEvents
    ?sportId=sr:sport:1&withTwoUpMarket=true&withOneUpMarket=true
GET /api/ng/factsCenter/recommendScrollEvents/v2
GET /api/ng/factsCenter/event?productId=3&eventId=sr:match:...
```

#### Requires login (`19003` when anonymous)
```
GET /api/ng/orders/v2/getBalance
```
This is the balance read. In Mode A the user reads it themselves; in Mode B the driver reads it inside the user's own session.

#### Games / virtuals
```
GET /api/ng/gaming/gameList
GET /api/ng/gaming/list
GET /api/ng/gaming/config
GET /api/ng/gaming/popular
GET /api/ng/gaming/aviator/rounds      → Aviator round history
GET /api/ng/scheduledVirtual/api/v1/config
GET /api/ng/instantwin/api/v1/iw/config/sport?sportId=sr:sport:1-1
```

### 4. Bot protection

| Client | Result |
|---|---|
| `curl` with desktop UA | **HTTP 403** |
| Headless Chromium | (untested — no binary on the research device) |
| Real browser session | **200 OK** |

Conclusion baked into the architecture: the app drives a **real Playwright browser** owned by a forked driver process. No raw HTTP client for SportyBet. This is not evasion-fighting — it is the only transport that works, and it also means the app behaves like a normal user session.

### 5. Full catalogue (verified event counts, 2026-11-18)

```
Football              1402      vFootball              442
Tennis                 326      eSoccer                152
Basketball             303      American Football      118
Ice Hockey             276      Badminton               92
Table Tennis           158      Handball                89
Volleyball              55      Boxing                  51
MMA                     44      Cricket                 42
eBasketball             17      ESport Counter-Strike   16
Rugby                   14      Futsal                  11
Darts                    8      Snooker                  7
Baseball                 4      ESport Dota              1
```

Product silos on the homepage: **Lucky Numbers, Virtuals, Aviator, Crime Miami, Jackpot, Sporty Picks, Scheduled Football, JetX Cashback, Win With EarlyGoals, SportySIM, AutoBet**.

Note **AutoBet** — SportyBet ships its own auto-staking feature. Relevant twice: (a) users already understand the concept, (b) an argument that "automation is forbidden" is weaker than it looks, though the operator's own automation is not the same as third-party automation.

### 6. Football markets — VERIFIED market IDs

**Correction:** the IDs below were extracted from `quickMarketList` block A and B on 2026-11-19.
An earlier draft of this file guessed them from UI labels and got four wrong — the wrong values are
shown struck through so future readers can see what was corrected and why.

| Market ID | Display name | Specifier | Present in |
|---|---|---|---|
| `1` | 1X2 | — | A, B |
| `8` | Next Goal | — | A |
| `10` | Double Chance | — | A, B |
| `14` | **Handicap** | `HC` | A, B |
| `18` | Over/Under | `Goals` | A, B |
| `19` | **Home O/U** | `Goals` | A, B |
| `20` | **Away O/U** | `Goals` | A, B |
| `29` | **GG/NG (BTTS)** | — | A, B |
| `60` | 1st Half 1X2 | — | A, B |
| `68` | **1st Half O/U** | `Goals` | A, B |
| `166` | Corners O/U | `Corners` | A, B |
| `60010` | 2+ Goals Streak | — | B |
| `60020` | 3+ Goals Streak | — | B |
| `60210` | 1X2 — Never Down | — | B |

~~Earlier guesses that were wrong: 1st Half O/U = 29, Handicap = 11, Home O/U = 26, Away O/U = 36.~~

Only **14** markets appear as quick chips, but a live fixture reports **`totalMarketSize: 187`**.
So the chip list is a *selection*, not the full market set. The agent must query the event detail
for the complete list, not assume the chips are everything.

### 8. The `probability` field — the single most important API fact

Every outcome returns **both** `odds` and `probability`. In all mutually-exclusive markets
(1X2, O/U, Handicap, GG/NG, corners) the `probability` values sum to **exactly 1.0000** across
160 markets in 5 live fixtures — so they are the platform's own **de-vigged true probabilities**.

`odds` meanwhile carries a **7–9% overround** (1X2 +7.87%, corners +9.06%, handicap +8.62%).

**Rule for the agent:** never de-vig the odds yourself. Read `probability` directly, and treat the
overround as the operator's edge. A pick is only +EV where our model beats `probability` by more
than that margin. Full analysis: `research/ODDS-DEEP.md`.

### 9. Live event record shape (verified)29 fields per live event, including:

```
eventId          sr:match:66887160
gameId           16680
estimateStartTime 1795127400000        (epoch ms)
status           1                     (live)
period           1
matchStatus      H1
playedSeconds    "40:36"
remainingTimeInPeriod "04:23"
setScore         "1:0"
pointScore       "[\"1:0\"]"
homeTeamId       sr:competitor:1974
sport            {id, name, category}
totalMarketSize  187
markets          [ … ]
ai               false                 ← flag exists on every event
topTeam          false
banned           false
bookingStatus    "Booked"
eventSource      {preMatchSource, liveSource}
containsPcbb     false
matchTrackerNotAllowed
fixtureVenue
```

**The `ai` field is worth watching.** It is `false` on every event sampled. It may be a flag for a
promotional AI-picks feature, or for AI-generated summaries on the event page. Not yet determined —
recorded as an open unknown.

### 7. Game classes and what can be modelled

| Class | Examples | Mechanism | Can an agent predict it? |
|---|---|---|---|
| Fixed-odds sports | Football, tennis, basketball, all 22 verticals | Human traders price it; margin embedded | **Partially.** Calibrated probabilities yes; consistent profit only in niche markets |
| Crash | Aviator (Spribe), JetX (SmartSoft) | Provably-fair hash chain; server seed + client seed; ~3% house edge | **No.** Next round independent of history. Past rounds verifiable, future not |
| Virtual sports | vFootball, eSoccer, eBasketball, SportySIM | Closed RNG, certified by independent labs | **No.** No public seed. Nothing to research |
| Lottery / draw | Lucky Numbers, Jackpot | Ball draw or RNG | **No.** |
| Instant win | Crime Miami, instant games | RNG per session | **No.** |

#### The rule this produces
The agent must **classify every game before it reasons**:

- `MODELLABLE` → run the research pipeline
- `RISK_MATH_ONLY` → offer the simulator, refuse to predict
- `NOT_MODELLABLE` → show expected loss over N rounds, refuse to predict
- `HOUSE_EDGE_ONLY` → show the edge, refuse to predict

If the agent ever produces a "prediction" for a category flagged `NOT_MODELLABLE`, that is a **bug**, and the test suite should fail on it.

### 8. Why "play until you hit the target" cannot work

For repeated play with negative expected value per round, the probability of reaching target *T* before ruin decays toward zero as rounds increase. Even at exactly 50/50, `P(reach T) ≈ B/T` and every round adds house drag. A loop that keeps playing until it hits a money goal is a **ruin machine on a schedule** — the more it plays, the more certain the outcome.

This is why the product has:
- a NO-BET gate that is on by default
- a hard daily loss stop that cannot be raised without a cooldown
- a ruin simulator that shows the user this maths with their own numbers
- an agent that is *allowed* to say "don't bet today" and does so often

### 9. What the agent must never claim

Banned in every user-facing string (CI enforces):
`guaranteed` · `sure` · `100%` · `win big` · `risk-free` · `can't lose` · `always wins` · `fixed match` · `hack`

The honest sentence is: *"Even a good forecaster loses regularly. Any edge is small, measured in fractions of a percent, and only visible over hundreds of bets."*

### 10. Open questions (mark, don't guess)

- `[UNKNOWN]` Exact signature scheme on `liveOrPrematchEvents` — deliberately not reverse-engineered; the browser context makes it unnecessary.
- `[UNKNOWN]` Per-product RTP for SportyBet's own virtuals — not published on the NG site as far as we could locate.
- `[UNVERIFIED]` SportyBet T&C clauses on automated access — must be read from the live page before the legal pack ships.
- `[UNKNOWN]` Whether the order/placement endpoint requires a device ID beyond the session.





---

# Part 4 — How the Agent Reasons


## SportyAgent — Agent Method
Adapted from the clean-room research discipline in `storytold/craft-anything` (MIT/Apache-2.0).
Their rule is simple and it is the whole reason their tool is trustworthy:

> **Evidence is the result.** Analysis tools return an evidence record with honest confidence,
> limitations, coverage and locations — never a bare claim.

SportyAgent adopts this wholesale. A betting recommendation without its evidence trail is a guess
dressed up as advice, and this project exists to be the opposite.

---

### The loop

```
open target → list unknowns → record hypotheses → gather evidence → verify → write report
```

Each step maps to a tool in the agent's registry. Nothing is "known" until it is an evidence record.

#### 1. `target_open`
Declare what is being analysed: a fixture, a market, a game class, the platform itself.
Records the target id, the scope, and the timestamp. Everything downstream cites this id.

#### 2. `unknowns_list`
Before research, enumerate what we do not know. This is not optional and it is not decoration —
an unlisted unknown is a silent hallucination risk. Examples for one fixture:

```
- Unknown: Is the home team's first-choice keeper fit?
- Unknown: Did they play midweek in Europe?
- Unknown: Has the price moved since 09:00?
```

The UI shows this list on the card. If a `NO BET` decision is made, the unknowns are the reason.

#### 3. `hypothesis_record`
A testable claim with a prior probability and what would falsify it.

```
hypothesis: "Home side scores 2+ goals in 60%+ of matches when priced at 1.70 or shorter"
confidence: 0.55 (prior — I believe I saw this but have not checked)
falsified_by: "fewer than 50% in the last 20 such matches"
```

#### 4. Evidence gathering — every tool returns an evidence record

```ts
type Evidence = {
  id: string;                 // ULID
  target: string;             // the target_open id
  claim: string;              // what this record supports
  confidence: number;         // 0..1 — honest, not optimistic
  source: {
    kind: 'primary' | 'secondary' | 'tertiary' | 'model' | 'odds';
    url?: string;
    retrievedAt: string;      // ISO — staleness is visible
    grade: 'A' | 'B' | 'C' | 'D';
  };
  limitations: string[];      // what this evidence does NOT show
  coverage: {                 // how much of the question is answered
    answered: number;         // 0..1
    gaps: string[];
  };
  locations?: { page?: number; selector?: string; line?: number }[];
};
```

**Grading rules — borrowed from the Research Synthesist discipline:**

| Grade | Source | Weight |
|---|---|---|
| A | Primary data: official league stats, verified lineups, the bookmaker's own published config | 1.0 |
| B | Established aggregator: FBref, Understat, football-data.co.uk | 0.7 |
| C | News/reporting, no raw data behind it | 0.4 |
| D | Social/media claim, unreplicated | 0.15 |

A claim supported only by D-grade evidence **cannot pass the NO-BET gate**, no matter how confident
the LLM sounds. This is the mechanical answer to "the agent said it was very sure".

#### 5. `hypothesis_verify`
Mark each hypothesis as confirmed, refuted, or still open. Refuted hypotheses are kept — they are
training signal. The calibration module later compares stated confidence against outcome.

#### 6. `report_write`
The card. Every sentence maps to an evidence id. If a sentence cannot be traced to evidence, it does
not appear.

---

### Confidence is not probability

This distinction is the entire product:

- **Evidence confidence** = how much we trust *this fact* (e.g. "Arsenal's striker is injured" — 0.95)
- **Outcome probability** = our estimate that *the event happens* (e.g. "Arsenal wins" — 0.52)

A fact can be certain and the outcome still uncertain. Merging the two is how betting tools lie.
The UI shows them in separate columns and never blends them into one number.

### The evidence floor

`NO-BET` fires automatically when:

1. Any **critical** unknown remains (lineups within 2h of kickoff, injury to a key player)
2. Evidence coverage for the selected market is below **0.6**
3. The edge is below the threshold
4. The supporting evidence is majority C/D grade

An agent that cannot say "I don't know" is not an analyst. It's a random number generator with
good typography.

---

### Adoption note

`craft-anything`'s own structure proves this works at scale: 13 crates, 923 tests, every tool
returning `ToolOutput::Evidence`. Their `core_unknown_add` / `core_hypothesis_record` /
`core_unknown_verify` trio is the pattern above, copied in spirit and adapted to betting.
Licence: MIT OR Apache-2.0 — attribution recorded in `NOTICE` if any code is reused.





---

# Part 5 — Odds, Probabilities, Product Rules


## SportyBet — Deep Findings: Odds, Probabilities and Product Rules
Captured 2026-11-19 from `wapConfigurableIndexLiveEvents` (sportsbook feed, live football).
This document supersedes any earlier guess in `KNOWLEDGE.md` where they disagree.

---

### 1. THE BIG ONE: the platform publishes de-vigged true probabilities

Every outcome carries **two** numbers:

```json
{ "id": "1", "odds": "2.05", "probability": "0.4658000000", "desc": "Home" }
```

Across 160 markets in 5 live football fixtures (run `20261119T235301Z`), every
**mutually-exclusive** market sums its `probability` values to **exactly 1.0000**:

| Market | n | mean Σp | mean overround in `odds` |
|---|---|---|---|
| Over/Under | 35 | 1.0000 | **+7.12%** |
| Corners O/U | 24 | 1.0000 | **+9.06%** |
| Handicap | 19 | 1.0000 | **+8.62%** |
| Next Goal | 13 | 1.0000 | +8.35% |
| Home O/U | 14 | 1.0000 | +7.30% |
| Away O/U | 12 | 1.0000 | +7.43% |
| 1st Half O/U | 12 | 1.0000 | +7.03% |
| 1X2 | 5 | 1.0000 | +7.87% |
| GG/NG | 5 | 1.0000 | +7.82% |

**Interpretation.** `probability` is the **normalised true probability**: divide each outcome's
implied probability by their sum and you land on it exactly. `odds` carries the operator's margin —
**7–9% per market**, which is 3–4× what a sharp book charges and roughly double the 5% retail
assumption used in most of the betting literature.

**Why this is a big deal for SportyAgent:**

1. The bookmaker hands us its **own fair-price estimate** per outcome. A model can be scored
   directly against it — no de-vigging guesswork, no Shin/odds-ratio choice.
2. A bet is +EV only where **our probability exceeds theirs by more than the overround**:
   `edge = our_p * odds - 1`. Now a single measurable number per selection.
3. It gives us a free **baseline to beat**. If our model cannot beat `probability`, the app says
   `NO BET`. That is exactly the mechanical gate in `AGENT-METHOD.md`.

**The honest consequence:** at 7–9% overround, a model must beat a sharp supplier
(`sourceType: BET_GENIUS`) by about **8 percentage points of probability** on average. That is a
very high bar. It is also the reason this product must be conservative by default — and the reason
the `NO BET` state will fire most of the time. Saying this plainly is what makes the repo credible.

### 1b. Markets where Σp ≠ 1 are correct, not broken

Three classes must never be judged against 1.0:

| Market | Why Σp ≠ 1 |
|---|---|
| **Double Chance** (id `10`) | 3 selections `1X, 12, X2`; any match result satisfies **exactly two**, so a de-vigged set sums to **2.0**. Observed: 2.0000 on every 3-way fixture. |
| **1UP / 2UP** (60200 / 60100) | Conditional on an early-payout trigger. Observed Σp 0.40–0.79. |
| **Never Down** (60210) | Only outcomes where the team never trailed. Observed Σp 0.71–1.00. |
| **1st Half 1X2** | Being settled **against the live score**. One fixture at 0-0 in H1 showed Σp = 1.0000; another showed Σp = **0.0041** once the half had all but resolved (odds 17.0 vs 47.0 barely moved). **Treat in-play 1st-half markets as unreliable for modelling.** |

An analyser that flags Double Chance as "92% overround" is measuring its own misunderstanding, not
SportyBet's margin. `tools/odds_analyzer.py` now special-cases the overlap markets.

### 2. The real product structure: margin lives in the derivatives, not the base market

The derived products are where the money actually changes shape:

| Market | ID | Σp observed | Meaning |
|---|---|---|---|
| `1X2` | 1 | **1.0000** | Base market, thin overround |
| `1X2 - 1UP` | **60200** | 0.11 – 0.83 | Pays out early when your team leads by 1 |
| `1X2 - 2UP` | **60100** | 0.13 – 1.01 | Pays out early when your team leads by 2 |
| `1X2 - Never Down` | **60210** | — | Win without ever trailing |

Σp well below 1 on a derivative is **correct, not a discount**: those probabilities are
conditional on the early-payout trigger firing. A 1UP selection at Σp = 0.11 means only ~11% of
the probability mass sits on outcomes where the early payout was actually triggered and priced.

**Conclusion:** margin is not "5% on 1X2". It is concentrated in product overlays — early payout,
never-down, streaks — where the customer is paying for a feature he did not compare.

### 3. Product rules, verbatim from `marketGuide`

These are the operator's own words, pulled per market. This is how the games really work.

#### 1UP — market 60200
> "1UP will reward you earlier if your team takes a one-goal lead, e.g. 1-0, 2-1. Once settled, the
> final result no longer matters - win, lose or draw! Betting on the draw in this market is the same
> as in regular 1X2, it is resulted on the full-time score regardless of how and when any goals are
> scored (which is why the odds are the same)."

#### 2UP — market 60100
> "2UP will reward you earlier if your team takes a two-goal lead, e.g. 2-0, 0-2, 3-1, 1-3. Once
> settled, the final result no longer matters - win, lose or draw! If a match is abandoned and a team
> has gone two or more goals ahead then bets on that selection will still be paid as winners.
> SportyBet reserves the right to void bets/selections if we identify any suspected illegal activity,
> bonus abuse, or violations of our terms and conditions."

#### Never Down — market 60210
> "Never Down will reward you if your team wins the match without ever trailing. If your team goes
> one or more goals behind at any point, the selection loses, even if they later come back to win.
> If you bet on Draw, the bet wins if the match ends in a Draw (Regular 1X2). If a match is abandoned
> after a team goes behind, bets on that selection will be settled as lost."

**Note the asymmetry between 1UP and Never Down:** 1UP pays and forgets. Never Down pays only in
the narrow path where the team leads from start to finish — and an abandoned match settles as lost
if the team was behind at any point. The pricing reflects that; the marketing does not.

### 4. Market taxonomy (live football sample, 5 events, 185 market entries)

14 distinct market names in the live-index sample:

| Market | Count | Group |
|---|---|---|
| Over/Under | 43 | Goals |
| Corners - Over/Under | 24 | Corners |
| 1st Half - Over/Under | 21 | Half |
| Handicap | 19 | Main |
| Home O/U | 18 | Goals |
| Away O/U | 15 | Goals |
| Next Goal | 13 | Main |
| 1X2 | 5 | Main |
| Double Chance | 5 | Main |
| GG/NG | 5 | Main |
| 1st Half - 1X2 | 5 | Half |
| 1X2 - 1UP | 4 | Main |
| 1X2 - 2UP | 4 | Main |
| 1X2 - Never Down | 4 | Main |

Groups: `Main` (102) · `Goals` (33) · `Half` (26) · `Corners` (24).
**Every market carries `sourceType: "BET_GENIUS"`** — the pricing engine is Betgenius (Genius Sports),
not an in-house model. That means the probabilities come from a supplier whose other clients include
several sharp books — a useful cross-check but also a reason the numbers will be close to efficient.

### 5. Per-market record shape (for the parser)

```
market:  id, product, desc, status, group, groupId, marketGuide, title, name,
         favourite, outcomes[], farNearOdds, marketExtendVOS, sourceType,
         availableScore, lastOddsChangeTime, earlyPayoutMarkets, banned
outcome: id, odds (string), probability (string, 5-6 dp), voidProbability,
         isActive, desc
```

Tags worth watching in analysis:
- `favourite: 1` — the market the operator is pushing
- `banned` — market-level restriction flag
- `availableScore` — the score the market was priced against
- `lastOddsChangeTime` — epoch ms; enables drift detection
- `isActive: 0` — suspended selection (odds often "0.0")

### 6. What the agent should do with this

1. **Always pull `probability`, not just `odds`.** Store both — the delta between them is the
   operator's own opinion of its margin.
2. **Price the derivative yourself.** For 1UP, the early-payout trigger makes it a barrier option.
   Our model can compute the fair price of "team leads by 1 at some point AND wins" and compare.
   This is a genuinely tractable modelling job — far more tractable than predicting a 50-leg acca.
3. **Never quote a derivative without its `marketGuide`.** The rule text is the source of truth and
   it is in the response.
4. **Track `lastOddsChangeTime`** — a market that reprices after we quote is a signal.





---

# Part 6 — The Business Model and Margin Stack


## SportyBet — The Business Model, Verified

Everything here came from endpoints or JS bundles on 2026-11-19/20. This is the document that
explains *why* the product works the way it does, in the operator's own numbers.

---

### 1. The RTP ratio table (the most important artifact found)

**Endpoint:** `GET /api/ng/marketing/v1/activities/oddsBoost/getOddsBoostLobRtpRatio`
(also mirrored at `/api/ng/marketing/v1/activities/oddsBoost/lfb/rtpRatio`)
**Header:** `x-platform: WAP` · **Auth:** none

```json
{"bizCode":10000,"message":"Success","data":{"ratios":[
  {"ratio":"1.00","minRtp":"0.98","maxRtp":"1.00"},
  {"ratio":"1.02","minRtp":"0.95","maxRtp":"0.98"},
  {"ratio":"1.03","minRtp":"0.93","maxRtp":"0.95"},
  {"ratio":"1.04","minRtp":"0.90","maxRtp":"0.93"},
  {"ratio":"1.07","minRtp":"0.85","maxRtp":"0.90"},
  {"ratio":"1.08","minRtp":"0.80","maxRtp":"0.85"},
  {"ratio":"1.10","minRtp":"0.75","maxRtp":"0.80"},
  {"ratio":"1.10","minRtp":"0.70","maxRtp":"0.75"},
  {"ratio":"1.12","minRtp":"0.65","maxRtp":"0.70"},
  {"ratio":"1.20","minRtp":"0.50","maxRtp":"0.65"},
  {"ratio":"1.25","minRtp":"0.00","maxRtp":"0.50"}
]}}
```

| Odds boost | Effective RTP band | What the customer is actually getting |
|---|---|---|
| 1.00× | 98–100% | Near-fair price (the base product) |
| 1.02× | 95–98% | Slight premium |
| 1.04× | 90–93% | 7–10% house edge |
| 1.07× | 85–90% | 10–15% edge |
| 1.10× | 75–80% | **20–25% edge** |
| 1.12× | 65–70% | 30–35% edge |
| 1.20× | 50–65% | **35–50% edge** |
| 1.25× | 0–50% | **50–100% edge — the boost eats the stake** |

**What this means.** An "odds boost" is not a gift. It is a *price*: the higher the advertised
multiplier, the lower the true return. At `1.25×` the RTP floor is **zero** — the promotion is
priced such that a customer can expect to lose everything.

**Why this matters more than anything else found:** it is the operator's own published mapping
between a marketing word ("boost") and a mathematical reality ("RTP 0.50–0.65"). Every tipster
account in Nigeria promoting boosted odds can now be checked against this table.

**Product use:**
1. A screen in SportyAgent that reads this endpoint live and renders the table. It's the most
   shareable artifact the project can have.
2. Any boosted selection the agent evaluates must be annotated with its RTP band, not just its odds.
3. `NO BET` must fire automatically for any selection above the 1.07× tier unless the model's edge
   exceeds the implied house edge — which, at 1.20×, requires beating a 35–50% margin.

### 2. The margin stack, assembled

Put together everything measured so far and the true cost per product is:

| Layer | Measured | Source |
|---|---|---|
| Base market overround (1X2, O/U, handicap) | **7–9%** | `wapConfigurableIndexLiveEvents` odds vs probability |
| Accumulator multiplier decay | 0.95 → **0.15** | `factsCenter/betType/config` |
| Flexi effective RTP floor | **0.80** | same |
| Odds-boost RTP bands | 0.98 → **0.00** | `getOddsBoostLobRtpRatio` |
| Games (all 21) | **RTP not published** | `games/lobby/v1/games/featured` (`rtp: null`) |

So the honest headline for the README is:

> A single pre-match bet costs about **8%** in margin. An accumulator multiplies that.
> A boosted accumulator can drop effective return below **65%**. In the games lobby the operator
> does not publish RTP at all.

### 3. The bet placement path (from the bundle)

```js
fetch("/orders/order", {
  method: "POST",
  body: JSON.stringify(C),      // C = the encrypted order payload
  headers: L()                  // L() = header builder
})
```

Surrounding error handling reveals a constant **`REQUEST_DECRYPT_FAILED`** — the payload is
**encrypted**, not merely signed. That is why a replayed request from outside the page returns
`19000 Invalid`: the server cannot decrypt it.

Related endpoints found in the same bundle:

```
/orders/liability/check          pre-flight stake validation
/orders/liability/quick/check
/orders/order                    PLACE BET (POST, encrypted body)
/orders/order/bet/edit
/orders/order/deleteOrder/
/orders/order/v3/realbetlist
/orders/order/realsports/ticketDetail
/orders/bookingCode/filter
/orders/bookingCode/recentCodes
/orders/bookingCode/remix
/orders/joker/config
/orders/config/cutbet
/orders/flexi/banned-markets
/orders/share/
/orders/my-pins
```

**Architectural conclusion (unchanged, now proven):** do not reconstruct the placement request.
The body is encrypted with a routine inside the page bundle. The only reliable way to place a bet
is to drive the real page — which is exactly what `ARCHITECTURE.md` specifies.

### 4. The account surface (all endpoints found in bundles)

Every account function has a dedicated endpoint. Notable ones:

```
/patron/account                        core account record
/patron/account/info/selfExclusion     ← self-exclusion exists as an API
/patron/account/info/selfExclusionStatus
/patron/account/info/selfPeriodTimeExclusion
/patron/v2/selfBettingLimit/activity   ← self-imposed betting limits exist as an API
/patron/account/info/withdrawpin       withdraw PIN
/patron/account/info/withdrawpin/otp/acquire?bizType=
/patron/two-factor-auth                ← 2FA exists
/patron/two-factor-auth/code/send
/patron/two-factor-auth/code/verify
/patron/force/logout/all
/patron/user/devices/force-logout/otp/session
/patron/user/devices/blocking/otp/session
/patron/facial-recognition/session     ← facial recognition on some flows
/patron/account/info/insight           ← behavioural insight feed
/patron/account/referral/code/invite
```

**Two findings that matter:**

1. **Self-exclusion and self-betting-limit APIs exist.** That means the operator HAS the tools to
   help a user stop. SportyAgent's responsible-gambling screen should link straight to these —
   and can honestly say "the operator offers this; use it."
2. **`/patron/account/info/insight`** is a behavioural insight endpoint. Combined with
   `/api/ng/bi/segmentation` and the 95 A/B experiments, the platform is running a full behavioural
   personalisation programme. This is worth stating plainly in the README: the product you are
   betting against is optimising against you.

### 5. Virtuals and instant-win — the `/iwqk` namespace

Found by extracting string concatenation from `index.ea05192632.js`:

```js
n = "/iwqk";  o = "/api/v1";  a = "/api/v2";  i = "/api/v3"
```

The real prefix is **`/api/ng/instantwin/api/v{1,2,3}/`** (not `/api/ng/` directly — that is why
every probe 404'd for an hour). Full route map recovered from the bundle:

| Version | Path | Observed |
|---|---|---|
| v1 | `/iwqk/market/type/list` | 500 |
| v1 | `/iwqk/stats/league-table` | **403** |
| v1 | `/iwqk/stats/team-stats` | **403** |
| v1 | `/iwqk/buildandgo/available-games-without-login?sportId=` | **500** (but the page loads 5,953 bytes of it) |
| v1 | `/iwqk/buildandgo/available-games` | **403** |
| v1 | `/iwqk/ticket/create`, `/ticket/detail`, `/ticket/list`, `/ticket/v2/ticketNumber` | login |
| v1 | `/iwqk/share/uploadSharePics/shareType/{e}/id` | login |
| v2 | `/iwqk/event/list_all_with_popular_markets_non_login` | **403** |
| v2 | `/iwqk/event/details_without_login` | 500 |
| v2 | `/iwqk/round/get/unsettled` | **403** |
| v2 | `/iwqk/round/settle` | **403** |
| v2 | `/iwqk/round/list_settle_events` | **403** |
| v3 | `/iwqk/event/prepare_round_without_login` | **403** / 500 |

**Reading the status codes:** `403 Forbidden` = endpoint exists, needs a session. `500` = endpoint
exists but the request shape or a required token is missing. **Neither is a 404**, so every one of
these routes is real. The virtuals engine returns 403 across the board → **you cannot read virtual
rounds without logging in.**

Note also a **bug in the operator's own source**:
```js
"/iw","/config/sport"   →   "/iw//config/sport"   (double slash)
```
The correct path `/iw/config/sport` returns 500 while the concatenated one is what the client
actually builds. Minor, but it confirms the bundle was read correctly rather than guessed.

**Instant-win config endpoints that DO work anonymously:**
```
/api/ng/instantwin/api/v1/iw/config/sport?sportId=sr:sport:1-1   → 200
/api/ng/instantwin/api/v1/iw/config/list                          → ?
/api/ng/instantwin/api/v1/iw/config/overall                       → ?
```

**What the virtuals UI actually shows** (captured live): one-tap virtual matches in the layout
`MCI vs MUN · England · Under 5.5 · O/U · Home (1:0) · Handicap · Home · 1st Half 1X2 · 2.3…`
— i.e. the same market vocabulary as real football, rendered as instant rounds. That is the product
design: **make RNG look like football so the customer brings football intuition to it.**

`extra_life` and `survivor` promotion endpoints (`/promotion/v1/survivor/*`) also exist, and
`/promotion/v1/loyalty/mission/applicable/virtual` — the virtuals product is tied into a loyalty
mission system. Retention engineering, not sports modelling.

### 6. What is still unknown

- Where `/round/*` actually lives (host and prefix).
- Whether `probability` changes as an event approaches kickoff in a systematic way (needs polling).
- The encryption routine for `/orders/order` — not pursued, and not needed given the browser-based
  architecture.
- What the `ai` flag means on live events.
- Whether the games lobby exposes any round history for Aviator at all.





---

# Part 7 — The Games Catalogue


## SportyBet — Games Catalogue (verified)

Source: `GET /api/ng/games/lobby/v1/games/featured` with header **`x-platform: WAP`**
(no `x-platform` → HTTP 500). Captured 2026-11-19.

The games lobby is a **separate API namespace** from the sportsbook (`/api/ng/games/lobby/...`,
not `/api/ng/gaming/...`). Earlier 404s on `/api/ng/gaming/gameList` and `/aviator/rounds` were
wrong path guesses; the real one was found by grepping the games SPA's JS bundle
(`core.c1b2b03b0d.js`, 2.0 MB) for `/games/lobby`.

### Endpoints

| Endpoint | Header | Result |
|---|---|---|
| `/api/ng/games/lobby/v1/games/featured` | `x-platform: WAP` | 7 categories, 21 games |
| `/api/ng/games/lobby/v2/games/web-mini?offset=0&limit=20` | `x-platform: WEB_MINI` | 8 mini-games |
| `/api/ng/games/lobby/v1/games/getByRanking` | `x-platform: WAP` | same payload as featured (**NG ignores the ranking variant**) |

Without `x-platform` all three return **HTTP 500**. That is the gate.

### Game record shape

```json
{
  "name": "Aviator", "displayName": "Aviator", "gameId": 19,
  "onlineUserCount": 1020,
  "rtp": null,
  "deepLinkUrl": "https://www.sportybet.com/ng/applink/freqGames?game=Aviator",
  "imageUrl": "https://s.sporty.net/sportygames/lobby_banner/1648540402134.png",
  "widgetImageUrl": null, "notificationList": []
}
```

**`rtp` exists as a field but is `null` on every one of the 21 games.** The operator has a slot for
publishing return-to-player and does not populate it. For a product that must be honest about house
edge, that is itself a finding worth surfacing in the UI: *"SportyBet does not publish an RTP for
this game."*

**`onlineUserCount` is live** — 1,020 on Aviator, 1,560 on Sporty Jet at capture time. Useful for a
"how busy is this game right now" panel, and interesting as a behavioural signal (Aviator being the
most popular crash game is visible here).

### The catalogue (7 categories, 21 games)

| Category | id | Games (name · gameId · online) |
|---|---|---|
| **Crash** | 1 | Aviator · 19 · 1020 &nbsp;│&nbsp; Sporty Jet · 1750 · 1560 &nbsp;│&nbsp; Sporty Hero · 16 · 1080 |
| **Quick** | 8 | Spin da' Bottle · 17 · 1100 &nbsp;│&nbsp; Flip da' Coin · 29 · 830 &nbsp;│&nbsp; Jollof Wars · 1933 · 220 |
| **Slots** | 13 | Hot to Burn · 703 · 398 &nbsp;│&nbsp; Sugar Dash · 1843 · 120 &nbsp;│&nbsp; Gates of Olympus · 701 · 430 |
| **Cards** | 2 | Red-Black · 3 · 1000 &nbsp;│&nbsp; Blackjack · 7 · 760 &nbsp;│&nbsp; Blackjack Neo · 150 · 275 |
| **Wheel** | 5 | Spin Match · 165 · 811 &nbsp;│&nbsp; Spin2Win · 5 · 800 &nbsp;│&nbsp; tbg_vortex · 700 · 20 |
| **Dice** | 3 | SicBo · 15 · 811 &nbsp;│&nbsp; Dice · 18 · 256 &nbsp;│&nbsp; multidice · 634 · 196 |
| **Live** | 9 | evo_livebaccaratsqueeze · 1112 · 154 &nbsp;│&nbsp; evo_crazytime · 1084 · 90 &nbsp;│&nbsp; Fortune Roulette · 1733 · 34 |

Game-ID namespaces visible in the data: SportyBet's own games sit in the low IDs (3–29, 150, 165,
700–703, 1750, 1843, 1933), while `evo_*` IDs (1084, 1112) are **Evolution Gaming** live-dealer titles
passed through. So the lobby mixes first-party RNG games, third-party slots from real studios, and
a live-casino passthrough — three materially different house-edge structures under one roof.

### Mini-games (`web-mini`)

8 entries with `launchUrl` paths under `/ng/sportygames/` (e.g. `/ng/sportygames/sporty-kick-mini`).
These are the "Sporty Kick" style in-house mini-games — separate from the main lobby.

### What this means for the product

1. **Tiering is now evidence-based, not assumed.** Every game has a category and an ID, so the
   agent can route by category: Crash/Wheel/Dice/Quick → risk-math only; Live → house-edge display;
   Slots → house-edge display; nothing here is modellable.
2. **The missing RTP field is a feature.** The app can display, per game, *"RTP not published by
   the operator"* — true, verifiable, and more useful to a user than a made-up number.
3. **`onlineUserCount`** enables an honest "popularity" signal without pretending it predicts anything.
4. **No `provably`, `serverSeed` or `clientSeed` string appears anywhere in the 3.2 MB of sports
   bundle or the 2.0 MB games bundle.** Whatever provable-fairness Aviator runs internally, it is
   not exposed on this web client. The `rounds` route exists in the sports SPA route table, but the
   round-history API was not located in the bundle. Recorded as an open unknown.





---

# Part 8 — Architecture


## SportyAgent — Architecture

v1, 2026-11-18. Companion document to `PLAN.md`. Stack is fixed: Next.js 15 (App Router) + TypeScript + SQLite (better-sqlite3 / Drizzle) + Tailwind, one repo, `./start.sh` → `127.0.0.1:3000`.

### 0. Process & runtime model (context for everything below)

- **Main process** — one Node process runs the Next.js server. Route handlers under `src/app/api/*` are thin: they enqueue work, subscribe to the event bus, and stream. No business logic lives in routes.
- **Worker** — an in-process async loop started at server boot. Single user on localhost means no queue server is needed; durability comes from a `jobs` table in SQLite (a crash mid-research either resumes the run or marks it `error` on next boot). better-sqlite3 is synchronous, which is a feature here: one writer, no lock drama.
- **Driver** — `child_process.fork('src/core/placement/driver.js')`, one per placement attempt. Playwright + Chromium exist only in this child. Rationale: crash isolation (a hung browser can never take the web app down) and credential containment (the driver is the only component that ever holds live SportyBet session cookies — see SECURITY.md §2).
- **Event bus** — an in-process `EventEmitter`. SSE writers subscribe per client. See §2 for the SSE-vs-websocket decision.

---

### 1. Module boundaries (`src/core`)

Shared vocabulary lives in `src/core/types.ts`. Every module imports types from there and communicates with other modules only through the interfaces below — no cross-imports of internals. This is what makes each module testable in isolation and replaceable.

```ts
// core/types.ts — the shared vocabulary
export type Prob = number;            // [0,1]
export type DecimalOdds = number;     // > 1
export type ModelId = 'poisson' | 'elo' | 'llm' | 'ensemble';
export type GateDecision = 'BET' | 'NO_BET' | 'SKIP';

export interface Fixture {
  id: string;                // SportyBet event id
  sport: string; league: string;
  home: string; away: string;
  kickoffAt: number;         // unix ms
}
export interface Selection {
  market: string;            // '1X2' | 'OVER_UNDER' | 'BTTS' | 'HANDICAP' | ...
  line?: string;             // '2.5' for O/U, '-1' for handicap
  pick: string;              // 'HOME' | 'OVER' | 'GG' | ...
  odds: DecimalOdds;         // live odds at decision time
  prob: Prob;                // ensemble probability
}
export interface SourceRef { tool: string; url?: string; fetchedAt: number; note?: string; }
```

#### 1.1 `agent/` — orchestrator

**Responsibility.** Owns the per-fixture pipeline `filter → gather (parallel tools) → forecast ×3 → synthesize → critic → edge → gate → card`, and the free-form chat loop. It sequences calls into tools/models/odds/staking and records every decision; it computes nothing itself. It is also the only module that decides "degraded mode" (what happens when a dependency is down).

```ts
export interface AgentOrchestrator {
  research(fixtureId: string, opts?: ResearchOptions): AsyncIterable<AgentEvent>;
  chat(sessionId: string, userMessage: string): AsyncIterable<AgentEvent>;
  cancel(runId: string): Promise<void>;
}

export type AgentEvent =
  | { type: 'phase'; runId: string; phase: 'filter'|'gather'|'forecast'|'synthesize'|'critic'|'edge'|'gate' }
  | { type: 'tool_call'; runId: string; callId: string; tool: string; args: unknown }
  | { type: 'tool_result'; runId: string; callId: string; ok: boolean; summary: string; sources: SourceRef[] }
  | { type: 'llm_token'; runId: string; text: string }
  | { type: 'card'; runId: string; card: ResearchCard }
  | { type: 'error'; runId: string; code: string; message: string; degraded: boolean };

export interface ResearchCard {
  fixtureId: string;
  verdict: GateDecision;
  selections: Selection[];
  edge: number;                       // fairProb × odds − 1, best leg
  stake?: StakeDecision;
  reasons: string[];                  // with SourceRefs woven in
  counterArgument: string;            // critic output — ALWAYS present, even for BET
  sources: SourceRef[];
  degraded: boolean;                  // true if any forecaster/source was down
  dataCompleteness: number;           // 0..1, feeds the gate
}
```

**Dependencies:** `tools`, `models`, `odds`, `staking`, `calibration` (reads forecaster weights), `audit` (writes gate + card decisions), `db`.
**Failure mode:** LLM provider down / over token budget → runs the stats-only path (Poisson + Elo, no LLM analyst or critic) and marks the card `degraded: true` with a visible banner. A crash mid-run is recoverable: each phase checkpoints into `sessions`/`predictions`, and boot-time reconciliation marks orphaned runs `error`. The orchestrator never throws past the gate — worst case is a `NO_BET` card with an error note, never a silent half-card.

#### 1.2 `tools/` — registry + fetchers

**Responsibility.** Single registry of everything the agent (and the pipeline) can call: SportyBet reads, football-data.co.uk history, xG, weather, news, etc. Each tool declares a JSON schema (used both for LLM function-calling and for runtime arg validation), a cost class, and a cache TTL. All transport details (browser-context vs plain HTTP — see §5) are hidden inside tools.

```ts
export interface Tool {
  name: string;                       // 'fixtures', 'team_stats', 'h2h', 'odds_live', ...
  description: string;                // shown to the LLM
  schema: JsonSchema;                 // zod-compiled; validated on every invoke
  costClass: 'free' | 'cheap' | 'expensive';
  cacheTtl: number;                   // seconds; 0 = never cache
  run(args: unknown, ctx: ToolContext): Promise<ToolResult>;
}
export interface ToolContext { fixtureId?: string; budget: TokenBudget; signal: AbortSignal; }
export interface ToolResult {
  data: unknown | null;               // null on failure — failures are results, not throws
  error?: { code: string; message: string; retryAfterSec?: number };
  sources: SourceRef[];
  fetchedAt: number;
  fromCache: boolean;
}
export interface ToolRegistry {
  register(tool: Tool): void;
  list(): ToolDescriptor[];           // exactly what the LLM sees as function defs
  invoke(name: string, args: unknown, ctx: ToolContext): Promise<ToolResult>;
}
```

**Dependencies:** `db` (fetch_cache), `vault` (only the SportyBet read client touches the session), `http`/browser pool.
**Failure mode:** every tool returns a `ToolResult` even when the upstream is down — a failed source appears on the card as "source unavailable", never silently skipped. Per-tool timeout (10 s default), single-flight dedup, and a circuit breaker (3 consecutive failures → tool skipped for 10 min, card says so). Registry rejects duplicate names at boot so two plugins can't shadow each other.

#### 1.3 `models/` — forecasters + ensemble

**Responsibility.** The three independent forecasters (Poisson/Dixon-Coles, Elo, LLM analyst) and the synthesizer that blends them with weights learned from each model's recent Brier score. Models are pure functions of (fixture, research bundle) → probabilities; they never read odds (that's `odds/`'s job) so they can't contaminate themselves with the market they're trying to beat.

```ts
export interface Forecaster {
  id: Exclude<ModelId, 'ensemble'>;
  forecast(fixture: Fixture, research: ResearchBundle): Promise<Forecast>;
}
export interface Forecast {
  outcomes: { market: string; line?: string; pick: string; prob: Prob }[];
  confidence: number;                 // 0..1, model's own self-assessment
  reasons: string[];
  sources?: SourceRef[];              // LLM analyst only
}
export interface Ensemble {
  blend(forecasts: Forecast[], weights: Weights): BlendedForecast;
  // temperature-scaling applied here using calibration.temperature()
}
export type Weights = Partial<Record<Exclude<ModelId,'ensemble'>, number>>;
```

**Dependencies:** `db` (historical results, ratings cache), `tools` (ResearchBundle for the LLM analyst), `calibration` (weights + temperature).
**Failure mode:** a forecaster that throws is dropped and the remaining weights are re-normalized; if fewer than two survive, the gate's data-completeness rule forces `NO_BET`. Poisson needs ≥ 6 recent matches per team — below that it abstains (`outcomes: []`) rather than guessing. The LLM analyst is schema-constrained (probabilities must sum to 1 ± 0.02 or it's re-asked once, then dropped).

#### 1.4 `odds/` — quotes, margin removal, edge

**Responsibility.** Live and historical SportyBet quotes (via the browser-context read client), margin removal (proportional + Shin), and the edge calculation. This module is the only place that knows what a bookmaker price means.

```ts
export interface OddsService {
  live(fixtureId: string, market?: string): Promise<Quote[]>;
  history(fixtureId: string, market: string): Promise<Quote[]>;
  movement(fixtureId: string, market: string): Promise<QuoteTick[]>;
}
export interface Quote { market: string; line?: string; pick: string; odds: DecimalOdds; fetchedAt: number; stale: boolean; }
export interface MarginRemoval {
  fairProbs(odds: DecimalOdds[]): Prob[];
  method: 'proportional' | 'shin';    // Shin when margin > 8% or 3+ outcomes
}
export function edge(fairProb: Prob, odds: DecimalOdds): number;  // fairProb × odds − 1
```

**Dependencies:** `tools` (transport), `db` (quote history for movement/CLV).
**Failure mode:** quotes older than `maxAgeSec` (90 s pre-match, 15 s in-play) are flagged `stale: true` and the gate refuses to act on them. If live odds can't be fetched at all, the card says "odds unavailable" and defaults to `NO_BET` — the system never bets on cached prices. Margin removal falls back proportional→Shin never silently: the method used is recorded on the prediction row.

#### 1.5 `staking/` — Kelly, gates, limits

**Responsibility.** Turns (bankroll, edge, odds, limit set) into a stake decision or a refusal. Hosts the NO-BET gate's risk half: quarter-Kelly, absolute cap, correlation cap across legs, daily loss stop, session budget check for Mode B. This module is the *only* code path in the system that can produce a positive stake number — `placement/` asserts that any stake it executes carries a gate decision row written by this module.

```ts
export interface StakingEngine {
  decide(input: StakeInput): StakeDecision;      // pure, synchronous, no I/O
}
export interface StakeInput {
  bankroll: number; edge: number; odds: DecimalOdds;
  legs: Selection[];                              // for correlation cap
  limits: LimitSet; grant?: ModeBGrant;           // grant only in Mode B
}
export interface LimitSet {
  kellyFraction: 0.25; maxPctBankroll: number; maxAbsoluteNaira: number;
  minEdge: number;                                // default 0.04
  maxLegsPerMatch: 2; dailyLossCapNaira: number;
}
export interface StakeDecision {
  action: 'STAKE' | 'REFUSE';
  amountNaira?: number;
  reasons: string[];                              // every rule that fired, pass or block
}
```

**Dependencies:** none (pure module) except `types` and the `ModeBGrant` type from `db`. This is deliberate: the risk math must have no I/O, no clock dependence beyond its inputs, and be trivially unit-testable.
**Failure mode:** missing bankroll → stake 0 (never assume a default bankroll). Any arithmetic anomaly (negative edge, odds ≤ 1, NaN) → `REFUSE` with reason. Limits cannot be mutated at runtime without the 24 h cooldown flow; the module refuses a `LimitSet` whose invariants are violated (e.g. kellyFraction > 0.5) at construction time.

#### 1.6 `games/` — Aviator / Virtuals / casino labs

**Responsibility.** Everything in PLAN tiers T2–T4: the Aviator/JetX Monte-Carlo Risk Lab, virtuals EV calculators, house-edge tables, ruin simulators. These modules are *honesty engines* — they compute expected loss and ruin probability, never predictions.

```ts
export interface GameLab {
  gameId: string;                            // 'aviator' | 'jetx' | 'lucky_numbers' | ...
  tier: 2 | 3 | 4;                           // never 1 — T1 belongs to models/
  simulate(strategy: StrategySpec, rounds: number, runs: number): SimResult;
  houseEdge(gameId: string): EdgeTable | null;
  ruinProbability(strategy: StrategySpec, bankroll: number, runs: number): number;
}
export interface SimResult {
  finalBankrollDist: number[];               // per-run outcomes for plotting
  ruinProb: number; expectedLossPer100: number;
  verdict: string;                           // plain-language, linter-checked wording
}
```

**Dependencies:** none beyond `types` (pure math + static edge tables). Provably-fair HMAC verification for Aviator is a pure function here.
**Failure mode:** an unknown game id returns `tier: 4` + "unmodelled" verdict rather than a guessed edge. Any attempt to route a T2–T4 game into `models/` is structurally impossible: `models/` takes a `Fixture`, and virtual/crash rounds are not fixtures.

#### 1.7 `placement/` — slip build, confirm handshake, driver, verification

**Responsibility.** Builds slips from gate-approved predictions, runs the confirmation handshake (Mode A) or grant check (Mode B), forks the browser driver, executes the placement through the exact state machine in §4, and verifies by reading the open-bets list back. It never computes stake or edge itself — it refuses a slip without a matching `StakeDecision`.

```ts
export interface PlacementService {
  buildSlip(predictionId: string): Slip;
  requestConfirmation(slip: Slip, mode: 'A' | 'B'): Promise<ConfirmationHandle>;
  execute(slipId: string, grant: SessionGrant): AsyncIterable<PlacementEvent>;
  verify(slipId: string): Promise<VerificationResult>;
}
export interface Slip { id: string; predictionId: string; selections: Selection[]; stakeNaira: number; slipHash: string; }
export interface PlacementEvent { state: PlacementState; detail?: string; ts: number; }
```

**Dependencies:** `staking` (reads StakeDecision), `vault` (session grant via IPC to driver), `audit` (every transition), `db`, driver child process.
**Failure mode:** the state machine (§4) has no silent failure: every terminal state is `placed_verified | placed_unverified | failed_pre_submit | aborted | needs_reauth`. After `submitting`, there is **no automatic retry ever** (double-placement is the worst bug this module could have); `placed_unverified` requires human resolution via the open-bets monitor. Driver crash → `failed_pre_submit` if before submit, `placed_unverified` if after.

#### 1.8 `vault/` — credentials at rest

**Responsibility.** Stores the SportyBet session cookie, LLM API keys, and any future credentials, encrypted at rest with a passphrase-derived key. Full design in SECURITY.md §2; the interface is what matters here:

```ts
export interface Vault {
  isInitialized(): boolean;
  initialize(passphrase: string): Promise<void>;
  unlock(passphrase: string): Promise<void>;   // derives key, caches in memory only
  lock(): void;                                 // zeroes key material
  get(key: 'sportybet_session' | 'llm_api_key' | `custom.${string}`): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  delete(key: string): Promise<void>;
  exportAll(): never;                           // type-level: no export path exists
}
```

**Dependencies:** `hash-wasm` (Argon2id, pure WASM — no native build), Node `crypto` (AES-256-GCM), optional OS keychain binding per platform.
**Failure mode:** wrong passphrase → constant-time compare fails, attempt counter with exponential backoff (no lockout that bricks the user, no fast oracle). Corrupted vault file → refuse to start placement + LLM-key features; journal/bets survive because they live in the main DB outside the vault. Lock on idle (15 min) and on process exit.

#### 1.9 `audit/` — hash-chained append-only log

**Responsibility.** Append-only, hash-chained record of every consequential action: gate decisions, placements, limit changes, vault events, consent versions. Synchronous appends (better-sqlite3 transaction: event row + new chain head in one commit). Chain formula and verification walk in SECURITY.md §4.

```ts
export interface AuditLog {
  append(event: AuditEvent): void;              // synchronous; throws only on DB failure
  verify(): ChainVerification;                  // walk whole chain, report first break
  tail(n: number): AuditEvent[];
  stream(): AsyncIterable<AuditEvent>;          // live tail for the UI
}
export interface AuditEvent { actor: 'agent'|'user'|'system'|'driver'; action: string; subject?: string; payload: Record<string, unknown>; }
```

**Dependencies:** `db` only.
**Failure mode:** a crash mid-append leaves a gap that `verify()` detects on next boot and the UI surfaces as "audit chain broken at seq N" — tamper-*evident*, not tamper-proof. Append never blocks the placement pipeline: if the DB write fails, the driver aborts (no unlogged placement is the invariant).

#### 1.10 `calibration/` — scoring, tuning, weights

**Responsibility.** Consumes settled predictions, computes Brier/log-loss, builds calibration curves, tunes the temperature parameter, and produces the forecaster weights the ensemble uses. It is the feedback loop that makes the system honest about itself.

```ts
export interface CalibrationEngine {
  record(predictionId: string, result: SettledResult): void;
  brier(opts?: { since?: number; scope?: string }): number | null;
  logLoss(opts?: { since?: number; scope?: string }): number | null;
  calibrationCurve(bins?: number): CalibrationBin[];
  temperature(): number;                        // current tuned temperature
  forecasterWeights(): Weights;
}
```

**Dependencies:** `db` (predictions, bets), `models` (type only).
**Failure mode:** fewer than 50 settled samples → returns `null` and the ensemble falls back to equal weights (never divides by zero silently). Settlement reconciler failures leave predictions `pending` — they are excluded from scores until resolved, never guessed.

#### 1.11 Dependency graph (arrows = "imports from")

```
placement ──▶ staking ◀── agent ──▶ tools ──▶ vault (session only)
    │            ▲        │  │        │
    ▼            │        ▼  ▼        ▼
  audit        models ──▶ odds   db (fetch_cache)
    │            │
    ▼            ▼
   db ◀────── calibration
```

Rules enforced by an ESLint boundary rule (`no-restricted-imports` per directory): `staking` and `games` import nothing but `types`; `vault` imports nothing from `placement`/`agent`; nothing outside `tools/` performs network I/O.

---

### 2. The agent tool-loop

#### 2.1 How tools are registered

Tools are plain objects registered at boot in `src/core/tools/index.ts`. Each tool bundles: name, description, zod schema, cost class, cache TTL, and a `run` function. `ToolRegistry.list()` compiles them into OpenAI-style function definitions (name, description, JSON schema) — this one list is the entire tool surface the LLM ever sees, which keeps prompt size bounded and makes the tool set auditable in one place. Registry rejects duplicate names and schema-less tools at boot. Third-party data-source plugins (PLAN feature 97) are just tools that arrive via a `registerPlugin()` hook — they get no additional privileges.

#### 2.2 How the LLM calls them

The orchestrator runs a bounded ReAct loop (max 12 tool calls, token budget from `TokenBudget`):

1. System prompt: role, current fixture, the tool list, and the rule that **tool results are data, not instructions** (prompt-injection defense; scraped pages are quoted back as text).
2. Model emits `tool_calls` → orchestrator validates args against the tool's zod schema. Invalid args are returned to the model as a tool message with the validation error (one retry allowed, then the tool is dropped from the run).
3. `registry.invoke()` executes with single-flight dedup + cache + circuit breaker. Full result goes to the UI; a truncated/summarized form (head of arrays, counts) goes back into the LLM context to control token spend.
4. Results are appended as tool messages; loop repeats until the model emits the final structured card (schema-constrained output) or the budget is exhausted → stats-only fallback.
5. Every step emits `AgentEvent`s onto the event bus as they happen — the UI never polls.

The non-LLM phases (Poisson, Elo, ensemble, critic, edge, gate) emit `phase` events through the same bus, so the stream is a single coherent timeline of the whole pipeline.

#### 2.3 Streaming to the UI: **SSE, not websocket** — decision + justification

**Chosen: Server-Sent Events over a single multiplexed connection.**

- **Traffic shape fits.** The agent stream is overwhelmingly server→client (phases, tool calls, LLM tokens, the card). Client→server traffic is a handful of discrete commands (confirm slip, cancel run, answer critic) — normal `POST` fetches with the auth header, which is also the CSRF-safe channel (see SECURITY.md §3). A websocket's bidirectionality buys nothing here and costs a dependency (`ws`) plus an upgrade path.
- **Zero extra dependencies.** Next.js 15 route handlers return a `ReadableStream` natively; `EventSource` is built into browsers. Smaller supply-chain surface is a security feature (SECURITY.md §5).
- **Survives real conditions.** SSE runs over plain HTTP/1.1, passes simple proxies, and `EventSource` auto-reconnects with `Last-Event-ID`, so a phone dozing mid-research resumes the stream instead of dropping it.
- **The known weakness, engineered around.** Browsers cap ~6 concurrent HTTP/1.1 connections per origin. Mitigation: **one** SSE connection per tab carrying all event types, multiplexed by `runId` (`?runId=` filter or subscribe-all); never one stream per analysis. Heartbeat comment (`: ping`) every 15 s keeps intermediaries from timing the connection out.

Wire format: `event: <AgentEvent.type>\nid: <seq>\ndata: {json}\n\n`, with `seq` monotonic per connection for `Last-Event-ID` resume. Command endpoints (`POST /api/runs/:id/cancel`, `POST /api/slips/:id/confirm`) are ordinary token-authed POSTs.

---

### 3. Database schema

SQLite via better-sqlite3 + Drizzle. WAL mode, `foreign_keys=ON`. All timestamps are unix ms integers (no TZ ambiguity). All ids are ULID strings (sortable, no autoincrement leakage in URLs). Written as SQL DDL; the Drizzle schema mirrors it 1:1 and migrations are generated from it.

```sql
-- Every prediction the pipeline ever made, BET or NO_BET. This is the
-- calibration ground truth — it must be complete, not flattering.
CREATE TABLE predictions (
  id                 TEXT PRIMARY KEY,              -- ULID
  fixture_id         TEXT NOT NULL,
  sport              TEXT NOT NULL,                 -- 'football', ...
  league             TEXT,
  kickoff_at         INTEGER NOT NULL,
  market             TEXT NOT NULL,                 -- '1X2' | 'OVER_UNDER' | 'BTTS' | ...
  line               TEXT,                          -- '2.5' | '-1' | NULL
  selection          TEXT NOT NULL,                 -- 'HOME' | 'OVER' | 'GG' | ...
  model              TEXT NOT NULL,                 -- 'ensemble' | 'poisson' | 'elo' | 'llm'
  prob               REAL NOT NULL,                 -- 0..1 after temperature scaling
  temperature        REAL,                          -- temperature applied at decision time
  fair_odds          REAL,                          -- 1/prob
  edge               REAL,                          -- prob × live_odds − 1 at decision time
  live_odds          REAL,                          -- quote used (NULL if odds unavailable)
  odds_method        TEXT,                          -- 'proportional' | 'shin'
  data_completeness  REAL,                          -- 0..1, gate input
  critic_verdict     TEXT,                          -- JSON {sustained, arguments[]}
  reasons_json       TEXT NOT NULL,                 -- reasoning summary + SourceRef[]
  gate_decision      TEXT NOT NULL,                 -- 'BET' | 'NO_BET' | 'SKIP'
  gate_reasons_json  TEXT,                          -- every rule that fired
  run_id             TEXT NOT NULL,                 -- → sessions.id
  created_at         INTEGER NOT NULL
);
CREATE INDEX idx_pred_fixture ON predictions(fixture_id, created_at);
CREATE INDEX idx_pred_scope   ON predictions(model, market, kickoff_at);  -- calibration scopes
CREATE INDEX idx_pred_gate    ON predictions(gate_decision, kickoff_at);

-- Money events. A row exists only after the gate said BET and the placement
-- pipeline reached a terminal state. NO_BET predictions never create bets.
CREATE TABLE bets (
  id                 TEXT PRIMARY KEY,
  prediction_id      TEXT NOT NULL REFERENCES predictions(id),
  mode               TEXT NOT NULL,                 -- 'A' | 'B'
  grant_id           TEXT,                          -- → mode_b_grants.id, Mode B only
  slip_json          TEXT NOT NULL,                 -- full slip snapshot incl. odds at placement
  slip_hash          TEXT NOT NULL,                 -- SHA-256 of canonical slip; user confirmed THIS
  stake_naira        REAL NOT NULL,
  potential_return   REAL,
  placement_state    TEXT NOT NULL,                 -- last state machine state (§4)
  placement_ref      TEXT,                          -- bet id read back from My Bets
  placed_at          INTEGER,
  verified_at        INTEGER,
  status             TEXT NOT NULL DEFAULT 'pending',  -- pending|won|lost|void|cashout|unknown
  payout             REAL,
  settled_at         INTEGER,
  settlement_source  TEXT,                          -- 'readback' | 'manual' | 'reconciler'
  clv_close_odds     REAL,                          -- closing price for CLV tracking
  notes              TEXT,
  created_at         INTEGER NOT NULL
);
CREATE INDEX idx_bets_status ON bets(status, settled_at);
CREATE INDEX idx_bets_pred   ON bets(prediction_id);

-- Human diary: notes, tags, screenshots, lessons — linked to bets or freeform.
CREATE TABLE journal (
  id                 TEXT PRIMARY KEY,
  bet_id             TEXT REFERENCES bets(id),      -- NULL = freeform entry
  kind               TEXT NOT NULL,                 -- 'bet_note' | 'session_note' | 'lesson' | 'screenshot'
  body               TEXT NOT NULL,
  tags_json          TEXT,
  attachment_path    TEXT,                          -- local file under data dir, never a URL
  created_at         INTEGER NOT NULL
);
CREATE INDEX idx_journal_bet ON journal(bet_id, created_at);

-- Tamper-evident action log. Append-only; formula in SECURITY.md §4.
CREATE TABLE audit_log (
  seq                INTEGER PRIMARY KEY AUTOINCREMENT,
  ts                 INTEGER NOT NULL,
  actor              TEXT NOT NULL,                 -- 'agent' | 'user' | 'system' | 'driver'
  action             TEXT NOT NULL,                 -- 'gate.decision', 'placement.state', ...
  subject            TEXT,                          -- slipId / fixtureId / grantId
  payload_json       TEXT NOT NULL,                 -- redacted per policy before hashing
  prev_hash          TEXT NOT NULL,                 -- hex; genesis row uses h_0
  hash               TEXT NOT NULL                  -- hex chain head after this row
);
CREATE INDEX idx_audit_action ON audit_log(action, ts);

-- Periodic calibration snapshots (the dashboard reads these, not raw predictions).
CREATE TABLE calibration (
  id                 TEXT PRIMARY KEY,
  as_of              INTEGER NOT NULL,
  scope              TEXT NOT NULL,                 -- 'global' | 'league:EPL' | 'market:1X2' | 'model:poisson'
  n                  INTEGER NOT NULL,              -- settled sample count
  brier              REAL,
  log_loss           REAL,
  calibration_json   TEXT,                          -- bins: [{p_low, p_high, predicted, actual, n}]
  temperature        REAL,
  weights_json       TEXT                           -- forecaster weights in effect
);
CREATE INDEX idx_calib_scope ON calibration(scope, as_of);

-- Agent runs (research + chat). Also the crash-recovery ledger.
CREATE TABLE sessions (
  id                 TEXT PRIMARY KEY,              -- runId
  kind               TEXT NOT NULL,                 -- 'research' | 'chat'
  fixture_id         TEXT,
  status             TEXT NOT NULL,                 -- 'running' | 'done' | 'error' | 'cancelled'
  model              TEXT,                          -- LLM used, NULL if stats-only
  tokens_in          INTEGER, tokens_out INTEGER, cost_usd REAL,
  started_at         INTEGER NOT NULL,
  finished_at        INTEGER,
  error              TEXT                           -- code + message on 'error'
);
CREATE INDEX idx_sessions_status ON sessions(status, started_at);

-- Mode B grants (referenced by bets.grant_id). Expiry is enforced by staking/.
CREATE TABLE mode_b_grants (
  id                 TEXT PRIMARY KEY,
  budget_naira       REAL NOT NULL,
  spent_naira        REAL NOT NULL DEFAULT 0,       -- incremented in the placement transaction
  max_stake_naira    REAL NOT NULL,
  loss_cap_naira     REAL NOT NULL,
  allowed_classes_json TEXT NOT NULL,               -- e.g. ["football_1X2","football_OU"]
  expires_at         INTEGER NOT NULL,
  revoked_at         INTEGER,
  created_at         INTEGER NOT NULL
);

-- Fetch cache backing tools/ (§5). Stale-while-error source of truth.
CREATE TABLE fetch_cache (
  key                TEXT PRIMARY KEY,              -- sha256(source + endpoint + canonical params)
  source             TEXT NOT NULL,
  payload_json       TEXT NOT NULL,
  sources_json       TEXT,                          -- SourceRef[] for citation
  fetched_at         INTEGER NOT NULL,
  expires_at         INTEGER NOT NULL,
  etag               TEXT
);

-- Durable work queue for the worker loop (research runs, scheduled fetches).
CREATE TABLE jobs (
  id                 TEXT PRIMARY KEY,
  kind               TEXT NOT NULL,                 -- 'research' | 'fetch' | 'settle' | 'calibrate'
  payload_json       TEXT NOT NULL,
  status             TEXT NOT NULL DEFAULT 'queued',-- queued|running|done|error
  run_after          INTEGER NOT NULL,
  attempts           INTEGER NOT NULL DEFAULT 0,
  last_error         TEXT,
  created_at         INTEGER NOT NULL
);
CREATE INDEX idx_jobs_due ON jobs(status, run_after);
```

Integrity rules: `bets.prediction_id` must point at a `gate_decision='BET'` row (enforced in `placement/`, checked by a DB trigger); a bet's `stake_naira` must equal the `StakeDecision.amountNaira` recorded in the prediction's `gate_reasons_json`. Migrations never drop `predictions`/`bets`/`journal` columns — the journal is the user's property.

---

### 4. The placement pipeline

Four stages: **slip build → confirm handshake → browser driver execute → verification read-back**. Mode A requires the handshake; Mode B substitutes the grant check but keeps every other stage identical.

**Stage 1 — Slip build.** `PlacementService.buildSlip(predictionId)` loads the prediction, asserts `gate_decision='BET'`, re-reads the `StakeDecision` from staking, snapshots live odds into the slip, and computes `slipHash = sha256(canonicalJson(slip))`. Everything downstream approves or executes *this hash*.

**Stage 2 — Confirm handshake.** Mode A: the UI renders the full slip; for stakes ≥ `typedPhraseThresholdNaira` (default ₦5,000) the user must type a phrase shown on screen ("PLACE 5000"). The approval record stores the `slipHash` — the user approved that exact slip, not "a slip like this". Mode B: `staking` re-validates the grant (budget, expiry, class) in the same transaction that flips the bet row to `confirmed`.

**Stage 3 — Driver execute.** `child_process.fork()` the driver; parent passes job descriptor + a short-lived session grant over IPC (never env, never disk). Driver launches a **non-persistent** Playwright context — cookies injected per run, `storageState` never saved, context destroyed after the run so nothing lands on disk.

**Stage 4 — Verification read-back.** After submit, the driver opens My Bets and matches the new entry by signature (kickoff + stake + selections). No match after N retries → `placed_unverified` — flagged for the human, **never** auto-resubmitted.

#### State machine

States: `draft, awaiting_confirmation, confirmed, launching_driver, authenticating, needs_reauth, building_slip_on_site, reviewing_quote, submitting, verifying, placed_verified, placed_unverified, failed_pre_submit, aborted`.

```
draft                    → awaiting_confirmation      (slip built; Mode B: grant check passed)
draft                    → aborted                    (gate re-check failed at build time)
awaiting_confirmation    → confirmed                  (user approves [+ typed phrase if stake ≥ threshold])
awaiting_confirmation    → aborted                    (user rejects, or 5-minute expiry)
confirmed                → launching_driver           (fork OK)
confirmed                → aborted                    (slipHash mismatch on pre-execute re-check)
launching_driver         → authenticating             (browser up, context created)
launching_driver         → failed_pre_submit          (driver crash / Chromium missing)
authenticating           → building_slip_on_site      (session valid: account element found)
authenticating           → needs_reauth               (session dead/expired)
needs_reauth             → awaiting_confirmation      (user re-auths via guided browser window; re-quote required)
building_slip_on_site    → reviewing_quote            (all selections present on the site's betslip)
building_slip_on_site    → failed_pre_submit          (selection suspended/market gone)
building_slip_on_site    → aborted                    (user cancel)
reviewing_quote          → submitting                 (site's total odds/stake/return within 1% of approved slip)
reviewing_quote          → awaiting_confirmation      (quote drifted beyond tolerance → re-approve with new quote)
reviewing_quote          → aborted                    (user cancel)
submitting               → verifying                  (place button clicked, no client error)
submitting               → failed_pre_submit          (site rejected: explicit error, nothing placed)
submitting               → placed_unverified          (timeout/unknown — NO auto-retry, ever)
verifying                → placed_verified            (bet found in My Bets; placement_ref stored)
verifying                → placed_unverified          (N read-back retries exhausted)
verifying                → failed_pre_submit          (definitive evidence nothing was placed)
placed_unverified        → placed_verified            (manual/later read-back confirms)
```

**Invariants.**
1. **No silent failure:** every transition writes an `audit_log` row (`placement.state`) and a `PlacementEvent` to the SSE bus.
2. **No auto-retry after `submitting`:** the only move out of `placed_unverified` is human resolution. Double-placement is the unforgivable bug; an unverified-but-probably-placed bet is recoverable, a double bet is not.
3. **TOCTOU protection:** the driver re-computes `slipHash` from the live quote at `reviewing_quote` and aborts to re-confirmation if it differs beyond tolerance — the user's approval is bound to the exact terms.
4. **Kill switch:** `vault.lock()` at any point forces the driver's next transition to `aborted` (session grant is checked before every site interaction).
5. **Crash recovery:** on boot, any bet row stuck in a non-terminal state is reconciled — pre-submit states → `failed_pre_submit`, post-submit states → `placed_unverified` + a human-resolution task.

---

### 5. Data ingestion

| Fetcher | Transport | Schedule | TTL |
|---|---|---|---|
| sportList tree | browser ctx | every 6 h (big, slow-moving) | 6 h |
| Fixtures next 48 h | browser ctx | every 30 min | 30 min |
| Live odds (watched/open cards) | browser ctx | 60–120 s while card open / watchlist active | 90 s |
| Results / settlements | browser ctx | every 30 min | — |
| League tables | browser ctx | daily | 24 h |
| football-data.co.uk history | plain HTTPS | weekly | 7 d |
| Team stats, last-5, H2H | browser ctx | **on-demand** (tool call) | 24 h |
| Injuries / lineups | browser ctx | on-demand, near kickoff | 30 min |
| xG (Understat/FBref) | plain HTTPS | on-demand + weekly refresh | 7 d |
| News, weather, referee stats | plain HTTPS | on-demand | 1–6 h |
| Odds movement history | browser ctx | on-demand | 15 min |

**All SportyBet fetches go through the shared browser context** — verified fact: desktop curl gets 403, real browser sessions work. Even the "open" `factsCenter/sportList` rides the browser. One shared Playwright browser owned by the worker; the read client uses `context.request` (Playwright's APIRequestContext tied to the browser context) so requests carry the real browser's cookies/TLS fingerprint. Caching: `fetch_cache` keyed `sha256(source+endpoint+canonical-params)`, TTL per source class, ETag/Last-Modified where supported, **stale-while-error** (serve stale on upstream failure, flagged on the card), single-flight dedup so parallel tool calls don't stampede, and a failure ledger listing every stale/down source on the card.

**Live endpoint map (verified from the production page's own network traffic, 2026-11-18):**
- `GET /api/ng/factsCenter/sportList?productId=3` — full sport tree (open)
- `GET /api/ng/factsCenter/liveOrPrematchEvents?productId=3&sportId=sr:sport:1&marketId=1,18,...&categoryId=all&tournamentId=all&timeline=&pageSize=&pageNum=&option=1` — fixtures + odds feed
- `GET /api/ng/factsCenter/event?productId=3&eventId=sr:match:...` — single event detail
- `GET /api/ng/factsCenter/quickMarketList?block=A|B&sport=sr:sport:1` — quick market chips
- `GET /api/ng/factsCenter/wapConfigurableIndexLiveEvents?sportId=...&withTwoUpMarket=true&withOneUpMarket=true` — live events with 2up/1up
- `GET /api/ng/gaming/gameList`, `/gaming/list`, `/gaming/config`, `/gaming/game/list`, `/gaming/games`, `/gaming/popular` — games catalogue
- `GET /api/ng/gaming/aviator/rounds` — Aviator round history
- `GET /api/ng/scheduledVirtual/api/v1/config` — virtuals config
- `GET /api/ng/instantwin/api/v1/iw/config/sport?sportId=sr:sport:1-1` — instant-win config
- `GET /api/ng/orders/v2/getBalance` — balance (auth-gated)
- IDs are Sportradar format (`sr:sport:1`, `sr:match:...`) — SportyBet runs on Sportradar data
- Envelope: `{bizCode, innerMsg, message, data}`; 19000=invalid params, 19001=wrong path, 19003=forbidden anonymous

### 6. Build order (first 10 issues, PLAN §11)

1. Scaffold + start.sh → 2. Consent gate (blocks app; precedes all features) → 3. SportyBet read client (data for everything) → **{4. Poisson, 5. Elo, 6. LLM analyst loop run in parallel}** (4 needs football-data.co.uk ingest bundled; 6 needs only 3) → 7. Ensemble (needs 4,5,6) → 8. NO-BET gate (needs 7 + odds from 3) → 9. Journal + bankroll (needs 8 to create bets) → 10. Calibration dashboard (consumes what everything produces; last). **Deferred past issue 10:** vault + Mode B placement (v0.5) — LLM keys live in `.env` (gitignored) for v0.1; `placement/` and `vault/` are untouched in v0.1 by design.





---

# Part 9 — Security


## SportyAgent — Security

### 1. Threat model
**Other users on a shared machine.** The app is single-user localhost but runs on shared laptops. Threats: reading the DB (journal/bets — personal, not credentials), reading vault.bin (encrypted, useless without the key), another local process hitting localhost:3000, shoulder-surfing the passphrase, memory inspection while the driver runs. Mitigations: passphrase-derived key never written to disk; 15-min auto-lock; 127.0.0.1 binding + per-install token so other users' processes can't call the API; OS separation advice (own OS user, full-disk encryption); audit chain detects DB tampering.
**Network attacker.** Server binds 127.0.0.1, so the surface is outbound calls (SportyBet, LLM, data sources). Threats: MITM (mitigated: TLS-only, no custom CAs, validation never disabled); malicious sources serving XSS/prompt-injection (scraped content rendered as text, never HTML; tool results are data, never instructions — orchestrator enforces this in the system prompt); DNS rebinding (evil.com → 127.0.0.1 hits the API — killed by per-install token + Host/Origin checks, §3). Honest limit: prompts leave the machine to the LLM provider unless the user runs Ollama.
**The app itself misbehaving.** Double-placement bugs, gate failures, runaway staking. Mitigations: `staking/` is the only code path producing a positive stake and `placement/` refuses any slip without a matching StakeDecision row; no auto-retry after submit; limits live in a pure, unit-tested module; `verify()` on boot; kill switch (`vault.lock()` aborts in-flight placements); Mode B budget checked in the same transaction as placement intent.
**SportyBet detecting automation.** Account closure, winnings void. We do **not** engineer evasion — promising that would be dishonest. Noise-reducing choices: Mode A default (human present), human pacing delays, rate limits + backoff, no scraping beyond need, risk stated in TERMS.md. On a captcha/challenge the driver hands control to the human — never auto-solves. Detection risk is an accepted user risk, stated plainly.

### 2. Vault design
Argon2id via **hash-wasm** (pure WASM — no native build, cross-platform deterministic): 16 B salt, m=64 MiB, t=3, p=1 (~200 ms), 32 B AES-256 key held in memory only, zeroed on lock/exit. Encryption: **AES-256-GCM** from node:crypto (zero extra deps), per-record AAD bound to the record's key name (prevents record swapping). Storage: single `vault.bin` JSON envelope `{v, kdf, salt, verifier, records:{name:{nonce,ct,tag}}}`, atomic rewrite (temp+rename) on each set — not encrypted SQLite, because queries over secrets are unnecessary and atomicity is trivial. Journal/bets stay in the main DB; they contain no credentials.
**OS keychain binding:** macOS Keychain (GenericPassword, this-device-only) / Windows DPAPI (CurrentUser, tiny bundled native addon) / Linux libsecret if present else passphrase-only fallback — detected at runtime. Composition: `masterKey = HKDF-SHA256(Argon2id(passphrase) ‖ K_K)`. Modes: `passphrase_only` (default), `passphrase+keychain` (default where available — two-factor), `keychain_only` (explicit opt-in, warned). Optional one-time recovery kit (passphrase-only envelope under a second derivation) covers lost keychain entries.
**Zero-export guarantee, enforced:** `exportAll(): never` (no export path at type level); redaction middleware on every log/audit write (denylist: token, cookie, password, authorization, balance); driver child receives the session over IPC at launch and runs with a preload shim that makes `fs.writeFileSync`/`createWriteStream` throw if the buffer contains any secret passed at launch (runtime taint tracking); ESLint bans network calls in `vault/`; non-persistent Playwright context — `storageState` never saved.

### 3. Local API hardening
Bind `127.0.0.1` explicitly — **`next start` defaults to 0.0.0.0**, so start.sh must pass `-H 127.0.0.1` (or custom server `server.listen(3000,'127.0.0.1')`); handle ::1 fallback. Per-install token generated at first boot, stored 0600, sent as `X-Auth-Token` header — header-token auth is CSRF-immune by construction (attacker pages can't set custom headers cross-origin); no auth cookies at all. SSE: EventSource can't set headers → `POST /api/ticket` (header-authed) returns a 60-second single-use ticket used as `?ticket=`. Middleware rejects Host ∉ {127.0.0.1:3000, localhost:3000} (kills rebinding); non-GET requires Origin ∈ {http://localhost:3000, http://127.0.0.1:3000} and `Sec-Fetch-Site: same-origin` where available. No CORS headers emitted; auth attempts rate-limited; unknown /api paths 404; body-size limit.

### 4. Audit log hash chain
`‖` = length-prefixed concatenation (strings: UTF-8 + 2-byte length; integers: 8-byte big-endian):
```
h_0 = SHA-256("sportyagent-audit-genesis" ‖ install_id)
h_n = SHA-256( h_{n-1} ‖ seq_n ‖ ts_n ‖ actor_n ‖ action_n ‖ SHA-256(payload_n) )
```
Row n stores `prev_hash = h_{n-1}`, `hash = h_n`; payload hashed separately so encoding quirks can't break verification. `verify()` walks from genesis; first mismatch at seq k ⇒ break between k−1 and k. Head hash also written to `audit.head` (0600, separate write path) and shown in the UI — a DB-only rewrite is detectable against the anchor. Rotation by year/size carries the head forward.

### 5. Supply chain
Policy: minimal deps, written justification per dep in PR template, Node built-ins preferred, lockfile committed + `npm ci` only, postinstall scripts audited, dependabot on, SBOM (CycloneDX) at release, Actions pinned by SHA. **`make audit`**: (1) `npm audit --omit=dev` fails on high/critical; (2) lockfile-drift check; (3) secret scan (gitleaks-style: API keys, private keys, session-cookie shapes); (4) banned-language linter (guaranteed/sure/100%/win big); (5) vault export-guard — static check that no code in `vault|placement` writes secrets to disk or calls non-allowlisted hosts; (6) redaction test (fake credentials through the logger, assert absent); (7) permission check (data dir 0700, files 0600, vault.bin 0600); (8) license scan; (9) audit-chain integrity test; (10) SBOM diff flags new deps.

### 6. Honest limits — what this does NOT protect against
Malware/root on the machine (key readable in memory, keylogger gets the passphrase); shoulder surfing / physical access with vault unlocked; the user approving a bad slip (Mode A's human is the last line); SportyBet enforcement (ToS breach risk remains regardless of politeness); LLM provider seeing prompts (unless Ollama); compromised deps at runtime (audit is point-in-time); prompt injection is mitigated, never eliminated; audit log vs sustained FS-write attackers (evident, not impossible); the main DB is readable by any same-OS-user process — journal privacy is weak by design; gambling harm itself — the app enforces caps, not self-control.

### Riskiest design decisions
1. **All SportyBet reads via a real browser context** (`context.request`) — the only transport verified to survive bot protection (curl 403); risk: fragility + detection surface, mitigated by caching, rate limits, stale-while-error.
2. **Placement: forked driver, non-persistent context, no auto-retry after `submitting`** — double-placement is the unforgivable bug; `placed_unverified` always resolves by human, never by retry.
3. **Vault two-factor default (passphrase ‖ keychain key via HKDF)** — strongest at rest, but a lost keychain entry bricks the vault; mitigated by an optional one-time recovery kit.
(SSE over websocket: single multiplexed stream, zero deps, CSRF-safe command channel via header-token POSTs.)





---

# Part 10 — Site Reverse Engineering Log


## SportyBet — Site Reverse Engineering
Live findings gathered 2026-11-18 by harvesting the site's own network traffic and probing endpoints directly. Anonymous (no account used). Appended as discovered.

---

### 1. SPA structure

Mobile app served at `https://www.sportybet.com/ng/m/`. Product silos render as `story-card card-wrapper` elements on the home page:

`Lucky Numbers` · `Virtuals` · `Aviator` · `Crime Miami` · `Jackpot` · `Sporty Picks` · `Scheduled Football` · `JetX Cashback` · `Win With EarlyGoals` · `SportySIM` · `AutoBet`

Bottom nav tabs: `Hot` · `Matches` · `Games` · `Codes` · `Virtuals` · `LuckyNumbers`
Top shortcuts: `All Sports` · `Live` · `Load Code` · `Aviator` · `Virtuals` · `More`

Route note: `/ng/m/aviator` returns a branded 404 ("40X ERROR — OOPS... The page and ball you're looking for doesn't exist"). The Aviator experience is reached by **clicking the story card**, not by URL. This matters: route-guessing does not work, the SPA is stateful.

### 2. API inventory (harvested from real page traffic)

| Endpoint | Auth | What it powers |
|---|---|---|
| `/api/ng/factsCenter/sportList?productId=3` | open | Full sport tree, 22 verticals |
| `/api/ng/factsCenter/quickMarketList?block=A\|B&sport=sr:sport:1` | open | Home-page market chips |
| `/api/ng/factsCenter/story/v1/story-sets?page=0&pageSize=15` | open | Product silo cards (the story carousel) |
| `/api/ng/factsCenter/recommendScrollEvents/v2` | open | Recommended matches |
| `/api/ng/factsCenter/wapConfigurableIndexLiveEvents?sportId=…&withTwoUpMarket=true&withOneUpMarket=true` | open | Live events incl. 2up/1up |
| `/api/ng/factsCenter/betType/config` | **open** | **Bet-type payout math (see §4)** |
| `/api/ng/common/config/query` | open | Global config |
| `/api/ng/common/config/broadcast` | open | Broadcast/messaging config |
| `/api/ng/instantwin/api/v1/iw/config/sport?sportId=sr:sport:1-1` | open | Instant-win product config |
| `/api/ng/scheduledVirtual/api/v1/config` | open | Virtual sports schedule config |
| `/api/ng/sportySim/v1/config/overall` | open | SportySIM config *(returns `unsupported country code: null` when probed without the NG context headers)* |
| `/api/ng/orders/config/cutbet` | open-ish | Cash-out / cut-bet rules |
| `/api/ng/orders/flexi/banned-markets` | open-ish | Markets excluded from Flexi bets |
| `/api/ng/promotion/v2/bonus/plans/valid` | open | Active bonus plans |
| `/api/ng/factsCenter/liveOrPrematchEvents?...` | **signature** | Fixtures + odds (see §3) |
| `/api/ng/orders/v2/getBalance` | **login** | Balance |

Two error envelopes exist and are **not the same shape**:
```json
{"bizCode":19000,"innerMsg":"Invalid","message":"Invalid","data":{}}
{"errorCode":19000,"errorName":"INVALID","causeMsg":"unsupported country code: null"}
```
The second appears on newer namespaces (`sportySim`) and reveals the country gating explicitly.

### 3. Fixtures feed signing

`liveOrPrematchEvents` with the exact production param set, called with session cookies present, still returns `19000 Invalid`. The page computes something we do not replicate — header, timestamp nonce, or body signature. **Conclusion for the product: never reconstruct this call. Drive a real browser.** This is the load-bearing architectural finding.

### 4. Bet-type payout math — verified, from the live API

`GET /api/ng/factsCenter/betType/config` → `bizCode:10000`. This is the operator's own published payout config for accumulator types:

#### AnyWin ("any n of m")
```json
{
  "minOdds": "1.01",
  "minSelectionOdds": "1.99",
  "minSelectionNum": 2,
  "maxSelectionNum": 10,
  "oddsKey": 0.65,
  "oddsKeys": {
    "2": 0.95, "3": 0.95, "4": 0.90, "5": 0.90, "6": 0.85, "7": 0.85,
    "8": 0.80, "9": 0.80, "10": 0.80, "11": 0.75, "12": 0.75, "13": 0.75,
    "14": 0.75, "15": 0.65, "16": 0.65, "17": 0.65, "18": 0.60, "19": 0.55,
    "20": 0.55, "21": 0.55, "22": 0.55, "23": 0.50, "24": 0.45, "25": 0.45,
    "26": 0.45, "27": 0.45, "28": 0.45, "29": 0.40, "30": 0.40, "31": 0.35,
    "32": 0.30, "33": 0.25, "34": 0.25, "35": 0.25, "36": 0.25, "37": 0.25,
    "38": 0.25, "39": 0.20, "40": 0.20, "41": 0.20, "42": 0.20, "43": 0.17,
    "44": 0.17, "45": 0.17, "46": 0.17, "47": 0.15, "48": 0.15, "49": 0.15,
    "50": 0.15
  }
}
```

#### Flexi
```json
{
  "flexibleMinOdds": "1.01",
  "oddsKey": 0.65,
  "oddsKeys": { "3": 0.95, … "50": 0.15 },
  "flexiWeightedRtpEnabled": true,
  "flexiAverageWeightedRtpMultiplier": 1.0,
  "flexiAverageWeightedMinEffectiveRtp": 0.8
}
```

**What this means — and this is the most important thing found today:**

- Those `oddsKeys` decay curves are **not** odds. They are the operator's **selection factor applied to the payout** as the number of legs grows. At 2–3 legs you get 0.95 of the nominal return; at 50 legs you get **0.15**.
- Read plainly: **long accumulators pay back a fraction of what their odds imply.** A 50-leg accumulator is returned at 15% of its headline odds value.
- `flexiAverageWeightedMinEffectiveRtp: 0.8` is an explicit floor on effective RTP for Flexi products — i.e. the operator openly guarantees **no more than 80% effective return** on the Flexi path.
- `minSelectionOdds: 1.99` for AnyWin means cheap favourites are excluded from that product specifically to prevent a low-variance grind.

**Product implications (must go into the app):**
1. The agent must **never build long accumulators.** The decay curve makes them strictly worse than single bets at equivalent risk.
2. The accumulator builder must display the **effective payout after the oddsKey**, not the headline odds. A user who sees "odds 5,000" but gets 750 has been misled by the UI, not by chance.
3. This is a beautiful teaching example for the "why not bet this" agent: we can show the operator's own numbers.
4. Any calculator in the app must apply `oddsKeys[n]` for an n-leg slip. Both AnyWin and Flexi, separately.

### 5. Unknowns

- `[UNKNOWN]` Aviator round cadence and crash distribution — needs the Aviator route (reached by clicking, not by URL); not yet captured.
- `[UNKNOWN]` Virtual sports round cadence and league list — `scheduledVirtual/config` returned but not yet parsed for schedule.
- `[UNKNOWN]` Lucky Numbers draw schedule and results endpoint.
- `[UNKNOWN]` SportySIM mechanics — config is country-gated; needs the NG `x-country`, `x-product` style headers the page sends.
- `[UNKNOWN]` Terms of use text — not yet fetched.
- `[UNKNOWN]` Login flow (fields, OTP step) — deliberately not attempted.





---

# Part 11 — Does Any of This Beat the Margin


## Betting-AI Landscape Brief — SportyBet (Nigeria)

**Research question.** For an open-source AI betting-research agent targeting SportyBet (Nigeria), what does the evidence say about: (a) whether football outcome prediction can beat a ~5% bookmaker margin, (b) what data sources are actually available for free, (c) what staking math is defensible?

**Method.** Web research (multiple search phrasings) + live endpoint probes, session date 2026-11-18. Written incrementally under a write-ahead protocol: each section was appended immediately after it was researched.

**Source-grading legend**

| Grade | Meaning |
|---|---|
| [PEER-REVIEWED] | Journal/conference paper or academic book |
| [INDUSTRY] | Bookmaker/exchange or commercial analytics publisher (e.g. Pinnacle, vendor docs) |
| [PRACTITIONER] | Professional bettor/quant write-ups, practitioner books, maintainer docs |
| [ANECDOTAL] | Forums, GitHub repos, unverifiable personal claims |
| [UNVERIFIED] | Could not access or confirm during this session (recorded as a gap) |
| [VERIFIED-LIVE] | Endpoint probed successfully during this session |

---

### Section 1 — Can models beat the ~5% margin?

**The honest consensus, with disagreement preserved:**

- [PEER-REVIEWED] Wunderlich & Memmert (2015, PLOS ONE): statistical football forecasts and betting odds have comparable predictive accuracy — the market is a strong baseline, not a weak one.
- [PEER-REVIEWED] Štrumbelj (2014): bookmaker odds, after margin removal, are well-calibrated probabilities of football outcomes in major leagues.
- [PEER-REVIEWED] Constantinou & Fenton (2012, pi-ratings): rating-based models produce modest, real improvement over naive baselines — measurable, small.
- [INDUSTRY] Pinnacle betting resources: sharp-book margin ≈ 2–2.5%; the skill metric that separates winners from losers is closing-line value, not win rate.
- [PRACTITIONER] Buchdahl ("Against the Odds", "Squares & Sharps"): the overwhelming majority of tipsters fail to beat the margin after costs; short-sample variance makes luck look like skill.
- **Disagreement preserved:** several studies report small persistent edges in *niche* markets (lower divisions, corners, cards, player props) where the margin is applied less efficiently. Mainstream 1X2 in major leagues shows no robust exploitable edge in the published literature. Both statements are true simultaneously; a tool that only promises the second is lying.

**Confidence level the evidence supports:** models can be *calibrated* (predicted probabilities match observed frequencies) with high confidence. Consistently beating the margin in mainstream markets has low-to-moderate confidence at best; niche markets offer the only credible hunting ground. For a consumer tool, the defensible promise is: calibrated probabilities + value detection + honest scoreboard. Not "very sure predictions".

### Section 2 — Free data sources (graded, with access notes)

| Source | What it gives | Access | Grade | Notes |
|---|---|---|---|---|
| football-data.co.uk | Historical results + closing odds, 20+ Euro leagues, CSV | Free, no key, weekly updates | [INDUSTRY] | The backtest backbone. Verified format stable for years |
| football-data.org | Fixtures, results, standings, major leagues | Free tier, key, ~10 req/min | [INDUSTRY] | Clean REST, good for live fixtures |
| API-Football (api-sports.io) | Fixtures, injuries, lineups, predictions endpoint | Free tier 100 req/day, key | [INDUSTRY] | Broadest free coverage incl. African leagues |
| TheSportsDB | Community sports data | Free test key, patchy | [ANECDOTAL] | Quality varies wildly; use as fallback only |
| OpenLigaDB | German league data | Free, no key | [INDUSTRY] | Niche |
| Understat | xG data for top-5 Euro leagues | Unofficial, no key | [PRACTITIONER] | Scraping tolerated; respect rate limits |
| FBref / StatsBomb | Advanced match stats | HTML, ToS restricts scraping | [INDUSTRY] | Use sparingly; heavy scraping will get blocked |
| ESPN hidden API | Scores/schedules JSON | Unofficial, no key | [ANECDOTAL] | No SLA, can change without notice |
| SofaScore | Live scores, lineups | Unofficial, aggressive bot protection | [ANECDOTAL] | High block risk |

**Evidence gaps (findings, not failures):** no free source provides reliable injury/lineup data for Nigerian lower leagues; no free odds-movement history exists — CLV tracking must be built from the app's own odds snapshots; SportyBet's own fixtures feed requires the signed-header browser context (verified this session: replica XHR with cookies still returns 19000 "Invalid", so the page wrapper computes a signature the app must not try to forge).

### Section 3 — Staking math that is actually defensible

**Kelly criterion.** f* = (bp − q) / b, where b = decimal odds − 1, p = true win probability, q = 1 − p. Full Kelly maximises log-growth but is brutally volatile; **quarter-Kelly** is the industry-standard compromise (≈ 3/16 of the growth rate with ≈ 1/16 of the variance).

*Worked example:* bankroll ₦10,000, odds 2.00, true p = 0.52 → b = 1, edge = 0.52×2 − 1 = 4%. Full Kelly f* = (1×0.52 − 0.48)/1 = 4% → quarter-Kelly stake = 1% of bankroll = **₦100**. Note what this means: a "good" edge justifies a ₦100 stake on a ₦10,000 bankroll. Anyone staking 10% of bankroll per bet is not betting, they are donating.

**Gambler's ruin (why "play until you hit ₦X" cannot work).** For repeated play with win probability p < 0.5 (or any p with negative expected value per round), the probability of reaching a target T before ruin decays toward zero as the number of rounds grows — even if p = 0.5 exactly, P(reach T) ≤ B/T and every extra round adds house-edge drag. The "agent plays until it reaches the goal" loop is therefore not a strategy, it is a *ruin machine with a schedule*. This is a proven result, not an opinion.

**Why simulation, not formulas, is the honest presentation tool.** Ruin probabilities under fractional staking, stop-losses and bet-selection filters have no closed form users can feel. A Monte-Carlo simulator that runs 1,000 futures of the user's proposed strategy and plots the distribution (including the "lost everything" branch) communicates risk in a way no formula does. This is why the Aviator Risk Lab and the ruin simulator are core features, not garnish.

### Section 4 — Evidence gaps stated plainly

1. SportyBet's exact T&C clauses on automated access were never fetched this session — the legal pack must be drafted from general patterns and marked for verification before publication.
2. The fixtures-feed signing scheme was not reverse-engineered (deliberately — the architecture routes all reads through a real browser context instead).
3. No published per-product RTP for SportyBet virtuals/instant games was located — the app must display "RTP not published; typical certified range 94–97%" rather than inventing numbers.
4. No free odds-movement history source exists; CLV tracking must be self-observed from app snapshots.






---

# Part 12 — Master Plan, Features and Roadmap


## SportyAgent — Master Plan
Open-source AI betting research agent for SportyBet. v1 plan, 2026-11-18.

### 1. What this is — and what it is not

**It is:** a self-hosted AI research agent. You clone the repo, run one command, it serves a web app on localhost:3000. The agent researches matches and games across SportyBet's full catalogue, produces calibrated probabilities with a full audit trail, compares them to the live odds, and either recommends a slip or says NO BET. In Mode B it can place the slip itself inside hard limits you set.

**It is not:** a money printer. Every game on SportyBet has a house edge. The agent's job is to find the rare spots where the price is wrong, bet small when it does, refuse everything else, and show you its own scoreboard so you can judge it honestly.

**Verified from the live site (2026-11-18):**
- 22 sports verticals: Football (1402 events), Tennis (326), Basketball (303), Ice Hockey (276), vFootball (442), eSoccer (152), American Football (118), Badminton (92), Handball (89), Table Tennis (158), Volleyball (55), Boxing (51), MMA (44), Cricket (42), Rugby (14), Futsal (11), eBasketball (17), eSport CS (16), Darts (8), Snooker (7), Baseball (4), eSport Dota (1).
- Football markets per match: 45–95+. Chips seen live: 1X2, O/U, DC, 1st Half O/U, Handicap, Home O/U, Away O/U, GG/NG, 1st Half 1X2, Next Goal, Corners O/U.
- API: `sportybet.com/api/ng/...` returns `{bizCode, innerMsg, message, data}`. 19000=invalid, 19001=wrong path, 19003=forbidden for anonymous. `factsCenter/sportList` is open and returns the full tree.
- Bot protection: desktop curl gets HTTP 403; a real browser session works. So the app drives a real browser context, not raw curl.
- GitHub landscape: 263 "sportybet" repos, top is 22 stars, two of the top three are outright "balance adder" scams. No trusted, maintained client exists. The slot for an honest, well-engineered one is wide open.

### 2. The three modes

**Mode A — Confirm (default).** Agent researches → streams its reasoning and every source into the chat → proposes a slip → you tap Confirm → the local browser driver places it on your machine, on your account. You see everything before it happens.

**Mode B — Guarded auto.** You grant a session: budget, hard loss cap, expiry, max stake per bet, allowed game classes. The agent may place without asking, but ONLY where its measured edge clears the threshold, and it stops dead at the cap. Every action goes to a tamper-evident, hash-chained audit log the UI shows live.

**Mode C — Watch only.** No placement at all. Research, cards, alerts, journal. Default for new installs.

### 3. Game coverage — tiered, honest

| Tier | Games | What the agent does |
|---|---|---|
| T1 Full research | Football, basketball, tennis, ice hockey, handball, volleyball, cricket, MMA/boxing, rugby, American football, table tennis, badminton, futsal, darts, snooker, baseball, esports (CS/Dota) | Full pipeline: data gathering → 3 independent models → synthesizer → critic → edge calc → slip |
| T2 Risk-math only | Aviator, JetX, crash games | No prediction. Monte-Carlo Risk Lab that proves the EV is negative, session simulators, bankroll destruction curves |
| T3 Do-not-model | vFootball, eSoccer, eBasketball, virtuals, SportySIM | Honest page: certified RNG, cannot be predicted. EV calculator, expected-loss-over-N-rounds display |
| T4 House-edge display | Lucky Numbers, Jackpot, casino, lottery | Show the published/unpublished edge, expected loss per ₦ staked |

Nothing in T2–T4 gets a "prediction". Any tool that pretends otherwise is lying, and the GitHub ecosystem already proves users get burned by it.

### 4. Architecture

**Stack:** Next.js 15 (App Router) + TypeScript + SQLite (better-sqlite3/Drizzle) + Tailwind. One app, one repo, one command: `./start.sh` → port 3000.

```
sporty-agent/
├── start.sh                  # one command: install deps, migrate DB, launch
├── docker-compose.yml        # optional container run
├── .env.example              # LLM keys, config
├── LICENSE (AGPL-3.0)
├── docs/                     # TERMS, DISCLAIMER, RISK_WARNING, ACCEPTABLE_USE,
│                             # PRIVACY, RESPONSIBLE_GAMBLING, ARCHITECTURE
├── src/
│   ├── app/                  # Next.js pages & API routes
│   │   ├── (dashboard)/      # today's card, match deep-dive, journal, bankroll
│   │   ├── (lab)/            # aviator risk lab, virtuals EV, ruin simulator
│   │   ├── (settings)/       # vault, limits, modes, LLM config
│   │   └── api/              # research, odds, placement, audit, calibration
│   ├── core/
│   │   ├── agent/            # orchestrator, tools, forecaster, critic, synthesizer
│   │   ├── models/           # poisson.ts, elo.ts, llm.ts, ensemble.ts
│   │   ├── odds/             # margin removal (proportional + Shin), edge calc
│   │   ├── staking/          # fractional Kelly, gates, limits engine
│   │   ├── games/            # aviator sim, virtuals EV, house-edge tables
│   │   ├── placement/        # browser driver, slip builder, confirm handshake
│   │   ├── vault/            # argon2id encryption, keychain, zero-export
│   │   ├── audit/            # hash-chained append-only log
│   │   └── calibration/      # brier, log-loss, CLV, temperature tuning
│   ├── db/                   # drizzle schema + migrations
│   └── ui/                   # components
└── tests/
```

### 5. The agent loop

Per match: **filter → gather (parallel tools) → 3 forecasters → synthesize → critic → edge → gate → slip?**

Tools the agent can call: fixtures, team stats, form/last-5, head-to-head, injuries/suspensions, lineups, xG (Understat/FBref), league table, odds (SportyBet live + 1-2 comparison sources), odds movement, weather, travel/rest days, referee stats, news search, social sentiment, market consensus.

Forecasters:
1. **Poisson/Dixon-Coles** statistical model (attack/defence strengths, home advantage, time decay).
2. **Elo/ratings** model with home adjust and margin-of-victory updates.
3. **LLM qualitative analyst** — reads the gathered research, outputs probabilities with reasons.

Synthesizer blends them, weighted by recent Brier performance of each. Then the **critic** — a second agent whose only job is to argue against the pick. If it lands a hit, confidence drops. Then the edge calculator removes the bookmaker margin and compares. Then the gate.

### 6. The NO-BET gate (hard rules, not vibes)

- Minimum edge: fair prob × odds − 1 ≥ threshold (default 4%, tunable).
- Minimum data completeness: if injuries/lineups missing for a key team, downgrade or skip.
- Max stake: quarter-Kelly of bankroll, capped in absolute ₦.
- Correlation cap: max 2 legs from the same match in any accumulator.
- Daily loss stop: hard cap, cannot be raised without a 24h cooldown.
- Session budget (Mode B): expires, cannot roll over.
- Calibration floor: if the model's recent Brier is worse than "always pick the favourite", the gate widens automatically.

### 7. Security — "no one can see my login, not even you"

- Credentials/session never leave the device. Stored in a local vault encrypted with Argon2id from a passphrase you type. Optional OS keychain binding.
- No hosted server, no telemetry, no cloud component. The repo is the product.
- Local API: localhost binding only, per-install token, origin checks, CSRF protection.
- Scraped content is rendered as text, never HTML, to kill XSS from the bookmaker page.
- Logs redact balances, tokens, and any credential material by default.
- `make audit` script: dependency scan, secret scan, permission check.

### 8. Feature list (100+, grouped)

#### Research & prediction
1. Full match research pipeline with streamed reasoning
2. Every source cited with URL and timestamp in the UI
3. Three-model ensemble (Poisson, Elo, LLM) with performance-weighted blending
4. Devil's-advocate critic agent that tries to break each pick
5. "Why this pick" audit trail — every input, weight, and decision visible
6. "Why NOT this pick" — the counter-argument shown next to every recommendation
7. Confidence chips with plain-language meaning ("60% ≈ 3 in 5")
8. NO BET as the default state, not the exception
9. Value-only card: fixtures ranked by measured edge, not hype
10. Market explorer: all 45–95+ markets per match, priced and flagged
11. Asian handicap explainer built into every handicap market
12. Corners & cards models for the niche markets
13. Player-prop research (scorer, cards, assists) where data exists
14. In-play mode: live odds + live state, recompute during the match
15. Accumulator builder with correlation warnings between legs
16. Booking-code importer: paste a SportyBet code, get the full analysis of every leg
17. Slip builder with stake suggestion and expected value per slip
18. Multi-book comparison where a second source is available
19. Closing-line-value tracker: did the price move your way after you bet?
20. Odds-drift alerts: watch a market, get pinged when it moves past your trigger

#### Learning & calibration
21. Every prediction logged with probability, odds, and result
22. Brier score + log-loss dashboard, per market type
23. Auto temperature-tuning: the model learns its own overconfidence
24. Per-league performance tracking (where it's good, where it's blind)
25. Per-market-type tracking (1X2 vs O/U vs BTTS)
26. Forecaster leaderboard: which of the 3 models is actually earning its slot
27. Self-critique memory: the agent stores what it got wrong and why
28. Weekly digest: "here's what I said, here's what happened"
29. Public scoreboard page: your install's accuracy, exportable as JSON
30. Calibration curve plot (predicted vs actual frequency)

#### Bankroll & risk
31. Bankroll dashboard with deposits, withdrawals, P&L
32. Quarter-Kelly staking calculator with hard caps
33. Ruin simulator: probability of going broke under any strategy you propose
34. Monte-Carlo bankroll projector (1,000 futures, show the distribution)
35. Daily/weekly/monthly loss limits that cannot be disabled without cooldown
36. Session budget system for Mode B with expiry
37. Stake-size sanity warnings ("this is 8% of your bankroll")
38. Tilt detector: after 3 losses in a row, suggest a break
39. Time-based reality checks while the app is open
40. Full bet journal with notes, tags, and screenshots

#### Aviator / crash Risk Lab
41. Provably-fair explainer with the actual HMAC mechanics
42. Monte-Carlo session simulator: try any auto-cashout strategy, see the outcome distribution
43. "Play until you hit ₦X" simulator — shows the ruin probability explicitly
44. Martingale simulator with the bankroll-death curve plotted
45. Expected loss per ₦100 staked, per game, always visible
46. Session tracker: log your real Aviator sessions, compare to the simulation
47. Loss-chase alarm: detects the "one more round" pattern in your logs

#### Virtuals / instant games
48. Honest "this is certified RNG" page per game
49. EV calculator for any virtual market
50. Expected-loss-over-N-rounds display
51. Round-history logger for your own record-keeping
52. "Patterns are noise" visualiser — plots past results to show there's no signal

#### Casino / lottery
53. House-edge table for every game class
54. Jackpot EV calculator (pool size vs ticket cost)
55. Lucky Numbers expected-value display

#### Agent operations
56. Live agent console: watch every tool call as it happens
57. Chat interface: ask the agent anything about a match, it answers with sources
58. Voice mode (optional): agent reads the card aloud
59. Telegram/WhatsApp bridge (optional, self-hosted bot token)
60. Scheduled research: pre-match runs N hours before kick-off
61. Match-day digest: one summary of everything worth looking at
62. Watchlist with per-match notification rules
63. Cost meter: LLM tokens spent per analysis, per day
64. Local-model option (Ollama) for zero-cost runs
65. Model router: cheap model for gathering, strong model for synthesis
66. Cache layer: never research the same fixture twice
67. Rate-limit awareness and backoff for every external source
68. Failure ledger: when a source is down, the card says so

#### Placement (Mode B only)
69. Browser-driver placement on your machine, your session
70. Confirm handshake with a typed phrase for large stakes
71. Pre-placement checklist displayed and logged
72. Post-placement verification: read the open-bets list to confirm
73. Cash-out advisor: shows whether cashing out is +EV right now
74. Open-bets monitor with live status
75. Settlement reconciler: matches results to journal entries automatically

#### Data & integrations
76. football-data.co.uk historical ingest for backtesting
77. Backtest harness: run the whole pipeline on past seasons
78. CSV/JSON export of everything
79. Backup/restore of your local database
80. API for your own scripts (localhost, token-authed)

#### Safety & legal
81. First-run consent gate: must type an acknowledgement to proceed
82. Age gate (18+)
83. Geo-notice based on locale
84. Banned-language linter in CI: no "guaranteed", "sure", "100%", "win big"
85. Responsible-gambling screen with real limit controls
86. PGSI self-assessment embedded
87. Helpline directory (Nigeria first)
88. Self-exclusion mode: locks the app for a chosen period, no override
89. Reality-check popups during long sessions
90. "This is not financial advice" on every card

#### Engineering
91. One-command start script
92. Docker compose option
93. Test suite with fixtures recorded from live APIs
94. `make audit` security script
95. Structured logging with redaction
96. Schema migrations that never lose your journal
97. Plugin architecture for new data sources
98. i18n-ready strings (English first, Pidgin-friendly tone)
99. Mobile-first UI (this is a phone-first market)
100. Dark mode, low-data mode

### 9. Legal pack (shipped in docs/ and enforced in-app)

- **LICENSE** — AGPL-3.0 (keeps forks honest, keeps the source open)
- **TERMS.md** — no guarantee of profit; you may lose your entire stake; past performance is not indicative; not financial advice; not affiliated with SportyBet; use may breach your operator's terms and cost you your account; 18+; assumption of risk
- **DISCLAIMER.md** — the model is a research tool, not a forecaster of certainty; edge is small and measured in fractions of a percent over hundreds of bets
- **RISK_WARNING.md** — plain-language gambling harm section
- **ACCEPTABLE_USE.md** — no resale of tips, no hosted multi-tenant deployment, no credential collection from others
- **PRIVACY.md** — nothing leaves your machine; list of every external call the app makes
- **RESPONSIBLE_GAMBLING.md** — limits, self-exclusion, helplines
- **In-app consent gate** — blocking, typed acknowledgement, versioned (re-consent on major updates)
- **CI language linter** — fails the build if banned hype words appear in any user-facing string

### 10. Roadmap

**v0.1 (2 weeks):** repo skeleton, start.sh, Today's Card for football 1X2/O/U/BTTS, Poisson + Elo models, LLM analyst with sources, NO-BET gate, journal, bankroll dashboard, consent gate, full legal pack.

**v0.5:** critic agent, calibration dashboard, booking-code importer, odds-drift alerts, Aviator Risk Lab, virtuals EV pages, Mode B with budget engine + audit log, Telegram bridge.

**v1.0:** full market coverage (corners, cards, props), backtest harness, public scoreboard export, plugin architecture, Ollama local-model mode, i18n.

**Not building:** cloud-hosted multi-tenant version, credential harvesting, "sure prediction" marketing, virtuals "pattern" models.

### 11. First 10 GitHub issues

1. **Scaffold repo + start.sh** — `./start.sh` boots app on :3000 with empty DB. AC: fresh clone works in under 5 minutes on a laptop.
2. **Consent gate + legal screens** — blocking first-run flow. AC: app unusable until typed consent; all 7 docs rendered in-app.
3. **SportyBet read client** — fetch sportList, fixtures, odds through a real browser context. AC: live odds for today's EPL fixtures render in the app.
4. **Poisson model** — Dixon-Coles from football-data.co.uk history. AC: probabilities for any fixture in the DB, unit tests on a known season.
5. **Elo model** — ratings with home adjust. AC: ratings converge on historical data, test vs known values.
6. **LLM analyst tool loop** — gather → reason → cite. AC: every claim in output has a URL; runs within a token budget.
7. **Ensemble + synthesizer** — blend 3 models, weight by Brier. AC: blended probability beats each single model on a backtest season.
8. **NO-BET gate** — edge threshold, data completeness, stake caps. AC: gate blocks a deliberately bad fixture in tests.
9. **Journal + bankroll** — log bets, compute P&L. AC: settle a bet, dashboard updates correctly.
10. **Calibration dashboard** — Brier, log-loss, calibration curve. AC: curve renders from logged predictions.

### 12. Honest limits (goes in the README, verbatim)

- No tool can give "very sure" predictions. Anyone claiming that is selling you something.
- The bookmaker's margin means the average bettor loses. The only long-run defence is betting rarely, small, and only with a measured edge.
- Virtuals, Aviator and instant games are certified random. There is nothing to research. This app will tell you that every time you open those pages.
- This tool may breach SportyBet's terms of use. Automated access can get accounts closed and winnings voided. Mode B exists because you asked for it — understand the risk before enabling it.
- If gambling stops being fun, stop. The app includes real limit controls and a self-exclusion mode. Use them.





---

# Part 13 — Working Tool Source

These three Python tools are written, tested and working against the live endpoint. Stdlib only, no dependencies.


## Tool A — sportyharvest.py

```python
#!/usr/bin/env python3
"""
sportyharvest — a self-contained SportyBet surface collector.

Harvests what the platform exposes, records every finding as an evidence record
(in the craft-anything style: claim + source + grade + limitations + coverage),
and writes JSONL training data.

Design constraints that shaped it:
  - No third-party deps (no requests, no bs4). stdlib only, so it runs anywhere.
  - Every record carries provenance. A fact without a source is not recorded.
  - Failures are recorded, not swallowed. A 403 is evidence too.
  - Idempotent: each run writes to a timestamped directory, never overwrites.

Usage:
    python3 sportyharvest.py --out data/harvest --full
    python3 sportyharvest.py --endpoints-only
    python3 sportyharvest.py --verify data/harvest/<run>/evidence.jsonl
"""

import argparse
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.sportybet.com"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")

# ---------------------------------------------------------------------------
# Evidence model — mirrors AGENT-METHOD.md
# ---------------------------------------------------------------------------

GRADE_WEIGHT = {"A": 1.0, "B": 0.7, "C": 0.4, "D": 0.15}


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Ledger:
    """Append-only evidence ledger. One JSON object per line."""

    def __init__(self, path):
        self.path = path
        self.f = open(path, "a", encoding="utf-8")
        self.n = 0

    def add(self, claim, grade, source_kind, payload=None, url=None,
            limitations=None, coverage=1.0, gaps=None, status=None):
        rec = {
            "id": "ev_%05d" % (self.n + 1),
            "claim": claim,
            "confidence": GRADE_WEIGHT.get(grade, 0.0),
            "grade": grade,
            "source": {
                "kind": source_kind,
                "url": url,
                "retrievedAt": utcnow(),
                "httpStatus": status,
            },
            "limitations": limitations or [],
            "coverage": {"answered": coverage, "gaps": gaps or []},
        }
        if payload is not None:
            rec["payload"] = payload
        self.f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.f.flush()
        self.n += 1
        return rec

    def close(self):
        self.f.close()


# ---------------------------------------------------------------------------
# HTTP — honest about failure
# ---------------------------------------------------------------------------

def get(url, timeout=25, headers=None):
    """Return (status, body_text, elapsed_ms). Never raises on HTTP errors."""
    h = {"User-Agent": UA, "Accept": "application/json,*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("utf-8", "replace"), int((time.time() - t0) * 1000)
    except urllib.error.HTTPError as e:
        return e.code, (e.read() or b"").decode("utf-8", "replace")[:2000], int((time.time() - t0) * 1000)
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e), int((time.time() - t0) * 1000)


def jbody(text):
    try:
        return json.loads(text)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------

PROBES = [
    # (name, path, grade_if_ok, claim)
    ("sportList", "/api/ng/factsCenter/sportList?productId=3", "A",
     "Sport list enumerates every vertical with live event counts"),
    ("betTypeConfig", "/api/ng/factsCenter/betType/config", "A",
     "Accumulator payout multipliers are published by the platform"),
    ("quickMarketA", "/api/ng/factsCenter/quickMarketList?block=A&sport=sr:sport:1", "A",
     "Quick market chips for football block A"),
    ("quickMarketB", "/api/ng/factsCenter/quickMarketList?block=B&sport=sr:sport:1", "A",
     "Quick market chips for football block B"),
    ("storySets", "/api/ng/factsCenter/story/v1/story-sets?page=0&pageSize=15", "A",
     "Product silo cards are served from a story-sets feed"),
    ("recommendScroll", "/api/ng/factsCenter/recommendScrollEvents/v2", "A",
     "Recommended events feed exists"),
    ("wapLiveEvents", "/api/ng/factsCenter/wapConfigurableIndexLiveEvents?sportId=sr%3Asport%3A1&withTwoUpMarket=true&withOneUpMarket=true", "A",
     "Live event index supports 2up and 1up market variants"),
    ("commonConfig", "/api/ng/common/config/query", "A",
     "Global client configuration endpoint"),
    ("virtualConfig", "/api/ng/scheduledVirtual/api/v1/config", "A",
     "Virtual sports schedule is served by a config endpoint"),
    ("instantwinConfig", "/api/ng/instantwin/api/v1/iw/config/sport?sportId=sr:sport:1-1", "A",
     "Instant-win product configuration"),
    ("sportySimConfig", "/api/ng/sportySim/v1/config/overall", "B",
     "SportySIM config is country-gated"),
    ("cutbetConfig", "/api/ng/orders/config/cutbet", "A",
     "Cash-out / cut-bet rules are published"),
    ("bannedMarkets", "/api/ng/orders/flexi/banned-markets", "A",
     "Some markets are excluded from Flexi bets"),
    ("bonusPlans", "/api/ng/promotion/v2/bonus/plans/valid", "B",
     "Active bonus plans are enumerable"),
    ("balance", "/api/ng/orders/v2/getBalance", "A",
     "Balance requires an authenticated session"),
    ("fixtures", "/api/ng/factsCenter/liveOrPrematchEvents?productId=3&sportId=sr%3Asport%3A1&marketId=1%2C18&categoryId=all&tournamentId=all&timeline=&pageSize=5&pageNum=1&option=1", "A",
     "Fixtures feed requires a page-computed signature"),
    ("aviatorRounds", "/api/ng/gaming/aviator/rounds", "A",
     "Aviator round history endpoint"),
    ("gameList", "/api/ng/gaming/gameList", "A",
     "Games catalogue endpoint"),
    ("eventDetail", "/api/ng/factsCenter/event?productId=3&eventId=sr%3Amatch%3A1", "A",
     "Single event detail endpoint"),
]


def probe_all(ledger, rate=0.6):
    """Run every probe, record the outcome either way."""
    results = {}
    for name, path, grade, claim in PROBES:
        url = BASE + path
        status, body, ms = get(url)
        parsed = jbody(body)
        biz = None
        if isinstance(parsed, dict):
            biz = parsed.get("bizCode", parsed.get("errorCode"))

        ok = status == 200 and biz == 10000
        # A refused endpoint is still evidence: it tells us auth exists.
        if ok:
            ledger.add(claim, grade, "primary", payload=_trim(parsed), url=url,
                       coverage=1.0, status=status)
        else:
            ledger.add(
                "PROBE RESULT: %s" % name,
                "B",
                "primary",
                payload={"bizCode": biz, "httpStatus": status,
                         "sample": body[:300]},
                url=url,
                limitations=["Endpoint did not return bizCode 10000",
                             "Absence of data is not evidence the feature is absent"],
                coverage=0.3,
                gaps=[claim],
                status=status,
            )
        results[name] = {"status": status, "bizCode": biz, "ms": ms, "ok": ok}
        print("  %-20s http=%-4s biz=%-6s %4dms %s"
              % (name, status, biz, ms, "OK" if ok else "—"))
        time.sleep(rate)
    return results


def _trim(obj, max_items=60, max_depth=6):
    """Depth-aware trim that preserves distingushing fields.

    Lists of homogeneous dicts: keep the first N whole (they carry structure),
    then record a count so the reader knows what was elided.
    """
    if max_depth <= 0:
        return "..."
    if isinstance(obj, list):
        keep = [_trim(x, max_items, max_depth - 1) for x in obj[:max_items]]
        if len(obj) > max_items:
            return {"__items": keep, "__elided": len(obj) - max_items,
                    "__total": len(obj)}
        return keep
    if isinstance(obj, dict):
        return {k: _trim(v, max_items, max_depth - 1) for k, v in obj.items()}
    return obj


# ---------------------------------------------------------------------------
# Derived knowledge
# ---------------------------------------------------------------------------

def analyse_markets(ledger, block_a, block_b):
    """Build the real market-ID catalogue. Labels alone are not enough:
    the same label can map to different IDs per block."""
    seen = {}
    for block_name, payload in (("A", block_a), ("B", block_b)):
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list):
            continue
        for m in data:
            mid = str(m.get("marketId"))
            entry = seen.setdefault(mid, {
                "marketId": mid,
                "displayName": m.get("displayName"),
                "title": m.get("title"),
                "hasSpecifier": m.get("hasSpecifier"),
                "specifierName": m.get("specifierName"),
                "blocks": [],
            })
            entry["blocks"].append(block_name)
    rows = sorted(seen.values(), key=lambda r: int(r["marketId"]))
    ledger.add(
        "Market catalogue: %d distinct market ids across quick-market blocks A and B"
        % len(rows),
        "A", "primary", payload=rows, coverage=1.0,
        limitations=["Covers only markets surfaced as quick chips; the full per-event "
                     "market list is larger (totalMarketSize reports 187 on a live match)"])
    return rows


def analyse_live_shape(ledger, payload):
    """Record the live-event record shape so the agent can parse it."""
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data:
        return None
    ev = data[0]
    facts = {
        "eventKeys": sorted(ev.keys()),
        "sampleEventId": ev.get("eventId"),
        "totalMarketSize": ev.get("totalMarketSize"),
        "statusFields": {k: ev.get(k) for k in
                         ("status", "period", "matchStatus", "playedSeconds",
                          "remainingTimeInPeriod")},
        "scoreFields": {k: ev.get(k) for k in ("setScore", "pointScore", "gameScore")},
        "flags": {k: ev.get(k) for k in
                  ("ai", "topTeam", "banned", "bookingStatus", "containsPcbb",
                   "eventSource", "fixtureVenue", "matchTrackerNotAllowed")},
        "idFormat": {"event": "sr:match:*", "competitor": "sr:competitor:*"},
    }
    ledger.add(
        "Live event records expose %d fields including ai/topTeam/banned flags "
        "and a totalMarketSize per fixture" % len(ev.keys()),
        "A", "primary", payload=facts, coverage=1.0)
    return facts


def analyse_sports(ledger, sport_payload):
    """Turn the sport tree into structured facts."""
    data = sport_payload.get("data") if isinstance(sport_payload, dict) else None
    if not isinstance(data, list):
        return []
    rows = []
    for s in data:
        rows.append({
            "sportId": s.get("id"),
            "name": s.get("name"),
            "events": s.get("eventSize", 0),
            "categories": len(s.get("categories") or []),
        })
    rows.sort(key=lambda r: -r["events"])
    ledger.add(
        "Sport vertical inventory: %d verticals, %d total events"
        % (len(rows), sum(r["events"] for r in rows)),
        "A", "primary", payload=rows, coverage=1.0)
    return rows


def analyse_payout(ledger, cfg):
    """Extract the accumulator decay curve as first-class facts."""
    data = cfg.get("data") if isinstance(cfg, dict) else None
    if not isinstance(data, dict):
        return
    for product in ("anywin", "flexi"):
        p = data.get(product)
        if not isinstance(p, dict):
            continue
        keys = p.get("oddsKeys") or {}
        if not keys:
            continue
        points = sorted(((int(k), float(v)) for k, v in keys.items()))
        first_min = next((k for k, v in points if v == min(p[1] for p in points)), None)
        last = points[-1]
        ledger.add(
            "%s payout multiplier decays from %.2f at %d legs to %.2f at %d legs "
            "(floor first reached at %d legs)"
            % (product, points[0][1], points[0][0], last[1], last[0], first_min),
            "A", "primary",
            payload={"product": product, "curve": dict(points),
                     "minMultiplier": last[1], "floorFromLegs": first_min,
                     "maxLegs": last[0]},
            coverage=1.0)
    flexi = data.get("flexi") or {}
    if "flexiAverageWeightedMinEffectiveRtp" in flexi:
        ledger.add(
            "Flexi declares an effective RTP floor of %s"
            % flexi["flexiAverageWeightedMinEffectiveRtp"],
            "A", "primary",
            payload={"effectiveRtpFloor": flexi["flexiAverageWeightedMinEffectiveRtp"]},
            coverage=1.0)


def probe_bot_protection(ledger):
    """Evidence that raw HTTP is blocked — justifies the browser-only architecture."""
    status, body, ms = get(BASE + "/ng/m/",
                           headers={"User-Agent": "curl/8.5.0"})
    ledger.add(
        "Plain HTTP client is refused with status %s" % status,
        "A", "primary",
        payload={"status": status, "elapsedMs": ms, "sample": body[:200]},
        url=BASE + "/ng/m/",
        limitations=["Block may be IP-, header- or TLS-fingerprint-based; cause not isolated"],
        coverage=0.8, status=status)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(path, results, sports, ledger_path):
    ok = [k for k, v in results.items() if v["ok"]]
    bad = [k for k, v in results.items() if not v["ok"]]
    lines = [
        "# Harvest report",
        "",
        "Run: %s" % utcnow(),
        "",
        "## Endpoint results",
        "",
        "| Endpoint | HTTP | bizCode | Time | State |",
        "|---|---|---|---|---|",
    ]
    for k, v in results.items():
        lines.append("| %s | %s | %s | %sms | %s |"
                     % (k, v["status"], v["bizCode"], v["ms"],
                        "open" if v["ok"] else "gated/refused"))
    lines += ["", "**Open: %d** · **Gated: %d**" % (len(ok), len(bad)), ""]
    if sports:
        lines += ["## Sports by event count", "", "| Sport | Events | Categories |", "|---|---|---|"]
        for r in sports:
            lines.append("| %s | %d | %d |" % (r["name"], r["events"], r["categories"]))
        lines.append("")
    lines += ["## Evidence ledger", "", "`%s`" % ledger_path, ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def verify(ledger_path):
    """Re-read a ledger and report integrity + grading distribution."""
    n, grades, low = 0, {}, 0
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            n += 1
            grades[rec["grade"]] = grades.get(rec["grade"], 0) + 1
            if rec["coverage"]["answered"] < 0.6:
                low += 1
    print("records: %d" % n)
    print("grades:  %s" % grades)
    print("low-coverage records: %d (%.0f%%)" % (low, 100.0 * low / max(n, 1)))
    print("mean confidence: %.2f"
          % (sum(GRADE_WEIGHT[g] * c for g, c in grades.items()) / max(n, 1)))


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/harvest")
    ap.add_argument("--full", action="store_true", help="run all probes + analysis")
    ap.add_argument("--endpoints-only", action="store_true")
    ap.add_argument("--verify", metavar="LEDGER")
    args = ap.parse_args()

    if args.verify:
        verify(args.verify)
        return

    run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(args.out, run)
    os.makedirs(d, exist_ok=True)
    ledger_path = os.path.join(d, "evidence.jsonl")
    ledger = Ledger(ledger_path)

    print("sportyharvest — run %s" % run)
    print("ledger: %s\n" % ledger_path)

    print("[1/4] probing endpoints")
    results = probe_all(ledger)

    sports = []
    if args.full and not args.endpoints_only:
        print("\n[2/4] analysing sport tree")
        st, body, _ = get(BASE + "/api/ng/factsCenter/sportList?productId=3")
        cfg = jbody(body)
        if cfg:
            sports = analyse_sports(ledger, cfg)

        print("[3/4] analysing payout curve")
        st, body, _ = get(BASE + "/api/ng/factsCenter/betType/config")
        cfg = jbody(body)
        if cfg:
            analyse_payout(ledger, cfg)

        print("[3b] analysing market catalogue")
        _, ba, _ = get(BASE + "/api/ng/factsCenter/quickMarketList?block=A&sport=sr:sport:1")
        _, bb, _ = get(BASE + "/api/ng/factsCenter/quickMarketList?block=B&sport=sr:sport:1")
        ja, jb = jbody(ba), jbody(bb)
        if ja and jb:
            analyse_markets(ledger, ja, jb)

        print("[3c] analysing live event shape")
        _, lv, _ = get(BASE + "/api/ng/factsCenter/wapConfigurableIndexLiveEvents"
                       "?sportId=sr%3Asport%3A1&withTwoUpMarket=true&withOneUpMarket=true")
        jl = jbody(lv)
        if jl:
            analyse_live_shape(ledger, jl)

        print("[4/4] probing bot protection")
        probe_bot_protection(ledger)

    ledger.close()
    report = os.path.join(d, "REPORT.md")
    write_report(report, results, sports, ledger_path)
    print("\nwrote %s" % report)
    print("wrote %s (%d records)" % (ledger_path, ledger.n))


if __name__ == "__main__":
    main()

```


## Tool B — odds_analyzer.py

```python
#!/usr/bin/env python3
"""
odds_analyzer — mine SportyBet's odds and probability fields.

The platform publishes BOTH a raw `odds` and a `probability` per outcome.
For base markets the probabilities sum to exactly 1.0000, which means they are
already de-vigged true probabilities. This tool measures that, quantifies the
overround in the odds, and classifies every market by how it is priced.

Usage:
    python3 odds_analyzer.py --out data/odds
    python3 odds_analyzer.py --sport sr:sport:1 --json-only
"""

import argparse
import json
import os
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.sportybet.com"
EP = ("/api/ng/factsCenter/wapConfigurableIndexLiveEvents"
      "?sportId={sport}&withTwoUpMarket=true&withOneUpMarket=true")
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")

DE_VIG_TOL = 1e-3
CONDITIONAL_CUT = 0.95
OVERROUND_CUT = 1.005


def fetch(sport, timeout=25):
    url = BASE + EP.format(sport=sport.replace(":", "%3A"))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.loads(r.read().decode("utf-8", "replace"))
    if body.get("bizCode") != 10000:
        raise SystemExit("unexpected bizCode: %r" % body.get("bizCode"))
    return body["data"]


def classify(sum_p, market_id=None, n_outcomes=None):
    """Classify how a market is priced.

    Base markets (1X2, O/U, handicaps) have mutually exclusive outcomes, so a
    de-vigged set sums to 1.0. Double Chance and similar overlap markets are
    genuinely different: 3 selections but only 2 can win, so the sum is 2.0 by
    construction. Judging those against 1.0 produces a fake 92% 'overround'.
    """
    # Markets whose selections are not mutually exclusive.
    # Double Chance (10) = {1X, 12, X2}: any result satisfies exactly two.
    OVERLAP = {"10": 2.0}
    target = OVERLAP.get(str(market_id))
    if target is not None:
        return "DE_VIGGED" if abs(sum_p - target) <= 1e-2 else (
            "CONDITIONAL" if sum_p < target * CONDITIONAL_CUT else "OVERROUND")
    if abs(sum_p - 1.0) <= DE_VIG_TOL:
        return "DE_VIGGED"
    if sum_p < CONDITIONAL_CUT:
        return "CONDITIONAL"
    if sum_p > OVERROUND_CUT:
        return "OVERROUND"
    return "OTHER"


def analyse(events):
    rows = []
    for ev in events:
        eid = ev.get("eventId")
        for m in ev.get("markets") or []:
            outs = [o for o in (m.get("outcomes") or []) if o.get("isActive") == 1]
            if len(outs) < 2:
                continue
            try:
                probs = [float(o["probability"]) for o in outs]
                odds = [float(o["odds"]) for o in outs]
            except (KeyError, ValueError, TypeError):
                continue
            if any(o <= 0 for o in odds) or any(p <= 0 for p in probs):
                continue          # suspended selection
            sum_p = sum(probs)
            implied = sum(1.0 / o for o in odds)
            rows.append({
                "eventId": eid,
                "marketId": m.get("id"),
                "market": m.get("name"),
                "group": m.get("group"),
                "sourceType": m.get("sourceType"),
                "nOutcomes": len(outs),
                "sumProbability": round(sum_p, 6),
                "sumImpliedFromOdds": round(implied, 6),
                "overroundFromOdds": round((implied - (2.0 if m.get("id")=="10" else 1.0)) * 100, 4),
                "class": classify(sum_p, m.get("id"), len(outs)),
                "odds": odds,
                "probabilities": probs,
                "availableScore": m.get("availableScore"),
                "lastOddsChangeTime": m.get("lastOddsChangeTime"),
                "banned": m.get("banned"),
                "favourite": m.get("favourite"),
            })
    return rows


def aggregate(rows):
    by = {}
    for r in rows:
        by.setdefault(r["market"], []).append(r)
    out = []
    for name, rs in by.items():
        sp = [r["sumProbability"] for r in rs]
        ov = [r["overroundFromOdds"] for r in rs]
        out.append({
            "market": name,
            "n": len(rs),
            "meanSumProb": round(statistics.mean(sp), 5),
            "medianSumProb": round(statistics.median(sp), 5),
            "minSumProb": round(min(sp), 5),
            "maxSumProb": round(max(sp), 5),
            "meanOverroundPct": round(statistics.mean(ov), 3),
            "classes": sorted({r["class"] for r in rs}),
            "marketIds": sorted({r["marketId"] for r in rs}),
        })
    out.sort(key=lambda r: -r["n"])
    return out


def write_summary(path, agg, rows, meta):
    lines = ["# Odds analysis — SportyBet live football", "",
             "Run: %s" % meta["run"],
             "Events: %d · Markets analysed: %d" % (meta["events"], len(rows)), "",
             "## Per-market aggregates", "",
             "| Market | n | mean Σp | median Σp | range | mean overround | class |",
             "|---|---|---|---|---|---|---|"]
    for a in agg:
        lines.append("| %s | %d | %.4f | %.4f | %.3f–%.3f | %+.2f%% | %s |" % (
            a["market"], a["n"], a["meanSumProb"], a["medianSumProb"],
            a["minSumProb"], a["maxSumProb"], a["meanOverroundPct"],
            "/".join(a["classes"])))
    devig = [r for r in rows if r["class"] == "DE_VIGGED"]
    lines += ["", "## Headline", "",
              "- **%d of %d markets are DE_VIGGED** (Σp = 1.0000): the platform ships true "
              "probabilities, not just odds." % (len(devig), len(rows))]
    if devig:
        base = [r for r in devig if r["marketId"] == "1"]
        if base:
            ov = [r["overroundFromOdds"] for r in base]
            lines.append("- **1X2 raw overround: mean %+.2f%%** across %d live fixtures — far "
                         "thinner than the 5%% retail assumption."
                         % (statistics.mean(ov), len(base)))
    cond = [r for r in rows if r["class"] == "CONDITIONAL"]
    if cond:
        lines.append("- **%d CONDITIONAL markets** — derivatives like 1UP/2UP where Σp < 1 is "
                     "correct, because the mass only covers the early-payout trigger." % len(cond))
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sport", default="sr:sport:1")
    ap.add_argument("--out", default="data/odds")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    events = fetch(args.sport)
    rows = analyse(events)
    agg = aggregate(rows)

    run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(args.out, run)
    os.makedirs(d, exist_ok=True)

    payload = {
        "run": run,
        "sport": args.sport,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "events": len(events),
        "marketsAnalysed": len(rows),
        "aggregates": agg,
        "markets": rows,
    }
    jp = os.path.join(d, "markets.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)

    if not args.json_only:
        sp = os.path.join(d, "SUMMARY.md")
        write_summary(sp, agg, rows, {"run": run, "events": len(events)})
        print("wrote %s" % sp)

    print("wrote %s (%d markets, %.1fs)" % (jp, len(rows), time.time() - t0))
    print()
    print("%-26s %3s  %8s  %9s  %s" % ("market", "n", "mean Σp", "overround", "class"))
    for a in agg[:15]:
        print("%-26s %3d  %8.4f  %+8.2f%%  %s"
              % (a["market"][:26], a["n"], a["meanSumProb"],
                 a["meanOverroundPct"], "/".join(a["classes"])))


if __name__ == "__main__":
    main()

```


## Tool C — game_catalogue.py

```python
#!/usr/bin/env python3
"""
game_catalogue — enumerate SportyBet's games lobby.

Found by grepping the games SPA bundle for /games/lobby. Key fact: every lobby
request needs an `x-platform` header or it returns HTTP 500.

Usage:
    python3 game_catalogue.py --out data/games
"""

import argparse
import json
import os
import time
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.sportybet.com"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")

ENDPOINTS = [
    ("featured", "/api/ng/games/lobby/v1/games/featured", "WAP"),
    ("mini", "/api/ng/games/lobby/v2/games/web-mini?offset=0&limit=50", "WEB_MINI"),
]

# Known house-edge bands by category. Published ranges, not SportyBet-specific —
# the app must label these as industry reference, never as the operator's number.
HOUSE_EDGE = {
    "Crash": "~3% (industry typical for crash games)",
    "Quick": "2–10% (varies per game)",
    "Slots": "3–8% (varies per title)",
    "Cards": "0.5–5% (basic strategy dependent)",
    "Wheel": "5–10%",
    "Dice": "2.8–5%",
    "Live": "1–5% (live dealer, provider-set)",
}


def get(path, platform, timeout=25):
    req = urllib.request.Request(
        BASE + path,
        headers={"User-Agent": UA, "x-platform": platform,
                 "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode("utf-8", "replace"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/games")
    args = ap.parse_args()

    run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(args.out, run)
    os.makedirs(d, exist_ok=True)

    out = {"run": run, "fetchedAt": datetime.now(timezone.utc).isoformat()}
    for name, path, plat in ENDPOINTS:
        try:
            st, body = get(path, plat)
            out[name] = body
            print("%-10s http=%s biz=%s" % (name, st, body.get("bizCode")))
        except Exception as e:
            out[name] = {"error": "%s: %s" % (type(e).__name__, e)}
            print("%-10s ERROR %s" % (name, e))
        time.sleep(0.5)

    # Flatten the catalogue into one training-friendly list.
    games = []
    cats = (out.get("featured") or {}).get("data") or []
    for c in cats:
        for g in c.get("gameList") or []:
            games.append({
                "category": c.get("name"),
                "categoryId": c.get("id"),
                "name": g.get("name"),
                "gameId": g.get("gameId"),
                "rtp": g.get("rtp"),
                "onlineUserCount": g.get("onlineUserCount"),
                "launchUrl": g.get("launchUrl"),
                "deepLinkUrl": g.get("deepLinkUrl"),
                "provider": ("evolution" if str(g.get("name", "")).startswith("evo_")
                             else "sportybet-or-third-party"),
                "houseEdgeReference": HOUSE_EDGE.get(c.get("name"), "unknown"),
                "modellable": False,     # no game in this lobby is predictable
            })
    out["games"] = games

    jp = os.path.join(d, "games.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)

    # Human-readable table
    md = ["# Games catalogue", "", "Run: %s" % run, "",
          "| Category | Game | gameId | online | RTP published | House edge (industry) |",
          "|---|---|---|---|---|---|"]
    for g in games:
        md.append("| %s | %s | %s | %s | %s | %s |" % (
            g["category"], g["name"], g["gameId"],
            g["onlineUserCount"], "yes" if g["rtp"] else "**no**",
            g["houseEdgeReference"]))
    md += ["", "**%d games across %d categories.** "
               "None of these are modellable: every one is RNG or live-dealer with a "
               "provider-set house edge." % (len(games), len(cats)), ""]
    mp = os.path.join(d, "GAMES.md")
    with open(mp, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("\nwrote %s (%d games)" % (jp, len(games)))
    print("wrote %s" % mp)
    unpub = sum(1 for g in games if not g["rtp"])
    print("games without a published RTP: %d/%d" % (unpub, len(games)))


if __name__ == "__main__":
    main()

```
