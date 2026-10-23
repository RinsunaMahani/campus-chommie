# Open questions

Facts we don't have yet and decisions only the team can make. The app shows "Not verified yet" wherever a fact is
missing; nothing here may be guessed. Tick an item and add a line (who, when, the answer or a link) when it's
settled.

Since 13 Oct 2026 the team is Rinsuna alone (Mandla Baloyi is no longer on it), so every decision here is hers: the
items that waited for Mandla now wait for her.

## Triage summary (23 Oct 2026)

The open questions have been audited and sorted into three categories:

### 1. Completed on `main` (ticked `[x]` below)
- **Hosting:** Render (API) and Neon (PostgreSQL direct connection) live; `/api/v1/ping` uptime check added (PR #41, #75).
- **Reused foundation:** Mandla's verbal permission recorded in `REUSE.md` (PR #74).
- **Crisis lines:** Verified by Rinsuna for UP, TUT, and SMU; now active on Support screen (PR #82).
- **My money screens (M3):** Built with runway, safe to spend, life fund, late-payment toggle, payday plan, and store-card wallet (PR #24, #56, #58, #84).
- **My week screens (M4):** Built with 8-week strip, class reps, verified events, timetable PDF import, and calendar views (PR #25, #50, #52, #57, #61).
- **UJ and UWC campuses:** Researched from university websites on 22 Oct 2026 (`docs/research/campuses-uj-uwc.md`) and added to map data packs.
- **OpenStreetMap campus outlines:** Researched on 22 Oct 2026 (`docs/research/osm-missing-campuses.md`) and mapped on `main` (PR #77, #78).

### 2. Research an agent can do (official pages, documents and PDFs)
- Check household income lines on the 7 funders in `funding.yaml` against their official pages.
- Check NSFAS 2027 closing date reconciliation (31 Oct vs 18 Nov) with official updates.
- Check SMU BSc first year: verify requirements and whether Life Orientation is counted.
- Check SMU maximum choices (confirm 2 choices).
- Research cheap things near SMU, TUT Soshanguve, Ga-Rankuwa, Polokwane, eMalahleni from official venue pricing.
- Collect other languages' words for test/exam/moved/cancelled in class announcements.
- Check DHET college registers and university province/type citations.

### 3. Decisions only Rinsuna can make (policy, approvals, legal, and credentials)
- Final human fact check and sign-off of data packs (`verified_by: "Rinsuna Mahani"`, `release: true`).
- Select course finder translation languages and sign off in `docs/translation_review.md`.
- Confirm Android package name `za.campuschommie.app` before first Play Store upload.
- Confirm official app slogan.
- Configure production email sender (`MAIL_DEFAULT_SENDER`, `MAIL_REPLY_TO`) and domain.
- Switch on Google sign-in (built in PR #94): the Google Cloud web and Android clients and their IDs in Render and
  `eas.json` (DEPLOY.md, "Google sign-in").
- Switch on the WhatsApp bot (built in PR #93): Meta's app, test number and keys in Render (DEPLOY.md, "The
  WhatsApp bot (M6)").
- Legal review and audit trail retention policy.

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
- [x] **Rinsuna's fact check, 22 Oct 2026** (her fact-check sheet): every SMU fact (SMU is now `release: true`), the six
  crisis lines (SMU, TUT, UP: they now show in Support), NSFAS's 2027 window, application and income limit, the
  seven funders' income lines, and the flagged course-list rows (DUT 10, UKZN 5), all marked correct. Where she
  checked only some facts from a source, those facts cite a `<source>-checked` copy carrying her name, so
  `verified_by` never covers a fact she didn't check.
- [ ] **Household income in the funding pack** (added 22 Oct 2026, `income` on seven funders): each is the funder's own
  words from a page the pack already cites, and decides who appears under "If your family earns too much for NSFAS"
  (a funder that names the missing middle, or a limit above NSFAS's R350 000). Check each against its source: NSFAS
  R350 000 (R600 000 with a disability), Thuthuka R350 000, Sasol Foundation R800 000, Allan Gray R1 million / R1.5
  million, and "missing middle" for NSFAS's loan scheme, TUT's Bursary Fund and UP's funding database. Funders whose
  pages say nothing about income stay out of that group; the app never asks what a family earns.
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
- [x] **Crisis lines** for a person to verify: UP crisis line 0800 006 428 and the UP Careline 0800 747 747 (with
  SADAG); TUT's 24-hour counselling line 0800 68 78 88. SMU publishes no 24-hour line; its clinic page sends students
  to campus control or 079 417 9546 / 6278 after hours. **Done:** Rinsuna verified all crisis lines on 22 Oct 2026 (PR #82, `rinsuna/checked-by-rinsuna`); they now show on the Support screen.
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

## All 26 universities

Every public university now has a pack (#30, 13 Oct 2026, [research/universities.md](research/universities.md)):
its points rule where it publishes one the engine can follow, and how and when to apply. Programmes are at UP, TUT
and SMU and, since #32 and #33, at VUT, WSU, UMP, MUT, SPU, UFS and UNIZULU; the rest follow in waves. All are agent drafts.

- [ ] **Check the 23 new packs** against their sources, in a browser: UJ, UKZN, DUT and CPUT were read through a
  search engine's copy (bot checks, an unreachable site, expired or broken certificates).
- [ ] **No points rule yet** at CUT, SPU, CPUT and Fort Hare (not published, or not readable in full), and none
  possible at UCT and Stellenbosch (a Faculty Points Score; averages). Each says why in the app. DUT's rule was added
  on 22 Oct 2026 from page 8 of its Study Opportunities 2027 (top six subjects without Life Orientation, levels 1 to
  7): check it against the PDF. Still needed: CUT's Student Calendar 2026 (section 4.1.5; its host refuses bots),
  Fort Hare's 2027 prospectus (its site refuses Anthropic's agents), CPUT's Issuu prospectus (Issuu refuses bots),
  each downloaded in a browser; and SPU's answer to "how many subjects count?", which none of its documents says.
- [ ] **Where the engine is close but not exact** (each pack's `note` says so): UMP, UWC, UFS, UKZN, NMU and WSU
  always count certain subjects; the engine counts the best ones, which is the same for a learner with seven
  subjects. NMU's 7 points for quintile 1 to 3 schools and SPU's home-language bonus need questions we don't ask.
- [ ] **Two closing dates** at VUT (30 Sep and 30 Oct 2026): both kept until VUT says which.
- [x] **Which universities get programmes next?** All of them, Rinsuna chose (13 Oct): agents draft them in waves,
  those still taking applications first. Wave 1 is #32, wave 2 is #33, wave 3 is #34, wave 5 is #35; UJ, UKZN, DUT,
  Fort Hare and UWC need documents downloaded in a browser (HANDOVER, "Only Rinsuna can do these").
- [ ] **Check wave 1's course lists** (#32): each university's note in [research/](research/) starts with what to
  check first. The ones that change what learners see:
  - **WSU's Education programmes count seven subjects, Life Orientation included.** WSU says so for Foundation Phase;
    six of the other nine programmes list seven subjects whose minimums add up to the points asked, so all ten count
    seven, and their extras ask learners to confirm with WSU. Keep seven, or go back to six?
  - **MUT: five subjects or six?** MUT's admission page counts "the best five subjects"; the CAO's default and most of
    MUT's programme rows point to six. The pack follows the page, which gives fewer points (the IT diplomas count
    six, as they say).
  - **MUT's access courses** (seven bridging courses into its diplomas): keep them in the list?
  - **SPU** doesn't say how many subjects its points count, so its 26 programmes say they can't be checked yet.
  - Smaller ones in the notes: VUT's Internal Auditing (Mathematical Literacy 6 or 5), Technical Mathematics for its
    engineering diplomas, points under 30%; UMP's Hospitality Management page repeating Culinary Arts' points.
- [ ] **Check wave 2's course lists** (#33, [ufs.md](research/ufs.md), [unizulu.md](research/unizulu.md)):
  - **UFS (172 programmes):** two ECPs keep `requirements: null` (extended BEd, extended Bachelor of Sustainable
    Food Systems); check the AP calculation for selection programmes and the 2026 faculty rule books' ECPs.
  - **UNIZULU (185 programmes):** the points scale now gives 8 for 90-100%, as policy section 5.4 does, and the 2027
    window (31 Oct; the 40 new B Eds 30 Nov) is in (#33, 15 Oct); duplicate
    B Ed codes in CAO new programmes list (ZU-M-ILF / ZU-M-ILI, ZU-M-ILZ / ZU-M-ILW / ZU-M-IEJ); confirm with UNIZULU
    whether Senior/FET B Eds have 2027 intake after the 2026 pause.
- [ ] **Check wave 5's course lists** (#35): each note in [research/](research/) starts with what to check first.
  The ones that change what learners see:
  - **Stellenbosch** uses its 2026 prospectus (the 2027 booklet is on a host that refuses honest requests); the 2027
    one already asks more for some programmes (BA 65% average, Actuarial Science 85%).
  - **CPUT:** 44 of 119 programmes wait for the Issuu prospectus; the 15 health programmes use CPUT's own stated
    points method. **Nelson Mandela:** 32 either/or minimums fall between levels (55%, 65%), so the app checks from
    the level below and says so; an engine change could take exact percentages there.
  - **UCT, Stellenbosch and CUT** can't be checked yet (a Faculty Points Score, averages, and no stated subject
    count); their programmes show the published minimums.
  - **UWC** has no programmes: its site answers 403 to every honest request.
- [ ] **Check DUT's course list** (89 programmes from Study Opportunities 2027, agent draft of 22 Oct;
  [dut.md](research/dut.md) starts with what to check first). The ones that change what learners see: whether
  "Mathematics OR / Mathematical Literacy OR / Accounting" rows make Accounting an option or a must (Accounting,
  Taxation, Hospitality, Tourism), Drama's 22 or 24 points, and Electronic Engineering's Technical Mathematics.
- [ ] **Check UKZN's course list** (66 programmes from UKZN's 2027 prospectus, agent draft 22 Oct,
  [ukzn.md](research/ukzn.md)): a person should compare every value with the prospectus. First: 13 of its CAO codes
  are missing from the CAO's 2027 handbook (8) or spelled differently there (5): the B Sc streams appear there only
  as a "B Sc Generic Degree", and the Engineering Access Programme is KN-H-UNT at 28 points in UKZN's prospectus but
  KN-H-UNP at 33 in the CAO's handbook. Ten programmes ask different minimums in the two (among them CS and IT,
  GIS, B Admin, Housing and B Ed Foundation Phase); the pack follows UKZN and says so in each one's extras.
- [ ] **A local wave 4 nobody should push.** On the night of 14 Oct another session built `rinsuna/courses-wave-4`
  (12 universities in about 70 minutes), never pushed. Its values cite pages that don't hold them, and Fort Hare's
  came from the site that disallows Anthropic's agents. Rinsuna chose to redo it carefully (wave 5); the branch and
  `.worktrees/courses-4` are left untouched for her to delete.
- [ ] **Sites that ask AI agents not to fetch them** (their `robots.txt`, checked 14 Oct 2026):
  - **Fort Hare** disallows ClaudeBot and anthropic-ai on its whole site. Its course list (81 programmes, from its
    2027 study guide) was drafted before the agent read that file, so it's held out of the repo. The clean way: Rinsuna
    downloads the guide in her browser, and we check the draft against her copy before it goes in.
  - **The funding pack:** the Gauteng City Region Academy bursary pages and the Reserve Bank's bursary PDF disallow
    every bot. The same fix: Rinsuna's own downloads, checked against the pack.
  - **Couldn't tell:** UP's file server, UJ, UKZN's applications site, DUT, Rhodes, UWC, ISFAP, the City of
    Tshwane and VTM refuse their `robots.txt` to an honest user agent. Also blocked for wave 5: Issuu (Wits's and
    CPUT's prospectuses), files.su.ac.za (Stellenbosch's 2027 booklet) and cms.cut.ac.za (`Disallow: /`).
  - Until 14 Oct the agents' brief told them to send a browser's user agent. That was wrong: they now read
    `robots.txt` first and use their own (HANDOVER, "For a coding agent").

## Subjects in Find my course

The picker offers every subject on the DBE's Grade 10 to 12 list, in folders ([research/nsc-subjects.md](research/nsc-subjects.md)).
**Decided** by Rinsuna on 13 Oct 2026: of several official languages besides English, the best-marked counts as the
other official language, and the results say which; second additional languages count towards points only.

- [ ] **Home and first additional level share one key.** `english` and `other_language` each cover both levels, so a
  programme that sets a different minimum for each (TUT's BEd in Foundation Phase Teaching: a home language at 5 and
  a first additional language at 4) keeps `requirements: null`. Should the schema hold the level?
- [ ] **Technical-school versions.** The DBE also lists Technical: Civil, Electrical and Mechanical Technology. The
  picker offers one entry for each subject, sent under the key the rules use. Nobody has checked whether the
  universities treat the two versions alike.
- [ ] **Subjects outside the DBE's list** (for example ones only an independent examining body offers) have no
  place in the picker yet. Rinsuna to decide whether to add them as points-only subjects, each from its own source.

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
- [x] **The reused foundation, with Mandla no longer on the team** (raised 13 Oct 2026). M0 copied code from our
  earlier project (© Team PR: Mandla and Rinsuna) and, through it, from TruConnect, an earlier project of Mandla's
  (REUSE.md). **Done:** Mandla gave verbal permission to continue using the foundation code, recorded in `REUSE.md` on 22 Oct 2026 (PR #74, `rinsuna/reuse-permission`).
- [ ] **Email sender.** Placeholders use `example.com` (we own no domain). Which address and inbox send the codes in
  production (`MAIL_DEFAULT_SENDER`, `MAIL_REPLY_TO`)?

## App and accounts

- [x] **Packs nobody has checked yet** are served, each labelled "Not yet confirmed by the team", so the demo works
  (Rinsuna, 9 Oct 2026). Whether production hides them can wait.
- [x] **Subjects a learner enters in the course finder:** the subjects admission rules name, plus up to three
  "another subject" rows that count towards points only; anything else is refused (Rinsuna, 9 Oct 2026). Since #27
  the marks screen's picker offers every subject on the DBE's list and sends each under one of these keys (see
  "Subjects in Find my course"). The API refuses a repeated subject, so the app sends each subject once.

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
  funding its fields point to (README, "Funding"; [funding](research/funding.md)). **App screens built on 15 Oct 2026**
  (`rinsuna/ag-funding-button`, #37): the plan's footer opens the Funding screen (NSFAS and the filterable list of
  other bursaries, merit awards and loans, goal fields first) and the funder detail screen.
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
- [x] **Your points at every university** (agreed by Rinsuna on 10 Oct 2026, after trying UniApplyForMe; Rinsuna to
  confirm the screen): `POST /pathways/points` gives the learner's points at UP, TUT and SMU, each by its own rule,
  and how many programmes they meet. Built on `rinsuna/qualify-first` (#29) and `rinsuna/all-universities` (#30) across
  all 26 public universities.
- [x] **Accepted: your first steps** (agreed by Rinsuna on 10 Oct 2026; Rinsuna to confirm the screen):
  `GET /universities/<id>/first-steps` gives accepting the offer, registering, orientation and the first lecture, on
  today's date, with what NSFAS does at registration. **Built on 15 Oct 2026** (`rinsuna/ag-accepted-step`, #38): the
  plan's "If you're accepted" card opens the next-steps timeline, and "Create my student account" hands the university
  id (in memory only, never marks) to onboarding.
- [x] **My money's screens** (M3), on the API in `rinsuna/m3-profile-and-money` (README, "A student's own
  profile and money"):
  - **Reliability:** income sources say how reliable they are (`on_time`, `sometimes_late`, `often_late`,
    `not_sure`); the wording is ours. A late-prone next payment adds a note suggesting the "late" view.
  - **Balance:** the student enters it once, with the day it was true. It then stays current from the spending
    they log and the payments they mark received, so the screen never has to ask again.
  - **Onboarding:** a university and campus picker for `PUT /me/profile`.
  - **Built** on `rinsuna/money-screens` (#24, 13 Oct 2026). The words chosen, for Rinsuna to confirm: reliability as
    "Always on time", "Sometimes late", "Often late" and "Not sure"; the life fund as "Go out", "Go easy" and
    "Paused" (the engine's green, amber and paused); a balance that isn't changed keeps the day it was entered for.
- [ ] **The university's own deadlines in My week** (agreed by Rinsuna on 10 Oct 2026; Rinsuna to confirm): calendar
  entries with `period: deadline` (re-marks, exclusion appeals, module changes, graduation applications) shown with
  the class deadlines in M4's week view. **Built** on `rinsuna/m4-my-week`: each week of `GET /week` lists the
  calendar entries for the student's campus (deadlines, test weeks, exams, recess) beside its verified events.
- [x] **My week's screens** (M4), on the API in `rinsuna/m4-my-week` (README, "My marks" and "Classes, reps
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
  - **Built** on `rinsuna/week-screens` (#25, 13 Oct 2026). Words chosen, for Rinsuna to confirm: the flag reasons as
    "Wrong date", "Wrong time", "Wrong venue", "Not happening", "Listed twice" and "Something else"; a field the
    engine was unsure of is marked "Check this"; My week and My marks sit on the Week tab, between Home and Money.
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
- [x] **App icon and colours:** Rinsuna chose them on 13 Oct 2026 (#31): her forest theme, sampled from her
  homescreen (forest moss, olive sage, warm sage gold, dusty mauve and terracotta rose, with dark forest-glass cards
  and a white pill for the main action), for the whole app, and her interlocking CC as the app icon, adaptive icon and
  splash. Text colours were checked for WCAG AA on every band of the wallpaper.
- [ ] **Slogan** ("From choosing a course to graduating.") is a placeholder drawn for M0: keep or replace.
- [ ] **Google sign-in** (built 23 Oct 2026): the button shows once `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID` is set, on
  the web app and the APK (never in Expo Go, which lacks the native module). Rinsuna makes the Google Cloud clients
  and sets the settings (DEPLOY.md, "Google sign-in"). Google sign-up asks the same 18-or-older and Privacy and Terms
  boxes as email sign-up. Until the Google Cloud consent screen is published, only its test users can sign in.
- [x] **Hosting** (brief section 14): which host, and an uptime check on `/api/v1/health`. **Done:** Deployed on Render (API) and Neon (PostgreSQL, direct connection) free tiers on 21 Oct 2026 (PR #41, `rinsuna/free-hosting` and PR #75, `rinsuna/web-live-docs`). `/api/v1/ping` uptime check added. Rate limits are counted in memory, which is
  right for one server process; more than one needs Redis (`RATELIMIT_STORAGE_URI`). Still open: whether to add error
  monitoring (an external service).

- [x] **`BEHIND_CLOUDFLARE` on Render** (security sweep 1, 21 Oct 2026; [SECURITY.md](SECURITY.md)): the live API sits
  behind Cloudflare, so without this setting every visitor's rate limits probably count as one (all the judges
  together: 20 demo sign-ins an hour). Turning it on is a hosting change, so it's Rinsuna's call; afterwards, check
  with a few `GET /ping` calls carrying different made-up `CF-Connecting-IP` values that the header can't be forged.
  Rinsuna, 21 Oct 2026: yes, "the judges should have as much access as possible"; Argon sets it with the next deploy.

## Campus maps

- [x] **Campus maps** (a scope change by Rinsuna, 12 Oct 2026: the brief had an interactive map on the roadmap only).
  She chose OpenStreetMap for the data, buildings as well as campus outlines, and to name SMU's buildings herself.
  Built on `rinsuna/campus-maps`: `GET /universities/<id>/map` (README, "Campus maps"), with what's mapped and
  the licence in [maps](research/maps.md).
- [ ] **SMU's building names** (Rinsuna, on campus): OpenStreetMap names only 6 of the shapes on SMU's campus, all
  sewage works. Rinsuna types names on a numbered map page the agent made (13 Oct); the agent copies them into
  `backend/data/maps/names/smu.yaml`, credited to her, and runs `python scripts/fetch_osm_maps.py --names-only smu`.
  First the two the Support screen already names: the Clinpath Building (Student Support Referral Unit, room
  3L003) and the Natural Science Building (Religious Desk).
- [ ] **Campuses not mapped yet** ([maps](research/maps.md)): six have no outline in OpenStreetMap (UP Hillcrest and
  GIBS; TUT Soshanguve North, eMalahleni, Mbombela and Polokwane), and two have an outline with almost no buildings
  in it (UP Onderstepoort has 2, TUT Ga-Rankuwa none). A person could draw them in OpenStreetMap.
- [x] **The map's background:** Rinsuna chose (22 Oct 2026) to draw the streets ourselves: the fetch script also
  takes the roads within about 120 m of each campus and the paths across it from OpenStreetMap, and the app draws
  them under the buildings with the main road names. No tile service, no account, works offline.
- [ ] **Every university mapped** (asked by Rinsuna, 22 Oct 2026): 20 of 26 universities now list their campuses,
  each from the university's own page (agent draft), and their OpenStreetMap outlines are in
  `backend/data/maps/osm_campuses.yaml`. Check each pack's new `campuses:` against its source. Still to do:
  - **UJ and UWC** (their sites answer 403 to honest requests) and **Fort Hare** (its robots.txt disallows
    Anthropic's agents): a person reads their campus pages in a browser; OpenStreetMap already has their outlines
    (UJ APK, APB, Doornfontein and Soweto; UWC Bellville; Fort Hare Alice, Bhisho and East London).
  - **Campuses with no outline in OpenStreetMap:** CUT Welkom, DUT Brickfield and Riverside, MUT's Natural
    Sciences campus, UKZN's Medical School and UMP Siyabuswa. The app says they aren't mapped yet.
  - **Choices to check:** Wits's Braamfontein East and West are one campus (OpenStreetMap doesn't tell them apart),
    and UCT's Upper, Middle and Lower are one (OpenStreetMap draws them as one); UL is Turfloop only (its about page
    names Ga-Rankuwa only in its history, before MEDUNSA became SMU); Stellenbosch is Stellenbosch and Tygerberg,
    the two its prospectus names (Elsenburg, where some students live, is the Elsenburg Agricultural Training
    Institute, not an SU campus).
  - **OpenStreetMap changes:** on 22 Oct SMU had 60 buildings, not 281: a data-repair account deleted 221 of them on
    9 Jun 2026 (our 13 Oct copy came from an out-of-date server). UP Prinshof went from 19 to 271, newly mapped.
- [ ] **"You are here"** (Rinsuna's call): a dot from the phone's own location. It would stay on the phone: the
  API takes no location and refuses one. It needs a location permission and a package the reused app removed.
- [ ] **The ODbL** (with the legal check above): our map files and the names we add stay under the ODbL, never "all
  rights reserved"; the public API is the free, machine-readable copy the licence asks us to offer (ODbL 4.6).

## Colleges (TVET and private)

From DHET's four publications (`backend/data/national/colleges.yaml`, read with a script on 20 Oct 2026). An agent
draft: `release: false` until a person compares the pack with the registers.

- [ ] **Check the pack against the registers**: every name, registration number and status, especially where the
  script had to work around the PDFs: the IIE's number (2007/HE07/002) was read from the register's plain text
  because its table cell is garbled; six bogus-list names were split across lines in the PDF and joined by hand.
- [ ] **No registration number in the register**: Empilweni Education (Pty) Ltd (listed as registered, with no
  number, sites or qualifications) and Adu Dlamini Business and Engineering Academy (Pty) Ltd. Ask DHET, or leave
  "not shown in the register".
- [ ] **One number, two entries**: 2008/HE07/008 (IHT Hotel School, both registered and cancelled), 2018/FE07/043
  (Mahikeng City College, cancelled; Easy Business Academic Centre, registered) and 2025/FE07/003 (Kitso Training
  and Moripe Business Training, both registered). Printed as DHET prints them; the check shows every match.
- [ ] **Numbers printed with typos** (kept as printed): 2008/SFE07/108, 2023/FE07/006F, 2019/FE007/031.
- [ ] **Conference and Events Organiser**: DHET's 2026 occupational list names no college for it.
- [ ] **Registers change** (DHET updates them every few months): who re-reads them, and how often? The last
  versions we used: private higher education 12 August 2026, private colleges 15 July 2026.
- [ ] **TVET websites** (checked 20 Oct 2026): 25 of the 50 addresses on DHET's contact page no longer work (gone,
  parked, suspended, empty or under construction), so the app shows no link for them. Argon found newer sites for
  most (for example `ksdcollege.edu.za`, `malutitvet.co.za`, `coastalkzn.co.za`; Argon's `argon-round3/task4-tvet-dates`
  in Rinsuna's Downloads). A person must confirm each is the college's own (the college's or DHET's page
  linking to it) before it replaces DHET's address in the pack.
- [ ] **Entry requirements**: colleges don't publish points scales, so the app says "check with the college" and
  links its site. TVET admission rules (NC(V), Report 191) could come later, each from its own source.

## Province and type of each university

Added on 20 Oct 2026 only where the university's own page prints it (Argon's Round 5, every page re-read):
province for 16 universities, type for 9 (the six universities of technology; UNIVEN, UNIZULU and WSU as
comprehensive). The app shows only these.

- [ ] **Province not confirmed on a source** (a person can confirm each from the university's contact page):
  DUT, NMU, NWU, SU, UCT, UJ, UNISA, UP, UWC, Wits. SU, UJ, UP and UWC block automated requests.
- [ ] **Type not stated by the university**: the 11 DHET calls "general academic" and the comprehensive ones
  that don't say so on their pages (UJ, NMU, SMU, SPU). DHET's per-university master list needs a login
  (`dhet.gov.za/MasterLists`). UMP's "comprehensive university" page redirects to a login; UNISA's page calls its
  teaching model "comprehensive", not the university.
- [ ] **WSU** says it is "one of six" comprehensive universities; DHET's 2022 statistics count nine.

## WhatsApp bot (M6)

- [ ] **WhatsApp test number:** Meta's free test number only talks to phones on its recipient list (added and
  confirmed in the Meta app), so judges can't message it unless their numbers are added. For the hackathon: show the
  bot in the demo video, and say so on the slide. Talking to anyone needs a real business number, which needs Meta's
  business verification: Rinsuna's call, after the hackathon.
- [ ] **The access token:** API Setup's temporary token stops after 24 hours; Render needs a system user's token
  (DEPLOY.md, "The WhatsApp bot"). Rinsuna sets it, never in the repo or a chat.
- [x] **"Salted hashes" for numbers (decided 23 Oct 2026):** a number is kept as HMAC-SHA256 with a server key
  (`WHATSAPP_PHONE_KEY`), not with a per-row salt: a message arrives with only the number, so the hash has to be
  found by the number, which a per-row salt prevents. Without the key, a leaked table can't be tested against any
  number. Changing the key unlinks everyone.
- [ ] **Push reminders over WhatsApp** (new events, 24 hours before a deadline): not built. They would need each
  number kept so the bot can start a chat, plus Meta's approved message templates. Class updates keep going to the
  app's Updates instead.

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
