# Open questions

Facts we don't have yet and decisions only the team can make. The app shows "Not verified yet" wherever a fact is
missing; nothing here may be guessed. Tick an item and add a line (who, when, the answer or a link) when it's
settled.

Since 13 Oct 2026 the team is Rinsuna alone (Mandla Baloyi is no longer on it), so every decision here is hers: the
items that waited for Mandla now wait for her.

## Facts for the data packs

Research notes from official documents, read on 9 and 10 Oct 2026 and not yet checked by a person:
[UP](research/up.md), [TUT](research/tut.md), [SMU](research/smu.md), [NSFAS](research/nsfas.md) and
[funding](research/funding.md) (bursaries, read on 11 Oct). Each lists its sources, gaps and inconsistencies. Other apps and services, for the deck: [competitors](research/competitors.md).

- [ ] **The funding pack** (`backend/data/national/funding.yaml`, 24 funders since 12 Oct): a person compares every value with its
  source by Thu 22 Oct, then sets `last_verified`, `verified_by` and `release: true`. Also confirm the choices listed
  in [funding](research/funding.md), "Choices made while building": the field tags, Clicks's year, ISFAP shown as
  closed, CSIR as postgraduate only, the Reserve Bank's online form, UP's 2026 amounts and no commercial lenders.
  Added 12 Oct: Limpopo Public Works counts as open because its page offers the 2027 form (its rule: closes 31 October
  every year), and Old Mutual's 2027 round opened "in April", with no day given.
- [ ] **NSFAS's 2027 closing date:** NSFAS's own page says 31 Oct 2026 at 23:59; the Minister's launch speech (18 Sep
  2026) and SAnews say 18 Nov 2026. The pack keeps 31 October, the earlier date, until a person checks with NSFAS.
- [ ] **SMU admissions:** re-check every value in `backend/data/universities/smu.yaml` against the current prospectus
  (copied from SMU's medicine admissions page on 30 Sep 2026; `verified_by` still says it needs the team's check).
  SMU's medicine page still matched the pack on 9 Oct.
- [ ] **SMU BSc first year:** admission requirements (the pack has `requirements: null`). Found on SMU's Science and
  Technology page: APS 25; English 4, Mathematics 5, Life Sciences 4, Physical Sciences 4, two more at 4. Open: those
  add up to 25 without Life Orientation, so does it count?
- [ ] **SMU maximum choices** per application (`max_choices: null`). Found: two (SMU's 2027 application page).
- [ ] **SMU calendar, allowance dates and support contacts** (counselling, crisis lines, financial aid, food support,
  tutoring, chaplaincy, health), each from an official source. Crisis contacts must be verified by a person before
  release. In `smu.yaml` since 10 Oct: the 2026 calendar, health, counselling, the referral unit (it refers to
  tutoring and financial aid) and the 2026 early-payment date. Added 11 Oct: the Financial Aid Office, the campus
  garden (food support) and the Religious Desk (SMU has no chaplaincy office), each from SMU's own pages. Still
  missing: the 2027 calendar (not published on 12 Oct), a 24-hour line and allowance dates.
- [ ] **SMU's Harambee Fund** gives struggling students food parcels and sanitary products (SMU news, Oct 2024), but no
  page says how a student asks for it. If Student Affairs can say, it belongs on Naledi's Support screen beside the
  garden.
- [x] **Changes to `smu.yaml`** that the research supports, for the team's OK: `max_choices: 2`; the BSc first-year
  requirements above; MBChB `places: 250`; the other SMU programmes; a considered route from SMU's first year into
  BDS (2 places); and the medicine foundation year's eligibility note, which leaves out SMU's population-group
  restriction (details in [smu.md](research/smu.md), "Notes for the data pack"). Approved by Rinsuna on 9 Oct 2026;
  applied on 10 Oct (`rinsuna/m1-data-packs`). Also marked BSc first year `selective: true`, because every SMU
  school page says selection is competitive: check.
- [x] **UP and TUT packs**, from official sources. Drafted on 10 Oct 2026: `up.yaml` (120 programmes) and `tut.yaml`
  (124; the Diploma in Fire Technology is left out, as it's only for people already in fire services). Both
  `release: false`, every source `verified_by: "agent draft, needs human check"`.
- [x] **How to apply** for UP, TUT and SMU, and NSFAS in a national pack (`backend/data/national/funding.yaml`).
  Drafted on 10 Oct 2026 (`rinsuna/m1-how-to-apply`): each pack's `applications` section (dates per intake,
  programmes with their own closing date, late windows, fee, documents, next steps) and NSFAS's 2027 window, documents
  and warnings. UP's application page can't be read automatically, so UP has dates only (see "Need a browser").
- [x] **Campuses, calendars, money dates and support** in all three packs. Drafted on 10 Oct 2026
  (`rinsuna/m1-after-acceptance`) from the research notes and the calendars:
  - UP: 2026 and 2027
  - TUT: 2026 and 2027, with the deadlines students miss at a cost (re-marks, exclusion appeals, module changes and
    cancellations, graduation applications), matched to their dates by position on the page
  - SMU: 2026
  - money dates: dates only, never amounts
  - support contacts: per campus where the source gives them
- [ ] **A person checks the packs** against their sources before any is released: every value in `up.yaml` and
  `tut.yaml`, the SMU values added on 10 Oct, the `applications` sections, `funding.yaml`, the calendars, money dates
  and support contacts (**every crisis line first**), and the lines marked "Check" in the packs and research notes.
  Then set `release: true` and fill in each source's `last_verified` and `verified_by`.
- [ ] **Campuses** for each university (needed for F1 and the support screen). In all three packs since 10 Oct; a
  person still checks them with the rest.
- [ ] **Cheap things to do near campus** (F4). Drafted on 10 Oct 2026 ([cheap-things.md](research/cheap-things.md)):
  four in Pretoria for UP and TUT (the national botanical garden, Freedom Park, the Voortrekker Monument, the
  DITSONG natural history museum) and the Lowveld botanical garden for TUT Mbombela, each priced from its own page.
  Still to do:
  - **Near SMU (Ga-Rankuwa) and TUT's Soshanguve and Ga-Rankuwa campuses:** Wonderboom Nature Reserve (R47) and the
    Tswaing Meteorite Crater (R60), added 12 Oct, are in northern Tshwane but not in walking distance. Closer places
    the team knows are still the best start, each with its own page and price.
  - **TUT Polokwane and eMalahleni:** nothing yet.
  - **Javett-UP, free for UP students:** its site couldn't be reached from our tools, so a person opens the page
    before it goes in.
- [ ] **Course finder languages:** which 2 or 3, and the fluent reviewers who sign them off in `docs/translation_review.md`.

### Gaps the research left

- [ ] **Need a browser:** UP's application page (where to apply, the fee and waiver, documents), offer deadline,
  registration payment and tuition per programme appeared only in search snippets. UP's web pages refuse automated
  reading; open them and save as PDF. Until then the app says "not verified yet" for UP's page, fee and documents.
- [ ] **Programmes per application** at UP and TUT: not published in the documents read.
- [ ] **TUT's APS:** how many subjects count (TUT says only "a minimum of six subjects", Life Orientation excluded).
  Until TUT confirms, the TUT pack counts the six subjects besides Life Orientation and says so (Rinsuna, 9 Oct 2026):
  if TUT counts more, we only under-count. An email to `admission@tut.ac.za` would settle it.
- [ ] **Tuition per programme** at TUT (charged per module; TUT has an online quotation page).
- [ ] **SMU 2027 calendar**, and **2028 entry dates** for UP and SMU (TUT's are published).
- [x] **NSFAS's 2027 window:** 18 Sep to 31 Oct 2026 at 23:59, free, no late applications (NSFAS's own pages, read
  on 10 Oct 2026; [nsfas.md](research/nsfas.md)).
- [ ] **NSFAS, still open:** 2027 allowance amounts and payment dates (for F4), and NSFAS's WhatsApp number (its
  how-to page and TUT's guide give different numbers, so the pack leaves it out).
- [ ] **TUT's July 2027 intake** (selected programmes; applications close 15 May 2027): TUT doesn't say which
  programmes, so plans don't show it.
- [ ] **TUT's closing dates for 2028:** the 2027 calendar names 15 June, 31 July and 30 September 2027 without saying
  which programme closes when. The app says so, suggests applying by 15 June to be safe, and gives the programme's
  2027 date.
- [ ] **Crisis lines** for a person to verify: UP crisis line 0800 006 428 and the UP Careline 0800 747 747 (with
  SADAG); TUT's 24-hour counselling line 0800 68 78 88. SMU publishes no 24-hour line; its clinic page sends students
  to campus control or 079 417 9546 / 6278 after hours. **Since M5 the Support screen holds every crisis line back
  until this is done:** in the pack's sources, set `verified_by` to the checker's name and `last_verified` to the
  date, by Thu 22 Oct so the judges see them.
- [ ] **Smaller inconsistencies** are listed at the end of each research note (for example, two closing dates for TUT's
  Bachelor of Geomatics, and a UP table that ends mid-row).

## Data-pack schema

Today's `Requirements` holds a fixed list of subjects and one APS. About 100 of UP's 120 programmes fit, about 18 of
TUT's 125, and most of SMU's.

Built on `rinsuna/engine-requirements` (not merged yet):

- **Decisions 1, 2, 6, 7 and 8:** `choices` (each option may set its own `min_points`), `subject_min_percents`, a
  programme's own `points_rules`, `count_from_level`, and the `SUBJECTS` list of known keys.
- **Plan tests:** they now run on SMU's data only, plus one cross-university test with a fictional university.

Decisions 3, 4 and 9 were taken by Rinsuna on 9 Oct 2026 (below). Decision 5 is still open. Decisions:

1. **Either/or subjects, each route with its own APS.** TUT almost everywhere ("Maths or Technical Maths 5, or Maths
   Literacy 7"; APS 26 or 28); UP in 6 programmes; SMU Oral Hygiene (28 or 31) and emergency care.
2. **Percentage minimums.** UP's extended programmes: 65% each for the five-year BEng, 58% for the four-year BSc.
3. **Fields** decide the cross-university safe choice (slot 3). Tagging UP's BSc Medical Sciences `health_sciences`
   makes it the safe choice for an SMU MBChB goal, which changes the current plan tests. Proposal: run those tests on
   SMU's data only and add a cross-university test. **Decided:** tag honestly. Once UP's pack lands, the brief's M1
   check (B Rad in slot 3 for the strong SMU learner) changes with it. **Built** (10 Oct):
   - **Ranking:** the third choice is a programme the learner meets without competitive selection, the closest by
     the share of fields in common, and never one already shown as a route.
   - **The M1 check now:** for the strong SMU learner, the third choice is UP's BSc Medical Sciences.
   - **Known weakness:** where fields tie (every engineering degree shares only `engineering`), the pick is
     alphabetical. More specific fields would fix it.
4. **UP's MBChB route after a degree year:** a considered bridge with 36 places open to all; the 66 places for
   designated groups go in its eligibility note only. **Decided:** as proposed.
5. **FLY@UP awards** can be worked out from course-finder marks. Show the 2026 amounts labelled "2026", or wait for
   2027's? Other awards keep UP's own eligibility wording, and we never ask.
6. **A points rule per programme.** SMU Pharmacy scores 90-100% as 8; SMU's BSc and emergency care tables leave Life
   Orientation out.
7. **TUT: a level-1 subject scores zero.**
8. **More subject keys:** technical mathematics, technical sciences, mathematical literacy, accounting, agricultural
   sciences, and "another language".
9. **TUT ranks every programme.** Proposal: `selective: true` only where TUT adds a test, interview, portfolio or
   audition or calls it highly competitive; published "admitted from" levels become `competitive_points`.
   **Decided:** as proposed.

**The brief's M1 sections** (built on `rinsuna/m1-after-acceptance`, 10 Oct 2026), refined from the brief's sketch:
- a calendar entry can name several campuses (none means every campus) and say who it's for (everyone,
  first-years or returning students); `step` marks the dates "first steps" come from
- more calendar kinds: revision, results, deadline, graduation, closed
- support kinds add careers and disability
- a money date can be a university's (fees), and its date key is `when`, because YAML reads `on` as true
- an applications section can say how to accept an offer; a funder can say what happens at registration

**How to apply** (built on `rinsuna/m1-how-to-apply`, 10 Oct 2026): a pack's `applications` section holds one window
per intake (the year a learner would start), with programmes that close on their own date, closing dates a
university names without saying which programme closes when, a late window or "no late applications", the fee in
cents, documents and next steps, each with its source. `funding.yaml` holds national funders the same way.

## Reading class announcements

- [ ] **Afrikaans words the engine reads** (added by Rinsuna's agent, 10 Oct 2026; a fluent speaker to check): toets,
  eksamen, vasvra, opdrag, werkopdrag, werkstuk, praktika, prak, verskuif, uitgestel, nuwe datum, gekanselleer,
  afgelas, "sal nie plaasvind nie", the months (Okt, Mrt, Mei, Des and the full names), the days, vandag and
  vanaand. They only read what a rep pastes; nothing is shown in Afrikaans. "Môre" is left out on purpose: it means
  "tomorrow" and "good morning".
- [ ] **Other languages' words** for test, exam, moved and cancelled (isiZulu, Sepedi, Setswana, Xitsonga and the
  others): not added, because we don't guess. A fluent speaker can list the words students really use. Messages that
  mix languages already work when the facts are in English (they're in the labelled set).

## Privacy and legal

- [ ] **Privacy Policy and Terms of Use** are drafts (`0.1-draft`, in `frontend/mobile/src/content/legal/`). They need
  the team's review and a legal professional's check before release. Each must name the information officer and
  contact details (not decided yet).
- [ ] **The audit trail stores personal data.** The reused code (see REUSE.md) records the full email address, IP
  address, user agent and session and device ids with every sign-in event, and keeps them with no deletion rule. The
  brief says audit events contain no personal data. Options: (a) store a keyed hash of the email and a shortened IP,
  (b) keep them for security with a stated retention period and say so in the Privacy Policy, (c) something else.
  Sessions and consent records also keep the IP address and app details.
- [ ] **Retention** for security records and for closed accounts. "Close my account" deactivates it; nothing removes
  a closed account's data yet. The brief's `DELETE /me` (delete the account and its data) and a complete
  `GET /me/export` are built on `rinsuna/privacy-export-delete` (10 Oct 2026), so the Security screen's "Delete my
  account and data: Coming soon" can become real. Still open: how long a closed account is kept, and the
  audit trail's records, which neither the export nor deleting touches.
- [ ] **The reused foundation, with Mandla no longer on the team** (raised 13 Oct 2026). M0 copied code from Akayza,
  © Team PR (Mandla and Rinsuna), and through it from TruConnect, an earlier project of Mandla's (REUSE.md). Both
  of Mandla's confirmations in REUSE.md are unsigned, and so is Rinsuna's. Rinsuna decides before the submission
  (Mon 26 Oct): get his written OK, or replace the reused files. LICENSE still names "Team PR (Mandla and
  Rinsuna)": also hers to decide. Agents don't edit REUSE.md or LICENSE.
- [ ] **Email sender.** Placeholders use `example.com` (we own no domain). Which address and inbox send the codes in
  production (`MAIL_DEFAULT_SENDER`, `MAIL_REPLY_TO`)?

## App and accounts

- [x] **Packs nobody has checked yet** are served, each labelled "Not yet confirmed by the team", so the demo works
  (Rinsuna, 9 Oct 2026). Whether production hides them can wait.
- [x] **Subjects a learner enters in the course finder:** the subjects admission rules name, plus up to three
  "another subject" rows that count towards points only; anything else is refused (Rinsuna, 9 Oct 2026). The M2
  marks screen offers these; see README, "Course finder". The API refuses a repeated subject, so the app keeps the
  last mark, says so (the engine's `duplicate` text), and sends each subject once.

- [x] **F6 "Fund and apply"** (agreed by Rinsuna on 9 Oct 2026 for M1; in scope since 13 Oct, when she became the
  whole team). The challenge asks us to
  help learners "compare funding options" and "complete applications". F6 shows funding routes for each choice in
  the plan, fees, and an application checklist. Like the course finder, it needs no account and stores nothing. Its
  facts come from the research notes. It should show TUT's late applications (14-22 January 2027, online, for
  programmes with space): the only way still open to apply for 2027 at our three universities. F6 goes beyond the
  brief's five features, so CLAUDE.md's Scope section now lists it. **Built in part on 10 Oct 2026** as
  "how to apply" inside the course finder's plan (`rinsuna/m1-how-to-apply`; README, "How to apply"): each
  choice's application status today, the dates still ahead, each university's fee, documents and next steps, and
  NSFAS. **Bursaries added on 11 Oct 2026:** Rinsuna asked for funding like UniApplyForMe's, reversing "no bursary
  list". `GET /funding` lists 19 funders (NSFAS, bursaries, UP's merit awards, a government loan scheme) with
  "N open now, N closing soon" and filters, `GET /funding/<id>` gives one in full, and each plan choice shows the
  funding its fields point to (README, "Funding"; [funding](research/funding.md)). The screens are in HANDOVER.
- [x] **Saving funding, with reminders** (new personal data: approved by Rinsuna on 11 Oct 2026). A
  signed-in student saves funders (UniApplyForMe's bookmark) and gets an alert when one opens after
  they saved it, and a week and a day before it closes; a switch turns the reminders off. We keep only the funder's
  id and the day, owner-only, in the export and deleted with the account. A saved list can hint at a funder's
  criteria (a population group, a disability), so no rep or admin view reads it and it's never counted. Built on
  `rinsuna/saved-funding` (README, "Saved funding").
- [ ] **Which intakes a plan shows** (decided by Rinsuna's agent while building, 10 Oct 2026; Rinsuna to confirm): the
  dates to start next year and the year after, plus this year's while a late window is still ahead, so the app asks
  nothing about the learner's grade. The alternative is one optional question ("When do you want to start?"), sent
  with the plan and never stored.
- [ ] **"Add these dates to my calendar":** the plan's `deadlines` list is ready for it. How (the phone's calendar or
  an .ics file) is Rinsuna's call; nothing goes to our server.
- [ ] **Your points at every university** (agreed by Rinsuna on 10 Oct 2026, after trying UniApplyForMe; Rinsuna to
  confirm the screen): `POST /pathways/points` gives the learner's points at UP, TUT and SMU, each by its own rule,
  and how many programmes they meet. It could open the course finder, before the learner picks a university.
- [ ] **Accepted: your first steps** (agreed by Rinsuna on 10 Oct 2026; Rinsuna to confirm the screen):
  `GET /universities/<id>/first-steps` gives accepting the offer, registering, orientation and the first lecture, on
  today's date, with what NSFAS does at registration. It could follow the plan, and greet a new student on Home
  before term. It's the "from acceptance" in the challenge.
- [ ] **My money's screens** (M3), on the API in `rinsuna/m3-profile-and-money` (README, "A student's own
  profile and money"):
  - **Reliability:** income sources say how reliable they are (`on_time`, `sometimes_late`, `often_late`,
    `not_sure`); the wording is ours. A late-prone next payment adds a note suggesting the "late" view.
  - **Balance:** the student enters it once, with the day it was true. It then stays current from the spending
    they log and the payments they mark received, so the screen never has to ask again.
  - **Onboarding:** a university and campus picker for `PUT /me/profile`.
- [ ] **The university's own deadlines in My week** (agreed by Rinsuna on 10 Oct 2026; Rinsuna to confirm): calendar
  entries with `period: deadline` (re-marks, exclusion appeals, module changes, graduation applications) shown with
  the class deadlines in M4's week view. **Built** on `rinsuna/m4-my-week`: each week of `GET /week` lists the
  calendar entries for the student's campus (deadlines, test weeks, exams, recess) beside its verified events.
- [ ] **My week's screens** (M4), on the API in `rinsuna/m4-my-week` (README, "My marks" and "Classes, reps
  and verified events"):
  - **Classes:** create one (you become its rep), join with a code (an invite code or a rep code, in the same box),
    and a rep's "add a rep" button that shows a one-time code to pass on.
  - **Rep panel:** paste an announcement; show `lines` and the `read_as` fields with the `needs_check` ones
    highlighted; the form starts from `proposed`; confirm or discard. For a "moved" or "cancelled" message,
    `changes_event` is the event it changes (the rep can choose another).
  - **Students:** their own announcements show "A class rep checks this before it goes live"; each event has a
    flag button with the six reasons.
  - **Week strip:** eight weeks with the `load` word (never colour alone), the `reason` line, and a tap to see the
    week's events and calendar entries.
  - **My marks:** modules with their assessments, the standing message, and the projection with its range.
- [ ] **Flag counts for reps** (decided by Rinsuna's agent while building, 10 Oct 2026; Rinsuna to confirm): a rep sees
  how many students flagged an event and why, from the first flag, never who. We read CLAUDE.md's "aggregates only
  when at least 5 students contribute" as covering marks and money. If the team reads it as covering flags too,
  reps would see counts only from 5 flags, and small classes would rarely see any.
- [x] **Every public university, and private colleges** (proposed by Rinsuna's agent and agreed by Rinsuna on 10 Oct
  2026): a directory of all 26 public universities with each one's application page, dates and fee, but not their
  admission rules; private colleges only as a link to DHET's register of private higher education institutions, so a
  learner can check a college is registered before paying; TVET colleges on the roadmap slide. **Paused** by Rinsuna
  the same day, after trying UniApplyForMe: it already covers 27 universities with their fees, so the time goes to
  support after acceptance instead ([competitors](research/competitors.md)). The directory, the DHET register link
  and TVET colleges go on the roadmap slide; the scope stays "SMU, UP or TUT for now".
- [ ] **Links to opportunity sites** (Graduates24, bursary websites): leads for us only, never a source for a fact. A
  "more opportunities" link in the app points learners at someone else's site, so it needs Rinsuna's OK. Never copy or
  scrape their listings. Rinsuna gave Graduates24's WhatsApp channel on 10 Oct 2026:
  https://whatsapp.com/channel/0029Va9MQ0jB4hdYtf0Wml0A. If Rinsuna agrees, it could sit beside the careers office on
  the Support screen; nothing in the app links to it yet.
- [ ] **Vac work, light version** (agreed for M1 the same day; Rinsuna to confirm):
  - In F6, a sourced "includes vac work" note on bursaries that offer it.
  - In My week, a nudge before each recess ("Recess from [date]: look for vac work in your field"). It links to the
    careers office: UP Career Services, TUT career counselling, or SMU's counselling centre, which offers career
    counselling.
  - A full opportunities board goes on the roadmap slide, not into the build.
- [x] **Demo accounts and the email code.** Signing in on a new phone or browser asks for a code sent to the account's
  email, and judges can't read the demo inbox. **Decided by Rinsuna on 10 Oct 2026:** demo accounts (made only by
  `flask seed`, fictional data only) skip the new-phone code. They can't be locked by wrong passwords, with 20 sign-in
  tries an hour per IP instead, and they can't change, reset or close. Built on `rinsuna/m5-alerts-support-demo`;
  Rinsuna reviews the identity change (#11).
- [ ] **Module alerts** (added by Rinsuna's agent in M5; Rinsuna to confirm): besides the brief's combined, heavy-week
  and money alerts, Home shows one when a module's target is out of reach, pointing to tutoring and counselling. Drop
  it if Home should keep to the brief's three.
- [x] **Expo and EAS.** The reused app config's EAS project id and owner were removed. Whose Expo account owns Campus Chommie's
  project (`eas init`), and who builds the Android preview? **Decided by Rinsuna on 10 Oct 2026**, because the team
  needs an installable app in different places: the project is `@rinsunamahani/campus-chommie`, under her own Expo
  account, and she builds the preview APK (README, "An installable Android app"). It signs in against the built-in
  mock until the backend is hosted. Since 13 Oct Rinsuna builds alone, so it stays under
  her own account.
- [ ] **Package name `za.campuschommie.app`.** Confirm before the first Play Store upload; it can't change after. The
  preview APK already uses it: changing it later is still possible, but phones with the preview would then see a
  second, separate app.
- [ ] **App icon, colours and slogan** ("From choosing a course to graduating.") are placeholders drawn for M0:
  keep or replace.
- [ ] **Google sign-in** is hidden until `GOOGLE_READY` (client ids and a native build). When it's switched on,
  Google sign-up must show the 18-or-older tick too (the backend already refuses it without).
- [ ] **Hosting** (brief section 14): which host, and an uptime check on `/api/v1/health`. Rate limits are counted in
  memory, which is right for one server process; more than one needs Redis (`RATELIMIT_STORAGE_URI`). **The backend
  is ready for any host that runs a container** (`rinsuna/ready-to-host`, 11 Oct 2026; [DEPLOY.md](DEPLOY.md)). Still
  to choose: the host, the managed PostgreSQL (a direct connection, not a transaction pooler), and whether to add
  error monitoring (an external service).

## Reminders for later milestones

- [x] M3: the first endpoint that takes numbers (money) gets the NaN/Infinity hostile-input test again: done on
  `rinsuna/m3-profile-and-money` (10 Oct 2026), with floats, text and booleans refused for cents too.
- M3: onboarding brings back an `(onboarding)` route group: 18-or-older confirmation (already recorded at sign-up),
  privacy notice, consent, university and campus. The student profile can read the 18-or-older date from the consent
  records.
- [x] M5: class updates (a new or changed event) are the first alerts a student can switch off, and the switches came
  back with them: done on `rinsuna/class-update-alerts` (10 Oct 2026).
- [x] M4: the money summary's life fund reads the student's week: done on `rinsuna/m4-my-week` (10 Oct 2026). The
  self-funded persona's heavy week now gives an amber life fund (the brief's M3 check); a student in no classes yet
  still sees "Your week isn't part of this yet".
- [x] M5: when a module's standing is out of reach, the alert points to the campus's tutoring and counselling from the
  pack: done on `rinsuna/m5-alerts-support-demo` (10 Oct 2026).
