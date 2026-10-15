# Handoff brief: two app screens for Antigravity

Written 15 Oct 2026 for Antigravity (Flash 3.8), working alongside Claude Code on Campus Chommie. Rinsuna Mahani owns
the project, reviews every pull request and merges. Claude Code reviews your pull requests before she does.

Read these first, in this order, and follow them: [CLAUDE.md](../../CLAUDE.md) (the project's rules),
[docs/HANDOVER.md](../HANDOVER.md) (where things stand), then this file. If anything here seems to contradict CLAUDE.md,
CLAUDE.md wins: stop and ask Rinsuna.

## What Campus Chommie is (in one paragraph)

A South African student app for the FNB App of the Year Hackathon 2026 ("Access to higher education"). A learner types
their marks, sees where they qualify at 26 universities, picks a goal, and gets a three-choice plan with how to apply
(the course finder, no account needed, stores nothing). A student with an account gets their week, their money, alerts
and campus support. One Expo app (`frontend/mobile`, Android and web), a Flask API (`backend/src`) and a Python engine
(`backend/campus_engine`).

## Your two tasks

You build **app screens only**, against APIs that already exist. Two tasks, one pull request each:

- **Task 1: Funding instead of "Change goal / Start again"** on the plan screen.
- **Task 2: "What happens if you're accepted"**: a step after the plan that takes a prospective student to the
  enrolled-student side of the app.

## Hard rules (breaking one means the pull request is closed)

1. **Never invent a fact.** No amounts, dates, requirements, contacts, names or places that the API didn't send you.
   If a value is missing or `null`, the screen says so in words (for example "Not published by the funder" or
   "Not verified yet"). Never fill a gap with an example, a placeholder figure or "typically R…".
2. **Never edit:**
   - `backend/` (no data packs, no API, no engine, no tests there);
   - `CLAUDE.md`, `AGENTS.md`, `docs/` other than this file's "Questions" section;
   - `frontend/mobile/src/shared/theme/tokens.ts` (use its tokens, don't add or change them);
   - `frontend/mobile/package.json` or the lock file (**no new packages**: ask Rinsuna first);
   - anything under `frontend/mobile/src/features/auth` except what Task 2 says.
3. **Colours and type only from `src/shared/theme/tokens.ts`.** No hex codes in screens. Text sits on dark forest
   glass (`colors.white` is the glass surface; `colors.ink` and `colors.text` are white text on it; `colors.accent` is
   the white pill, with `colors.pillText` on it).
4. **Words, not colour alone.** Every status (open, closing soon, closed, not published) shows its label in words.
5. **The course finder stores nothing and needs no account.** Never put marks in storage, logs, analytics or a URL.
   Marks stay in the course finder's in-memory state (`features/courseFinder/state.tsx`).
6. **No university logos, crests or brand colours.** University names in text only.
7. **No secrets.** Never print, log or commit `.env` values, tokens, passwords or sign-in links.
8. **Git:** work on your own branch, cut from `rinsuna/courses-by-faculty` (PR #36), in a separate git worktree.
   - Branches: `rinsuna/ag-funding-button` (Task 1), `rinsuna/ag-accepted-step` (Task 2, cut from Task 1's branch).
   - Small commits, each named by feature, for example `F2: funding button on the plan`.
   - Never merge, never force-push, never rewrite history, never use a bare `git stash`.
   - Open a pull request into the branch you were cut from, and stop there.
9. **Servers:** if you run the app, use port 8090 for Expo and 5090 for the API (the preview setup in HANDOVER,
   "For a coding agent"). Never stop a process you didn't start, and never touch ports 5000 or 8081 (Rinsuna's).
10. **When unsure, stop and ask.** Write the question under "Questions" at the end of this file in your branch and say so
    in your pull request. Don't guess.

## Before every commit (all must pass)

```bash
cd frontend/mobile
npx tsc --noEmit
npx jest
npx expo lint
```

And check every new screen at **360 px wide** on the web build (`npx expo start --web --port 8090`): nothing may
overflow sideways, and nothing may hide behind the bottom buttons.

## How the app is built (what you'll touch)

- Routes: Expo Router in `src/app`. The course finder is `src/app/course-finder/` (`index` = marks, `qualify`,
  `university/[id]`, `plan`). Each route file only re-exports a screen from `src/features/courseFinder/screens/`.
- Screens: `src/features/courseFinder/screens/`. Components: `src/features/courseFinder/components/`. API calls:
  `src/features/courseFinder/api/courseFinderApi.ts` (uses `api()` from `@/shared/api/client`). Types:
  `src/features/courseFinder/types.ts`.
- Shared parts you should reuse rather than rebuild:
  - `HeroScreen` (title on the wallpaper, `back`, and a `footer` pinned at the bottom);
  - `Button` (`variant` primary, accent, secondary, danger; `compact`; `icon`);
  - `Card`, `InfoNote`, `Tag`, `ListRow`, `IconTile` (in `shared/components/Parts.tsx`);
  - `SourceLink` (opens a source in the in-app browser);
  - `ErrorBox` and `SkeletonCards` (loading and errors);
  - `SlidingTabs`, `FadeIn`, `PressScale` (in `shared/motion/`; they already respect reduced motion).
- Words: every string goes through `t()` from `@/shared/i18n`, with its English text added to
  `src/shared/i18n/en.ts` (key names like `courseFinder.fundingButton`). English only is visible.
- Tests: Jest with `@testing-library/react-native`, next to the feature in `__tests__/`. Mock `@expo/vector-icons`
  and `motionOff` as `features/courseFinder/__tests__/Faculties.test.tsx` does.

## Task 1: Funding instead of "Change goal / Start again"

**Why:** the plan screen is the longest screen in the app. The back button already changes the goal, so the footer's
two buttons are wasted. Learners need to find funding at exactly this moment.

**Change:** in `screens/PlanScreen.tsx`, replace the footer's two buttons with one full-width **Funding** button
(`variant="primary"`, icon `dollar-sign` or `award`). Keep "Start again" reachable as a small text button near the
top of the screen (under the subtitle), because it clears the marks. Remove `courseFinder.changeGoal` from the footer
only (keep the key if anything else uses it).

**The Funding button opens a new route** `src/app/course-finder/funding/index.tsx` (screen
`screens/FundingScreen.tsx`) with two choices as large cards:

1. **NSFAS:** opens `course-finder/funding/[id]` with id `nsfas`.
2. **Other bursaries and loans:** a list of every other funder.

**Data:** both come from the public API (no account, nothing sent about the learner):

- `GET /api/v1/funding`: answer `data`:
  `{ today, summary, counts: {total, open_now, closing_soon}, fields: [{id, label, funders}], funders: [card] }`.
  Each `card`: `id, name, short_name, kind, kind_label, sector, sector_label, any_field, fields: [{id,label}],
  not_fields, stages: [{id,label}], study_at, applying, status, label, intake, heading, opens, closes, next_date,
  days, lines: [string], why, url, source_url, checked`.
  Optional filters as query strings: `field`, `status`, `kind`, `stage` (see README, "Funding").
- `GET /api/v1/funding/<id>`: answer `data.funder` has everything in the card plus
  `who_can_apply: {items, source_url} | null`, `covers: {items, source_url} | null`,
  `obligations: {items, source_url} | null`, `apply: {url, how, fee_cents, fee_note, contact, documents, after,
  tips, warnings, windows: [window], lines, source_url}` and `sources: [{url, publisher, title, retrieved,
  last_verified}]`. A `window` is `{intake, heading, status, label, opens, closes, late_opens, late_closes,
  next_date, days, lines, source_url}`.
- Add both calls to `courseFinderApi.ts` (`fundingList(filters?)`, `funder(id)`) and their types to `types.ts`
  (extend the existing `FundingCard`; don't break its current users).

**The list screen (Other bursaries and loans):**
- Each row: name, `kind_label` (Bursary, Merit award, Loan), and status in words (`label`, for example
  "Open, closes in 12 days"). Tap opens the funder's page.
- Filter chips from `fields` (Commerce, Engineering, Health…), one at a time, plus "All". Use the same chip style as
  the Courses tab in `UniversityScreen.tsx`.
- Show `summary` at the top ("24 funding options: 5 open now.").
- If the plan's goal programme has `fields`, preselect nothing, but sort funders that fund those fields to the top and
  say so in words ("Funding for Health first, from your goal").
- Show the API's `notice` when `confirmed` is false (the funding list is an agent draft until Rinsuna checks it).

**The funder page (`course-finder/funding/[id]`), in this order:**
1. Name, `kind_label`, `sector_label`, status in words, and when it opens or closes (`opens`, `closes`, `days`).
2. **What it covers:** `covers.items` as a list. **This is "how much the package is":** show exactly what the items
   say. If no item names an amount, add one line: "The funder doesn't publish an amount." Never compute or estimate one.
   If `covers` is `null`, say "Not published by the funder."
3. **Who can apply:** `who_can_apply.items` (null: "Not published by the funder").
4. **What you owe back:** `obligations.items` (work-back years, loan repayment). Hide the section if `null`.
5. **How to apply:** `apply.how`, `apply.documents.items`, `apply.windows` (each with its label in words),
   `apply.fee_cents` (format cents as rands: 15000 is "R150"; `null` is "No fee published"), and an **Apply on
   the funder's site** button that opens `apply.url` in the in-app browser (as `SourceLink` does).
6. **Sources:** each `sources[]` entry as a `SourceLink`, with "Read on <retrieved date>".

**Tests (Jest):** the footer shows Funding and not "Change goal"; NSFAS opens its page; a funder without `covers`
shows "Not published by the funder"; a funder whose covers name no amount shows the "doesn't publish an amount" line;
fee formatting (`15000` is "R150", `null` is "No fee published"); the list filters by field. Record one real answer
from `GET /funding` and one from `GET /funding/nsfas` as fixtures (as `__tests__/fixtures/points.json` was).

## Task 2: "What happens if you're accepted"

**Why:** the brief says the app takes a student "from choosing a course to graduating". Today the course finder and
the student side don't connect. This step joins them.

**Change:** on the plan screen, under the three choices, add a card **"If you're accepted at <university>"** with a
**See what happens next** button. It opens a new route `src/app/course-finder/next/[id].tsx` (screen
`screens/NextStepsScreen.tsx`) for the plan's university.

**Data (public, no account):**
- `GET /api/v1/universities/<id>/first-steps`: answer `data`:
  `{university, today, first_steps: [{intake, notes: [string], steps: [{key, title, status, label, starts, ends,
  days, lines: [string], source_urls: [string]}]}]}`. Steps run from accepting an offer, through registration and
  orientation, to the first lecture.
- `GET /api/v1/universities/<id>/map?campus=`: each campus's map outline (see README, "Campus maps"). Optional: show
  a campus list with a "Map" link only if the answer says `mapped: true`. Don't draw maps yourself (no new map
  package): if it would need one, leave the map out and write the question in "Questions".
- **Not available signed out:** `GET /support` and `GET /money/cheap-things` need a signed-in student. Don't call
  them here. Instead, show one line: "After you sign up, Support and Money show your campus's counselling, financial
  aid and cheap things nearby."

**The screen, in this order:**
1. Title: "If you're accepted at <university name>".
2. A timeline of `first_steps[0].steps`: each step's `title`, its `label` in words (status), dates (`starts`/`ends`,
   formatted like "Mon 19 Jan 2027"), its `lines`, and its sources as `SourceLink`s. If `first_steps` is empty, say
   "Not published yet" and link the university's own page if the answer gives one.
3. The line about Support and Money (above).
4. A primary **Create my student account** button. It goes to `/(auth)/create-account` and passes the university as
   a route parameter (`?university=<id>`). In onboarding (`features/profile/screens/CampusScreen.tsx`), if that
   parameter is present **and** the id is in the list `profileApi.universities()` returns, preselect it; otherwise
   behave exactly as today. Change nothing else in sign-up: the 18-or-older confirmation, consent, validation and
   security stay untouched.
5. Marks are **never** passed to sign-up or saved anywhere. Only the university id travels.

**Tests (Jest):** the plan shows the "If you're accepted" card; the next-steps screen lists step titles and labels
from a recorded fixture; empty `first_steps` shows "Not published yet"; the Create account button navigates with
`university` and no marks; onboarding preselects a listed university from the parameter and ignores an unknown one.

## Definition of done (for each task)

- [ ] `npx tsc --noEmit`, `npx jest` and `npx expo lint` pass.
- [ ] Checked at 360 px on the web build: no sideways overflow, nothing hidden behind the footer.
- [ ] Every value on screen comes from the API; every missing value says so in words.
- [ ] No files changed outside `frontend/mobile/src` (apart from this file's "Questions").
- [ ] Pull request opened into the branch you were cut from, describing what you built, with screenshots at 360 px,
      and listing anything you weren't sure about. End the description with which model and tool wrote it.

## Questions

(Write questions for Rinsuna or Claude Code here, in your branch, with the date. Don't guess.)
