# Security

SportyAgent is a local tool. The threat model starts from that fact, and from a harder one: credentials and model keys must never leave the user's machine.

## How to report a vulnerability

Open a private advisory at https://github.com/hookupt7/Casino/security/advisories/new. Please do not file a public issue for a vulnerability.

Include enough to reproduce the problem: a description, affected version or commit, and what an attacker would gain. Do not attach live credentials, session cookies, or vault files. Use placeholders.

We will acknowledge reports as soon as a maintainer can look at them, and we will not discuss the details in public until a fix is available or we have agreed otherwise.

## What Phase 0 already enforces

- The local page binds `127.0.0.1` only. `./start.sh` and the Python server both refuse a public bind address. (`next start`, when it arrives in Phase 1, defaults to `0.0.0.0`; the launcher must keep passing an explicit loopback host.)
- `.gitignore` excludes `.env`, vault files, and keys. Do not commit secrets "just this once."
- There is no login, no credential prompt, and no outbound placement in Phase 0.

## Planned controls (later phases)

These are recorded so later work does not walk them back. Details live in `docs/ARCHITECTURE.md` and in the handoff.

- Local vault: Argon2id key derivation, AES-256-GCM, OS keychain binding where available, a short auto-lock.
- Per-install token sent as a header, no auth cookies, Host and Origin checks, body size limits.
- Hash-chained audit log, with the head hash stored outside the database.
- `make audit` will grow from today's banned-language check into a ten-part suite: dependency audit, lockfile drift, secret scan, slop linter, vault export guard, redaction test, permission check, licence scan, audit-chain integrity, SBOM diff.

Reads of signed SportyBet feeds go through a real browser session. The app must not try to forge the fixtures-feed signature. Bet placement, if it ever ships, is driven through the page itself; the order body is encrypted by the site and a reconstructed payload fails.

## Honest limits

Malware on the machine wins. A tool that runs locally cannot protect a user from software that already has the same privileges.

A user who approves a bad slip has still approved a bad slip. Confirmation dialogs and loss caps reduce accidents; they do not remove responsibility.

If placement ever ships, automated access may breach the operator's terms and can get an account closed. That risk will be stated in the consent screen.

We do not claim this design is complete, or that it will stay ahead of every attack.
