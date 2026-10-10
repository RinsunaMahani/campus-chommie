# Handover: start here, Mandla

Written on 9 Oct 2026 and updated on 10 Oct by Rinsuna's coding agent, for Mandla and for Mandla's coding agent. It
covers:
- where the build stands
- what was decided while you were away
- what we need from you
- how your agent picks up M2

The rules are still in [CLAUDE.md](../CLAUDE.md); this file doesn't change them. The brief (`BUILD_BRIEF.md`) isn't in
git, so Mandla has his own copy; the M2 part is quoted below.

## Where things stand

`main` holds only the empty first commit. All work sits in six stacked pull requests:

| PR | Branch | What | Reviewer |
|---|---|---|---|
| #1 | `rinsuna/m0-foundation` | M0: accounts, sign-in, security, notifications, audit, the app shell, the engine starter, CI | Mandla |
| #2 | `rinsuna/university-research` | research notes for UP, TUT and SMU, and the open questions they raise | Rinsuna; Mandla for the F6 and vac-work items |
| #3 | `rinsuna/engine-requirements` | engine: either/or subjects, percentage minimums, per-programme points tables | Rinsuna |
| #4 | `rinsuna/m1-course-finder-api` | the course-finder API and this file | Mandla |
| #5 | `rinsuna/m1-data-packs` | draft UP and TUT packs, the approved SMU changes, and how the plan picks its third choice | Rinsuna; Mandla for the changed M1 check |
| #6 | `rinsuna/m1-how-to-apply` | how to apply, on today's date: each choice's application dates, NSFAS, fees, documents and next steps; notes on NSFAS and on other apps | Rinsuna for the engine and data; Mandla for the plan's new `apply` fields |

**How to merge:**
- Each PR targets the branch below it, so its diff shows only its own work.
- Merge in order: #1 into `main`, then #2, #3, #4, #5 and #6, retargeting each to `main` once the one below has
  merged.
- Use **Create a merge commit**, not squash or rebase, so every commit stays in `main`'s history (CLAUDE.md: never
  rewrite history).

## Decided while you were away

Everything is recorded, with who and when, in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

- **M1 started early** (Fri 9 Oct) as stacked PRs, because the brief gives it only Mon 12 to Tue 13 Oct.
- **Research:** facts for UP, TUT and SMU were read from their official documents ([research/](research/)). No
  person has checked them yet.
- **Engine (#3):** the data-pack schema was extended to hold those rules: either/or subjects with their own minimum
  points, percentage minimums, and a programme's own points table.
- **API (#4):**
  - Packs nobody has checked yet are served, labelled "Not yet confirmed by the team".
  - Learners enter the subjects that admission rules name, plus up to three "another subject" rows.
- **Data:**
  - Rinsuna approved the SMU fact changes.
  - Programmes are tagged as related honestly, and the plan's third choice is the closest related programme the
    learner can count on (#5). So the brief's M1 test changed: for the strong SMU learner, the third choice is
    now UP's BSc Medical Sciences, not SMU's B Rad.
  - TUT counts six subjects until TUT confirms.
  - UP's MBChB route and TUT's selection flags go in as proposed.
- **How to apply (#6, 10 Oct):** the challenge asks us to help learners "complete applications", and nothing did.
  Every plan now says, for each choice, whether applications are open, closing soon, closed or not published yet,
  every date still ahead, each university's fee, documents and next steps, and NSFAS (open until 31 Oct 2026). This
  delivers most of F6 inside the course finder, without a new feature.
- **Proposed, waiting for you** (OPEN_QUESTIONS, "App and accounts"): which intakes a plan shows, and links to
  opportunity sites such as Graduates24. An application directory for all 26 public universities was proposed and
  then paused, because UniApplyForMe already does it well; the time goes to support after acceptance.
- **Other apps:** [research/competitors.md](research/competitors.md) compares UniApplyForMe, UniAPS and others, and
  says where we differ. Worth reading before the deck.

## What we need from you

1. **Review #1, then #4** (app and API are yours). Also read #2's changes to OPEN_QUESTIONS.
2. **Decide F6 "Fund and apply" and the vac-work nudge for M1** (OPEN_QUESTIONS, "App and accounts"): yes, no or
   change. Also there: which intakes a plan shows, "Add these dates to my calendar" and links to opportunity sites.
3. **Your open items in OPEN_QUESTIONS:**
   - demo accounts and the email code (before M5)
   - who owns the Expo/EAS project
   - the package name `za.campuschommie.app` (it can't change after the first Play Store upload)
   - app icon, colours and slogan
   - Google sign-in
   - hosting
   - the email sender
4. **REUSE.md:** confirm the rows that came from TruConnect.
5. **Human deadlines:**
   - **Sonke:** create the team by Tue 20 Oct.
   - **WhatsApp:** set up WhatsApp Business (Meta app, test number) before Fri 23 Oct.
   - **Hackathon:** Fri 23 Oct 08:30 to Sun 25 Oct 17:00 SAST. M6 doesn't start before 08:30 on the Friday.
   - **Submission:** Mon 26 Oct 23:59 SAST.

## Your next build: M2, the Find my course screens (brief: Wed 14 to Thu 15 Oct)

From the brief: "University, then marks (add or remove rows, up to 9), then tier cards, then the three-choice plan and
sources. Add i18n plumbing with English only visible. Acceptance: works at 360 px wide on Android and web. Tier labels
are words, not colour alone. Every card shows its 'why' lines and source. Jest tests cover the tier card and the plan."

The course finder works signed out: the M5 judge flow ends with "use the course finder without an account". So its
route sits outside the protected `(app)` group, reachable from the welcome screen as well as from Home.

The API is in #4, with details in the [README](../README.md), "Course finder":

| Screen | Call | Use |
|---|---|---|
| University | `GET /universities` | `id`, `name`, and `confirmed` and `notice` |
| Tier cards | `POST /pathways/assess` with `{university, marks: [{subject, percent}]}` | `matches`, best tiers first |
| Plan | `POST /pathways/plan` with `{university, goal, marks}` | `plan.goal`, `plan.bridge`, `plan.safe`, `plan.other_routes`, `plan.notes` |
| How to apply | the same plan answer | each slot's `apply`, and `plan.apply`: `deadlines`, `universities`, `funding`, `notes` |

**What the screens must handle:**
- **Cards:**
  - Each card has `tier`, `label`, `points`, `min_points`, `gap`, `failed`, `explanation` (the "why" lines) and
    `source_url`.
  - Bridge slots add `bridge` (`guarantee_label`, `conditions`, `max_places`, `eligibility_note`, `source_url`).
  - Show `label` in words; colour can add to it but never replace it.
  - `tier` is one of `reach`, `meets_minimum`, `competitive`, `not_yet`, `unverified`.
- **Unchecked data:** when `confirmed` is false, show `notice` ("Not yet confirmed by the team.") with the university
  and on each card.
- **Subjects:** offer the keys in `SUBJECTS` (`backend/campus_engine/schemas.py`), each with a display name the app
  owns, plus up to three "Another subject" rows (`another_subject_1` to `another_subject_3`).
- **Repeats:** the API refuses a repeated subject (422). Keep the last mark, show the `duplicate` text and send each
  subject once.
- **Nothing stored:**
  - Don't save marks on the phone (no AsyncStorage or SecureStore) and don't log them.
  - The course finder needs no account (CLAUDE.md: POPIA and minors).
- **Errors:**
  - 404 with `UNIVERSITY_NOT_FOUND` or `PROGRAMME_NOT_FOUND`
  - 422 `VALIDATION_ERROR` with per-field `errors`
  - 429 `RATE_LIMITED` with `Retry-After`
- **How to apply** (#6; README, "How to apply"):
  - **Under each plan card:** the slot's `apply` list, one entry per intake. Show its `heading` ("To start in
    2027"), its `label` in words, and its `lines`. `status` is one of `open`, `closing_soon`, `check`,
    `opens_later`, `late_open`, `late_ahead`, `closed`, `not_published`; `days` and `next_date` drive a countdown.
  - **Dates to remember:** `plan.apply.deadlines`, soonest first, each with `date`, `days`, `text` and `source_url`.
    "Add these dates to my calendar" is your call (OPEN_QUESTIONS).
  - **Each university:** `plan.apply.universities`, with `url`, `fee_cents` (format as rand), `documents.items`,
    `after` and `lines`. Missing facts come as `null` and a "not verified yet" line: show that line, never a blank.
  - **Funding:** `plan.apply.funding` (NSFAS): its `windows` (the 2027 countdown), `who_can_apply`, `documents`,
    `tips` (the eight document mistakes NSFAS sees most) and `warnings` ("Never pay anyone to apply").
  - The app never asks about income, disability or family: it shows NSFAS's own words and links to it.
  - Each university and funder has `confirmed` and `notice`, as on the cards.
- **Ideas from UniApplyForMe**, which Rinsuna tried on 10 Oct (your call): one topic per onboarding screen with a
  review step, deadline cards with a day count, and the level shown as a mark is typed.
  [research/competitors.md](research/competitors.md) lists them, and what we won't copy (race questions, logos,
  paywalls).
- **English text to reuse:** `backend/campus_engine/i18n.py` has the course finder's English strings: the title,
  slot titles, "Nothing you enter here is saved.", the `duplicate` text and the how-to-apply headings. English is the
  only visible language until a fluent speaker signs one off.

## For your agent: how to pick this up

1. **Read first:** [CLAUDE.md](../CLAUDE.md) (AGENTS.md points every agent there), then this file.
2. **Branch:**
   - Start from the top of the stack: `git fetch origin`, then `git checkout rinsuna/m1-how-to-apply`.
   - Branch `mandla/<topic>` from there, for example `mandla/course-finder-screens`.
   - Once #1 to #6 are merged, branch from `main` instead.
3. **Run the API** (README, "Backend"):
   - Use your own PostgreSQL, or Docker (option B uses port 5434).
   - Then `python scripts/make_env.py`, `flask db upgrade` and `python app.py`.
   - Agents use ports 5090 (API) and 8090 (Expo), and never stop someone else's server on 5000 or 8081.
   - Never connect to Rinsuna's or any production database.
4. **Point the app at the API:** in `frontend/mobile/.env`, set `EXPO_PUBLIC_API_URL` (for example
   `http://localhost:5090/api/v1`, or the PC's address from a phone) and `EXPO_PUBLIC_USE_MOCK_API=false`.
5. **Where code goes:**
   - Screens in `frontend/mobile/src/features/<feature>`, routes in `src/app`.
   - Colours and type only from `src/shared/theme/tokens.ts`.
   - University names in text only, no logos.
6. **Before each commit:**
   - In `backend`: `python -m pytest -q tests` and `python scripts/validate_data.py`.
   - In `frontend/mobile`: `npx tsc --noEmit`, `npx jest` and `npx expo lint`.
   - Commits are small and named, for example `M2: tier card`.
7. **Ask the humans before:** adding an external service, changing a fact in a data pack, making a language visible,
   collecting new personal data, or changing hosting.
8. **Never:** invent facts, start M6 before Fri 23 Oct 08:30 SAST, force-push or rewrite history, or commit secrets.

## Rinsuna's next work, so you don't collide

- **Data packs:** done in #5 (`backend/data/universities/`), with how to apply in #6. A person still has to check
  every value before any pack is released.
- **Next:** the brief's other M1 pack sections (campuses, calendar, funding cycles, support services, cheap things),
  which My week, My money and Support run on, then the backend for M3 to M5.

All of this is in `backend/` and `docs/`; the app is yours.
