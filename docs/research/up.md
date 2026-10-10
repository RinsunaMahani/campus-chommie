# University of Pretoria (UP): research notes

Agent draft, read from UP's own documents on 9 Oct 2026. Nobody has checked these values yet. A person compares each
one with its source before it goes into `backend/data/universities/up.yaml` with `release: true` (CLAUDE.md, "Facts:
never invent them"). Anything missing stays `null` and the app shows "Not verified yet".

- **Source** gives a source id from the table below and a page. Use the same ids in `up.yaml`.
- **Check** marks a value seen only in a search engine's summary of a UP web page. UP's web pages refuse automated
  reading, so open the page in a browser before using it.
- Staff names and personal email addresses are left out on purpose: we keep office numbers and shared addresses.

## Sources

| Id | Document | Published | Link |
|---|---|---|---|
| s-up-req-2027 | 2027 Application requirements for undergraduate programmes (4 pages) | Department of Enrolment and Student Administration, Dec 2025 | [PDF](https://drupalwebprod-files.up.ac.za/Public/2026-03/UP_DESA_Application%20requirements%20tables_2027_web.pdf?VersionId=vw30gCBk2BMAXzOhFSBflmkFOHOMFOoa) |
| s-up-mbchb-2027 | Selection criteria of MBChB students, 2026 for 2027 (6 pages) | Faculty of Health Sciences, 13 Apr 2026 | [PDF](https://drupalwebprod-files.up.ac.za/Public/2026-04/2026%20for%202027%20Selection%20of%20MBChB%20students_13April%202026%20%282%29.pdf?VersionId=Zhz6Br5WLsS8ahAYQXZ3RDGUkfIq_RNy) |
| s-up-cal-2026 | Academic calendar 2026, main dates (amended, S0002/25) | UP | [PDF](https://linus.up.ac.za/calendars/2026_MAINDATES.pdf) |
| s-up-cal-2027 | Academic calendar 2027, main dates (S0002/26) | UP | [PDF](https://linus.up.ac.za/calendars/2027_MAINDATES.pdf) |
| s-up-infoguide-2026 | InfoGuide 2026 (52 pages) | UP, Dec 2025 | [PDF](https://drupalwebprod-files.up.ac.za/Public/2025-12/UP_InfoGuide%202026_V5-c.pdf) |

## Applications (F6)

| Fact | Value | Source |
|---|---|---|
| Closing date for 2027 entry | 30 June 2026, all faculties except Veterinary Science | s-up-req-2027 p1-3 |
| Veterinary Science closing date | 31 May 2026 | s-up-req-2027 p3 |
| MBChB application window | 1 April to 30 June 2026; no late applications | s-up-mbchb-2027 p1 |
| MBChB and choices | Applicants who put MBChB as first or second choice are considered | s-up-mbchb-2027 p5 |
| Health Sciences and choices | "In certain programmes only first-choice applicants will be considered"; programmes that take second choices say so | s-up-mbchb-2027 p2 |
| 2028 entry dates | Not published | - |
| Programmes per application (`max_choices`) | Not found | - |
| Application fee | R300 for 2027, waived if household income is R150 000 a year or less. **Check** | snippet of up.ac.za/online-application/application-fee |
| Documents | ID or passport, latest school results, academic records if you studied before, as PDFs. **Check** | snippet of up.ac.za/online-application |
| Accepting an offer | By 30 September. **Check** | snippet of up.ac.za/online-application/important-dates |

Today (9 Oct 2026) a Grade 12 learner can no longer apply to UP for 2027.

## Points (APS) rule (F2)

UP counts six 20-credit subjects on the NSC 1 to 7 scale, so the highest APS is 42. Life Orientation (10 credits) is
left out. Source: s-up-mbchb-2027 p1 (UP's general admissions page could not be read).

| Level | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|---|---|
| Marks | 80-100% | 70-79% | 60-69% | 50-59% | 40-49% | 30-39% | 0-29% |

For `up.yaml`: `subjects_counted: 6`, `life_orientation: exclude`, the standard scale. English means English Home
Language or English First Additional Language at the same level.

## Programmes and minimums (F2)

All from s-up-req-2027. "Selection" means UP marks it as a selection programme ("additional selection criteria
apply"). Levels are NSC levels unless a percentage is shown. 120 rows in all.

### Economic and Management Sciences (closes 30 June; p1)

| Programme | English | Mathematics | APS | Selection | Note |
|---|---|---|---|---|---|
| Bachelor of Administration in Public Administration and International Relations | 5 | 3, or Mathematical Literacy 4 | 28 | | either/or |
| BCom in Accounting Sciences | 5 | 6 | 34 | | |
| BCom, three-year programme | 5 | 4 | 30 | | |
| BCom, four-year programme | 4 | 3 | 26 | yes | |
| BCom specialising in Investment Management | 5 | 6 | 34 | | |
| BCom specialising in Econometrics | 5 | 6 | 32 | | |
| BCom specialising in Economics | 5 | 5 | 32 | | |
| BCom specialising in Financial Management Sciences | 5 | 5 | 32 | | |
| BCom specialising in Law | 5 | 5 | 32 | | |
| BCom specialising in Statistics and Data Science | 5 | 5 | 32 | | |
| BCom specialising in Agribusiness Management | 5 | 5 | 30 | | |
| BCom specialising in Information Systems | 5 | 5 | 30 | | also listed under EBIT (interfaculty) |
| BCom specialising in Business Management | 5 | 4 | 30 | | |
| BCom specialising in Supply Chain Management | 5 | 4 | 30 | | |
| BCom specialising in Marketing Management | 5 | 4 | 30 | | |
| BCom specialising in Human Resource Management | 5 | 4 | 30 | | |

### Education (closes 30 June; p1)

| Programme | English | APS | Selection | Note |
|---|---|---|---|---|
| BEd in Early Childhood Care and Education | 4 | 28 | | |
| BEd in Foundation Phase Teaching (Grade R to 3) | 4 | 28 | | |
| BEd in Intermediate Phase Teaching (Grades 4 to 6) | 4 | 28 | | |
| BEd in Senior Phase and FET Teaching (Grades 7 to 12) | 4 | 28 | yes | |
| Higher Certificate in Sports Sciences, one-year | 4 | 20 | yes | |
| Higher Certificate in Sports Sciences, two-year | 4 | 20 | yes | part-time online |

### Law (closes 30 June; p1)

| Programme | English | APS | Note |
|---|---|---|---|
| Bachelor of Laws (LLB) | 6 | 35 | BA Law: see Humanities. BCom Law: see EMS. |

### Engineering, Built Environment and IT (closes 30 June; p2)

| Programme | English | Mathematics | Physical Sciences | APS | Selection | Note |
|---|---|---|---|---|---|---|
| BEng in Chemical, Civil, Computer, Electrical, Electronic, Industrial, Mechanical, Metallurgical or Mining Engineering (9 programmes) | 5 | 6 | 6 | 35 | | |
| BEng, five-year programme (all disciplines; previously ENGAGE) | 65% | 65% | 65% | 33 | | percentages; first year offers foundation modules |
| BSc in Architecture | 5 | 4 | 4 | 30 | yes | |
| BSc in Construction Management | 5 | 5 | 4, or Accounting 4 | 30 | | either/or (footnote on this row) |
| BSc in Real Estate | 5 | 5 | 4, or Accounting 4 | 30 | | shares the row above; the footnote marks only Construction Management. **Check** |
| BSc in Quantity Surveying | 5 | 5 | 4, or Accounting 4 | 30 | | as above. **Check** |
| Bachelor of Town and Regional Planning | 5 | 4 | - | 30 | | |
| BSc in Computer Science | 5 | 6 | - | 30 | | |
| BSc in IT in Information and Knowledge Systems | 4 | 6 | - | 30 | | |
| Bachelor of IT in Information Systems | 5 | 5 | - | 30 | | |
| Bachelor of Information Science | 4 | - | - | 28 | | |
| Bachelor of Information Science specialising in Multimedia | 4 | 5 | - | 30 | | possible new name: Interactive Technology |
| Bachelor of Information Science specialising in Publishing | 5 | - | - | 28 | | |

### Health Sciences (closes 30 June; p2). All are selection programmes.

| Programme | English | Mathematics | Third subject | APS |
|---|---|---|---|---|
| Bachelor of Dental Surgery (BDS) | 5 | 6 | Physical Sciences 5 | 35 |
| Bachelor of Oral Hygiene | 4 | 4 | Physical Sciences 4 | 25 |
| Bachelor of Occupational Therapy | 4 | 4 | Physical Sciences 4 | 30 |
| Bachelor of Physiotherapy | 4 | 4 | Physical Sciences 4 | 30 |
| Bachelor of Radiography in Diagnostics | 4 | 4 | Physical Sciences 4 | 30 |
| Bachelor of Dietetics | 4 | 4 | Physical Sciences 4 | 28 |
| Bachelor of Nursing Science | 4 | 4 | Life Sciences 4 (not Physical Sciences) | 28 |
| Bachelor of Medicine and Surgery (MBChB) | 5 | 6 | Physical Sciences 5 | 35 |
| Bachelor of Sports Science | 4 | 4 | Physical Sciences or Life Sciences 4 (either/or) | 30 |
| Bachelor of Clinical Medical Practice (BCMP) | 4 | 4 | Physical Sciences 4 | 28 |

BSc Food Management is listed under Natural and Agricultural Sciences; BA Audiology and BA Speech-Language Pathology
under Humanities.

### Humanities (closes 30 June; p3)

| Programme | English | Mathematics | APS | Selection | Note |
|---|---|---|---|---|---|
| Bachelor of Arts | 5 | - | 30 | | |
| BA in Audiology | 5 | 4 | 32 | yes | |
| BA in Speech-Language Pathology | 5 | 4 | 32 | yes | |
| BA in Fine Arts, four-year | 5 | - | 30 | | |
| BA in Fine Arts, five-year | 4 | - | 26 | | |
| BA in Information Design | 5 | - | 30 | yes | |
| BA specialising in Languages | 5 | - | 30 | | |
| BA specialising in Law | 5 | - | 34 | | |
| BA specialising in Philosophy, Politics and Economics | 5 | 5 | 32 | | |
| BA specialising in Visual Studies | 5 | - | 30 | | |
| Bachelor of Drama, three-year | 5 | - | 30 | | |
| Bachelor of Drama, four-year | 4 | - | 26 | | |
| Bachelor of Political Science specialising in International Studies | 5 | - | 30 | | |
| Bachelor of Political Science specialising in Political Studies | 5 | - | 30 | | |
| Bachelor of Social Science in Heritage and Cultural Sciences (option: Heritage and Cultural Tourism) | 5 | - | 30 | | possible new name: BSocSci specialising in Heritage and Cultural Tourism |
| Bachelor of Social Science specialising in Industrial Sociology and Labour Studies | 5 | - | 30 | | |
| Bachelor of Social Work | 5 | - | 30 | | |
| Bachelor of Music, four-year | 5 | - | 30 | | Music 4 (50-59%), or Grade VII Practical and Grade V Theory (Unisa, Royal Schools or Trinity) or comparable; and a practical audition and theory test passed with 60% |
| Bachelor of Music, five-year | 4 | - | 26 | | Music 4 (50-59%), or Grade V Practical and Grade III Theory or comparable; and a practical audition and theory test passed with 50% |

### Theology and Religion (closes 30 June; p3)

| Programme | English | APS |
|---|---|---|
| Bachelor of Theology | 4 | 28 |
| Bachelor of Divinity | 4 | 28 |
| Diploma in Theology | 4 | 24 |

### Veterinary Science (closes 31 May; p3). Both are selection programmes.

| Programme | English | Mathematics | Third subject | APS |
|---|---|---|---|---|
| Bachelor of Veterinary Science (BVSc) | 5 | 5 | Physical Sciences 5 | 35 |
| Bachelor of Veterinary Nursing | 4 | 4 | Physical Sciences or Life Sciences 4 (either/or) | 28 |

### Natural and Agricultural Sciences (closes 30 June; p4)

| Programme | English | Mathematics | Physical Sciences | APS | Note |
|---|---|---|---|---|---|
| BSc in Biochemistry, Biotechnology, Ecology, Entomology, Genetics, Human Genetics, Human Physiology, Human Physiology Genetics and Psychology, Medical Sciences, Microbiology, Plant Science or Zoology (12 programmes) | 5 | 5 | 5 | 32 | |
| BSc four-year programme in Ecology or Human Physiology (2) | 58% | 58% | 58% | 30 | percentages; first year offers foundation modules |
| BSc in Agriculture in Agricultural Economics in Agribusiness Management, Agriculture in Animal Science, Agriculture in Applied Plant and Soil Sciences, Agriculture in Plant Pathology, Food Management (Culinary Science), Food Management (Nutritional Science) or Food Science (7) | 5 | 5 | 5 | 32 | |
| BSc four-year programme in Agriculture in Applied Plant and Soil Sciences or Agriculture in Plant Pathology (2) | 58% | 58% | 58% | 30 | percentages |
| BSc in Chemistry, Physics, Geography (option Geography and Environmental Science), Geoinformatics, Geology, Meteorology or Environmental and Engineering Geology (7) | 5 | 5 | 5 | 34 | |
| BSc four-year programme in Chemistry, Geoinformatics, Geology, Meteorology or Physics (5) | 58% | 58% | 58% | 32 | percentages |
| BSc in Actuarial and Financial Mathematics | 5 | 7 | - | 36 | |
| BSc in Mathematics, three-year | 5 | 6 | - | 34 | |
| BSc in Applied Mathematics | 5 | 6 | - | 34 | |
| BSc in Mathematical Statistics | 5 | 6 | - | 34 | |
| BSc in Mathematics, four-year | 58% | 65% | - | 32 | percentages; marked * but the footnote is missing from the PDF |
| Bachelor of Consumer Science specialising in Clothing Retail Management | 5 | 4 | - | 28 | |
| Bachelor of Consumer Science specialising in Food Management | - | - | - | - | values missing: the PDF ends after this row's name |

## MBChB selection (F2)

From s-up-mbchb-2027.

- **Merit Point Score (MPS):** Grade 11 English % + Mathematics % + Physical Sciences % + the next three best
  20-credit subjects, leaving out Life Orientation, Mathematical Literacy and Mathematics paper 3. Value-added
  attributes (job shadowing, leadership) don't count. (p1, p3)
- **Provisional offers** are confirmed if the final NSC MPS is no more than five points below the Grade 11 MPS and the
  minimums are still met. (p2, p5)
- **Places for 2027: 300** (p5).

| Category | Places | Who |
|---|---|---|
| 1 School leavers, open | 88 (NSC 66, IEB 16, Cambridge or IB 6) | all school-leaving applicants compete here first |
| 8 School leavers, designated groups | 100 | in UP's words, South Africans or permanent residents "of Black African or Coloured African descent" not successful in category 1 |
| 3 Previous university experience, open | 36 | all applicants with university experience compete here first |
| 9 Previous university experience, designated groups | 66 | as category 8, for applicants not successful in category 3 |
| 6 SANDF-sponsored | 10 | |

- **Previous university experience** (p4, p6): at least one year of degree study; every module passed at the first
  attempt; at least four modules with marks; a final NSC (or tertiary) result of at least 50% (HG) or level 4 in
  Mathematics and Physical Sciences. Scored by the University Module Achievement Score (UMAS, highest 80 plus bonus
  points for completed degrees). Three-year diplomas don't count.
- We never ask learners about population group. In a data pack this is only an eligibility note, and the learner
  decides.

## Calendar (F3)

Test weeks apply to the Hatfield and Groenkloof campuses.

| Event | 2026 (s-up-cal-2026) | 2027 (s-up-cal-2027) |
|---|---|---|
| Academic year starts | 5 Jan | 4 Jan |
| Welcome Day | 31 Jan | 30 Jan |
| First-year orientation (Hatfield and Groenkloof) | 2-6 Feb | 1-5 Feb |
| Semester 1 lectures | 9 Feb - 27 May | 8 Feb - 26 May |
| Last day of registration, semester 1 | 20 Feb | 19 Feb |
| Test week 1 | 14-20 Mar, 28 Mar, 11 Apr | 6 Mar, 13-20 Mar |
| Autumn recess | 29 Mar - 6 Apr | 21-29 Mar |
| Test week 2 | 2-9 May, 16 May | 17 Apr, 24 Apr, 3-8 May |
| Exams | 30 May - 18 Jun | 29 May - 17 Jun |
| Supplementary exams | 22-27 Jun | 21-26 Jun |
| July recess | 28 Jun - 19 Jul | 27 Jun - 18 Jul |
| Semester 2 lectures | 20 Jul - 6 Nov | 19 Jul - 4 Nov |
| Last day of registration, semester 2 | 31 Jul | 30 Jul |
| Test week 1 | 22-29 Aug, 5 Sep | 14 Aug, 21-28 Aug |
| UP Wellness Day (no lectures) | 16 Sep | 15 Sep |
| September recess | 17-27 Sep | 16-26 Sep |
| Test week 2 | 10-17 Oct, 24 Oct | 2 Oct, 9-16 Oct |
| Exams | 7-25 Nov | 6-24 Nov |
| Supplementary exams | 30 Nov - 5 Dec | 29 Nov - 4 Dec |
| End of the academic year | 5 Dec | 4 Dec |
| University closes | 23 Dec, 10:00 | 23 Dec, 10:00 |
| Next year starts | 4 Jan 2027 | 3 Jan 2028 |

Recesses (and December to January) are the windows for the vac-work nudge.

Deadlines in the same calendars (read on 10 Oct 2026 for the pack's calendar):

| Deadline | 2026 (s-up-cal-2026) | 2027 (s-up-cal-2027) |
|---|---|---|
| Dropping or swapping (2026), or changing or cancelling (2027), modules: after this, fees and GPA are affected | 9 Mar (semester 1); 17 Aug (semester 2) | 8 Mar; 16 Aug |
| Online registration opens for senior students | 5 Jan | 4 Jan |
| Graduation ceremonies | 4 - 29 May (autumn); 31 Aug - 4 Sep (spring) | 28 Apr - 28 May; 30 Aug - 3 Sep |
| Study period before exams | 28-29 May | 27-28 May; 18-20 Jun; 5 Nov; 25-28 Nov |

## Campuses (F1)

From s-up-infoguide-2026 p6.

| Campus | Houses |
|---|---|
| Hatfield | Economic and Management Sciences; Engineering, Built Environment and IT; Humanities; Law; Natural and Agricultural Sciences; Theology and Religion |
| Groenkloof | Education |
| Hillcrest | TuksSport and the High Performance Centre |
| Mamelodi | Post-school mathematics and science programmes; community engagement |
| Onderstepoort | Veterinary Science |
| Prinshof | Health Sciences |
| GIBS (Sandton, Johannesburg) | Gordon Institute of Business Science |

## Support (F5)

From s-up-infoguide-2026. Crisis numbers must be checked by a person before release (CLAUDE.md).

| Need | Contact | Hours | Page |
|---|---|---|---|
| UP crisis line (toll-free) | 0800 006 428 | 24 hours | p6, p24, p25 |
| UP Careline, with SADAG: telephonic counselling for registered students | 0800 747 747; SMS 31393 for a call-back | 24/7 | p24, p26 |
| Student Counselling Unit | +27 (0)12 420 2333; studentcounselling@up.ac.za | 07:30-16:00 | p26 |
| After hours (counselling page; also the 24-hour Operational Centre on p6) | +27 (0)12 420 2310 or 2760 | after hours | p6, p26 |
| Student Health Services | +27 (0)12 420 2500; info.shs@up.ac.za | | p24, p27 |
| Access, Disability and Inclusion Services (ADIS) | +27 (0)12 420 2064 | | p29 |
| Academic success coaches (+27 (0)12) | EBIT 420 6532; NAS 420 6740; EMS 420 6743; Humanities 420 6963; Education 420 5968; Health 356 3351; Law 420 6830; Theology 420 6707; Veterinary 420 4990 | | p24 |
| Career Services (advertises vacancies, graduate programmes, internships and vacation work on TuksCareers) | +27 (0)12 420 6438; careerservices@up.ac.za | | p38 |
| Centre for Sexualities, AIDS and Gender | +27 (0)12 420 4391 | | p24 |
| Student Service Centre | +27 (0)12 420 3111; ssc@up.ac.za | | p6 |
| Thuthuzela Care Centre (outside UP; after sexual assault) | +27 (0)12 354 1874 | | p24 |

Food support (SNAPP, the Health Sciences food parcel project, Phahama Feed-a-Student) appeared only in search
snippets. **Check.** Chaplaincy: not found.

## Fees and funding (F4, F6)

| Fact | Value | Source |
|---|---|---|
| Paying tuition (2026) | Half by 30 April; all by 31 July | s-up-infoguide-2026 p12 |
| Early payment | 2.5% discount if the account is paid in full by 30 April | p12 |
| Bursaries from sponsors | The sponsor's confirmation letter must state the amount and what it covers | p10 |
| UP funding database | Any UP student can register to be considered for bursaries and other funding; no guarantee of funding | p13 |
| NSFAS | Apply at nsfas.org.za; the allocation is a bursary; students already funded don't re-apply | p13 |
| Fundi (formerly Eduloan) | Study loans; +27 (0)12 362 8818 | p13 |
| Registration payment | R11 000 (2026). **Check** | snippet |
| Tuition per programme | Not readable (UP's fee pages refuse automated reading); estimates seen only in snippets | - |

**FLY@UP Assist First-Year Awards 2026** (p14-15). Paid automatically to first-time entering first-years (straight
from school or after a gap year); not to anyone who registered at a tertiary institution before. The average is not
rounded; re-marked results don't count.

| Award | Rule | Amount |
|---|---|---|
| A | Average of the six best subjects (NSC/IEB), leaving out Life Orientation and Practical Music grades 4 and 5: 80-89.99% | R18 000 |
| A | Same average, 90-100% | R45 000 |
| B (only with award A) | Mathematics (or Advanced, Further, Alpha, Additional Mathematics) 80-100% | R2 000 per subject |
| B (only with award A) | Physical Sciences (or Advanced, Further Physical Sciences) 80-100% | R2 000 per subject |

UP adds: "Mathematical Literacy, Technical Mathematics, Technical Sciences and equivalent subjects are not eligible for
this award." Other 2026 awards (Table 3, p15):
- **JuniorTukkie Grade 11 Award:** R16 000, for "the 40 learners with the best Grade 12 results".
- **Grade 12 Dux Scholar Award:** R11 000, at schools UP identifies.
- **Vice-Chancellor's Distinguished Merit Award:** covers three years' tuition.
- **Vice-Chancellor's Previously Disadvantaged Group Award:** R15 700. UP's eligibility wording is "Top prospective
  African and Coloured students with the highest average percentage will be considered". We never ask about this.
The 2027 amounts are not published.

## Notes for the data pack

- **Fits today's schema:** about 100 of the 120 rows (the APS rule, English, Mathematics, Physical or Life Sciences
  as fixed subjects).
- **Waits for the schema** (requirements `null` with a comment until it changes):
  - **Either/or subjects (6):** BAdmin; Construction Management, Real Estate and Quantity Surveying; Sports Science;
    Veterinary Nursing.
  - **Percentage minimums (11):** the five-year BEng and the four-year BSc rows, including four-year Mathematics.
  - **Music audition (2).**
  - **Unreadable (1):** Food Management under Consumer Science.
- **`selective: true`** for every selection programme. The others land on "Meets the minimum" with "no guarantee".
- **Bridge into MBChB:** "previous university experience" is a `considered` bridge from the closest BSc programmes,
  with 36 places open to all. The 66 designated-group places go in the eligibility note.
- **Extended programmes are not bridges.** The five-year BEng, four-year BSc, BCom, Drama and five-year Fine Arts and
  Music are separate programmes. No published route between the extended and mainstream versions was found.
- **`max_choices`:** stays `null`.
- **Fields:** the tags decide the cross-university safe choice (decision 3 in [OPEN_QUESTIONS](../OPEN_QUESTIONS.md)).

## Gaps and inconsistencies

- Consumer Science, Food Management: values missing (s-up-req-2027 p4 ends mid-table).
- Four-year BSc Mathematics is marked * but the footnote isn't in the PDF.
- Construction Management footnote: Accounting instead of Physical Sciences may apply to Real Estate and Quantity
  Surveying too.
- MBChB programme code: 10130003 on s-up-mbchb-2027 p1, 10130004 on p5.
- Semester 2 end date: the InfoGuide says Q4 ends 5 Nov 2026; the amended calendar says lectures end 6 Nov (use the
  calendar).
- Not found or not readable: 2028 dates, programmes per application, tuition per programme, 2027 FLY@UP amounts,
  chaplaincy. Snippet-only (**Check**): application fee and waiver, documents, offer acceptance date, registration
  payment, food support.
