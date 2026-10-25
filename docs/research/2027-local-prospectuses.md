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

The 25 October follow-up reduces 55 missing requirements to 35. Optional English Home/First Additional
Language input resolves five UWC and ten UJ BEd/social-science rules. UJ Information Management and Sport and
Exercise Science, CPUT Clothing/Textile mainstream and ECP, and UFH Public Administration now encode the
published subject routes. Where a route omits its APS, the result is only "Subjects met", never an eligibility claim.

These remain `requirements: null`:

- **UFH (4):** Education Commerce names Business management; Education Science names Computer science;
  extended LLB omits Mathematics-route APS; mainstream Crops omits the English level.
- **UJ (16):** Geography BEd's ambiguous alternative; three BEd routes needing named non-English language roles;
  four extended Humanities routes with bounded APS ranges; four extended engineering rows without an explicit
  science-column OR; four Physical Sciences rows whose Mathematics footnote differs from the table.
- **CPUT (2):** Banking mixes vocational/NSC terminology and omits its APS method; Senior/FET BEd requires
  named language roles and electives.
- **Other universities (13):** unresolved placement, prior-qualification, audition and language conditions or
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

On 25 October, further official pages brought support coverage to **91 contacts across all 26 universities**.
Coverage is still uneven by campus and service type. Each added contact cites its own page. General switchboards
and referral offices are labelled as such; unpublished hours were omitted. Fort Hare's current counselling email
differs from the downloaded research CSV: the official FYE page takes precedence. UNIVEN's exact counselling-unit
URL supplied in that research resolved the earlier unavailable links.

Official PDFs/pages add CPUT (10), DUT (11), Rhodes (10), UCT (7) and NWU first-year (3) calendar entries.
CPUT revision periods are not labelled tests, inferred recesses are omitted, and Rhodes's tentative shutdown
is excluded. Terms can include assessment periods; campus/cohort exceptions are preserved in notes.
Seventeen universities still have no calendar entries and 22 have no priced/free activities. These remain
research gaps, not verification failures. The downloaded `calendar.csv` is a discovery aid, not sufficient
evidence by itself: some entries infer dates not actually stated in their cited document.

## Verification decision, 25 October 2026

Rinsuna instructed: "for verification if it is from the official university thats good enough".
The 471 dated sources hosted by the universities now explicitly use `verification_basis: official_university`.
Acceptance is based on their recorded provenance, not a claim that every URL was fetched again on 25 October.
Source URLs, retrieval dates, existing human sign-offs and agent attribution are preserved. No new personal
verification dates were invented. Non-university publications retain their existing review requirements.
The schema rejects lookalike domains and missing retrieval dates. Contradictions and missing programme rules
remain separate from source authenticity, as does incomplete calendar/support/activity coverage.

## Source-review checklist

Run `python scripts/data_readiness.py --as-of 2026-10-25 --json` from `backend` for each source URL, retrieval date,
reviewer and verification date. Compare pack values with those pages or the identified PDF pages. Only record a
person's name/date for values that person actually checked. Resolve conflicts before enabling assessment.
Preserve the existing SMU and critical funding/crisis sign-offs.

The validator flags empty programme/source lists and requires accepted source evidence for releases.
Stale and future evidence dates are release errors. University confirmation and crisis visibility accept dated
official university evidence as well as human review. Funding sources retain the existing human-review gate.

## Validation of this change

- Pack validator: zero errors after the 25 October support/calendar imports; coverage warnings remain.
- Frontend: TypeScript and Expo lint passed; 35 Jest suites / 280 tests passed.
- Focused English-role and verification regression tests passed. The fresh complete backend suite is running
  against an isolated agent-owned PostgreSQL database; replace this line with its final result when complete.
- No production database was used. Work remains local to `rinsuna/data-completeness`, uncommitted and undeployed.
