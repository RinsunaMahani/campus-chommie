# SSDLC answers for Sonke (draft)

Draft answers for the SSDLC form on the team page, from [SECURITY.md](../SECURITY.md), which holds the full threat
model and test evidence. Rinsuna fits these into the form's own questions. Numbers were true on 22 Oct 2026; re-check
the test counts the day you submit.

## 1. Requirements: what we protect and why

- **Who uses it:** learners choosing a course (often under 18, no account) and enrolled students (18 or older, with
  an account).
- **What is sensitive:** a student's marks, money entries and spending; their account and sign-in state; consent
  records. Course-finder marks are never stored at all.
- **Rules we set ourselves before writing code** (CLAUDE.md):
  - POPIA first: the course finder needs no account and stores nothing; accounts need an 18-or-older confirmation
    and recorded consent.
  - Collect the minimum: no ID numbers, bank or account numbers, NSFAS or bank credentials, race, religion or
    health data. Sign-up takes email, password, consent and the age confirmation only.
  - Owner-only data: marks, money and spending are visible only to their owner; no rep or admin view reads them.
  - Nothing in the app moves money; amounts are whole cents.
  - Never invent facts: every admission rule, date and contact cites its official source, and missing values say
    "Not verified yet".

## 2. Design: threat model

We listed each threat and its control (full table in SECURITY.md). The main ones:

| Threat | Control |
|---|---|
| Stolen or guessed password | bcrypt; lockout after 5 wrong tries for 15 minutes, during which a right password gets the same answer as a wrong one (no hint to a guesser); rate limits per IP and per IP + email; a new phone needs a 6-digit email code (two factors) |
| Stolen token | 15-minute access tokens tied to a live session; rotating refresh tokens; a reused refresh token revokes the session |
| Reading someone else's data (IDOR) | every query takes the user from the token; another user's record answers 404, the same as a missing one |
| Account enumeration | sign-up, resend and forgot-password give the same answer for any email |
| Junk or hostile input | strict schemas refuse unknown fields; size, depth and NUL-character limits; money as whole cents, no floats |
| Flooding | a rate limit on every route (a test fails if a route has none) |
| A learner's marks kept or leaked | the course finder runs no database statement and never logs a mark |
| Wrong facts shown as true | every data pack is validated on load: each fact's source must exist; unchecked packs say so in the app |
| Learners sent to fake application pages | packs link only to official https pages; NSFAS's "never pay anyone to apply" warning is shown |
| Tracking a student through the map | the map takes no location; a "you are here" dot would stay on the phone |
| Secrets leaking | secrets only in environment settings; the app refuses to start with missing or short keys; codes and links never logged |
| Tampering with the audit trail | the database refuses to change or delete audit rows (trigger) |
| A web page or script abusing an API answer | Content-Security-Policy that loads nothing, no framing, no sniffing, no caching; cross-origin isolation |
| A lost or shared phone | sign-in tokens and wallet cards in the phone's secure store; app data left out of phone backups |

## 3. Implementation: secure coding

- **Layered backend** (Flask): routes, schemas, services, repositories and models per feature; the decision engine is
  pure Python with no web or database code (architecture tests enforce the boundaries).
- **Validation everywhere:** Marshmallow and Pydantic schemas refuse unknown fields; percentages 0 to 100; dates
  checked against today in SAST.
- **Least data:** export (`GET /me/export`) and real deletion (`DELETE /me`) of everything we hold about a student.
- **Wellbeing wording:** alerts never call a student "at risk" or diagnose, and always point to campus support.
  Crisis lines stay hidden until a person verifies them.
- **Secrets:** generated per environment and typed into the host's settings; never in the repository; the demo
  password comes from an environment setting, never the code or the app.

## 4. Testing

- **Automated tests on every pull request** (GitHub Actions): 1,434 backend tests on PostgreSQL 16, including
  hostile-input tests for every endpoint, rate-limit tests, IDOR tests (404 for someone else's data), privacy
  export and deletion tests, and audit-trail tamper tests, with 99% engine coverage. The app: TypeScript check,
  ESLint and 253 Jest tests.
- **Security scanning in CI:** Bandit (code; a medium or high finding fails the build), `pip-audit` and an npm audit
  gate (a high or critical advisory fails the build), and a gitleaks secrets scan of every branch's history.
- **Our own pen test (21 Oct 2026):** a script of 105 attacks on a copy of the API running with the production config
  on our own computer: forged and replayed tokens, reading or changing another student's data by id, extra fields
  (`user_id`, `is_demo`), hostile bodies (50,000-deep JSON, 2 MB, 10^30 cents, NUL bytes, SQL), booby-trapped PDFs
  (400 pages, cut off, not a PDF), account enumeration, lockout, code guessing and rate limits. It found three
  problems, all fixed the same day with tests: the lock told a guesser when a password was right; deleting a module
  with marks crashed; no Content-Security-Policy. 105 of 105 now pass. The script is in the repository
  (`backend/scripts/security/pentest_local.py`) and refuses to run against any other computer.
- **Scanners run by hand the same day:** Semgrep (698 files: false positives only), OWASP ZAP baseline on the API and
  the reset page (no failures; three header gaps fixed), and MobSF on the signed APK (no trackers, no secrets in the
  app; backups and five unused permissions removed).
- **Manual checks:** every screen walked at 360 px wide; data spot-checked against official sources.

## 5. Deployment

- **Container:** runs as a normal user, holds no secrets or tests, starts in production mode, which refuses weak
  secrets and fake email; the access log has no IP address and no query string.
- **Hosting:** Render (API, HTTPS) and Neon (PostgreSQL, TLS required) free tiers, both in Frankfurt. Settings
  typed into the host by the owner, never committed.
- **CORS:** only named https origins in production; `*` and plain http are refused at start-up.
- **Behind Cloudflare:** the live API reads the visitor's address from Cloudflare's own header, so rate limits
  count each visitor separately (to be set with the next deploy: confirm from Argon's report before submitting).
- **Headers:** HSTS for a year, Content-Security-Policy, no framing, no caching, cross-origin isolation.
- **Health:** `/api/v1/ping` for uptime (no database), `/api/v1/health` for a full check.

## 5b. The Android app

- **Permissions:** internet, network state, vibrate and camera (only to scan a store card's barcode, nothing
  recorded). Permissions that libraries add but no feature uses (draw over other apps, storage, fingerprint and face
  unlock) are stripped from the build.
- **Data on the phone:** sign-in tokens and wallet cards in the secure store (Android Keystore); app data excluded
  from phone backups; nothing in the app holds a secret (the demo password, mail and database settings appear nowhere
  in it, checked in the built APK).
- **No trackers, no analytics, no ads** (MobSF found none).
- **Signed** by EAS with a key kept in our Expo account; from the next build, built for phone processors only.
- **Old phones:** it installs from Android 7 on purpose, because many students' phones are old. The server checks
  everything, and the phone only ever holds the student's own data.

## 6. Maintenance and response

- Dependency advisories are reviewed with a date; CI fails when the date passes, forcing a re-check.
- The demo accounts hold only fictional data and are rebuilt every day, so anything a visitor changes is undone.
- **Known gaps we are honest about:** the inherited audit trail keeps email and IP addresses with no deletion rule;
  the Privacy Policy and Terms are drafts awaiting legal review; rate-limit counters live in memory (right for the
  one process we run).
