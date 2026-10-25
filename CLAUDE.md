# CLAUDE.md

Campus Chommie takes a South African student from choosing a course to graduating: course finder, the student's
week (calendar, class deadlines, workload, marks), their money (runway, safe to spend, life fund), alerts and campus
support. Our entry for the FNB App of the Year Hackathon 2026, challenge "Access to higher education", by Rinsuna
Mahani: she builds the app, the API, the engine and the data, and reviews every change.

Shape: one Expo app (Android + web build) in `frontend/mobile`, a Flask API with PostgreSQL in `backend/src`, and a
pure Python engine in `backend/campus_engine` that does the thinking. Gaps and decisions for the team are in
[docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md); the threat model and controls in [docs/SECURITY.md](docs/SECURITY.md);
what came from our earlier project in [REUSE.md](REUSE.md).

## Facts: never invent them

- **Never invent** admission rules, points scales, calendar dates, allowance dates or amounts, contacts, prices or
  places. If a value is missing, use `null`, show "Not verified yet" in the app, and add the gap to
  `docs/OPEN_QUESTIONS.md`.
- Every fact in a data pack (`backend/data/universities/*.yaml`) cites a source id; the validator fails CI on a broken
  reference. Official university publications are sufficient verification (Rinsuna, 25 Oct 2026): record
  `verification_basis: official_university` with the source URL and its actual retrieval date. This accepts
  provenance without claiming a person checked it; preserve existing `verified_by` and `last_verified` history.
  Incomplete packs keep `release: false`. Contradictory or missing rules remain unresolved until evidence settles
  them. Non-university sources, including NSFAS dates and income limits, retain their existing review requirements.
  Only a value a person checked gets their name in `verified_by`.
- Demo data is fictional and labelled ("Demo data: fictional student"), never presented as NSFAS or university figures.
- Translations: never machine-translate for release. A language becomes visible only after a fluent speaker signs it
  off in `docs/translation_review.md`; a translated rule always shows beside its English original and source.

## Rules that always apply

- **POPIA and minors.** The course finder needs no account and stores nothing (never store or log marks typed there).
  Student accounts require confirming 18 or older (sign-up enforces it). Show a plain privacy notice and record
  consent at sign-up.
- **Collect the minimum.** No ID numbers, bank or account numbers, NSFAS or bank credentials, and no religion, race or
  health data. Never ask learners about protected characteristics; routes with eligibility restrictions show their
  note and the learner decides.
- **Owner-only data.** Marks, money and spending are visible only to their owner. No rep or admin view reads them.
  Class-level views show aggregates only when at least 5 students contribute.
- **Security by design.** Scope every query to the signed-in user and answer "not yours" with 404 (IDOR). Strict
  schemas that refuse unknown fields. A rate limit on every route (`tests/architecture/test_every_route_is_rate_limited.py`
  enforces it). Audit events contain no personal data (see the open question on the inherited audit trail). Every new
  endpoint gets hostile-input tests.
- **Secrets.** Never commit, print or log `.env` values, tokens, OTPs, passwords or links that sign people in. Demo
  passwords come from environment variables, never the repo. Use only your own sandbox database; never connect to
  anyone else's or any production database.
- **Money** is integer cents everywhere; nothing in the app moves money. **Dates and times** are Africa/Johannesburg
  (SAST).
- **WhatsApp (M6).** Verify the `hub.verify_token` handshake. Check `X-Hub-Signature-256` (HMAC-SHA256 of the raw body
  with the app secret) and reject unsigned or stale requests. Private chats only, never groups. Phone numbers stored
  as salted hashes.
- **Wellbeing wording.** Never call a student "at risk", never diagnose, always point to campus support. Crisis
  contacts require human review or a dated official university source before release.
- **No university logos or trademarks.** University names in text only.
- **SSDLC.** Keep `docs/SECURITY.md` current: threat model, controls, test evidence.

## Architecture

- `backend/campus_engine` imports nothing from `src/`, Flask, SQLAlchemy or the web stack
  (`tests/architecture/test_engine_boundaries.py`). Services call the engine; routes never do. Every threshold lives in
  `backend/config.yaml`, and every engine function returns a plain-words explanation with its numbers.
- Domains live in `backend/src/domains/<area>/<feature>` with the same five folders (api, schemas, services,
  repositories, models). `shared/` never imports a domain; no feature reads another feature's repositories; identity
  stays behind `account_service` (`tests/architecture/test_domain_boundaries.py`).
- Keep the API conventions in `src/core/`: the response envelope and stable error codes. Every new table comes with a
  migration (`flask db migrate`, then read it: autogenerate misses schemas, functions and triggers).
- App: Expo Router in `frontend/mobile/src/app`, one route group per stage (`(auth)`, `(app)`, `(legal)`); screens in
  `src/features/<feature>`, shared UI in `src/shared`. Colours and type only from `src/shared/theme/tokens.ts` and `palette.tsx` (the student side uses the black `night` palette; Find my course and sign-in the `forest` one; components read colours with `usePalette()`/`useStyles()`).

## Scope

Build the five features in the brief (F1 university profile, F2 find my course, F3 my week, F4 my money, F5 alerts and
support), F6 fund and apply: funding and how to apply (agreed by Rinsuna on 9 Oct 2026), and campus maps from
OpenStreetMap (her scope change of 12 Oct 2026; a student's location never leaves the phone). **Do not build:**
study-partner matching, the skills-demand outlook, peer tutors, any payment or money movement, bank or NSFAS account
linking, or any commerce, supplier or trader feature. M6 (the WhatsApp bot) must not start before Fri 23 Oct 2026
08:30 SAST.

## Workflow

- Picking up work? Read [docs/HANDOVER.md](docs/HANDOVER.md) first: where the pull requests stand, what was decided,
  and what comes next.
- Branches are `rinsuna/<topic>` (`rinsuna/money-screens`, `rinsuna/engine-schema`). Merge into `main` only with CI
  green and Rinsuna's approval.
- Commits are small and name the feature or milestone (`F4: late-payment toggle`). **Never force-push or rewrite
  history:** the git log is the honest record of what was built before and during the hackathon.
- Before a commit: backend `python -m pytest -q tests` (engine and architecture tests run without a database),
  `python scripts/validate_data.py`, and in `frontend/mobile` `npx tsc --noEmit`, `npx jest`, `npx expo lint`.
- Local servers: Rinsuna's own run on ports 5000 (API) and 8081 (Expo). Agents use other ports (e.g. 5090 and 8090)
  and never stop someone else's server.

## Ask Rinsuna first

Before adding an external service or paid API; changing a fact in a data pack; making a language visible; collecting
any new personal data; deleting files outside the brief's strip list; changing hosting or deployment.

## Never

Invent facts; build out-of-scope features; start M6 early; copy files from TruConnect (reference only); commit
secrets; connect to someone else's or a production database; use university logos.
