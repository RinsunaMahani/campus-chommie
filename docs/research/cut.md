# CUT: undergraduate programmes for the 2027 intake

Agent draft, read on Thu 15 Oct 2026. Nobody has checked these values yet. `release` stays false.

## What was read

- **robots.txt per host.**
  - `www.cut.ac.za`: robots.txt returns 404, so nothing is disallowed. Its pages were read with curl's own user agent.
  - `cms.cut.ac.za`: robots.txt says `User-agent: *` / `Disallow: /`. Nothing was fetched from it (see "Blocked" below).
  - `www.online.cut.ac.za`: allowed apart from preview paths. Its sitemap lists only advanced and postgraduate diplomas, so it's out of scope.
- [Programmes offered](https://www.cut.ac.za/programmes-offered) has the list of 40 "first-time entering" undergraduate programmes.
  The [A-Z index](https://www.cut.ac.za/a-to-z) and the [course calculator](https://www.cut.ac.za/Course-calculator) add two
  more: the Diploma in Engineering Technology in Civil Engineering and the Higher Certificate in Retail Management. That makes **42 programmes**.
- One CUT programme page per programme (`https://www.cut.ac.za/programmes/<slug>`), each with "Programme-Specific
  Requirements" and "Selection Process" sections. Every programme's `requirements` cites its own page. Three links
  on the list page were broken (404). The working pages for those three came from the A-Z index: `dip-eng-tech-mechanical-engineering`,
  `dip-somatology` and `foundation-phase-teaching`.
- [Course calculator](https://www.cut.ac.za/Course-calculator) gives "Minimum points" for every programme.
- [Extended Curriculum Programmes](https://www.cut.ac.za/extended-curriculum-programme-ecp) says you can't apply for an ECP
  directly. You apply for the normal programme, and CUT may place you in the ECP stream. So the ECPs aren't separate programmes
  in the pack. Instead, the programmes that have an ECP mention it in `extras`.
- [Admission points (AP)](https://www.cut.ac.za/admission-points-ap) was read again for the points rule.

**Year.** The programme pages don't name an intake year. They are CUT's live pages during the 2027 application cycle (the
site footer says "Application Cycle 2027"), and they are the newest CUT has published. CUT calls its full prospectus the
"Student Calendar". The newest one is the 2026 edition, and it is on the blocked host.

## Blocked: a person should download these in a browser

All of these are on `cms.cut.ac.za`, which disallows every user agent. They are linked from https://www.cut.ac.za/calendar:

- CUT Student Calendar 2026 (CUT calls it "the prospectus of the university with full details on all programmes"):
  https://cms.cut.ac.za/Files/Froala/eb2a99cd-f346-42c9-9aae-3598ecd7dfab.pdf
- Grade 9 to 12 Subject Choice Guide (linked from Programmes offered):
  https://cms.cut.ac.za/Files/Froala/98dbd744-3e0a-4e80-9939-2dfc1f510f78.pdf

The Student Calendar should settle the points rule (section 4.1.5) and the conflicts listed below.

## Points rule: still null

The AP page gives the scale: 30-39% = 2 up to 90-100% = 8. Life Orientation counts at most 1, and you need 27 to be
admitted (22 to 26 means a selection test, 21 or less means no admission). It still doesn't say **how many subjects count**.
The course calculator doesn't settle it either. It adds up every subject you tick, and its dropdowns use levels 1 to 7 (80-100% = 7). That
disagrees with the AP page's 2-to-8 scale. So `points_rules` stays null and the app says points can't be checked yet.

## Approximations and choices

- **min_points from the programme page only.** 15 pages state no points minimum. Those programmes have `min_points: null` and an
  extras line quoting the course calculator's figure ("CUT's course calculator lists 27 points"). The 15 are: HC Mathematics for Engineering
  Technology, HC Dental Assisting, Dip Somatology, BSc Environmental Health (calculator: 30), Dip Design and Studio Art,
  Dip Language Practice and Media Studies, all seven BEds, Dip Agricultural Management and Dip Public Management.
  A reviewer may decide the calculator is good enough to fill these in, but a second source would be needed to cite it.
- **Dip Agricultural Management:** the page says no applicant under 23 points will be considered for selection, but the
  calculator says 27. Because the two disagree, it's `min_points: null`, with both figures in extras.
- **Dip Public Management:** the page says "a minimum score is required" and that candidates under 27 may go through
  selection, but it never names a minimum outright. So it's `null`, and the calculator's 27 is in extras.
- **HC Community Development Work:** CUT calls 26 "a recommended minimum" (the calculator also says 26). I used 26.
- **Accountancy and Internal Auditing:** the pages say "M-Score: Minimum 27". Other CUT pages say "APS (M-score)", so I
  treated it as the same scale.
- **"Computer Science"** (Dip Computer Networking, Dip IT) isn't an NSC subject key. Those two programmes have a choice of Mathematics 3 or Mathematical
  Literacy 5, and CUT's Computer Science alternative goes in extras.
- **BEd Foundation Phase and BEd Language Education:** the page names one of Sesotho, Afrikaans, Setswana, isiXhosa or
  isiZulu at 50%. I mapped that to `other_language: 4` and named the five languages in extras. The engine will accept any other language.
- **HC Dental Assisting:** "Physical Sciences: required as a Grade 12 subject" with no mark. I used `physical_sciences: 1`
  (taken, any mark), as nmu.yaml does.
- **HC Information Technology:** "language proficiency in English at NQF level 4" is ambiguous (NQF level isn't an
  achievement level). It's left out of subject_minimums and quoted in extras.
- **HC Mathematics for Engineering Technology:** 30% in Mathematics or Technical Mathematics was entered as level 2.
- **Selective** is true where the page names a selection process, test, interview, portfolio or limited places. That covers 18
  programmes, including Marketing, Accountancy and Internal Auditing, whose pages say a selection test "may be required".
  HRM and the HC Construction-type programmes only test people *below* the points minimum, so they aren't marked selective.
- Pre-2008 Senior Certificate rules, NCV/TVET routes, RPL and graduation modules are left out. Campuses and ECP routes are in extras.
- No requirements are null. All 42 programmes have requirements.

## Check first

1. The two conflicts between programme pages and the course calculator: Agricultural Management (23 or 27) and the 15
   programmes whose page has no figure. Check them against the 2026 Student Calendar.
2. The points rule: how many subjects CUT counts, and whether the scale is 1-7 (calculator) or 2-8 (AP page).
3. Agricultural Management's page says "1 year (full-time)" but 360 credits. The duration looks wrong on CUT's page. It isn't
   used in the pack.
4. BEd Mathematics and BEd Natural Sciences pages say their ECP is "not available for the Bachelor of Education in
   Foundation Phase Teaching". This looks like a copy-paste slip on CUT's site. It isn't used in the pack.
5. Bachelor of Construction in Construction Management and in Health and Safety Management ask only for an "NSC", not
   a bachelor's pass, which is unusual for a degree. Confirm this.
