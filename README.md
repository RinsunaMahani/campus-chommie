# Campus Chommie

A mobile app that takes a South African student from choosing a course to graduating. The student picks their
university and the app adapts to it: programmes and admission rules, the academic calendar, allowance rhythm, campus
support and student life. Our entry for the FNB App of the Year Hackathon 2026 ("Access to higher education"), by
Team PR (Mandla Baloyi and Rinsuna Mahani).

**Status: M0 (foundation).** Sign-up (with the 18-or-older confirmation and consent), email verification, two-factor
sign-in, account security and sign-out work against the API. The engine and the SMU data pack are in, with their tests.
The features come next: course finder (M1 and M2), profile and money (M3), my week (M4), alerts and support (M5).

## What's where

```text
backend/
  campus_engine/         the pure Python engine: matching, plans, workload, runway, forecasts, extraction
  data/universities/     one YAML data pack per university (smu.yaml; _template.yaml for new ones)
  data/demo/             fictional demo personas
  config.yaml            every engine threshold and weight
  src/                   the Flask API: core/, shared/, domains/<area>/<feature>/, master_scheduler/
  migrations/            Alembic (one baseline so far)
  scripts/               validate_data.py (data packs), setup_db.sql and make_env.py (local setup)
  tests/                 engine/ and architecture/ run without a database; the rest use PostgreSQL
frontend/mobile/         the Expo app (Android and web): src/app (routes), src/features, src/shared
docs/                    OPEN_QUESTIONS.md (gaps for the team), SECURITY.md (threat model and controls)
CLAUDE.md                rules for everyone working here, people and coding agents
REUSE.md                 what came from our earlier project, and the permissions to confirm
```

## Backend

Needs Python 3.12 and PostgreSQL 16 or newer (your own install, or Docker).

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

**Database, option A: your own PostgreSQL.** Run once, as the postgres admin user, from the repo root (on Windows,
psql is in `C:\Program Files\PostgreSQL\<version>\bin`; add `-p 5433` if that version listens on another port):

```bash
psql -U postgres -h localhost -v app_password="CHOOSE-A-PASSWORD" -f backend/scripts/setup_db.sql
```

**Database, option B: Docker.**

```bash
docker run -d --name campus-chommie-pg -e POSTGRES_USER=campus_chommie -e POSTGRES_PASSWORD=CHOOSE-A-PASSWORD \
  -e POSTGRES_DB=campus_chommie_dev -p 127.0.0.1:5434:5432 postgres:16
docker exec campus-chommie-pg createdb -U campus_chommie campus_chommie_test
```

Then write `backend/.env` (git-ignored) and build the tables:

```bash
python scripts/make_env.py        # asks for the database password, generates the secret keys
# edit backend/.env: POSTGRES_PORT if not 5432 (5434 for option B), and the MAIL_* settings
flask db upgrade
python app.py                      # http://localhost:5000/api/v1/health
```

Sign-up and new-phone sign-in send a 6-digit code by email, so real codes need the `MAIL_*` settings in
`backend/.env` (for example a Gmail account with an app password). Codes are never written to any log. The tests use a
fake mail provider and need none of this.

**Demo accounts for the judges.** Set `DEMO_PASSWORD` in `backend/.env` (your own choice; never commit it), then:

```bash
flask seed                         # safe to run again
```

This makes three fictional students from `backend/data/demo/personas.yaml`, entered through the real services:
`naledi.demo@example.com` (short money, a heavy week ahead), `sipho.demo@example.com` (a heavy week now) and
`thabo.demo@example.com` (a class rep with a classmate's message waiting). A scheduler job re-bases them every day
from 02:00 SAST, so their dates stay current. They skip the new-phone code, can't be locked by wrong passwords and
can't change their password; `GET /me` says `demo: true`, and the app shows "Demo data: fictional student".

**Course finder (no account; nothing stored).** All under `/api/v1`, in the usual envelope:

| Endpoint | Body | Answer |
|---|---|---|
| `GET /universities` | none | each data pack: id, name, and whether a person has checked it (`confirmed`, `notice`) |
| `GET /universities/<id>` | none | the whole pack: programmes, requirements, routes, application dates, campuses, calendar, money dates, support and sources |
| `GET /universities/<id>/first-steps` | none | from accepting an offer to the first lecture, on today's date (SAST) |
| `POST /pathways/points` | `{marks: [{subject, percent}]}` | the learner's points at every university, each by its own rule, and how many programmes they meet |
| `POST /pathways/assess` | `{university, marks: [{subject, percent}]}` | every programme at that university, best tiers first, each with its reasons and source |
| `POST /pathways/plan` | `{university, goal, marks: [...]}` | the three-choice plan: the goal, a route into it and a safer related choice, and how to apply (below) |

A learner sends 1 to 9 subjects, each once, with marks from 0 to 100. Subject keys are those in
`campus_engine/schemas.py` (`SUBJECTS`) plus `another_subject_1` to `another_subject_3` for subjects no rule names.

**How to apply**, on today's date in South Africa (`campus_engine/applications.py`):
- Each slot in a plan has `apply`: one entry per intake (next year's and the year after, plus this year's while a
  late window is still ahead). Each says whether applications are open, closing soon, closed or not published yet,
  with its dates, days left, plain-words `lines` and `source_url`.
- `plan.apply` has the date it used (`today`), every date still ahead (`deadlines`, soonest first), each
  university's fee, documents and next steps (`universities`), national funding (`funding`: NSFAS) and `notes`.
- Dates come from each pack's `applications` section and from `backend/data/national/funding.yaml`. A date nobody
  has published shows as not published, never guessed.

**A student's own profile and money (signed in; owner-only).** Amounts are integer cents:

| Endpoint | Body | Answer |
|---|---|---|
| `GET` / `PUT /me/profile` | `{university, campus}` | university and campus (checked against the packs), and the 18-or-older confirmation from sign-up |
| `GET` / `PUT /money/settings` | `{balance_cents, balance_on, essentials_per_day_cents, life_fund_reserve_cents}` | the balance and the day it was true, essentials a day, the life-fund reserve |
| `GET` / `POST /money/income-sources`, `PUT` / `DELETE /money/income-sources/<id>` | `{label, amount_cents, day_of_month or expected_on, reliability}` | money the student expects, monthly or once |
| `GET /money/payments`, `PATCH /money/payments/<id>` | `{expected_on?, amount_cents?, received?}` | expected payments from a month back to 120 days ahead; move one, change it, or tap "received" |
| `GET /money/spending?days=30`, `PUT` / `DELETE /money/spending/<YYYY-MM-DD>` | `{amount_cents}` | one spending number per day |
| `GET /money/summary?late=true` | none | the balance now, the spending pace, the runway (with its range), safe to spend, the life fund (which reads this week's load), the next payment; `late` plans for it arriving two weeks late |

**My marks (signed in; owner-only).** Weights and marks are percentages:

| Endpoint | Body | Answer |
|---|---|---|
| `GET` / `POST /academics/modules` | `{code, name?, target?}` | the student's modules, each with its assessments, `standing` (where they stand, and the average needed on the rest for their target), `projection` (a projected final mark with a likely range) and plain-words `lines`. The target defaults to 50 |
| `PUT` / `DELETE /academics/modules/<id>` | `{code, name, target}` | change a module, or delete it with its assessments |
| `POST /academics/modules/<id>/assessments`, `PUT` / `DELETE .../assessments/<aid>` | `{name, weight, mark?}` | weights add up to at most 100 (a weight not entered yet counts as still to come); a mark from 0 to 100, or null until it's written |

**Classes, reps and verified events (signed in).** A class is one module on one campus in one year. Only a rep's
confirmation makes an event *verified*; until then a student's announcement stays unverified. Nobody is ever listed:
views give counts.

| Endpoint | Body | Answer |
|---|---|---|
| `POST /classes` | `{university, campus, module_code, module_name?, year}` | a new class with its `invite_code`; you're its first rep |
| `POST /classes/join` | `{code}` | an invite code joins the class; a rep code makes you a rep (up to 3 per class) |
| `GET /classes/mine` | none | your classes, your `role`, and how many `members` and `reps` |
| `POST /classes/<id>/reps` | none | rep only: a one-time rep code for the next rep, valid 48 hours, shown once |
| `DELETE /classes/<id>/membership` | none | leave the class |
| `POST /classes/<id>/announcements` | `{text, sent_on?}` | a candidate: what the engine read (`read_as`), its `confidence`, the fields to check (`needs_check`), the confirm form's starting values (`proposed`) and `lines`. For a "moved" or "cancelled" message, `changes_event` is the event it most likely changes |
| `GET /classes/<id>/candidates` | none | waiting for a rep: all of them for a rep, only your own otherwise |
| `POST /candidates/<id>/confirm` | `{change, event_id?, kind, title, on, at, venue, weighting}` | rep only: a new verified event, or the change to one (each changed field is recorded and the `version` goes up), with `lines` |
| `POST /candidates/<id>/discard` | none | a rep turns it down, or the student who sent it takes it back |
| `GET /classes/<id>/events?from=&to=` | none | verified events with their `changes`; reps also get `flags` (how many and why, never who) |
| `POST` / `DELETE /events/<id>/flag` | `{reason}` | `wrong_date`, `wrong_time`, `wrong_venue`, `not_happening`, `duplicate` or `other` |
| `GET /week?weeks=8&from=YYYY-MM-DD` | none | the week strip: each week `Manageable`, `Busy` or `Heavy` (`colour` green, amber or red) with a one-line `reason` and its verified `events`, and beside it the university's `calendar` for the student's campus, which never adds to the score |

The engine reads announcements in English and the Afrikaans words students use for the same things (toets, eksamen,
verskuif, gekanselleer, the months and days); greetings in any language are passed over.

**Alerts, support and cheap things (signed in; worked out on each request, nothing stored):**

| Endpoint | Body | Answer |
|---|---|---|
| `GET /alerts` | none | today's alerts, most pressing first: `combined` (a heavy week in the next 3 weeks while money runs short before the next payment), `heavy_week`, `money`, or `module` (a target out of reach). Each has a `title`, a `message` and `actions`; an action's `target` is `week`, `money`, `cheap_things`, `marks` or `support`, and a support action carries the campus's own `service` when the pack has one |
| `GET /support` | none | every kind of support the brief lists for the student's campus (counselling, crisis lines, financial aid, food support, tutoring, chaplaincy, health, then careers and disability where listed), each with its `services` (contact, hours, source, when a person last checked it) or "Not verified yet". Crisis lines show only once a person has checked them |
| `GET /money/cheap-things` | none | the pack's cheap things near the student's campus, with cost notes, sources and when a person last checked them |

## App

Needs Node 22 or newer.

```bash
cd frontend/mobile
npm install
copy .env.example .env             # macOS/Linux: cp .env.example .env
```

In `.env`, `EXPO_PUBLIC_USE_MOCK_API=true` runs sign-in against a built-in mock (no backend needed);
set it to `false` and point `EXPO_PUBLIC_API_URL` at the backend to use the real API. On a phone, `localhost` is the
phone itself: use your PC's address (for example `http://192.168.1.20:5000/api/v1`).

```bash
npx expo start --web               # in the browser
npx expo start --go                # on a phone with Expo Go; or a development build (EAS) with `npm start`
npx expo export --platform web     # the web build, into dist/
```

**An installable Android app (preview APK)**, for people who aren't near the PC. The Expo project is
`@rinsunamahani/campus-chommie`; sign in to Expo with access to it (`npx eas-cli login`), then:

```bash
npx eas-cli build --profile preview --platform android   # built on Expo's servers, 10 to 30 minutes
```

The build page gives an install link to send to anyone with an Android phone (their phone asks to allow installs from
that source). The preview signs in against the built-in mock (`eas.json`), so it works anywhere with no server, until
the backend is hosted. It holds the app as it was when built: build again to share new screens.

## Checks (CI runs all of these)

```bash
cd backend
python -m pytest -q tests                                        # all backend tests (needs the database)
python -m pytest -q tests/engine tests/architecture --cov=campus_engine --cov-fail-under=80   # no database
python scripts/validate_data.py                                  # data packs: errors fail, warnings list gaps

cd frontend/mobile
npx tsc --noEmit && npx jest && npx expo lint
```

## Licence

All rights reserved, Team PR. See [LICENSE](LICENSE) and [REUSE.md](REUSE.md).
