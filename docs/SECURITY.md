# Security

How Campus Chommie protects its users, kept current for the SSDLC form. Version for **M3**: the M0 foundation
(accounts, sign-in, account security, notifications, audit); the public course finder (with how to apply) and
university catalogue, which need no account and store nothing; and the student's own profile and money, which only
they can see. Update it whenever a milestone adds data or endpoints.

## What we protect

| Asset | Where | Notes |
|---|---|---|
| Accounts | `identity.users`, `identity.password_credentials` | email and a bcrypt password hash; nothing else is asked at sign-up |
| Consent records | `identity.consents` | which Privacy Policy and Terms versions, the 18-or-older confirmation, when, IP and app |
| Sign-in state | `identity.sessions`, `email_codes`, `trusted_phones`, `password_resets`, `devices` | hashes only: codes, reset tokens and phone tokens are stored as HMACs |
| Alerts | `platform.notifications` | owner-only; templates can't carry personal details |
| Audit trail | `audit.audit_events` | append-only (see the open question on the personal data it holds) |
| Marks typed into the course finder | memory, for one request only | never stored or logged; learners using it may be under 18 |
| University data packs | `backend/data/universities/*.yaml` | public facts, each citing its source: admission rules, application dates, campuses, calendars, money dates (never amounts) and support contacts; served read-only; changed only by pull request. Crisis lines are verified by a person before any pack is released |
| National funding pack | `backend/data/national/funding.yaml` | NSFAS's public facts, under the same rules as a university pack |
| Student profile | `student.profiles` | university and campus (data-pack ids); owner-only |
| My money | `student.money_settings`, `income_sources`, `expected_payments`, `spending_entries` | the student's own entries in integer cents: balance, essentials, life-fund reserve, expected income, one spending number per day. Owner-only; no rep or admin view. No bank or NSFAS details, and nothing moves money. Spending is kept for a rolling year |
| Later milestones | marks (owner-only); classes and announcements | the threat model grows with them |

## Threats and controls

| Threat | Control | Where |
|---|---|---|
| Stolen or guessed password | bcrypt hashing; 5 wrong passwords lock the account for 15 minutes; rate limits per IP and per IP + email; a new phone needs a 6-digit code from the email (two factors) | `domains/identity/auth/services/auth_service.py`, `auth/rate_limit/policies.py`, `auth/models/trusted_phone.py` |
| Stolen token | 15-minute access tokens tied to a live session; rotating refresh tokens, and a reused refresh token revokes the whole session; "sign out other phones" | `auth/models/credentials.py` (Session), `auth/services/jwt_callbacks.py`, `session_service.py` |
| Fishing for which emails have accounts | sign-up, resend and forgot-password give the same answer whatever the email; an existing account's owner gets an email instead | `auth_service.register`, `forgot_password` |
| Reading someone else's data (IDOR) | every query takes the signed-in user from the token; another user's row is the same 404 as a missing one (alerts, profile, every money record) | `core/decorators.py`, each feature's repository |
| Money gone wrong through rounding or bad input | amounts are whole cents, built as shared/finance's `Money`: floats (even 1250.0), text, booleans, NaN and infinity are refused; at most R1 000 000; dates checked against today (no future spending, nothing more than a year back) | `domains/student/money/schemas/`, `services/` |
| Keeping money records longer than needed | the student deletes any record for real (no soft delete); spending older than a year is deleted daily | `money_repository.py`, `jobs/forget_old_spending.py` |
| Junk or hostile input | strict schemas refuse unknown fields (422); requests over 1 MB refused (413); JSON deeper than 32 levels refused (400); NUL characters refused anywhere (400). The course finder takes 1 to 9 known subjects, each once, with marks from 0 to 100 (NaN and infinity refused). A plan's "today" is the server's date in SAST; a client can't send a date | `domains/*/schemas`, `src/__init__.py` (`_register_input_guard`), `config.py` |
| Flooding | a rate limit on every route: per user for signed-in routes (money changes 60 a minute, profile changes 30), per IP for public ones (the course finder, the points list, the catalogue and first steps allow 120 a minute, because a school computer lab shares one address) | `@limiter.limit` on each route; `shared/rate_limit/` |
| A learner's marks kept or leaked (POPIA; learners may be under 18) | the course finder (points, tiers and plan) needs no account, runs no database statement and never logs a mark; refusals never repeat a mark; its rate-limit refusals aren't audited, so no IP address is kept either | `domains/pathways/course_finder/` |
| Wrong facts shown as true | every pack is validated as it loads: each fact's source must exist, subject keys must be known, levels 1 to 8, percentages 0 to 100; application windows must close after they open, late windows must follow the last closing date, and closing dates may name only programmes that exist; calendar periods must end after they start and name only campuses that exist; a date nobody has published shows as not published, never guessed; a pack nobody has checked yet is served with "Not yet confirmed by the team" | `campus_engine/schemas.py`, `campus_engine/applications.py`, `domains/catalogue/` |
| Learners sent to fake application or payment pages | packs link only to official pages, over https (validation refuses anything else); NSFAS's own warnings are shown ("Never pay anyone to apply"); bank account numbers are left out of the packs, and the app never takes a payment or asks for bank details | `campus_engine/schemas.py` (`Applications`), `backend/data/` |
| Children's personal information (POPIA) | accounts require confirming 18 or older; only the JSON value `true` is accepted; recorded with the consent | `auth/schemas/auth_schemas.py`, `accounts/services/account_service.py` |
| Collecting too much | sign-up takes email, password, consent and the age confirmation only; any other field is refused | `RegisterSchema` |
| Secrets leaking | secrets only in git-ignored `.env`; the app refuses to start with missing or short (< 32 characters) keys; codes and reset links are never logged; production refuses the fake mail provider and requires an https base address | `config.py`, `shared/email/` |
| Tampering with history | the database refuses UPDATE, DELETE and TRUNCATE on the audit trail (trigger) | `migrations/versions/0001_baseline.py` |
| Spoofed client IP | forwarding headers are ignored unless the server sits behind Cloudflare alone (`BEHIND_CLOUDFLARE`) | `shared/net/client_ip.py` |
| Browser attacks on API responses | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`; CORS only in development | `src/__init__.py` |
| Design rot | architecture tests: the engine imports no app, web or database code; routes never call the engine (services do); `shared/` never imports a domain; identity stays sealed; finance stays a leaf; every route has a rate limit | `backend/tests/architecture/` |
| Vulnerable dependencies, committed secrets | CI runs `pip-audit` and an npm audit gate (any high or critical advisory fails, except the accepted ones below), and a gitleaks scan, on every pull request | `.github/workflows/ci.yml`, `frontend/mobile/scripts/check-audit.mjs` |

## Test evidence (M1)

Backend: **699 tests pass** on PostgreSQL 16 (10 Oct 2026), including:

| Tests | What they prove |
|---|---|
| `tests/domains/identity/test_hostile_input.py` | bad emails, over-long and emoji passwords, wrong types, broken and deeply nested bodies, NUL characters, unknown fields (including an ID number) and every non-`true` 18-or-older value are refused, never a crash |
| `tests/domains/identity/test_auth.py`, `test_two_factor.py`, `test_account_security.py` | sign-up, verification, lockout, the same answer for unknown emails, refresh rotation and reuse detection, new-phone codes, sign-out everywhere, the data export holds no secrets |
| `tests/domains/identity/test_rate_limits.py`, `tests/shared/test_client_ip.py` | limits trigger, forged forwarding headers don't buy more tries |
| `tests/domains/platform/test_notifications*.py` | owner-only alerts (404 for someone else's), strict queries, per-user limits |
| `tests/domains/security/test_audit.py` | audit events are written, and the database refuses to edit or delete them |
| `tests/shared/test_email.py` | sign-in codes never reach the logs; production refuses fake email |
| `tests/domains/catalogue/test_universities_api.py` | the catalogue is public and read-only, labels unchecked packs, answers 404 for unknown universities, refuses query parameters and is limited per IP |
| `tests/domains/pathways/test_course_finder_api.py` | the brief's M1 check (the strong SMU learner's plan), with reasons, a source and the check status on every card |
| `tests/domains/pathways/test_course_finder_api.py` (how to apply, points) | on a fixed date, each choice's application status, the dates still ahead (NSFAS first), each university's fee and documents, and NSFAS, all with sources and the check status; the points at every university in name order |
| `tests/domains/catalogue/test_universities_api.py` (first steps) | on a fixed date, a new student's steps from accepting an offer to the first lecture, dates not yet published said to be so, 404 for an unknown university, no query parameters, limited per IP |
| `tests/domains/pathways/test_course_finder_hostile.py` | odd bodies, impossible marks (out of range, NaN, infinity, text), repeated or unknown subjects, ten subjects, unknown fields (including an ID number, a date or a grade), huge and deeply nested bodies are refused, for the points list too; no database statement runs and no mark reaches a log during a request; limited per IP |
| `tests/domains/student/test_profile.py` | university and campus checked against the packs; unknown fields (an ID number, race) refused; each student sees only their own profile; limited per student |
| `tests/domains/student/test_money.py` | settings, income becoming expected payments, "received?" taps, one spending number per day, a balance that stays current, and the brief's M3 check (the allowance-funded persona runs short, the life fund pauses, "late" moves the payment 14 days) |
| `tests/domains/student/test_money_hostile.py` | amounts that aren't whole cents, NaN and infinity, impossible dates, unknown fields (an ID or bank number, an NSFAS password), another student's rows (404), at most ten income sources, per-student limits, and old spending deleted |
| `tests/architecture/` | the boundaries above, including every route having a rate limit and routes never calling the engine |
| `tests/engine/` | 232 engine tests, 99% coverage with the API tests (the floor is 80%), including data-pack validation, spot checks of the shipped packs against their sources, every application status on either side of each date, and every first step's status either side of its dates |

App: TypeScript check, ESLint (no warnings) and Jest pass, including a test of the exact sign-up request.

## Accepted dependency risks

Checked 9 Oct 2026. Werkzeug (3.1.9) and PyJWT (2.15.0) were upgraded and the Expo SDK 57 packages patched, which
cleared every other advisory. These remain because no fixed release exists yet; each has a review date, and CI fails
once it passes.

| Advisory | Package | Why it's accepted for now | Review by |
|---|---|---|---|
| PYSEC-2026-4146 | PyJWT | needs code that decodes with signature checks off while reusing an options dict; our code never calls PyJWT, and Flask-JWT-Extended builds a fresh dict with checks on every time | when PyJWT ships a fix |
| GHSA-vfj7-8cjw-p6xm | braces | denial of service through nested glob patterns, reached only through build tooling (Metro, Jest) with our own patterns; not in the app or web bundle | 23 Oct 2026 |
| GHSA-86w9-cpqp-85rv | node-forge | signature-check flaw in the Expo CLI's code-signing helper, which we don't use; not in the app or web bundle | 23 Oct 2026 |

The `.gitleaksignore` file holds one reviewed false positive: the testing config's placeholder JWT key.

## Known gaps

Tracked with options in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md):

- The audit trail (inherited) stores full email addresses and IP addresses with no deletion rule.
- No removal of a closed account's data yet, and `DELETE /me` isn't built. The profile and money tables go with the
  account (`ON DELETE CASCADE`) once it is.
- `GET /me/export` covers what identity holds. The profile and every money record are readable through their own
  endpoints; one combined export comes with `DELETE /me`.
- Demo accounts need a decision on the new-phone email code before M5.
- Rate-limit counters live in memory: correct for one server process only.
- The Privacy Policy and Terms are drafts awaiting legal review.
