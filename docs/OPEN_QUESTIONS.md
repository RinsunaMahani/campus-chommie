# Open questions

Facts we don't have yet and decisions only the team can make. The app shows "Not verified yet" wherever a fact is
missing; nothing here may be guessed. Tick an item and add a line (who, when, the answer or a link) when it's
settled.

## Facts for the data packs (Rinsuna)

Research notes from official documents, read on 9 Oct 2026 and not yet checked by a person: [UP](research/up.md),
[TUT](research/tut.md), [SMU](research/smu.md). Each lists its sources, gaps and inconsistencies.

- [ ] **SMU admissions:** re-check every value in `backend/data/universities/smu.yaml` against the current prospectus
  (copied from SMU's medicine admissions page on 30 Sep 2026; `verified_by` still says it needs the team's check).
  SMU's medicine page still matched the pack on 9 Oct.
- [ ] **SMU BSc first year:** admission requirements (the pack has `requirements: null`). Found on SMU's Science and
  Technology page: APS 25; English 4, Mathematics 5, Life Sciences 4, Physical Sciences 4, two more at 4. Open: those
  add up to 25 without Life Orientation, so does it count?
- [ ] **SMU maximum choices** per application (`max_choices: null`). Found: two (SMU's 2027 application page).
- [ ] **SMU calendar, allowance dates and support contacts** (counselling, crisis lines, financial aid, food support,
  tutoring, chaplaincy, health), each from an official source. Crisis contacts must be verified by a person before
  release. Found: the 2026 calendar, health, counselling, the referral unit (it refers to tutoring and financial aid)
  and 2026 fees. Still missing: the 2027 calendar, a 24-hour line, food support, chaplaincy and allowance dates.
- [x] **Changes to `smu.yaml`** that the research supports, for the team's OK: `max_choices: 2`; the BSc first-year
  requirements above; MBChB `places: 250`; the other SMU programmes; a considered route from SMU's first year into
  BDS (2 places); and the medicine foundation year's eligibility note, which leaves out SMU's population-group
  restriction (details in [smu.md](research/smu.md), "Notes for the data pack"). Approved by Rinsuna on 9 Oct 2026;
  applied on 10 Oct (`rinsuna/m1-data-packs`). Also marked BSc first year `selective: true`, because every SMU
  school page says selection is competitive: check.
- [x] **UP and TUT packs**, from official sources. Drafted on 10 Oct 2026: `up.yaml` (120 programmes) and `tut.yaml`
  (124; the Diploma in Fire Technology is left out, as it's only for people already in fire services). Both
  `release: false`, every source `verified_by: "agent draft, needs human check"`.
- [ ] **A person checks the packs** against their sources before any is released: every value in `up.yaml` and
  `tut.yaml`, the SMU values added on 10 Oct, and the lines marked "Check" in the packs and research notes. Then set
  `release: true` and fill in each source's `last_verified` and `verified_by`.
- [ ] **Campuses** for each university (needed for F1 and the support screen). Found for all three; a person still
  checks them with the rest.
- [ ] **Course finder languages:** which 2 or 3, and the fluent reviewers who sign them off in `docs/translation_review.md`.

### Gaps the research left

- [ ] **Need a browser:** UP's application fee and waiver, documents, offer deadline, registration payment and tuition
  per programme appeared only in search snippets. UP's web pages refuse automated reading; open them and save as PDF.
- [ ] **Programmes per application** at UP and TUT: not published in the documents read.
- [ ] **TUT's APS:** how many subjects count (TUT says only "a minimum of six subjects", Life Orientation excluded).
  Until TUT confirms, the TUT pack counts the six subjects besides Life Orientation and says so (Rinsuna, 9 Oct 2026):
  if TUT counts more, we only under-count. An email to `admission@tut.ac.za` would settle it.
- [ ] **Tuition per programme** at TUT (charged per module; TUT has an online quotation page).
- [ ] **SMU 2027 calendar**, and **2028 entry dates** for UP and SMU (TUT's are published).
- [ ] **NSFAS:** the 2027 application window and allowance dates (not researched yet).
- [ ] **Crisis lines** for a person to verify: UP crisis line 0800 006 428 and the UP Careline 0800 747 747 (with
  SADAG); TUT's 24-hour counselling line 0800 68 78 88. SMU publishes no 24-hour line; its clinic page sends students
  to campus control or 079 417 9546 / 6278 after hours.
- [ ] **Smaller inconsistencies** are listed at the end of each research note (for example, two closing dates for TUT's
  Bachelor of Geomatics, and a UP table that ends mid-row).

## Data-pack schema (Rinsuna)

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

## Privacy and legal (both)

- [ ] **Privacy Policy and Terms of Use** are drafts (`0.1-draft`, in `frontend/mobile/src/content/legal/`). They need
  the team's review and a legal professional's check before release. Each must name the information officer and
  contact details (not decided yet).
- [ ] **The audit trail stores personal data.** The reused code (see REUSE.md) records the full email address, IP
  address, user agent and session and device ids with every sign-in event, and keeps them with no deletion rule. The
  brief says audit events contain no personal data. Options: (a) store a keyed hash of the email and a shortened IP,
  (b) keep them for security with a stated retention period and say so in the Privacy Policy, (c) something else.
  Sessions and consent records also keep the IP address and app details.
- [ ] **Retention** for security records and for closed accounts. "Close my account" deactivates it; nothing removes
  a closed account's data yet, and the brief's `DELETE /me` (delete the account and its data) isn't built. The
  Security screen shows "Delete my account and data: Coming soon" until it is.
- [ ] **Email sender.** Placeholders use `example.com` (we own no domain). Which address and inbox send the codes in
  production (`MAIL_DEFAULT_SENDER`, `MAIL_REPLY_TO`)?

## App and accounts (Mandla)

- [x] **Packs nobody has checked yet** are served, each labelled "Not yet confirmed by the team", so the demo works
  (Rinsuna, 9 Oct 2026). Whether production hides them can wait.
- [x] **Subjects a learner enters in the course finder:** the subjects admission rules name, plus up to three
  "another subject" rows that count towards points only; anything else is refused (Rinsuna, 9 Oct 2026). The M2
  marks screen offers these; see README, "Course finder". The API refuses a repeated subject, so the app keeps the
  last mark, says so (the engine's `duplicate` text), and sends each subject once.

- [ ] **F6 "Fund and apply"** (agreed by Rinsuna on 9 Oct 2026 for M1; Mandla to confirm). The challenge asks us to
  help learners "compare funding options" and "complete applications". F6 shows funding routes for each choice in
  the plan, fees, and an application checklist. Like the course finder, it needs no account and stores nothing. Its
  facts come from the research notes. It should show TUT's late applications (14-22 January 2027, online, for
  programmes with space): the only way still open to apply for 2027 at our three universities. F6 goes beyond the
  brief's five features, so if confirmed, CLAUDE.md's Scope section gains it.
- [ ] **Vac work, light version** (agreed for M1 the same day; Mandla to confirm):
  - In F6, a sourced "includes vac work" note on bursaries that offer it.
  - In My week, a nudge before each recess ("Recess from [date]: look for vac work in your field"). It links to the
    careers office: UP Career Services, TUT career counselling, or SMU's counselling centre, which offers career
    counselling.
  - A full opportunities board goes on the roadmap slide, not into the build.
- [ ] **Demo accounts and the email code.** Signing in on a new phone or browser asks for a code sent to the account's
  email, and judges can't read the demo inbox. Decide before M5, for example: the team keeps the demo inbox and
  pre-trusts nothing, or demo accounts (and only they) skip the new-phone code, with tighter rate limits.
- [ ] **Expo and EAS.** The reused app config's EAS project id and owner were removed. Whose Expo account owns Campus Chommie's
  project (`eas init`), and who builds the Android preview?
- [ ] **Package name `za.campuschommie.app`.** Confirm before the first Play Store upload; it can't change after.
- [ ] **App icon, colours and slogan** ("From choosing a course to graduating.") are placeholders drawn for M0:
  keep or replace.
- [ ] **Google sign-in** is hidden until `GOOGLE_READY` (client ids and a native build). When it's switched on,
  Google sign-up must show the 18-or-older tick too (the backend already refuses it without).
- [ ] **Hosting** (brief section 14): which host, and an uptime check on `/api/v1/health`. Rate limits are counted in
  memory, which is right for one server process; more than one needs Redis (`RATELIMIT_STORAGE_URI`).

## Reminders for later milestones

- M3: the first endpoint that takes numbers (money) gets the NaN/Infinity hostile-input test again (it went with
  the reused business-profile tests).
- M3: onboarding brings back an `(onboarding)` route group: 18-or-older confirmation (already recorded at sign-up),
  privacy notice, consent, university and campus. The student profile can read the 18-or-older date from the consent
  records.
- M4: class updates are the first alerts a student could switch off; notification switches come back with them.
