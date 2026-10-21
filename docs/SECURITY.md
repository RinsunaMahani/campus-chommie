# Security

How Campus Chommie protects its users, kept current for the SSDLC form. Version for **M1**: the M0 foundation
(accounts, sign-in, account security, notifications, audit), plus the public course finder and university catalogue,
which need no account and store nothing. Update it whenever a milestone adds data or endpoints.

## What we protect

| Asset | Where | Notes |
|---|---|---|
| Accounts | `identity.users`, `identity.password_credentials` | email and a bcrypt password hash; nothing else is asked at sign-up |
| Consent records | `identity.consents` | which Privacy Policy and Terms versions, the 18-or-older confirmation, when, IP and app |
| Sign-in state | `identity.sessions`, `email_codes`, `trusted_phones`, `password_resets`, `devices` | hashes only: codes, reset tokens and phone tokens are stored as HMACs |
| Alerts | `platform.notifications` | owner-only; templates can't carry personal details |
| Audit trail | `audit.audit_events` | append-only (see the open question on the personal data it holds) |
| Marks typed into the course finder | memory, for one request only | never stored or logged; learners using it may be under 18 |
| University data packs | `backend/data/universities/*.yaml` | public facts, each citing its source; served read-only; changed only by pull request |
| Later milestones | students' marks, money, spending (owner-only); classes and announcements | the threat model grows with them |

## Threats and controls

| Threat | Control | Where |
|---|---|---|
| Stolen or guessed password | bcrypt hashing; 5 wrong passwords lock the account for 15 minutes; rate limits per IP and per IP + email; a new phone needs a 6-digit code from the email (two factors) | `domains/identity/auth/services/auth_service.py`, `auth/rate_limit/policies.py`, `auth/models/trusted_phone.py` |
| Stolen token | 15-minute access tokens tied to a live session; rotating refresh tokens, and a reused refresh token revokes the whole session; "sign out other phones" | `auth/models/credentials.py` (Session), `auth/services/jwt_callbacks.py`, `session_service.py` |
| Fishing for which emails have accounts | sign-up, resend and forgot-password give the same answer whatever the email; an existing account's owner gets an email instead | `auth_service.register`, `forgot_password` |
| Reading someone else's data (IDOR) | every query takes the signed-in user from the token; another user's row is the same 404 as a missing one | `core/decorators.py`, each feature's repository |
| Junk or hostile input | strict schemas refuse unknown fields (422); requests over 1 MB refused (413); JSON deeper than 32 levels refused (400); NUL characters refused anywhere (400). The course finder takes 1 to 9 known subjects, each once, with marks from 0 to 100 (NaN and infinity refused) | `domains/*/schemas`, `src/__init__.py` (`_register_input_guard`), `config.py` |
| Flooding | a rate limit on every route: per user for signed-in routes, per IP for public ones (the course finder and catalogue allow 120 a minute, because a school computer lab shares one address) | `@limiter.limit` on each route; `shared/rate_limit/` |
| A learner's marks kept or leaked (POPIA; learners may be under 18) | the course finder needs no account, runs no database statement and never logs a mark; refusals never repeat a mark; its rate-limit refusals aren't audited, so no IP address is kept either | `domains/pathways/course_finder/` |
| Wrong facts shown as true | every pack is validated as it loads: each fact's source must exist, subject keys must be known, levels 1 to 8, percentages 0 to 100; a pack nobody has checked yet is served with "Not yet confirmed by the team" | `campus_engine/schemas.py`, `domains/catalogue/universities/` |
| Children's personal information (POPIA) | accounts require confirming 18 or older; only the JSON value `true` is accepted; recorded with the consent | `auth/schemas/auth_schemas.py`, `accounts/services/account_service.py` |
| Collecting too much | sign-up takes email, password, consent and the age confirmation only; any other field is refused | `RegisterSchema` |
| Secrets leaking | secrets only in git-ignored `.env`; the app refuses to start with missing or short (< 32 characters) keys; codes and reset links are never logged; production refuses the fake mail provider and requires an https base address | `config.py`, `shared/email/` |
| Tampering with history | the database refuses UPDATE, DELETE and TRUNCATE on the audit trail (trigger) | `migrations/versions/0001_baseline.py` |
| Spoofed client IP | forwarding headers are ignored unless the server sits behind Cloudflare alone (`BEHIND_CLOUDFLARE`) | `shared/net/client_ip.py` |
| Browser attacks on API responses | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`; CORS only in development | `src/__init__.py` |
| Design rot | architecture tests: the engine imports no app, web or database code; routes never call the engine (services do); `shared/` never imports a domain; identity stays sealed; finance stays a leaf; every route has a rate limit | `backend/tests/architecture/` |
| Vulnerable dependencies, committed secrets | CI runs `pip-audit` and an npm audit gate (any high or critical advisory fails, except the accepted ones below), and a gitleaks scan, on every pull request | `.github/workflows/ci.yml`, `frontend/mobile/scripts/check-audit.mjs` |

## Test evidence (M1)

Backend: **457 tests pass** on PostgreSQL 16 (9 Oct 2026), including:

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
| `tests/domains/pathways/test_course_finder_hostile.py` | odd bodies, impossible marks (out of range, NaN, infinity, text), repeated or unknown subjects, ten subjects, unknown fields (including an ID number), huge and deeply nested bodies are refused; no database statement runs and no mark reaches a log during a request; limited per IP |
| `tests/architecture/` | the boundaries above, including every route having a rate limit and routes never calling the engine |
| `tests/engine/` | 105 engine tests, 97.2% coverage (the floor is 80%), including data-pack validation |

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
- No removal of a closed account's data yet, and `DELETE /me` isn't built.
- Demo accounts need a decision on the new-phone email code before M5.
- Rate-limit counters live in memory: correct for one server process only.
- The Privacy Policy and Terms are drafts awaiting legal review.
