# Security

How Campus Chommie protects its users, kept current for the SSDLC form. Version for **M5**: the M0 foundation
(accounts, sign-in, account security, notifications, audit); the public course finder (with how to apply), the
university catalogue, the funding list and the campus maps, which need no account and store nothing; the student's own profile, money and marks, which
only they can see; classes, where reps confirm tests and deadlines; alerts and campus support, worked out on each
request and never stored; and the judges' demo accounts. Update it whenever a milestone adds data or endpoints.

## What we protect

Data completeness update (25 October 2026): optional English and named-language Home/First Additional Language metadata travels
only with the existing transient course-finder request. It is neither persisted nor logged. Strict input validation
rejects language roles on non-language subjects, unknown names and duplicate named languages across APS slots.
Language identity stays on the existing mark row and never creates a second points entry. University source acceptance requires a dated HTTPS URL on an allowlisted
university domain; subdomain-boundary checks reject lookalikes and URL credentials. It does not create a human
sign-off. Rinsuna also accepted dated official funder, government and venue publications on 25 October; these use
an explicit publisher-domain allowlist and retain existing review history. Missing route-specific APS cannot produce an eligibility claim, and unknown
English roles cannot pass a role-dependent boundary. Regression tests cover these decisions in the engine and API.
The crisis-contact gate remains limited to human review or dated official university sources; accepting a venue
or funder source does not make it sufficient evidence for a crisis contact.

Alternative entry based on external qualifications or experience is referred for university assessment; the app
does not collect or assume those qualifications. Published APS bands are assessed only within their recorded
range. Scores above that range remain unverified, rather than extrapolating an eligibility claim.

| Asset | Where | Notes |
|---|---|---|
| Accounts | `identity.users`, `identity.password_credentials` | email and a bcrypt password hash; nothing else is asked at sign-up |
| Consent records | `identity.consents` | which Privacy Policy and Terms versions, the 18-or-older confirmation, when, IP and app |
| Sign-in state | `identity.sessions`, `email_codes`, `trusted_phones`, `password_resets`, `devices` | hashes only: codes, reset tokens and phone tokens are stored as HMACs |
| Alerts | `platform.notifications` | owner-only; templates can't carry personal details |
| Saved funding | `student.saved_funders` | owner-only: the funder's id and the day it was saved, nothing else. A saved list can hint at what a funder's criteria say about a student (a population group, a disability), so no rep or admin view reads it, it's never counted, and it's in the export and deleted with the account |
| Timetable | `student.timetable_entries` | owner-only: the classes a student types for their week (module code, kind, weekday, start and end, venue, an optional name); nothing about them. Another student's class is a 404; in the export and deleted with the account (ON DELETE CASCADE); the demo's fictional timetable is rebuilt daily |
| Exams | `student.exam_entries` | owner-only: the exam papers a student keeps (module code, its name and paper, date, start, length, venue); nothing about them. Another student's exam is a 404; in the export (with the timetable) and deleted with the account (ON DELETE CASCADE); cleared with the demo's daily reset |
| Own plans | `student.activities` | owner-only: what a student adds to their week besides classes (their own words, a broad kind, weekly or once, times, an optional place). The kinds are personal, social, errands, exercise, work and other: we never ask about religion or anything sensitive, and only the student sees the name. Another student's plan is a 404; in the export and deleted with the account (ON DELETE CASCADE) and in the demo's daily reset |
| Money goals | `student.money_goals` | owner-only: what a student is putting money aside for (a label, the amount and how much is aside, a date, and whether the date came from their university's fee dates; the amount always comes from the student). Another student's goal is a 404; in the money export and deleted with the account (ON DELETE CASCADE) and in the demo's daily reset |
| Audit trail | `audit.audit_events` | append-only (see the open question on the personal data it holds) |
| Marks typed into the course finder | memory, for one request only | never stored or logged; learners using it may be under 18 |
| University data packs | `backend/data/universities/*.yaml` | public facts, each citing its source: admission rules, application dates, campuses, calendars, money dates (never amounts) and support contacts; served read-only; changed only by pull request. Crisis lines are verified by a person before any pack is released |
| Colleges pack | `backend/data/national/colleges.yaml` | public facts from DHET: public TVET colleges (name, province, office line, head-office location, website) and its registers of private institutions (name, registration number, status, sites, registered qualifications), with its list of bogus colleges. Contact persons' and principals' names, their phones and emails are left out on purpose |
| National funding pack | `backend/data/national/funding.yaml` | public facts about NSFAS and 23 other funders (bursaries, merit awards, a loan scheme), under the same rules as a university pack. Each fact comes from the funder's own page, never from a site that lists bursaries; eligibility is shown in the funder's words and never asked |
| Campus maps | `backend/data/maps/*.yaml` | public map data from OpenStreetMap (© OpenStreetMap contributors, under the ODbL): each campus's outline, its buildings and named places, and names a person added on campus, each citing its source; served read-only; changed only by pull request. No one's location is asked, sent or kept |
| Student profile | `student.profiles` | university and campus (data-pack ids); owner-only |
| My money | `student.money_settings`, `income_sources`, `expected_payments`, `spending_entries` | the student's own entries in integer cents: balance, essentials, life-fund reserve, expected income, one spending number per day. Owner-only; no rep or admin view. No bank or NSFAS details, and nothing moves money. Spending is kept for a rolling year |
| My marks | `student.modules`, `student.assessments` | the student's modules, assessment weights and marks. Owner-only; no rep or admin view. Deleted for real when the student deletes them |
| Classes | `classes.classes`, `class_members`, `rep_invites` | a class holds no personal data (who made it isn't kept). Members are never listed, not even to reps: views give counts. Rep codes are kept as SHA-256 hashes only, work once and expire after 48 hours. A class is deleted after its academic year and one more |
| Announcements | `classes.announcements`, `event_candidates` | pasted text may hold personal data: only the class's reps and the student who sent it see it. The text is deleted 30 days after a rep confirms or discards it; an announcement nobody decides on goes after 60 days; a candidate goes when it's decided |
| Verified events | `classes.class_events`, `event_changes` | tests and deadlines a rep confirmed, and each change to them. Who confirmed or changed one is kept as a user id that's never returned, and cleared when that account goes |
| Demo accounts | `identity.users` (`is_demo`), `platform.demo_accounts` | three fictional students, made only by `flask seed`; their shared password comes from `DEMO_PASSWORD`, never the repo; their data is rebuilt every day |
| WhatsApp links | `classes.whatsapp_links`, `whatsapp_link_codes`, `whatsapp_seen` | a linked number is kept only as HMAC-SHA256 with a server key (`WHATSAPP_PHONE_KEY`), never the number; a link code only as its HMAC, once, for 10 minutes; message ids as HMACs for 48 hours. Owner-only; at most 5 numbers per account; in the export (how many and since when) and deleted with the account (ON DELETE CASCADE). No money, marks or private data is ever sent over WhatsApp |
| Flags | `classes.event_flags` | one per student per event, with a reason from a fixed list (no free text). Reps see how many and which reasons, never who. Kept 12 months |

## Threats and controls

| Threat | Control | Where |
|---|---|---|
| Stolen or guessed password | bcrypt hashing; 5 wrong passwords lock the account for 15 minutes; rate limits per IP and per IP + email; a new phone needs a 6-digit code from the email (two factors) | `domains/identity/auth/services/auth_service.py`, `auth/rate_limit/policies.py`, `auth/models/trusted_phone.py` |
| Google sign-in abused | the backend verifies every Google ID token itself (Google's signature, issuer, expiry, our web client as its audience, a verified email); an email with a password account is never merged silently (the password links it once); an unverified email sign-up is taken over only by the Google-proven owner, and its password is deleted (pre-hijack defence); a new account needs the same 18-or-older and consent boxes. The app keeps the token in memory for the next step only, never stored or logged. Closing or deleting a Google-only account needs a fresh Google sign-in with the same linked Google account; a password account still needs its password | `identity/auth/services/google_verifier.py`, `auth_service.google_sign_in`, `_require_owner`; `frontend/mobile/src/features/auth/google/` |
| Stolen token | 15-minute access tokens tied to a live session; rotating refresh tokens, and a reused refresh token revokes the whole session; "sign out other phones" | `auth/models/credentials.py` (Session), `auth/services/jwt_callbacks.py`, `session_service.py` |
| Fishing for which emails have accounts | sign-up, resend and forgot-password give the same answer whatever the email; an existing account's owner gets an email instead | `auth_service.register`, `forgot_password` |
| Reading someone else's data (IDOR) | every query takes the signed-in user from the token; another user's row is the same 404 as a missing one (alerts, profile, every money record, modules and assessments). Alerts and support read only the signed-in student's own records. Classes are reached only through the student's own membership: a class they're not in, and its candidates, events and flags, are the same 404 as ones that don't exist | `core/decorators.py`, each feature's repository, `classes/classes/services/class_service.py` (`membership`) |
| A student acting as a rep | the rep role belongs to one class: a rep elsewhere is a student here. Only a rep confirms (403 for a student's own candidate); a student sees only their own candidates (anyone else's is a 404); a change can only touch an event in the candidate's own class | `classes/events/services/events_service.py`, `class_service.require_rep` |
| Guessing invite or rep codes | invite codes are 8 characters from a 31-character alphabet (about 850 billion codes) and rep codes 10; joining is limited to 20 tries an hour per student; a rep code works once, for 48 hours, and only its hash is stored; a class has at most 3 reps, and codes already waiting can never make a fourth (the class row is locked while reps change) | `classes/classes/` |
| Unverified information shown as fact | nothing goes live without a rep's confirmation, and the engine never publishes; fields it's unsure of are flagged to the rep (`needs_check`); a student's announcement says it's unverified until a rep confirms; the week strip and the life fund count verified events only; the university calendar beside the week is context and never counted | `campus_engine/extraction.py`, `classes/events/` |
| Demo accounts misused, or the judges locked out | only `flask seed` makes one, and never from a real account; they hold fictional data only and say so (`GET /me`: `demo: true`); they skip the new-phone code (the judges can't read the demo inbox) but can't be locked by wrong passwords, so each IP gets 20 sign-in tries an hour on them instead; their password can't be changed, reset or used to close them; everything a visitor changes is undone at the next daily re-base | `identity/auth/services/auth_service.py`, `auth/rate_limit/policies.py` (`DEMO_LOGIN`), `domains/platform/demo/` |
| A wrong crisis number shown as true | crisis lines show only once a person has checked their source (a name, not an agent draft, and a date); until then Support says so. Every other support entry shows its source and when a person last checked it, or "Not verified yet" | `domains/student/alerts/services/alert_service.py` |
| An alert that leaks who did what, or carries someone's words | class updates go to the other members only, with fixed wording: the module, the kind and the dates; never who confirmed it, and never a title or venue someone typed. A student can switch class updates off; security alerts have no switch. A test fails if a template is added without the migration the alerts table's checks need | `platform/notifications/templates.py`, `classes/events/services/event_alerts.py`, `tests/domains/classes/test_class_alerts.py` |
| Wording that labels or frightens a student | alerts describe the situation and end in things to do; they never say "at risk" and never diagnose, and the heavier ones always point to campus counselling (engine tests check the words) | `campus_engine/alerts.py` |
| A forged or replayed WhatsApp message | the webhook is a 404 while the bot is off; Meta's handshake needs our verify token (constant-time compare) and echoes only a plain challenge, as text; every POST must carry `X-Hub-Signature-256`, HMAC-SHA256 of the raw body with the app secret (constant-time compare; 401 otherwise, nothing read); only our own business number's messages are read; a message more than 5 minutes old (or 1 minute ahead) is dropped, and one seen before is answered once (Meta retries); group messages are ignored (private chats only); any other shape is ignored | `classes/whatsapp/services/signature.py`, `whatsapp_service.receive`, `tests/domains/classes/test_whatsapp.py` |
| Someone else's number linked to an account, or acting as a rep from WhatsApp | linking needs a one-time code shown only in the signed-in app: 8 characters from 31 (about 850 billion codes), valid 10 minutes, once, stored as an HMAC, and a new code ends the last; LINK tries are limited to 5 an hour per number, every number to 30 messages a minute and 300 a day. Once linked, the bot acts as that account through the same services as the app: Confirm and Discard go through the rep checks (a student can't confirm; another class's announcement is not found), an incomplete one is finished in the app, and STOP or the app unlinks | `classes/whatsapp/`, `classes/events/services/events_service.py` (`announce_text`, `confirm_as_read`) |
| Phone numbers or messages leaked | numbers are never stored or logged (only their keyed hash); the bot replies to the number a message came from, so it never needs one; message text goes only into the announcement (kept as in the app); a failed reply logs Meta's status code only, never the number, the words or the token; the access token stays in the host's settings | `classes/whatsapp/services/sender.py` |
| Spam through announcements | 60 an hour per student, at most 10 waiting per student in one class, at most 2 000 characters; the text is never logged | `classes/events/constants.py`, `events_service.announce` |
| Marks gone wrong through bad input | percentages from 0 to 100 (a weight above 0); text, booleans, NaN, infinity and huge integers refused; a module's weights can't pass 100% | `domains/student/academics/schemas/`, `services/` |
| Money gone wrong through rounding or bad input | amounts are whole cents, built as shared/finance's `Money`: floats (even 1250.0), text, booleans, NaN and infinity are refused; at most R1 000 000; dates checked against today (no future spending, nothing more than a year back) | `domains/student/money/schemas/`, `services/` |
| A price typed into "Can I afford this?" kept or leaked | `POST /money/afford` stores nothing and logs nothing: the price is used once against the student's own projection and dropped. Strict body (whole positive cents only, no query string), per-student limit | `money/api/routes.py`, `services/money_service.py`, `campus_engine/money_plan.py` |
| Store-card numbers stolen (a barcode is often all a till needs to spend points) | the wallet never leaves the phone: cards are kept in the phone's secure storage (Android Keystore, iOS Keychain), are never sent to the API or logged, and each signed-in student has their own wallet under a hashed key (not their email). The camera is used only while scanning, nothing it sees is kept, and its permission says so. Store names are text only: no logos. At most 12 cards | `frontend/mobile/src/features/wallet/` |
| Keeping money records longer than needed | the student deletes any record for real (no soft delete); spending older than a year is deleted daily | `money_repository.py`, `jobs/forget_old_spending.py` |
| A student can't see or remove what we hold (POPIA) | `GET /me/export` gives everything we hold about the signed-in student: identity's part, then every feature's own section, registered at start-up (`shared/privacy`); nothing about anyone else and no secrets. `DELETE /me`, after the password, deletes the account, and every feature's rows go with it (`ON DELETE CASCADE`). A test fails if a new table points at an account without an export section | `identity/auth/services/auth_service.py` (`export_my_data`, `delete_account`), `src/__init__.py` (`_register_exporters`), `tests/domains/platform/test_privacy.py` |
| Keeping class data longer than needed | daily jobs: announcement text 30 days after a decision, undecided announcements after 60 days, flags after 12 months, expired rep codes, and classes after their academic year and one more (with their members, announcements and events) | `classes/events/jobs/forget_old_announcements.py`, `classes/classes/jobs/forget_old_classes.py` |
| Junk or hostile input | strict schemas refuse unknown fields (422); requests over 1 MB refused (413); JSON deeper than 32 levels refused (400); NUL characters refused anywhere (400). The course finder takes 1 to 9 known subjects, each once, with marks from 0 to 100 (NaN and infinity refused). The funding list takes four known filters, each once (a repeated one is refused), with at most 10 known field ids. Saving a funder takes no body and no query, only a funder the pack lists, and at most 50. The campus map takes one
| A hostile or private PDF sent to the timetable import | `POST /me/timetable/import` needs an account and its own limit (6 a minute, 30 an hour per student). Only a file that starts `%PDF-` under the 1 MB request limit is read, locked PDFs and more than 30 pages are refused, and any reading error is one plain 422, never a stack trace. The PDF is read in memory by pypdf (6.21.2, past every known advisory on 25 Oct 2026: 6.19.0 was replaced on 22 Oct when five advisories about a crafted PDF's parsing work and image decoding were published, and 6.21.1 on 25 Oct for three more) and is never written to disk, stored or logged; the answer is only what the document lists (the exam list's student numbers are dropped) and nothing is saved until the student checks rows and sends them to `/batch`, which takes all or none | `timetable/services/pdf_pages.py`, `import_service.py`, `campus_engine/timetable_import.py` |
optional campus id (lowercase letters, digits and underscores, up to 40 characters), given once. A plan's "today" is the server's date in SAST (or a development preview's test date, below); a client can't send a date | `domains/*/schemas`, `src/__init__.py` (`_register_input_guard`), `config.py` |
| Flooding | a rate limit on every route: per user for signed-in routes (money, marks and saved funding changes 60 a minute, profile and class changes 30, new classes 10 an hour, joining 20 an hour, announcements 60 an hour, WhatsApp link codes 10 an hour), per IP for the WhatsApp webhook (600 a minute: every student's messages come through Meta's servers) and for public ones (the course finder, the points list, the catalogue, first steps, the funding list, the colleges list and check, and the campus maps allow 120 a minute, because a school computer lab shares one address) | `@limiter.limit` on each route; `shared/rate_limit/` |
| A learner's marks kept or leaked (POPIA; learners may be under 18) | the course finder (points, tiers and plan) needs no account, runs no database statement and never logs a mark; refusals never repeat a mark; its rate-limit refusals aren't audited, so no IP address is kept either | `domains/pathways/course_finder/` |
| A learner sorted by race, income or other personal details to "match" funding | the funding list filters only by field, status, kind and stage; a funder's own criteria (some name a population group or a household income) are shown in its words, and the learner decides; nothing is stored or logged, and no database statement runs | `domains/catalogue/funding/` |
| A student's whereabouts tracked through the map | the map route takes no location: `near`, or any field but `campus`, is refused (422). It needs no account, runs no database statement and stores nothing. A "you are here" dot, if it's added, keeps the phone's location on the phone (OPEN_QUESTIONS, "Campus maps") | `domains/catalogue/maps/` |
| Map data used against its licence | every map answer carries the credit OpenStreetMap asks for and names and links the ODbL, and so does every map file; our copy, with the names we add, stays under the ODbL and is listed in REUSE.md | `campus_engine/maps.py`, `scripts/fetch_osm_maps.py`, `REUSE.md` |
| Wrong facts shown as true | every pack is validated as it loads: each fact's source must exist, subject keys must be known, levels 1 to 8, percentages 0 to 100; application windows must close after they open, late windows must follow the last closing date, and closing dates may name only programmes that exist; calendar periods must end after they start and name only campuses that exist; field tags must be known, and a funder may name only universities we have; map points must lie in South Africa, each place's centre on its
campus, and a map may name only campuses its university's pack lists; a building without a name is drawn as a
shape, never named by guess; a funder's page that says "open" without dates counts for 14 days, then asks the learner to check; a date nobody has published shows as not published, never guessed; a pack nobody has checked yet is served with "Not yet confirmed by the team" | `campus_engine/schemas.py`, `campus_engine/applications.py`, `domains/catalogue/` |
| Learners sent to fake application or payment pages | packs link only to official pages, over https (validation refuses anything else); NSFAS's own warnings are shown ("Never pay anyone to apply"); bank account numbers are left out of the packs, and the app never takes a payment or asks for bank details | `campus_engine/schemas.py` (`Applications`), `backend/data/` |
| Children's personal information (POPIA) | accounts require confirming 18 or older; only the JSON value `true` is accepted; recorded with the consent | `auth/schemas/auth_schemas.py`, `accounts/services/account_service.py` |
| Collecting too much | sign-up takes email, password, consent and the age confirmation only; any other field is refused | `RegisterSchema` |
| Wrong dates shown because of a preview's test date | `CAMPUS_PREVIEW_TODAY` is read by the development settings only. Production, and any environment but development, refuses to start with it set, and anything but a plain date stops the start; tests ignore it. A plan worked out on a test date says so (`test_date`) and the app shows a note. A client can never send a date | `src/shared/clock/clock.py`, `config.py`, `tests/shared/test_clock.py` |
| Secrets leaking | secrets only in git-ignored `.env`; the app refuses to start with missing or short (< 32 characters) keys; codes and reset links are never logged; production refuses the fake mail provider and requires an https base address | `config.py`, `shared/email/` |
| Tampering with history | the database refuses UPDATE, DELETE and TRUNCATE on the audit trail (trigger) | `migrations/versions/0001_baseline.py` |
| Spoofed client IP | forwarding headers are ignored unless the server sits behind Cloudflare alone (`BEHIND_CLOUDFLARE`) | `shared/net/client_ip.py` |
| Browser attacks on API responses | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`; CORS in development, and in production only for the https addresses in `CORS_ORIGINS` (none by default; `*` and plain http refused at start-up) | `src/__init__.py`, `src/config.py` |
| Background jobs running twice, or racing a migration | only the process holding a PostgreSQL advisory lock runs the jobs, across every worker and instance; a one-off command (`flask db upgrade`, `flask seed`) never starts them | `src/master_scheduler/lock.py`, `trigger.py`, `src/__init__.py` (`_one_off_command`) |
| A container that leaks or can do too much | the image runs as a normal user, holds no `.env` and no tests, and starts in production mode (which refuses weak secrets and fake email); the access log has no IP address and no query string | `backend/Dockerfile`, `.dockerignore`, `gunicorn.conf.py` |
| Design rot | architecture tests: the engine imports no app, web or database code; routes never call the engine (services do); `shared/` never imports a domain; identity stays sealed; finance stays a leaf; every route has a rate limit | `backend/tests/architecture/` |
| Vulnerable dependencies, committed secrets | CI runs `pip-audit` and an npm audit gate (any high or critical advisory fails, except the accepted ones below), and a gitleaks scan, on every pull request | `.github/workflows/ci.yml`, `frontend/mobile/scripts/check-audit.mjs` |

## Test evidence (M5)

Backend: **1,434 tests pass** on PostgreSQL 16 (22 Oct 2026), including:

| Tests | What they prove |
|---|---|
| `tests/domains/identity/test_hostile_input.py` | bad emails, over-long and emoji passwords, wrong types, broken and deeply nested bodies, NUL characters, unknown fields (including an ID number) and every non-`true` 18-or-older value are refused, never a crash |
| `tests/domains/identity/test_auth.py`, `test_two_factor.py`, `test_account_security.py` | sign-up, verification, lockout, the same answer for unknown emails, refresh rotation and reuse detection, new-phone codes, sign-out everywhere, the data export holds no secrets |
| `tests/domains/identity/test_rate_limits.py`, `tests/shared/test_client_ip.py` | limits trigger, forged forwarding headers don't buy more tries |
| `tests/domains/platform/test_notifications*.py` | owner-only alerts (404 for someone else's), strict queries, per-user limits |
| `tests/domains/security/test_audit.py` | audit events are written, and the database refuses to edit or delete them |
| `tests/shared/test_email.py` | sign-in codes never reach the logs; production refuses fake email |
| `tests/shared/test_clock.py` | a preview's test date is used and can be told apart; anything but a plain date stops the start; production and unknown environments refuse one; tests ignore it |
| `tests/domains/catalogue/test_universities_api.py` | the catalogue is public and read-only, labels unchecked packs, answers 404 for unknown universities, refuses query parameters and is limited per IP |
| `tests/domains/pathways/test_course_finder_api.py` | the brief's M1 check (the strong SMU learner's plan), with reasons, a source and the check status on every card |
| `tests/domains/pathways/test_course_finder_api.py` (how to apply, points) | on a fixed date, each choice's application status, the dates still ahead (NSFAS first), each university's fee and documents, and NSFAS, all with sources and the check status; the points at every university in name order |
| `tests/domains/catalogue/test_maps_api.py` | every campus in the pack's order, with the unmapped ones saying so; one campus at a time; 404s for an unknown university or campus, never repeating it; empty, upper-case, over-long, repeated, location (`near`) and unknown queries refused; the credit and the licence in every answer; no database statement runs; limited per IP |
| `tests/domains/catalogue/test_colleges_api.py` | the colleges list's counts, filters and pages; a search by trade (electrician); one college in full with its sources, a TVET college's occupational qualifications, a cancelled college with DHET's warning signs; "is this college registered?" for a bogus name, a registration number and a name we don't have (never called bogus); 404 for an unknown college without repeating it; unknown filters, short, over-long, repeated or control-character searches refused; a NUL refused before any route; no database statement runs and no search reaches the logs; limited per IP |
| `tests/domains/catalogue/test_funding_api.py` | on a fixed date, the funding list's counts, order (open first, soonest closing first) and filters; one funder in full with its sources; an automatic award with no dates; 404 for an unknown funder without repeating it; unknown, personal (income, race), repeated, empty or over-long filters refused; no database statement runs; limited per IP |
| `tests/domains/pathways/test_course_finder_api.py` (funding) | each plan choice shows up to five funders for its fields, for first-years, usable at its university; NSFAS once for the whole plan; no bursary dates in the plan's own list |
| `tests/domains/catalogue/test_universities_api.py` (first steps) | on a fixed date, a new student's steps from accepting an offer to the first lecture, dates not yet published said to be so, 404 for an unknown university, no query parameters, limited per IP |
| `tests/domains/pathways/test_course_finder_hostile.py` | odd bodies, impossible marks (out of range, NaN, infinity, text), repeated or unknown subjects, ten subjects, unknown fields (including an ID number, a date or a grade), huge and deeply nested bodies are refused, for the points list too; no database statement runs and no mark reaches a log during a request; limited per IP |
| `tests/domains/student/test_profile.py` | university and campus checked against the packs; unknown fields (an ID number, race) refused; each student sees only their own profile; limited per student |
| `tests/domains/student/test_money.py` | settings, income becoming expected payments, "received?" taps, one spending number per day, a balance that stays current, and the brief's M3 check (the allowance-funded persona runs short, the life fund pauses, "late" moves the payment 14 days) |
| `tests/domains/student/test_money_hostile.py` | amounts that aren't whole cents, NaN and infinity, impossible dates, unknown fields (an ID or bank number, an NSFAS password), another student's rows (404), at most ten income sources, per-student limits, and old spending deleted |
| `tests/domains/student/test_academics.py` | My marks: the engine's standing and projection for a persona's module, weights short of 100% counted as still to come, weights never past 100%, odd numbers (text, booleans, NaN, a 400-digit integer) and unknown fields refused, another student's modules and assessments (404), per-student limits |
| `tests/domains/classes/test_classes.py` | classes and invite codes, rep codes bringing in up to 3 reps (used once, expiring, hashed, never a fourth), only a rep makes rep codes, nobody ever listed, odd input refused, joining slowed to 20 tries an hour, old classes and expired codes deleted |
| `tests/domains/classes/test_events.py` | the brief's M4 checks: a student's announcement stays unverified until a rep confirms it; a change message updates the event and writes `event_changes` rows; flags show reps counts, never who; the week strip with the university calendar; and the brief's M3 check that needed the week: the self-funded persona's heavy week makes his life fund amber |
| `tests/hosting/test_hosting.py` | one process holds the scheduler's lock, the scheduler starts only with it and gives it back, one-off commands never start it, the demo's re-base runs at start; gunicorn runs one process and logs no IP or query string; the container runs as a normal user and keeps secrets out; production allows browsers only from named https addresses. The image itself was also built and run twice against an empty database: migrations ran, both answered the health check, and only one ran the jobs |
| `tests/domains/classes/test_class_alerts.py` | classmates told once about a new, moved, changed or cancelled event, the rep and outsiders never; no names, titles or venues in the words; switches off and on, each student's own; odd switch changes refused; the export has the switches; the database allows every template |
| `tests/domains/classes/test_events_hostile.py` | odd announcements and confirmations (a "verified" flag, impossible times, dates a year out), a rep's role not carried into another class, other classes' candidates and events (404), floods, and old announcement text and flags deleted |
| `tests/domains/student/test_saved_funding.py` | saving, seeing and unsaving funders with today's status; a funder the pack doesn't list (404, nothing kept, the id not repeated); another student's list never seen or changed; bodies and queries refused (income, race, lists, text); the cap; per-student limits; the alerts: when a saved funder opens after it was saved, a week and a day before it closes, each once, none once closed, unsaved or switched off, and naming only the funder and its dates |
| `tests/domains/student/test_timetable_api.py` | adding, changing and removing classes read back with the week in words and clashes; another student's class is a 404 and stays untouched; signed out refused; odd modules, kinds, weekdays (strings, booleans), times (format, 5-minute steps, 06:00 to 22:00, end before start), long or multi-line venues, blank names and unknown fields refused; at most 60 classes; in the export; limited per student |
| `tests/domains/student/test_timetable_import_api.py` | a made-up week grid and exam list PDF are read back and nothing is saved; student numbers aren't passed on; non-PDFs, garbage after `%PDF-`, 31 pages, a file over 1 MB (413), a missing or second file, another field name, an unknown layout or form field, a JSON body and a query string refused; signed out refused; the import's own 6-a-minute limit; batches save all or none, replace clears first, stay within 60 classes or 40 exams, refuse unknown fields and a non-boolean replace; exams read back with the next one and clashes, another student's exam is a 404, odd exams refused, in the export |
| `tests/engine/test_timetable_import.py` | back-to-back periods merge into one class; practicals and tutorials read; a code later in a line is a venue; a line without a code continues the class; touching pieces join; a venue spelt two ways is one class; rows and columns fall back to halfway without drawn lines; no grid or exam list says so; exam papers once each, without student numbers, with impossible dates and lengths left out; exams in words |
| `tests/domains/student/test_alerts_support.py` | the personas' alerts (a combined alert for short money and a heavy week ahead, a heavy-week alert with the campus's own tutoring and counselling), a module out of reach, another student's alerts never shown; every kind of support for a campus, "Not verified yet" where the pack has none, crisis lines held back until a person checks them; cheap things for the campus only |
| `tests/domains/platform/test_privacy.py` | the export holds every feature's data and nothing of anyone else's; `DELETE /me` needs the password, leaves no row behind in any table, signs the student out everywhere, keeps the class's events nameless and touches no one else; demo accounts refused; odd requests refused; limited; every table that points at an account has an export section |
| `tests/domains/platform/test_demo.py` | `flask seed` (a strong password from the environment, never echoed; a real account never converted), demo sign-in without the code, no lockout, no password change, reset or closing, the stricter demo limit, the personas built as written, and the daily re-base moving every date and undoing what visitors changed |
| `tests/architecture/` | the boundaries above, including every route having a rate limit and routes never calling the engine |
| `tests/engine/` | 355 engine tests, 99% coverage from the engine and architecture tests alone (the floor is 80%), including data-pack validation, spot checks of the shipped packs against their sources, every application status on either side of each date, every first step's status either side of its dates, every funder's status (including a page that says "open" or "closed" without dates), the funding list's order, filters and matches, saved funding's reminders, the campus maps (their sources, every point in South Africa and on its campus, each campus as the map screen sees it, support placed only on a building its contact names, and OpenStreetMap's answers and campus names read offline), and 57 labelled class messages (new events, moved and cancelled, mixed languages, dates to check: several dates in one message, ranges, bare hours) |

App: TypeScript check, ESLint (no warnings) and Jest pass, including a test of the exact sign-up request.

## Security sweep 1 (21 Oct 2026)

Before the hackathon weekend we attacked our own system, only ever a copy on our own computer: the API run with the
production config (HSTS, strict CORS, real-looking keys made up for the run, mail pointed at a closed port) on
127.0.0.1, against our own sandbox database. The live server got one `GET /ping` to read its headers, nothing more.

| Tool | What it covered | Result |
|---|---|---|
| Bandit 1.9.4 | the backend's code (`src`, `campus_engine`, `scripts`), 17,560 lines | 27 findings, all reviewed: 25 low (event names and rate limits containing the word "password" or "token"; two `assert`s that only narrow types), and two false positives (the plain-text email templates aren't HTML-escaped because they are never HTML; a data script opens fixed https addresses), which carry `# nosec` with the reason above them. **Now in CI**: any medium or high finding fails the build. |
| Semgrep 1.140 (`p/python`, `p/flask`, `p/typescript`, `p/react`, `p/secrets`) | backend and app code, 698 files | 7 findings, all false positives: six log lines named after tokens or passwords that log only ids, a masked email and a reason; and the plain-text email templates again |
| pip-audit, npm audit | the backend's and app's dependencies | none for the backend (PyJWT's PYSEC-2026-4146 is no longer reported, so CI ignores nothing now); for the app, the two accepted advisories below and nothing else high or critical |
| gitleaks 8.28 | every commit on every branch | nothing beyond the three reviewed false positives in `.gitleaksignore` |
| Our pen test, [`backend/scripts/security/pentest_local.py`](../backend/scripts/security/pentest_local.py) | 105 attacks on the running API (below) | **105 pass** after the fixes below (103 before) |
| OWASP ZAP 2.16.1 baseline | the API and the password reset page | no failures; warnings below |

What the pen test tries, signed in as two demo personas (A and B) and with one throwaway account per run:

- **Tokens:** none, garbage, `alg: none`, signed with a guessed key, someone else's id or a later expiry in the
  payload, a refresh token used as an access token and the other way round; refresh rotation (a used refresh token
  shown again ends the whole session, and its access tokens stop); sign-out stops both tokens and leaves other
  sessions working.
- **Someone else's data (IDOR):** A creates a goal, income source, plan, exam, class, module and assessment; B tries to
  change and delete each by its id (also A's assessment through B's own module, A's expected payment, and made-up
  notification and candidate ids). Every try is a 404, nothing of A's changes, and none of it appears in B's lists or
  data export. The owner then deletes everything.
- **Mass assignment:** `user_id`, `is_demo`, `email`, a chosen `id` and unknown query fields are refused.
- **Hostile input:** broken JSON, a list for an object, JSON nested 50,000 deep, a 2 MB body (413), the wrong content
  type, amounts of 10^30, negative, fractional, text or `true`, 30 February, 25:99, a NUL byte, path traversal and SQL
  in ids, SQL in a title (stored as plain text), SQL in a search, a script in the reset page's link (not echoed).
- **PDF import:** not a PDF, a cut-off PDF, 400 pages, 2 MB, no layout, an extra field, no file, signed out.
- **Accounts:** registering a taken email, a wrong password and an unknown email, and forgot-password for a real and an
  unknown email each look the same; the 18-or-older box must be exactly `true`; 5 wrong passwords lock the account;
  the login and email-code limits trigger; the judges' demo password can't be changed and demo accounts can't be
  closed.
- **Everywhere:** security headers on every answer, JSON 404 and 405 (never 500), a stranger's website refused by CORS,
  `/ping` limited, and no answer ever showing a traceback, SQL or a driver name.

To run it again, start the API as production on this computer, then
`PENTEST_PASSWORD=<demo password> python scripts/security/pentest_local.py http://127.0.0.1:<port>` (it refuses any
other host). Use a freshly started server: the per-hour limits on register and forgot-password rightly catch a
second run.

### Found and fixed

| Finding | Severity | Fix |
|---|---|---|
| While an account was locked, the right password got `423 ACCOUNT_LOCKED` and a wrong one `401`, so a guesser learned each correct guess during the lock: 5 tries a minute instead of 5 per 15 minutes | Medium | every try during a lock gets the same generic answer, which now says sign-in pauses after several wrong tries; the owner learns of the lock from the in-app alert; the audit record notes whether the password was right, for investigation (`test_while_locked_the_right_password_looks_like_a_wrong_one`) |
| Deleting a module that still had assessments was a 500 (SQLAlchemy blanked the assessments' `module_id` instead of letting the database cascade) | Low: a crash, no data exposed | the relationship leaves it to `ON DELETE CASCADE` (`test_deleting_a_module_takes_its_marks_with_it`) |
| No Content-Security-Policy | Low (hardening) | API answers: `default-src 'none'; frame-ancestors 'none'; base-uri 'none'`. The reset page: only its own style and script, by a fresh nonce each time, and its form posts only to itself |
| ZAP: no Permissions-Policy, no cross-origin isolation | Low (hardening) | `Permissions-Policy` turns off camera, microphone, location and payment; `Cross-Origin-Opener-Policy` and `Cross-Origin-Resource-Policy` are `same-origin` (the API serves no images, so nothing the app loads is blocked) |

ZAP warnings we accept: the version in the `Server` header comes from the local development server only (the app
removes it; live, Cloudflare puts its own); "non-storable content" is our `no-store`, on purpose; the reset ticket is
in the email link's address by design (one use, 30 minutes, no referrer, not cached, not in gunicorn's logs).

### The APK (MobSF 4.5.3, 21 Oct 2026)

The signed preview APK (EAS build of `7a0e134`, the code merged as #62) was scanned with MobSF, run in Docker on our
own computer. No trackers. Our own JavaScript holds no secret: the demo password, mail and database settings, API
keys and local addresses each appear 0 times in it (it holds only the public API address).

| MobSF finding | Verdict |
|---|---|
| Backups allowed (`allowBackup=true`) | **Fixed**: `allowBackup: false`. Tokens and wallet cards are in SecureStore anyway |
| Permissions no feature uses: draw over other apps, storage, fingerprint and face unlock (added by libraries) | **Fixed**: `blockedPermissions` strips them; the app keeps camera (the wallet's barcode scan), internet, network state and vibrate |
| Installs on Android 7 (minSdk 24), which no longer gets security updates | Accepted: many students' phones are old, and access is the point of the app. The server checks everything; the phone holds only the student's own data |
| WebView debugging, file access in a WebView, MD5, "hardcoded" strings, `taskAffinity`, the profile installer's receiver | Library code (Expo's error screen and WebView, its file cache, React Native, AndroidX), none of it ours; the "secrets" are byte tables and compiled C++ names |

The fixes take effect from the next build. The first APK was 140 MB, 58 MB of it native code for x86 processors
(PC emulators); from the next build it carries phone processors only (64-bit and 32-bit ARM).

### Open, for the team

- **Rate limits on Render may count every visitor as one.** The live API sits behind Render's proxy and Cloudflare
  (`Server: cloudflare` and `CF-RAY` in its answers). With `BEHIND_CLOUDFLARE` off, the app reads the proxy's address
  as the client's, so per-IP limits are probably shared by everyone: all the judges together would get 20 demo
  sign-ins an hour. The fix is a setting, not code: `BEHIND_CLOUDFLARE=true` on Render, so the app reads
  `CF-Connecting-IP`, which Cloudflare sets itself. It's a hosting change, so Rinsuna decides. Afterwards, check that
  the header can't be forged: a few `GET /ping` calls, each with a different made-up `CF-Connecting-IP`, must count
  down one shared `X-RateLimit-Remaining` rather than each starting fresh.
  **Decided (Rinsuna, 21 Oct 2026): yes, the judges should have as much access as possible.** Argon turns it on
  with the next deploy. In the same spirit, a demo persona's right password no longer counts towards any limit:
  only wrong ones count (20 an hour per address and persona), plus a flood guard of 60 sign-ins a minute, since
  each one writes a session row (`test_judges_can_sign_in_as_often_as_they_need`).

## Accepted dependency risks

Checked 9 Oct 2026. Werkzeug (3.1.9) and PyJWT (2.15.0) were upgraded and the Expo SDK 57 packages patched, which
cleared every other advisory. These remain because no fixed release exists yet; each has a review date, and CI fails
once it passes.

| Advisory | Package | Why it's accepted for now | Review by |
|---|---|---|---|
| GHSA-vfj7-8cjw-p6xm | braces | denial of service through nested glob patterns, reached only through build tooling (Metro, Jest) with our own patterns; not in the app or web bundle | 6 Nov 2026 |
| GHSA-mrhx-c7xc-m3w5 | zod | memory exhaustion on oversized input, reached only through the Expo CLI (`@expo/cli` pins zod 3.25.76) that builds the app on the developer's computer; not in the app or web bundle; the only offered fix is an old Expo | 8 Nov 2026 |
| GHSA-86w9-cpqp-85rv | node-forge | signature-check flaw in the Expo CLI's code-signing helper, which we don't use; not in the app or web bundle | 6 Nov 2026 |

The `.gitleaksignore` file holds three reviewed false positives: the testing config's placeholder JWT key, and a
storage key's name in two files on the closed, unmerged tabs branch. PyJWT's PYSEC-2026-4146, accepted on 9 Oct,
is no longer reported (21 Oct).

## Known gaps

Tracked with options in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md):

- The audit trail (inherited) stores full email addresses and IP addresses with no deletion rule.
- `DELETE /me` deletes an account and everything it holds, but "Close my account" only deactivates one, and nothing
  removes a closed account's data yet (OPEN_QUESTIONS, "Retention").
- Neither the export nor deleting reaches the audit trail's security records, which nothing may change; they keep
  the email and IP address of past sign-ins (OPEN_QUESTIONS). The record of a deletion keeps no email.
- Reps see how many students flagged an event from the first flag (never who). We read CLAUDE.md's 5-student rule
  as covering aggregates of marks and money; the team confirms or changes this in OPEN_QUESTIONS.
- A student's announcement text is seen by the class's reps by design: it's how they check it.
- The demo accounts' password is shared with the judges by design, so those accounts hold fictional data only.
- Crisis lines stay hidden until a person checks them: every pack's are still agent drafts (OPEN_QUESTIONS).
- Rate-limit counters live in memory: correct for one server process only, which is what the container runs
  (`gunicorn.conf.py`). More processes need Redis first (DEPLOY.md).
- The Privacy Policy and Terms are drafts awaiting legal review.
