# Handover: start here

First written on 9 Oct 2026 for Mandla Baloyi, and kept current by Rinsuna's coding agents. Since 13 Oct 2026 Rinsuna
Mahani works alone: Mandla is no longer on the team, so the app, the API, the engine and the data are all hers, and so
is every review and decision. This file is for her and for any coding agent picking up the work. It covers:
- where the build stands
- what was decided
- what only Rinsuna can do
- the app screens to build next (M2 to M5)
- how an agent picks up work

The rules are in [CLAUDE.md](../CLAUDE.md); this file doesn't change them. The brief (`BUILD_BRIEF.md`) sits in the
repo folder but is kept out of git; the parts the screens need are quoted below.

## Where things stand

`main` holds only the empty first commit. All work sits in twenty-nine stacked pull requests:

| PR | Branch | What |
|---|---|---|
| #1 | `rinsuna/m0-foundation` | M0: accounts, sign-in, security, notifications, audit, the app shell, the engine starter, CI |
| #2 | `rinsuna/university-research` | research notes for UP, TUT and SMU, and the open questions they raise |
| #3 | `rinsuna/engine-requirements` | engine: either/or subjects, percentage minimums, per-programme points tables |
| #4 | `rinsuna/m1-course-finder-api` | the course-finder API and this file |
| #5 | `rinsuna/m1-data-packs` | draft UP and TUT packs, the approved SMU changes, and how the plan picks its third choice |
| #6 | `rinsuna/m1-how-to-apply` | how to apply, on today's date: each choice's application dates, NSFAS, fees, documents and next steps; notes on NSFAS and on other apps |
| #7 | `rinsuna/m1-after-acceptance` | your points at every university; campuses, calendars, money dates and support in the packs; first steps from acceptance to the first lecture |
| #8 | `rinsuna/m3-profile-and-money` | M3's backend: the student's profile (university and campus) and My money (settings, income, expected payments, spending, summary) |
| #9 | `rinsuna/m1-cheap-things` | cheap things to do near campus, each priced from the place's own page |
| #29 | `rinsuna/qualify-first` | Find my course marks first: your marks, then where you qualify (every university with your points there and how many programmes you meet, funding open now), then one university (points card opening per subject, courses and how to apply on sliding tabs), then the plan; a violet header and movement from the HTML Rinsuna chose (press, shimmer, sliding tabs, swipe rows, opening sections), in the app's own colours; the points answer gives each subject's points, and the assess answer how to apply there |
| #28 | `rinsuna/apply-preview` | "What you can still do now" at the top of the plan (open now, coming up, not published, closed), from the plan's own dates; a test date for previews only (`CAMPUS_PREVIEW_TODAY`, which production refuses), which the plan says it's using; tests for both |
| #27 | `rinsuna/subject-picker` | Find my course's subject picker: every subject on the DBE's Grade 10 to 12 list in folders (languages, mathematics, sciences and so on), ticked in one go with every language by name; the best-marked language besides English goes as the other official language and the results say which; Jest tests for the picker and how marks reach the API |
| #26 | `rinsuna/alerts-support-screens` | M5: Home's alerts (each action opening its screen) and updates with their switches; the Support tab (crisis lines held back until checked); cheap things nearby; "Delete my account and data" for real; Jest tests for alerts and support. The brief's judge flow runs end to end |
| #25 | `rinsuna/week-screens` | M4: the Week tab (eight weeks, each load in words with its reason) and a week (events, flags, the university calendar); classes (start, join, invite and rep codes), the rep panel and confirming class messages; My marks; Jest tests for the week strip, the rep panel, confirming and marks |
| #24 | `rinsuna/money-screens` | M3: onboarding (privacy notice, then university and campus) and the My money screens (the Money tab with runway, safe to spend, life fund and "two weeks late"; balance and budget, money coming in, expected payments, spending); the demo banner; Jest tests for the runway card and the life fund |
| #23 | `rinsuna/course-finder-screens` | M2: the Find my course screens (university, marks, tier cards, the three-choice plan with how to apply), from the welcome screen and Home; Jest tests for the tier card, the plan and the marks |
| #22 | `rinsuna/campus-maps` | campus maps from OpenStreetMap: each campus's outline, buildings and named places, `GET /universities/<id>/map` with the credit and the licence, the fetch script, and the validator's map checks |
| #21 | `rinsuna/solo-team` | the rules and docs for a team of one: CLAUDE.md, this file, OPEN_QUESTIONS, and the README's status |
| #20 | `rinsuna/more-funders` | five more funders from their own pages (24 in all; 5 open on 12 Oct) |
| #19 | `rinsuna/smu-gaps` | SMU's financial aid office, food support and Religious Desk on the Support screen; cheap things in northern Tshwane for SMU and TUT's nearby campuses |
| #18 | `rinsuna/saved-funding` | saving funding (UniApplyForMe's bookmark) with reminders when it opens and a week and a day before it closes; a switch for them; migration 0006 |
| #17 | `rinsuna/funding-list` | funding like UniApplyForMe's: 19 funders from their own pages (NSFAS, bursaries, UP's merit awards, a loan scheme), `GET /funding` with "N open now, N closing soon" and filters, `GET /funding/<id>`, and each plan choice's funding |
| #16 | `rinsuna/extraction-50` | the engine reads every date in a message (the new one in a "moved" message, ranges, bare hours) and asks the rep to check; 57 labelled class messages |
| #15 | `rinsuna/ready-to-host` | the backend ready for any host: a container, gunicorn, one process running the background jobs, production CORS for the web build, and DEPLOY.md |
| #14 | `rinsuna/class-update-alerts` | class updates as alerts (a rep's confirmation tells the rest of the class), with a switch to turn them off |
| #13 | `rinsuna/privacy-export-delete` | POPIA: `GET /me/export` holds everything we keep about a student, and `DELETE /me` deletes the account and all of it |
| #12 | `rinsuna/android-preview` | the installable Android app (EAS preview APK, built-in mock sign-in), under Rinsuna's Expo account |
| #11 | `rinsuna/m5-alerts-support-demo` | M5's backend: alerts, the Support screen's data, cheap things for the campus, and the judges' demo accounts (`flask seed`, re-based daily) |
| #10 | `rinsuna/m4-my-week` | M4's backend: classes, invite codes and reps, announcements to verified events (changes and flags), the week strip, My marks; the life fund reads the week; 44 labelled class messages |

**Review:** Rinsuna reviews and merges every PR; agents open them but never merge. Look hardest at the ones that touch
accounts or the database: #1, #8, #10, #11, #14 and #18 add migrations, #11 also lets demo accounts skip the
new-phone code, and #13 deletes accounts.

**How to merge:**
- Each PR targets the branch below it, so its diff shows only its own work.
- Merge in order: #1 into `main`, then #2 to #29, retargeting each to `main` once the one below has merged.
- Use **Create a merge commit**, not squash or rebase, so every commit stays in `main`'s history (CLAUDE.md: never
  rewrite history).

## Decided so far

Everything is recorded, with who and when, in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

- **The team (13 Oct):** Rinsuna works alone from now on. The app screens, which were Mandla's, are ours to build.
  Everything that waited for Mandla in OPEN_QUESTIONS now waits for Rinsuna, and F6 (fund and apply), which she agreed
  on 9 Oct, is in CLAUDE.md's Scope.
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
- **Funding (#17, 11 Oct):** Rinsuna asked for funding like UniApplyForMe's, reversing "no bursary list". The list now
  has 24 funders, each read on its own page (#20), and saving one brings reminders (#18).
- **Campus maps (#22, 12 Oct):** a scope change Rinsuna made. Each campus's outline and buildings come from
  OpenStreetMap and are served with its credit and licence (the ODbL); she names SMU's buildings herself. The
  map's background and "you are here" are hers to decide (OPEN_QUESTIONS, "Campus maps").
- **Proposed, waiting for Rinsuna** (OPEN_QUESTIONS, "App and accounts"): which intakes a plan shows, and links to
  opportunity sites such as Graduates24. An application directory for all 26 public universities was proposed and
  then paused, because UniApplyForMe already does it well; the time goes to support after acceptance.
- **Other apps:** [research/competitors.md](research/competitors.md) compares UniApplyForMe, UniAPS and others, and
  says where we differ. Worth reading before the deck. Rinsuna tried both: UniApplyForMe is very good but stops at
  the application, so we stand out after acceptance.
- **After acceptance (#7, 10 Oct):**
  - **Your points at every university,** as UniApplyForMe does well.
  - **The packs' calendars, money dates and support,** which My week, My money and Support run on.
  - **First steps from acceptance to the first lecture.**
  - Three screen decisions are in OPEN_QUESTIONS.
- **My week (#10, 10 Oct):**
  - A rep's confirmation is the only way an event becomes verified; a student's announcement waits for one.
  - Members are never listed, not even to reps, so a rep brings in the next rep with a one-time code.
  - Reps see how many students flagged an event, never who (Rinsuna to confirm: OPEN_QUESTIONS, "Flag counts").
  - The engine also reads Afrikaans words in announcements; a fluent speaker is to check the list.
  - The brief's M3 check that waited for M4 passes: Sipho's heavy week makes his life fund amber.
- **Alerts, support and demo (#11, 10 Oct):**
  - Demo accounts skip the new-phone code, can't be locked by wrong passwords and can't change their password
    (Rinsuna's decision; the identity change in #11 needs her review).
  - Crisis lines stay hidden on Support until a person checks them; every pack's are still agent drafts.
  - Besides the brief's three alerts, a module out of reach gets one (Rinsuna's to keep or drop).

## Only Rinsuna can do these

1. **Review and merge the stack,** #1 first (above).
2. **Check the facts by Thu 22 Oct:** the packs (crisis lines first: Support hides them until then) and the funding
   pack. Compare every value with its source, then set `last_verified`, `verified_by` and `release: true`
   (OPEN_QUESTIONS, "Facts for the data packs").
3. **The reused foundation** (REUSE.md; OPEN_QUESTIONS, "Privacy and legal"). #1 copies code from our earlier project
   (© Team PR: Mandla and Rinsuna) and, through it, from TruConnect, an earlier project of Mandla's. Mandla's
   confirmations in REUSE.md are still unsigned. Before the submission, get his written OK or replace the reused
   files. LICENSE still names "Team PR (Mandla and Rinsuna)". Agents don't change REUSE.md's permissions or
   LICENSE: they're Rinsuna's call.
4. **Name SMU's buildings** on campus, the Clinpath and Natural Science buildings first (OPEN_QUESTIONS, "Campus
   maps").
5. **Decisions waiting for her** (OPEN_QUESTIONS, "App and accounts" and "Campus maps"):
   - the map's background, and "you are here"
   - which intakes a plan shows, and "Add these dates to my calendar"
   - flag counts for reps, and module alerts
   - links to opportunity sites
   - the package name `za.campuschommie.app` (it can't change after the first Play Store upload)
   - app icon, colours and slogan
   - Google sign-in
   - hosting
   - the email sender
6. **Human deadlines:**
   - **Sonke:** create the team by Tue 20 Oct.
   - **WhatsApp:** set up WhatsApp Business (Meta app, test number) before Fri 23 Oct.
   - **Hackathon:** Fri 23 Oct 08:30 to Sun 25 Oct 17:00 SAST. M6 doesn't start before 08:30 on the Friday.
   - **Submission:** Mon 26 Oct 23:59 SAST.

## Next build: the app screens, M2 to M5

The screens were Mandla's; since 13 Oct they're ours. The brief gives M2 Wed 14 to Thu 15 Oct, M3 Fri 16 to Sat 17,
M4 Sun 18 to Mon 19 and M5 Tue 20 to Wed 21. M2 to M5 are built (#23 to #26, 13 Oct), and the judge flow runs end to end. #27 (13 Oct) replaces the marks screen's one-subject-at-a-time rows with a picker in folders, #28 puts what a learner can still do at the top of the plan, and #29 puts the marks first. Next: hosting (Azure for Students, once Rinsuna activates it), a preview APK on the hosted API, polish (the plan screen is long), and M6 from Fri 23 Oct.

**M2, the Find my course screens.** From the brief: "University, then marks (add or remove rows, up to 9), then tier
cards, then the three-choice plan and sources. Add i18n plumbing with English only visible. Acceptance: works at 360
px wide on Android and web. Tier labels are words, not colour alone. Every card shows its 'why' lines and source. Jest
tests cover the tier card and the plan."

The course finder works signed out: the M5 judge flow ends with "use the course finder without an account". So its
route sits outside the protected `(app)` group, reachable from the welcome screen as well as from Home.

**The order since 13 Oct (#29), Rinsuna's choice:** marks first, then where you qualify, then a university, then the
plan. The brief's "University, then marks" came first in #23. Routes: `course-finder` (marks), `course-finder/qualify`,
`course-finder/university/[id]`, `course-finder/plan`. The screens open on a violet band (`shared/components/HeroScreen`),
and the moving parts live in `shared/motion` (press, shimmer, sliding tabs, swipe rows, opening sections, rising
content); each changes at once when the phone asks for reduced motion.

The API is in #4, with details in the [README](../README.md), "Course finder":

| Screen | Call | Use |
|---|---|---|
| Where you qualify (#29) | `POST /pathways/points` with `{marks}` | per university: `points`, `tiers`, `subjects` (each subject's level and points there), `lines`, `confirmed` and `notice` |
| A university (#29) | `POST /pathways/assess` with `{university, marks: [{subject, percent}]}` | `matches`, best tiers first; `apply.guide` for the How to apply tab |
| Plan | `POST /pathways/plan` with `{university, goal, marks}` | `plan.goal`, `plan.bridge`, `plan.safe`, `plan.other_routes`, `plan.notes` |
| How to apply | the same plan answer | each slot's `apply`, and `plan.apply`: `deadlines`, `universities`, `funding`, `notes` |
| Points everywhere (#7) | `POST /pathways/points` with `{marks}` | `universities`: each with `points`, `summary`, `lines` (how it counts), `tiers` |
| Funding (#17) | `GET /funding?field=&status=&kind=&stage=`, `GET /funding/<id>` | `summary`, `counts`, `fields` (filter chips) and `funders` (cards); one funder's `who_can_apply`, `covers`, `obligations`, `apply` and `sources` |
| First steps (#7) | `GET /universities/<id>/first-steps` | `first_steps`: per intake, `steps` (accept, register, orientation, first lecture) with `status`, `label`, dates, `days`, `lines`, `source_urls` |

**The M3 screens (Fri 16 to Sat 17 Oct) have their API in #8** (README, "A student's own profile and money"):
- **Onboarding:** the 18-or-older confirmation and consent are already recorded at sign-up; add the privacy notice,
  then university and campus (`PUT /me/profile`).
- **My money:** settings, income sources, the "received?" tap on each payment, one spending number per day, and the
  runway card from `GET /money/summary`, with the "two weeks late" toggle as `?late=true`.
- **What the summary gives you:** every part has plain-words `lines`; `life_fund.state` is `green`, `amber` or
  `paused`; amounts are integer cents (format as rand).
- **Demo personas:** `tests/domains/student/student_helpers.py` shows them set up through the API.

**The M4 screens (Sun 18 to Mon 19 Oct) have their API in #10** (README, "My marks" and "Classes, reps and verified
events"); the screen notes are in OPEN_QUESTIONS, "My week's screens":
- **Classes:** `POST /classes`, `POST /classes/join` (an invite code or a rep code), `GET /classes/mine`, and
  `POST /classes/<id>/reps` for a rep's one-time code.
- **Rep panel:** `POST /classes/<id>/announcements` returns the candidate; confirm with
  `POST /candidates/<id>/confirm`, starting the form from `proposed` and highlighting `needs_check`.
- **Week strip:** `GET /week?weeks=8`. Each week has `load` (say the word; colour can only add to it), `reason`,
  `events` and the university's `calendar`.
- **My marks:** `/academics/modules` and its assessments; every answer carries `standing`, `projection` and `lines`.
- **Test helpers:** `tests/domains/classes/class_helpers.py` shows a rep making a class and confirming events.

**Class updates (#14)** arrive in the alerts inbox the app already has. A `class` link opens that class's events, and
`GET` / `PUT /me/notifications/switches` is the "Class updates" switch for the settings screen.

**A Map screen (#22; README, "Campus maps"):** `GET /universities/<id>/map`, open to anyone.
- A campus picker from `campuses`; one not mapped yet shows its line.
- Fit the first view to `south_west` and `north_east`. Draw `outline`, then each place's `outline` (a pin when it
  has none). Label the named ones; the rest stay plain shapes, never guessed. `kind` picks the icon.
- A tap shows the place's name, or "No name yet".
- Each `support` entry's `place` lets the Support screen offer "Show on map".
- Always show `attribution` linked to `attribution_url`, and the licence (`licence`, `licence_url`) in the map's
  info. While `confirmed` is false, show `notice`.
- `react-native-svg` (already in the app) can draw the shapes with no external service. A background map is
  Rinsuna's call, and the phone's location never goes to the API (OPEN_QUESTIONS, "Campus maps").

**The Security screen's "Delete my account and data"** can stop saying "Coming soon": `DELETE /me` with
`{password}` (#13) deletes everything, and `GET /me/export` now holds every feature's data.

**The M5 screens (Tue 20 to Wed 21 Oct) have their API in #11** (README, "Alerts, support and cheap things"):
- **Home:** `GET /alerts`. Show each alert's `title`, `message` and `actions`; an action opens its `target` (Week,
  Money, cheap things, My marks or Support), and a support action may already carry the campus's `service` (name,
  contact, hours). `notes` say what's missing (no classes yet, no money entered).
- **Support:** `GET /support`. One section per `kind`, in the order given; each service with its source and when a
  person last checked it, or the `line` ("Not verified yet", or why crisis lines aren't shown yet).
- **Cheap things:** `GET /money/cheap-things`, with cost notes and sources.
- **Demo banner:** `GET /me` (and the sign-in answer's `user`) has `demo: true` on demo accounts: show "Demo data:
  fictional student". The judges sign in with the three `*.demo@example.com` accounts (README, "Demo accounts").

**What the screens must handle:**
- **Cards:**
  - Each card has `tier`, `label`, `points`, `min_points`, `gap`, `failed`, `explanation` (the "why" lines) and
    `source_url`.
  - Bridge slots add `bridge` (`guarantee_label`, `conditions`, `max_places`, `eligibility_note`, `source_url`).
  - Show `label` in words; colour can add to it but never replace it.
  - `tier` is one of `reach`, `meets_minimum`, `competitive`, `not_yet`, `unverified`.
- **Unchecked data:** when `confirmed` is false, show `notice` ("Not yet confirmed by the team.") with the university
  and on each card.
- **Subjects:** the API takes the keys in `SUBJECTS` (`backend/campus_engine/schemas.py`) plus up to three
  points-only `another_subject_1` to `another_subject_3`. Since #27 the picker offers every subject on the DBE's
  list, in folders, and sends each under one of those keys ([research/nsc-subjects.md](research/nsc-subjects.md)).
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
    "Add these dates to my calendar" is Rinsuna's call (OPEN_QUESTIONS).
  - **Each university:** `plan.apply.universities`, with `url`, `fee_cents` (format as rand), `documents.items`,
    `after` and `lines`. Missing facts come as `null` and a "not verified yet" line: show that line, never a blank.
  - **Funding:** `plan.apply.funding` (NSFAS): its `windows` (the 2027 countdown), `who_can_apply`, `documents`,
    `tips` (the eight document mistakes NSFAS sees most) and `warnings` ("Never pay anyone to apply").
  - **Funding for each choice (#17):** the slot's `funding`: up to five `funders` (cards), `count` in all,
    `open_now` and a line. A "See all" can open the Funding list filtered by the slot's `fields`
    (`GET /funding?field=a,b`).
  - The app never asks about income, disability or family: it shows NSFAS's own words and links to it.
- **A Funding screen (#17; F6):** like UniApplyForMe's, open to anyone. The top line is `summary`
  ("24 funding options: 5 open now."); chips from `fields`; tabs or a picker for `kind` (bursaries, merit awards,
  loans) and `stage`. Each card: `name`, `label` in words with the `days` count, `lines[0]`, the fields, and
  "Checked on" (`checked`). The detail screen shows `who_can_apply`, `covers` and `obligations` (work-back
  conditions matter to learners), then `apply` (`how`, `documents`, `windows`, `contact`) and the `sources`. A
  `seen` status line says the funder's own page said so on a date: show it as written. Never add a question about
  race, income or anything personal to "match" funding: the funder's words are shown and the learner decides.
- **Saved funding (#18), signed in:** a bookmark on each funder card and on the detail screen (`PUT` /
  `DELETE /me/funding/<id>`), and a "Saved" list (`GET /me/funding`: the same cards, each with `saved_on`). Signed
  out, the bookmark can ask the learner to sign in. The reminders arrive as ordinary alerts (`funding.open`,
  `funding.closing`) whose link is `{type: "funding", id}`: open that funder's detail screen. The alert switches
  screen gains "Funding you saved: when it opens, and before it closes" (`funding_reminders`) with no change in the
  app, because the screen lists `GET /me/notifications/switches`.
  - Each university and funder has `confirmed` and `notice`, as on the cards.
- **Ideas from UniApplyForMe**, which Rinsuna tried on 10 Oct (Rinsuna's call): one topic per onboarding screen with
  a review step, deadline cards with a day count, and the level shown as a mark is typed.
  [research/competitors.md](research/competitors.md) lists them, and what we won't copy (race questions, logos,
  paywalls).
- **English text to reuse:** `backend/campus_engine/i18n.py` has the course finder's English strings: the title,
  slot titles, "Nothing you enter here is saved.", the `duplicate` text and the how-to-apply headings. English is the
  only visible language until a fluent speaker signs one off.

## For a coding agent: how to pick this up

1. **Read first:** [CLAUDE.md](../CLAUDE.md) (AGENTS.md points every agent there), then this file.
2. **Branch:**
   - Start from the newest PR's branch (the first row after #9 above; today `rinsuna/alerts-support-screens`): `git fetch origin`,
     then check it out.
   - Branch `rinsuna/<topic>` from there, for example `rinsuna/money-screens`. Once the stack is merged, branch from
     `main` instead.
   - Another session may have uncommitted work in the main checkout: work in a git worktree, and never use a bare
     `git stash` or `git stash pop` (the stash is shared by every worktree).
3. **Run the API** (README, "Backend"):
   - Use your own sandbox database: a Docker PostgreSQL 16 on a spare port, removed when you're done. Never Rinsuna's
     own database or a production one.
   - Leave `backend/.env` alone (it's Rinsuna's): give your process the sandbox's settings as environment variables,
     which win over the file. Then `flask db upgrade` and `python app.py`.
   - Agents use ports 5090 (API) and 8090 (Expo), and never stop Rinsuna's servers on 5000 or 8081.
   - To walk the apply steps while applications are closed, give the API `CAMPUS_PREVIEW_TODAY` (for example
     `2026-06-01`): the plan then shows a "Test date" note. Never on a hosted API (production refuses it).
4. **Seeing it on a phone:** with the phone on the PC's Wi-Fi, Expo Go opens `exp://<the PC's address>:8090`. The
   app's `EXPO_PUBLIC_API_URL` must be an address the phone can reach, through a program Windows' firewall lets in
   (on 13 Oct, Node was allowed and the preview's Python wasn't, so a small Node relay forwarded to the API).
5. **Point the app at the API:** set `EXPO_PUBLIC_API_URL` (for example `http://localhost:5090/api/v1`, or the PC's
   address from a phone) and `EXPO_PUBLIC_USE_MOCK_API=false` for your Expo process, as with the API.
6. **Where code goes:**
   - Screens in `frontend/mobile/src/features/<feature>`, routes in `src/app`.
   - Colours and type only from `src/shared/theme/tokens.ts`.
   - University names in text only, no logos.
7. **Before each commit:**
   - In `backend`: `python -m pytest -q tests` and `python scripts/validate_data.py`.
   - In `frontend/mobile`: `npx tsc --noEmit`, `npx jest` and `npx expo lint`.
   - Commits are small and named, for example `M2: tier card`.
8. **Ask Rinsuna before:** adding an external service, changing a fact in a data pack, making a language visible,
   collecting new personal data, deleting files outside the brief's strip list, or changing hosting.
9. **Never:** invent facts, start M6 before Fri 23 Oct 08:30 SAST, merge a PR, force-push or rewrite history, or
   commit secrets.

## Backend and data: done, and what's left

- **Data packs:** done in #5 (`backend/data/universities/`), with how to apply in #6. A person still has to check
  every value before any pack is released.
- **Pack sections:** campuses, calendars, money dates and support are in #7; cheap things near UP and TUT in #9;
  SMU's financial aid office, food support, Religious Desk and first two cheap things (northern Tshwane) in #19.
- **M3 backend:** done in #8 (profile and My money).
- **M4 backend:** done in #10 (classes, reps, verified events, the week, My marks).
- **M5 backend:** done in #11 (alerts, support, cheap things, demo accounts).
- **Ready to host:** #15 and [DEPLOY.md](DEPLOY.md). Choosing the host is still Rinsuna's decision (OPEN_QUESTIONS).
- **Funding:** #17 (`backend/data/national/funding.yaml`, `campus_engine/funding.py`, `GET /funding`), with the
  leads still to check in [research/funding.md](research/funding.md). Saving funding and its reminders: #18.
- **Campus maps:** #22 (`backend/data/maps/`, `campus_engine/maps.py`, `GET /universities/<id>/map`,
  `scripts/fetch_osm_maps.py`), with what's mapped and the licence in [research/maps.md](research/maps.md).
- **Next:** a person checks the packs (crisis lines first) and the funding pack; M6 (the WhatsApp bot) only from Fri
  23 Oct 08:30 SAST.
