# Security

How Campus Chommie protects its users, kept current for the SSDLC form. Version for **M5**: the M0 foundation
(accounts, sign-in, account security, notifications, audit); the public course finder (with how to apply) and
university catalogue, which need no account and store nothing; the student's own profile, money and marks, which
only they can see; classes, where reps confirm tests and deadlines; alerts and campus support, worked out on each
request and never stored; and the judges' demo accounts. Update it whenever a milestone adds data or endpoints.

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
| My marks | `student.modules`, `student.assessments` | the student's modules, assessment weights and marks. Owner-only; no rep or admin view. Deleted for real when the student deletes them |
| Classes | `classes.classes`, `class_members`, `rep_invites` | a class holds no personal data (who made it isn't kept). Members are never listed, not even to reps: views give counts. Rep codes are kept as SHA-256 hashes only, work once and expire after 48 hours. A class is deleted after its academic year and one more |
| Announcements | `classes.announcements`, `event_candidates` | pasted text may hold personal data: only the class's reps and the student who sent it see it. The text is deleted 30 days after a rep confirms or discards it; an announcement nobody decides on goes after 60 days; a candidate goes when it's decided |
| Verified events | `classes.class_events`, `event_changes` | tests and deadlines a rep confirmed, and each change to them. Who confirmed or changed one is kept as a user id that's never returned, and cleared when that account goes |
| Demo accounts | `identity.users` (`is_demo`), `platform.demo_accounts` | three fictional students, made only by `flask seed`; their shared password comes from `DEMO_PASSWORD`, never the repo; their data is rebuilt every day |
| Flags | `classes.event_flags` | one per student per event, with a reason from a fixed list (no free text). Reps see how many and which reasons, never who. Kept 12 months |

## Threats and controls

| Threat | Control | Where |
|---|---|---|
| Stolen or guessed password | bcrypt hashing; 5 wrong passwords lock the account for 15 minutes; rate limits per IP and per IP + email; a new phone needs a 6-digit code from the email (two factors) | `domains/identity/auth/services/auth_service.py`, `auth/rate_limit/policies.py`, `auth/models/trusted_phone.py` |
| Stolen token | 15-minute access tokens tied to a live session; rotating refresh tokens, and a reused refresh token revokes the whole session; "sign out other phones" | `auth/models/credentials.py` (Session), `auth/services/jwt_callbacks.py`, `session_service.py` |
| Fishing for which emails have accounts | sign-up, resend and forgot-password give the same answer whatever the email; an existing account's owner gets an email instead | `auth_service.register`, `forgot_password` |
| Reading someone else's data (IDOR) | every query takes the signed-in user from the token; another user's row is the same 404 as a missing one (alerts, profile, every money record, modules and assessments). Alerts and support read only the signed-in student's own records. Classes are reached only through the student's own membership: a class they're not in, and its candidates, events and flags, are the same 404 as ones that don't exist | `core/decorators.py`, each feature's repository, `classes/classes/services/class_service.py` (`membership`) |
| A student acting as a rep | the rep role belongs to one class: a rep elsewhere is a student here. Only a rep confirms (403 for a student's own candidate); a student sees only their own candidates (anyone else's is a 404); a change can only touch an event in the candidate's own class | `classes/events/services/events_service.py`, `class_service.require_rep` |
| Guessing invite or rep codes | invite codes are 8 characters from a 31-character alphabet (about 850 billion codes) and rep codes 10; joining is limited to 20 tries an hour per student; a rep code works once, for 48 hours, and only its hash is stored; a class has at most 3 reps, and codes already waiting can never make a fourth (the class row is locked while reps change) | `classes/classes/` |
| Unverified information shown as fact | nothing goes live without a rep's confirmation, and the engine never publishes; fields it's unsure of are flagged to the rep (`needs_check`); a student's announcement says it's unverified until a rep confirms; the week strip and the life fund count verified events only; the university calendar beside the week is context and never counted | `campus_engine/extraction.py`, `classes/events/` |
| Demo accounts misused, or the judges locked out | only `flask seed` makes one, and never from a real account; they hold fictional data only and say so (`GET /me`: `demo: true`); they skip the new-phone code (the judges can't read the demo inbox) but can't be locked by wrong passwords, so each IP gets 20 sign-in tries an hour on them instead; their password can't be changed, reset or used to close them; everything a visitor changes is undone at the next daily re-base | `identity/auth/services/auth_service.py`, `auth/rate_limit/policies.py` (`DEMO_LOGIN`), `domains/platform/demo/` |
| A wrong crisis number shown as true | crisis lines show only once a person has checked their source (a name, not an agent draft, and a date); until then Support says so. Every other support entry shows its source and when a person last checked it, or "Not verified yet" | `domains/student/alerts/services/alert_service.py` |
| Wording that labels or frightens a student | alerts describe the situation and end in things to do; they never say "at risk" and never diagnose, and the heavier ones always point to campus counselling (engine tests check the words) | `campus_engine/alerts.py` |
| Spam through announcements | 60 an hour per student, at most 10 waiting per student in one class, at most 2 000 characters; the text is never logged | `classes/events/constants.py`, `events_service.announce` |
| Marks gone wrong through bad input | percentages from 0 to 100 (a weight above 0); text, booleans, NaN, infinity and huge integers refused; a module's weights can't pass 100% | `domains/student/academics/schemas/`, `services/` |
| Money gone wrong through rounding or bad input | amounts are whole cents, built as shared/finance's `Money`: floats (even 1250.0), text, booleans, NaN and infinity are refused; at most R1 000 000; dates checked against today (no future spending, nothing more than a year back) | `domains/student/money/schemas/`, `services/` |
| Keeping money records longer than needed | the student deletes any record for real (no soft delete); spending older than a year is deleted daily | `money_repository.py`, `jobs/forget_old_spending.py` |
| A student can't see or remove what we hold (POPIA) | `GET /me/export` gives everything we hold about the signed-in student: identity's part, then every feature's own section, registered at start-up (`shared/privacy`); nothing about anyone else and no secrets. `DELETE /me`, after the password, deletes the account, and every feature's rows go with it (`ON DELETE CASCADE`). A test fails if a new table points at an account without an export section | `identity/auth/services/auth_service.py` (`export_my_data`, `delete_account`), `src/__init__.py` (`_register_exporters`), `tests/domains/platform/test_privacy.py` |
| Keeping class data longer than needed | daily jobs: announcement text 30 days after a decision, undecided announcements after 60 days, flags after 12 months, expired rep codes, and classes after their academic year and one more (with their members, announcements and events) | `classes/events/jobs/forget_old_announcements.py`, `classes/classes/jobs/forget_old_classes.py` |
| Junk or hostile input | strict schemas refuse unknown fields (422); requests over 1 MB refused (413); JSON deeper than 32 levels refused (400); NUL characters refused anywhere (400). The course finder takes 1 to 9 known subjects, each once, with marks from 0 to 100 (NaN and infinity refused). A plan's "today" is the server's date in SAST; a client can't send a date | `domains/*/schemas`, `src/__init__.py` (`_register_input_guard`), `config.py` |
| Flooding | a rate limit on every route: per user for signed-in routes (money and marks changes 60 a minute, profile and class changes 30, new classes 10 an hour, joining 20 an hour, announcements 60 an hour), per IP for public ones (the course finder, the points list, the catalogue and first steps allow 120 a minute, because a school computer lab shares one address) | `@limiter.limit` on each route; `shared/rate_limit/` |
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

## Test evidence (M5)

Backend: **967 tests pass** on PostgreSQL 16 (10 Oct 2026), including:

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
| `tests/domains/student/test_academics.py` | My marks: the engine's standing and projection for a persona's module, weights short of 100% counted as still to come, weights never past 100%, odd numbers (text, booleans, NaN, a 400-digit integer) and unknown fields refused, another student's modules and assessments (404), per-student limits |
| `tests/domains/classes/test_classes.py` | classes and invite codes, rep codes bringing in up to 3 reps (used once, expiring, hashed, never a fourth), only a rep makes rep codes, nobody ever listed, odd input refused, joining slowed to 20 tries an hour, old classes and expired codes deleted |
| `tests/domains/classes/test_events.py` | the brief's M4 checks: a student's announcement stays unverified until a rep confirms it; a change message updates the event and writes `event_changes` rows; flags show reps counts, never who; the week strip with the university calendar; and the brief's M3 check that needed the week: the self-funded persona's heavy week makes his life fund amber |
| `tests/domains/classes/test_events_hostile.py` | odd announcements and confirmations (a "verified" flag, impossible times, dates a year out), a rep's role not carried into another class, other classes' candidates and events (404), floods, and old announcement text and flags deleted |
| `tests/domains/student/test_alerts_support.py` | the personas' alerts (a combined alert for short money and a heavy week ahead, a heavy-week alert with the campus's own tutoring and counselling), a module out of reach, another student's alerts never shown; every kind of support for a campus, "Not verified yet" where the pack has none, crisis lines held back until a person checks them; cheap things for the campus only |
| `tests/domains/platform/test_privacy.py` | the export holds every feature's data and nothing of anyone else's; `DELETE /me` needs the password, leaves no row behind in any table, signs the student out everywhere, keeps the class's events nameless and touches no one else; demo accounts refused; odd requests refused; limited; every table that points at an account has an export section |
| `tests/domains/platform/test_demo.py` | `flask seed` (a strong password from the environment, never echoed; a real account never converted), demo sign-in without the code, no lockout, no password change, reset or closing, the stricter demo limit, the personas built as written, and the daily re-base moving every date and undoing what visitors changed |
| `tests/architecture/` | the boundaries above, including every route having a rate limit and routes never calling the engine |
| `tests/engine/` | 279 engine tests, 99% coverage from the engine and architecture tests alone (the floor is 80%), including data-pack validation, spot checks of the shipped packs against their sources, every application status on either side of each date, every first step's status either side of its dates, and 44 labelled class messages (new events, moved and cancelled, mixed languages, dates to check) |

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
- `DELETE /me` deletes an account and everything it holds, but "Close my account" only deactivates one, and nothing
  removes a closed account's data yet (OPEN_QUESTIONS, "Retention").
- Neither the export nor deleting reaches the audit trail's security records, which nothing may change; they keep
  the email and IP address of past sign-ins (OPEN_QUESTIONS). The record of a deletion keeps no email.
- A Google-only account has no password, so it can't confirm `DELETE /me` yet (Google sign-in is switched off).
- Reps see how many students flagged an event from the first flag (never who). We read CLAUDE.md's 5-student rule
  as covering aggregates of marks and money; the team confirms or changes this in OPEN_QUESTIONS.
- A student's announcement text is seen by the class's reps by design: it's how they check it.
- The demo accounts' password is shared with the judges by design, so those accounts hold fictional data only.
- Crisis lines stay hidden until a person checks them: every pack's are still agent drafts (OPEN_QUESTIONS).
- Rate-limit counters live in memory: correct for one server process only.
- The Privacy Policy and Terms are drafts awaiting legal review.
