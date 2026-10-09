# Security

How Campus Chommie protects its users, kept current for the SSDLC form. Version for **M0** (foundation: accounts,
sign-in, account security, notifications, audit; no student data yet). Update it whenever a milestone adds data or
endpoints.

## What we protect

| Asset | Where | Notes |
|---|---|---|
| Accounts | `identity.users`, `identity.password_credentials` | email and a bcrypt password hash; nothing else is asked at sign-up |
| Consent records | `identity.consents` | which Privacy Policy and Terms versions, the 18-or-older confirmation, when, IP and app |
| Sign-in state | `identity.sessions`, `email_codes`, `trusted_phones`, `password_resets`, `devices` | hashes only: codes, reset tokens and phone tokens are stored as HMACs |
| Alerts | `platform.notifications` | owner-only; templates can't carry personal details |
| Audit trail | `audit.audit_events` | append-only (see the open question on the personal data it holds) |
| Later milestones | marks, money, spending (owner-only); classes and announcements | the threat model grows with them |

## Threats and controls

| Threat | Control | Where |
|---|---|---|
| Stolen or guessed password | bcrypt hashing; 5 wrong passwords lock the account for 15 minutes; rate limits per IP and per IP + email; a new phone needs a 6-digit code from the email (two factors) | `domains/identity/auth/services/auth_service.py`, `auth/rate_limit/policies.py`, `auth/models/trusted_phone.py` |
| Stolen token | 15-minute access tokens tied to a live session; rotating refresh tokens, and a reused refresh token revokes the whole session; "sign out other phones" | `auth/models/credentials.py` (Session), `auth/services/jwt_callbacks.py`, `session_service.py` |
| Fishing for which emails have accounts | sign-up, resend and forgot-password give the same answer whatever the email; an existing account's owner gets an email instead | `auth_service.register`, `forgot_password` |
| Reading someone else's data (IDOR) | every query takes the signed-in user from the token; another user's row is the same 404 as a missing one | `core/decorators.py`, each feature's repository |
| Junk or hostile input | strict schemas refuse unknown fields (422); requests over 1 MB refused (413); JSON deeper than 32 levels refused (400); NUL characters refused anywhere (400) | `domains/*/schemas`, `src/__init__.py` (`_register_input_guard`), `config.py` |
| Flooding | a rate limit on every route, per user for signed-in routes | `@limiter.limit` on each route; `shared/rate_limit/` |
| Children's personal information (POPIA) | accounts require confirming 18 or older; only the JSON value `true` is accepted; recorded with the consent | `auth/schemas/auth_schemas.py`, `accounts/services/account_service.py` |
| Collecting too much | sign-up takes email, password, consent and the age confirmation only; any other field is refused | `RegisterSchema` |
| Secrets leaking | secrets only in git-ignored `.env`; the app refuses to start with missing or short (< 32 characters) keys; codes and reset links are never logged; production refuses the fake mail provider and requires an https base address | `config.py`, `shared/email/` |
| Tampering with history | the database refuses UPDATE, DELETE and TRUNCATE on the audit trail (trigger) | `migrations/versions/0001_baseline.py` |
| Spoofed client IP | forwarding headers are ignored unless the server sits behind Cloudflare alone (`BEHIND_CLOUDFLARE`) | `shared/net/client_ip.py` |
| Browser attacks on API responses | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`; CORS only in development | `src/__init__.py` |
| Design rot | architecture tests: the engine imports no app, web or database code; `shared/` never imports a domain; identity stays sealed; finance stays a leaf; every route has a rate limit | `backend/tests/architecture/` |
| Vulnerable dependencies, committed secrets | CI runs `pip-audit`, `npm audit --omit=dev --audit-level=high` and a gitleaks scan on every pull request | `.github/workflows/ci.yml` |

## Test evidence (M0)

Backend: **392 tests pass** on PostgreSQL 16 (9 Oct 2026), including:

| Tests | What they prove |
|---|---|
| `tests/domains/identity/test_hostile_input.py` | bad emails, over-long and emoji passwords, wrong types, broken and deeply nested bodies, NUL characters, unknown fields (including an ID number) and every non-`true` 18-or-older value are refused, never a crash |
| `tests/domains/identity/test_auth.py`, `test_two_factor.py`, `test_account_security.py` | sign-up, verification, lockout, the same answer for unknown emails, refresh rotation and reuse detection, new-phone codes, sign-out everywhere, the data export holds no secrets |
| `tests/domains/identity/test_rate_limits.py`, `tests/shared/test_client_ip.py` | limits trigger, forged forwarding headers don't buy more tries |
| `tests/domains/platform/test_notifications*.py` | owner-only alerts (404 for someone else's), strict queries, per-user limits |
| `tests/domains/security/test_audit.py` | audit events are written, and the database refuses to edit or delete them |
| `tests/shared/test_email.py` | sign-in codes never reach the logs; production refuses fake email |
| `tests/architecture/` | the boundaries above, including every route having a rate limit |
| `tests/engine/` | 83 engine tests, 96.8% coverage (the floor is 80%) |

App: TypeScript check, ESLint (no warnings) and Jest pass, including a test of the exact sign-up request.

## Known gaps

Tracked with options in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md):

- The audit trail (inherited) stores full email addresses and IP addresses with no deletion rule.
- No removal of a closed account's data yet, and `DELETE /me` isn't built.
- Demo accounts need a decision on the new-phone email code before M5.
- Rate-limit counters live in memory: correct for one server process only.
- The Privacy Policy and Terms are drafts awaiting legal review.
