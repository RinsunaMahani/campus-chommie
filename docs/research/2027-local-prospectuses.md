# Official 2027 documents supplied on 24 October 2026

Rinsuna downloaded these documents and authorised data changes. The agent read the local files from Downloads,
without circumventing sites' robots rules or access controls. Supplying the files does not mean Rinsuna checked
every extracted value. New sources have `retrieved: 2026-10-24`, `last_verified: null`,
`verified_by: "agent draft, needs human check"`; packs remain `release: false`.

PDFs and extraction/rendering caches are not committed. These hashes identify the editions read:

| University | Filename | Pages | SHA-256 |
|---|---|---:|---|
| CPUT | `2027-Prospectus-080526.pdf` | 15 | `5a663050603b0e220bb4b32d9960efc3eae6756722d6c8dd12e920ad85c858fc` |
| UFH | `Study-Guide-2027.pdf` | 2 | `895253006fad088839bae08689ac81ed20b375c18f43f1afedce4368ec59a3c5` |
| UWC | `SEMU-8-Panel-Print-Admissions-2027.pdf` | 2 | `f3e4e797c052a54c3e1f4f1c920aa1a43dda7ff3b413214c11812935fead064d` |
| UJ | `uj_undergrad_prospectus2027_online_25jun2026.pdf` | 100 | `998901c32c614f00a5b8f9fe22b6f4e3c06772c2bf00bf07fd6bef1304ea499c` |

Pack URLs identify official admissions/prospectus landing pages, not guessed PDF URLs. Page references below
refer to these files.

## Coverage added

- **UFH:** 52 qualification rows across six faculties, from both pages; Alice, Bisho and East London campuses
  from p.1. BSc streams remain under the parent BSc. The guide lacks a complete university-wide APS calculation
  table, so subject checks are available but points remain manual. Management and Commerce's explicit LO cap
  of 4 has not been extrapolated to other faculties.
- **UWC:** 39 qualification rows from p.2 and financial aid contacts from p.1. BA majors remain under BA with
  additional Mathematics restrictions in the notes. Much of the table is graphical: rendered pages were read.
- **UJ:** 175 programme/major-combination entries. Art/Design pp.32–34; Business/Economics pp.40–47; Education
  pp.54–55; Engineering pp.60–63; Health pp.66–69; Humanities pp.74–76; Law p.82; Science pp.86–94. Language Practice
  is printed twice on p.75 but counted once. Public Management's identical APK/SWC routes are one entry.
  These are NSC rules, not NASCA/NCV rules. Support contacts come from pp.20–24; no new crisis number is made visible.
- **CPUT:** 40 of 44 previously empty requirement records filled. Business p.9; media/ICT/planning p.13;
  engineering/construction pp.14–15. Method 1 on p.3 sums six percentages and divides by ten, excluding LO.
  Construction uses NSC levels instead. Method 2 and unspecified methods retain manual points. The p.13 Technical
  Maths column explicitly caters for TVET students; the new records encode NSC Mathematics/Mathematical Literacy
  routes and direct TVET applicants to the faculty. Departmental portfolio/selection checks remain in notes.

The original 57 missing requirement records are reduced to 17. New programmes expose additional unassessed rows;
a smaller warning count alone is not proof of complete data. See [the queue](../DATA_READINESS.md).

## Rules requiring confirmation before assessment

The first 25 October follow-up reduced 55 missing requirements to 35. Optional English Home/First Additional
Language input resolves five UWC and ten UJ BEd/social-science rules. UJ Information Management and Sport and
Exercise Science, CPUT Clothing/Textile mainstream and ECP, and UFH Public Administration now encode the
published subject routes. Where a route omits its APS, the result is only "Subjects met", never an eligibility claim.

These remain `requirements: null`:

- **UFH (3):** Education Commerce names Business management; Education Science names Computer science;
  mainstream Crops omits the English level. Extended LLB now checks its published subject routes while leaving
  the missing Mathematics-route APS unassessed.
- **UJ (9):** Geography BEd's ambiguous alternative;
  four extended engineering rows without an explicit
  science-column OR; four Physical Sciences rows whose Mathematics footnote differs from the table.
- **CPUT (2):** Banking mixes vocational/NSC terminology and omits its APS method; Senior/FET BEd requires
  named language roles and electives.
- **Other universities (9):** unresolved placement, prior-qualification and language conditions or
  contradictory/unpublished rules. Programme IDs are listed in [the generated queue](../DATA_READINESS.md).

UWC application dates remain contradictory: opening is unknown, and both published closing-date possibilities
are retained. Official provenance does not settle conflicting statements. Programme-specific additional
selection and module restrictions remain visible in notes.

## Additional campus information

Wits public pages were read on 24 October after checking robots rules:

- [2027 term dates](https://www.wits.ac.za/students/academic-matters/term-dates/2027-term-dates/): thirteen periods,
  with Health Sciences exceptions and cohort-specific registration. No summer-break end date was invented.
- [Student support](https://www.wits.ac.za/teaching-and-learning/student-support/): CCDU counselling/careers contacts.
- [Financial aid](https://www.wits.ac.za/study-at-wits/financial-aid-and-scholarships-administration/): phone,
  walk-in hours and the query portal rather than obsolete email instructions.
- [Art Museum](https://www.wits.ac.za/wam/visit-us/): free entry, published opening hours and entrance.

On 25 October, further official pages brought support coverage to **92 contacts across all 26 universities**.
Coverage is still uneven by campus and service type. Each added contact cites its own page. General switchboards
and referral offices are labelled as such; unpublished hours were omitted. Fort Hare's current counselling email
differs from the downloaded research CSV: the official FYE page takes precedence. UNIVEN's exact counselling-unit
URL supplied in that research resolved the earlier unavailable links.

Official PDFs/pages add CPUT (10), DUT (11), Rhodes (10), UCT (7) and NWU first-year (3) calendar entries.
CPUT revision periods are not labelled tests, inferred recesses are omitted, and Rhodes's tentative shutdown
is excluded. Terms can include assessment periods; campus/cohort exceptions are preserved in notes.
At that stage, seventeen universities had no calendar entries and 22 had no priced/free activities; the internet
follow-up below fills those empty sections. The downloaded `calendar.csv` is a discovery aid, not sufficient
evidence by itself: some entries infer dates not actually stated in their cited document.

## Verification decision, 25 October 2026

Rinsuna instructed: "for verification if it is from the official university thats good enough".
The 471 dated sources hosted by the universities now explicitly use `verification_basis: official_university`.
Acceptance is based on their recorded provenance, not a claim that every URL was fetched again on 25 October.
Source URLs, retrieval dates, existing human sign-offs and agent attribution are preserved. No new personal
verification dates were invented. Rinsuna subsequently accepted dated official funder, government and venue
publications too. These use `verification_basis: official_publisher`; 57 existing dated official sources were
accepted without rewriting retrieval dates or claiming they were all freshly fetched.
The schema rejects lookalike domains and missing retrieval dates. Contradictions and missing programme rules
remain separate from source authenticity, as does incomplete calendar/support/activity coverage.

## Source-review checklist

Run `python scripts/data_readiness.py --as-of 2026-10-25 --json` from `backend` for each source URL, retrieval date,
reviewer and verification date. Compare pack values with those pages or the identified PDF pages. Only record a
person's name/date for values that person actually checked. Resolve conflicts before enabling assessment.
Preserve the existing SMU and critical funding/crisis sign-offs.

The validator flags empty programme/source lists and requires accepted source evidence for releases.
Stale and future evidence dates are release errors. University confirmation and crisis visibility accept dated
official university evidence as well as human review. Funding accepts approved official publisher provenance
and still requires the pack's separate release flag.

## Internet follow-up, 25 October 2026

The subsequent search fills nine more programme rules: UP Food Management, both UP Music programmes,
SU Public Accountability, UFH extended LLB, and four UJ extended BA programmes. There are **26 remaining null
requirements**. The Music alternatives require university assessment of external qualifications; SU's experience
or prior-qualification route is likewise not assumed from school marks. UJ's published APS 24–26/27 bands are
checked with the appropriate English thresholds; a higher APS is referred to UJ instead of extrapolated.

New admission evidence:

- [UP 2027 Natural and Agricultural Sciences brochure](https://drupalwebprod-files.up.ac.za/Public/2026-01/UP_FB%20Natural%20and%20Agricultural%20Sciences%202027_DevV6_web.pdf?VersionId=EDlRCPB_tAeNHibkLpQTK5Ug.QvByUSZ): Food Management, English 5, Mathematics 4, APS 28.
- [SU Public Accountability](https://www.su.ac.za/en/faculties/economy/departments/public-leadership/study-spl/diploma-public-accountability): NSC route and alternative experience/qualification routes.
- [UJ official 2027 prospectus](https://www.uj.ac.za/wp-content/uploads/2026/06/uj_undergrad_prospectus2027.pdf), p.76, corroborates the supplied PDF's extended BA bands and interview condition.
- [MUT department page](https://www.mut.ac.za/faculty-of-applied-and-health-sciences/department-of-community-extension/) still differs from its general prospectus and [2026 admissions notice](https://www.mut.ac.za/notice-to-prospective-students-and-parent/). No invented reconciliation.
- [CPUT Banking course page](https://prospectus.cput.ac.za/index.php/course-details?f=60&q=D3BNKG) directs applicants to general requirements and does not settle the supplied table's additional-subject ambiguity.

All 26 universities now have some calendar, support and activity coverage, with **93 support contacts**. This is
not a claim of complete campus/service coverage or complete 2027 calendars. The generated readiness report lists
calendar counts by year and uncovered campuses. Sources for every imported entry are in its pack.

Calendar checks include VUT's official spreadsheet (merged cells determine date spans), the UNIVEN general
calendar (rendered pages 7–8), UNIZULU's general calendar, WSU's 2026 prospectus (rendered p.16), UFS's senate-approved
2027 calendar, SU's published 2027 dates, and the universities' current registration/almanac pages. CUT's separate
registration cohorts replace the research CSV's combined window. UWC's revised second semester takes precedence.
WSU's inconsistent public-holiday column was not imported. Fort Hare's 2026 orientation, late-registration and
lecture-start dates came from the **official page's search-index excerpt**, explicitly identified in source title
and entry notes; no direct request bypassed its robots policy.

Activities use official venue, university or municipality publications. These include SANBI's Thohoyandou visitor
prices for UNIVEN; East London Museum for UFH/WSU; and Bakone Malapa for UL/TUT. The latter uses Schedule 10,
printed p.158 of [Gazette 3828](https://www.polokwane.gov.za/wp-content/uploads/APPROVED-TARIFFS-2026-2027-GAZETTE-NO.3828.pdf),
effective 1 July 2026, checked visually. The [August erratum](https://www.polokwane.gov.za/wp-content/uploads/ERRATUM-TARIFFS-GAZETTE-NO.3851.pdf)
does not alter that schedule. UNIZULU's Science Centre listing explicitly describes educational group visits,
minimum group charges and the need to confirm eligibility; no individual walk-in price is inferred.

Optional named-language roles now resolve UJ Afrikaans, isiZulu and Sepedi BEd requirements (2027 prospectus p.55):
APS 28, English HL 5/FAL 6 and the named language HL 4/FAL 5. Language identity travels on its existing mark row;
additional languages never add duplicate APS entries. Old clients without identity remain unverified for these rules.
Remaining software limitations include teaching elective combinations. Remaining evidence
gaps include conflicting UFS/MUT rules, UJ science alternatives/footnotes, missing UFH English/subject equivalence,
and faculty-selected or prior-degree routes. Official source acceptance does not settle these contradictions.
SPU's externally hosted 2027 prospectus remains the one university source without accepted verification metadata:
its [official prospectus page](https://www.spu.ac.za/index.php/prospectus-2026/) links through a protected redirect
that stops at a Mimecast portal, so the current destination could not be matched to the existing Adobe document.
The Adobe domain was not broadly approved and the existing citation/retrieval history was preserved.

## Validation of this change

- Pack validator: zero errors after the 25 October support/calendar imports; coverage warnings remain.
- Frontend: TypeScript and Expo lint passed; 35 Jest suites / 281 tests passed.
- Full backend run including named-language assessment: 1,641 passed; two existing Flask-Migrate
  deprecation warnings. SPU image provenance/text follow-up is checked separately by the catalogue tests.
- English-role and source-verification regression tests passed. Database tests used an isolated agent-owned
  PostgreSQL database on port 55439.
- No production database was used. Work remains on `rinsuna/data-completeness`, undeployed.

## Campus support follow-up, 26 October 2026

The [CPUT official directory](https://www.cput.ac.za/about-cput/contact-details) supplies Granger Bay campus
security contacts, explicitly labelled security rather than counselling.
The [UFH 2026 orientation guide](https://fye.ufh.ac.za/wp-content/uploads/2026/01/2026-Orientation-Guide.pdf)
adds financial aid for Alice/East London (printed pp.24–25), disability desks in each city (p.37), and the
university-wide GBV/safety telephone service (p.42). Relevant PDF pages were rendered and checked visually.
The central telephone service can be used by Bhisho students; its only published physical offices are Alice
and East London, and the app states that distinction. These five additions bring support contacts to 98.
All listed campuses now have at least one contact; this does not establish complete on-site service coverage.
The guide's calendar heading and weekdays are inconsistent, so no new calendar dates were inferred from it.
Both sites' robots rules allowed these document paths. No blocked UFH main-site page was fetched.

## Additional 2027 dates, 26 October 2026

[UJ's 2027 academic calendar](https://www.uj.ac.za/wp-content/uploads/2025/06/2027-academic-calendar.pdf)
(Senate S 221/2025) supplies 15 student registration, teaching, assessment, revision and recess periods.
The official search index exposed the complete table; direct retrieval was robots-blocked and was not attempted
through another tool. Source title and calendar notes explicitly identify indexed evidence. Semesters retain their
published span, including recesses; no orientation dates or December holiday end were inferred.
[CUT's registration page](https://www.cut.ac.za/enrolment-process) now publishes 2027 first-year registration,
senior registration and course-control dates. The first two have separate cohort labels. The postgraduate-only
window is omitted from this school-leaver flow. These additions retain the existing 2026 calendar records.
