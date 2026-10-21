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
