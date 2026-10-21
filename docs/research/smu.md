# Sefako Makgatho Health Sciences University (SMU): research notes

Agent draft, read from SMU's own pages and documents on 9 Oct 2026. Nobody has checked these values yet. A person
compares each one with its source before it changes `backend/data/universities/smu.yaml` (the team approves fact
changes in a data pack first; CLAUDE.md, "Ask the team first"). Anything missing stays `null` and the app shows "Not
verified yet".

- **Source** gives a source id from the table below. `s-smu-med` is the id `smu.yaml` already uses.
- **Check** marks a value that is ambiguous in the document.
- Staff names and personal email addresses are left out on purpose: we keep office numbers and shared addresses. SMU's
  bank details are left out too; the app never handles payments.
- The school admission pages are undated. SMU's 2027 application page sends applicants to them.

## Sources

| Id | Document | Link |
|---|---|---|
| s-smu-apply-2027 | Online application: submission of 2027 applications | [page](https://www.smu.ac.za/students/apply/online-application/) |
| s-smu-med | Medicine undergraduate admission requirements (MBChB, MBChB ECP, B Rad, emergency medical care) | [page](https://www.smu.ac.za/schools/medicine/medicine-undergraduate-admission-requirements/) |
| s-smu-dent | Dentistry undergraduate admission requirements (BDS, B Dental Therapy, B Oral Hygiene) | [page](https://www.smu.ac.za/schools/oral-health-sciences/oral-health-sciences-undergraduate-admission-requirements/) |
| s-smu-pharm | Pharmacy undergraduate admission requirements (B Pharm) | [page](https://www.smu.ac.za/schools/pharmacy/pharmacy-undergraduate-admission-requirements/) |
| s-smu-hcs | Health Care Sciences undergraduate admission requirements | [page](https://www.smu.ac.za/schools/health-care-sciences/health-care-sciences-undergraduate-admission-requirements/) |
| s-smu-sst | Science and Technology undergraduate admission requirements (BSc) | [page](https://www.smu.ac.za/schools/science-and-technology/science-and-technology-undergraduate-admission-requirements/) |
| s-smu-cal-2026 | 2026 General Calendar, approved 23 Jan 2026 (sessional dates pp5-16) | [PDF](https://www.smu.ac.za/download/221/applications/275117/general-calendar-2026_approved_23_jan) |
| s-smu-fees-2026 | Undergraduate student fees 2026 (3 pages) | [PDF](https://www.smu.ac.za/download/221/applications/275139/undergraduate-fees-2026.pdf) |
| s-smu-finance-2026 | 2026 Registration guidelines: finance (7 pages) | [PDF](https://www.smu.ac.za/download/162/new-category/274875/registration-guidelines-finance-perspectives-2026.pdf) |
| s-smu-prospectus-2027 | Prospectus 2026/2027 (86 pages; its text extracts partly garbled, so used only to cross-check) | [PDF](https://www.smu.ac.za/wp-content/uploads/2026/04/Prospectus-2027-for-web.pdf) |
| s-smu-health | Campus Health and Wellness | [page](https://www.smu.ac.za/students/student-affairs/campus-health-and-wellness/) |
| s-smu-counselling | Centre for Student Counselling and Development | [page](https://www.smu.ac.za/students/student-affairs/centre-for-student-counselling-and-development/) |
| s-smu-referral | Student Support Referral Unit | [page](https://www.smu.ac.za/students/campus-affairs/student-life-smu/student-support-referral-unit/) |
| s-smu-contacts | Student Affairs contact numbers | [page](https://www.smu.ac.za/students/student-affairs/student-affairs-contact-numbers/) |

## Applications (F6)

| Fact | Value | Source |
|---|---|---|
| Applications for 2027 open | 1 April 2026 | s-smu-apply-2027; s-smu-cal-2026 |
| Undergraduate closing date | Friday 31 July 2026 | s-smu-apply-2027 |
| Late applications | None: "it will not be possible to submit your application after the closing date" | s-smu-apply-2027 |
| **Programmes per application** | **Two**; the first one chosen counts as the first choice | s-smu-apply-2027 |
| Application fee | R300, not refundable; pay with your ID number as the reference (one fee also covers a postgraduate application) | s-smu-apply-2027 |
| Documents | Certified ID or passport (compulsory); certified Grade 11 end-of-year results if in Grade 12, or the NSC or IEB certificate; degree certificates and academic records if you studied at SMU or another university; marriage certificate if it applies; proof of payment | s-smu-apply-2027 |
| Missing documents | The application isn't processed, and isn't considered if documents are still missing after two months | s-smu-apply-2027 |
| Meeting the minimum | Doesn't guarantee admission: SMU receives more applications than it can take | s-smu-apply-2027 |
| Residence | Limited; first come, first served; admission doesn't guarantee a room | s-smu-apply-2027 |
| Enquiries | 012 521 4058, 5886, 4315, 4319, 4137, 4204 or 4979 | s-smu-apply-2027 |
| Grade 11 pre-selection | MBChB, BDS, B Dental Therapy, B Oral Hygiene and B Rad make provisional offers on final Grade 11 results; Grade 12 results decide | s-smu-med; s-smu-dent |
| 2028 entry dates | Not published | - |

Today (9 Oct 2026) a Grade 12 learner can no longer apply to SMU for 2027.

## Points (APS) rule (F2)

- NSC and IEB levels: 7 = 80-100%, 6 = 70-79%, 5 = 60-69%, 4 = 50-59%, 3 = 40-49%, 2 = 30-39%, 1 = 0-29%.
  (s-smu-med and s-smu-dent, Table 2; level 8 exists only for some A-level and HIGCSE results.)
- Medicine, Dentistry, Pharmacy and Health Care Sciences tables add seven subjects: English, Mathematics, Physical
  Sciences, Life Sciences, Life Orientation and two more. This matches `smu.yaml` today (`subjects_counted: 7`,
  `life_orientation: full`).
- **Pharmacy uses its own scale:** 90-100% = 8, 80-89% = 7, 70-79% = 6, 60-69% = 5, 50-59% = 4 (s-smu-pharm,
  Table 2).
- **BSc and emergency care tables leave Life Orientation out.** The BSc minimums add up to 25 without it (English 4 +
  Maths 5 + Life Sciences 4 + Physical Sciences 4 + two others at 4). The emergency care totals (15 to 19) also
  have no Life Orientation. Whether it counts there: **Check** with SMU.

## Programmes and minimums (F2)

Every SMU programme selects on merit for limited places. Years come from the 2026 fee schedule (s-smu-fees-2026,
years I to VI) unless shown.

| Programme | Years | Places | Subject minimums | APS | Selection notes | Source |
|---|---|---|---|---|---|---|
| MBChB | 6 | 250 | English 6, Maths 6, Physical Sciences 6, Life Sciences 6, Life Orientation 5, two others 5 and 4 | 38 | Grade 11 pre-selection (APS 38; the five named subjects must total 29). Final ranking on actual % in Maths, Physical Sciences, Life Sciences, Life Orientation and English | s-smu-med |
| MBChB Extended Curriculum (foundation year, then MBChB) | 1 + 6 | 50 | Physical Sciences 5, Life Sciences 5, Maths 5, English 5 (4 if the APS stays competitive), Life Orientation 4, two others 4 | 32 | Restricted eligibility (see below). Pass all six foundation modules with 50%+ to enter MBChB I; a failed module can't be repeated | s-smu-med |
| Bachelor of Diagnostic Radiography (B Rad) | 4 | 40 | English 4, Maths 4, Physical Sciences 4, Life Sciences 4, Life Orientation 3, two others 3 | 25 | Grade 11 pre-selection; a combined 19 in the four subjects and Life Orientation must be kept | s-smu-med |
| Higher Certificate in Emergency Medical Care | 1 | - | NSC with higher certificate endorsement: English 3; Maths 3 or Maths Lit 4; Life Sciences or Physical Sciences 3; two others 3 | 15 (16 with Maths Lit) | Medical and physical fitness evaluations (prospectus p15) | s-smu-med |
| Diploma in Emergency Medical Care | 2 (prospectus p14) | - | NSC with diploma endorsement: English 3 (first language) or 4 (second language); Maths 3 (Maths Lit not accepted); Life Sciences 3; Physical Sciences 3; two others 3 | 18 or 19 | Medical and physical fitness evaluations | s-smu-med |
| Bachelor of Dental Surgery (BDS) | 5 | 42 | English 5, Maths 6, Physical Sciences 6, Life Sciences 6, Life Orientation 5, two others 5 and 4 | 37 | Grade 11 pre-selection (the four named subjects must total 23); ranked on actual % in the four, Life Orientation breaks ties | s-smu-dent |
| Bachelor of Dental Therapy | 3 | 25 | All 4: English, Maths, Physical Sciences, Life Sciences, Life Orientation, two others | 28 | Grade 11 pre-selection (four subjects total 16) | s-smu-dent |
| Bachelor of Oral Hygiene | 3 | 25 | English 4; Maths 4, or Maths Lit 7; Physical Sciences 4; Life Sciences 4; Life Orientation 4; two others 4 | 28 with Maths; 31 with Maths Lit | Grade 11 pre-selection (16; 19 with Maths Lit) | s-smu-dent |
| Bachelor of Pharmacy | 4 | - | Life Sciences 5, Maths 5, Physical Sciences 5, English 5, Life Orientation 4, two others 4 ("preferably Accounting and Economics") | 32 on Pharmacy's scale | Ranked by APS; register with the SA Pharmacy Council before 31 March of the first year | s-smu-pharm |
| BSc Dietetics | 4 | - | Maths 4, Physical Sciences 4, English 4, Life Sciences 4, Life Orientation 3, two others 3 | 25 | Selection committee | s-smu-hcs |
| Bachelor of Nursing and Midwifery | 4 | - | Life Sciences 4, Maths 4, Physical Sciences 4, English 4, two others 3, Life Orientation 3 | 25, or a combined 16 in the first four subjects | NSC with bachelor's endorsement; register with the SA Nursing Council within 30 days | s-smu-hcs |
| Bachelor of Occupational Therapy | 4 | - | Life Sciences 4, Maths 4, Physical Sciences 4, English 4, Life Orientation 3, two others 3 | 25 | Selection committee | s-smu-hcs |
| BSc Physiotherapy | 4 | - | All seven subjects at 4 | 28 | Preference to applicants who chose it first | s-smu-hcs |
| Bachelor of Speech-Language Pathology | 4 | - | Maths 4, English 4, Life Sciences 4, any language at home or first additional level 4, Life Orientation 3, two others 3 | 25 | Selection committee | s-smu-hcs |
| Bachelor of Audiology | 4 | - | as Speech-Language Pathology | 25 | Selection committee | s-smu-hcs |
| BSc: Life Sciences, Mathematical Sciences, Physical Sciences, or Occupational and Environmental Health Sciences | 3 | - | English 4, Maths 5, Life Sciences 4, Physical Sciences 4, two others 4; plus 5 in the stream's subject (Life Sciences, Maths, Physical Sciences, Life Sciences) | 25 | NSC with bachelor's endorsement | s-smu-sst |
| BSc Extended Curriculum: Life, Mathematical or Physical Sciences | 4 | - | English 4, Maths 4, Life Sciences 4, Physical Sciences 4, two others 4 | 24 | NSC with bachelor's endorsement | s-smu-sst |

Not on the admissions pages but in the 2026 fee schedule: BSc Environmental Management and Toxicology, BSc
Biotechnology, and the Bachelor of Nursing Science (BNSA, being phased out).

**Places in detail.** MBChB, 250 (s-smu-med, Table 3):
- 145 for NSC holders entering for the first time
- 5 firm offers to the top applicants with last year's Grade 12 results
- 5 for applicants from Lesotho and Swaziland
- 30 for SMU graduates
- 5 for graduates of other universities
- 5 for SANDF cadets
- 5 for SMU BSc I, BDS I or BSc ECP II students
- 50 from MBChB ECP II

BDS, 42 (s-smu-dent, Table 3):
- 30 for NSC holders entering for the first time
- 3 for applicants who matriculated up to two years earlier without university study
- 2 for top SMU BSc I, MBChB I or BSc ECP II students
- 1 for an applicant from the SADC
- 4 for SMU graduates
- 2 for graduates of other universities

B Rad, Dental Therapy and Oral Hygiene each reserve two places (5%) for transfers and graduates.

**Routes in** (bridges for the data pack):
- **SMU first year into MBChB I** (already in `smu.yaml`): the top five students who completed BSc I, BDS I or BSc
  ECP II, with at least three distinctions and an average of 75% or more. Considered, not guaranteed.
- **SMU first year into BDS I** (new): the top two students who completed BSc I, MBChB I or BSc ECP II, on the same
  conditions. Considered, not guaranteed. (s-smu-dent 1.1.3)
- **MBChB ECP into MBChB I** (already in `smu.yaml`): by rule, on passing all six foundation modules.

**Eligibility and demographics.** We never ask learners about these. Data packs carry them only as notes, and the
learner decides.
- **MBChB ECP:** in SMU's words, it is "only available to Indigenous South African (Black) students from quintiles 1
  and 2 schools only who have not previously been engaged in tertiary education and have not been able to get
  admission into the six year SMU medicine degree program" (s-smu-med). The current note in `smu.yaml` mentions
  quintile and prior study but not population group.
- **Other medicine and dentistry selection:** SMU applies demographic quotas based on census figures, the ECP
  excepted (s-smu-med; s-smu-dent Table 4).

## Calendar (F3)

From s-smu-cal-2026. The calendar says recess dates for clinical students follow each school's timetable where they
differ. SMU's 2027 calendar is not published; the 2026 calendar says SMU resumes on 5 Jan 2027.

| Event | 2026 |
|---|---|
| University resumes; returning students register | 5 Jan |
| Lectures start for returning students | 6 Jan |
| Last day of registration, returning students | 16 Jan |
| Lectures start for BSc II and III, and BSc ECP II to IV | 20 Jan |
| First-year registration | 21-30 Jan |
| First-year orientation | 27-30 Jan |
| Academic year starts for first-years | 2 Feb |
| Late registration and course changes close | 13 Feb |
| Autumn recess | 30 Mar - 2 Apr |
| Applications for 2027 open | 1 Apr |
| Open Day | 7 May |
| Last day to cancel courses or interrupt studies | 15 May |
| Revision week | 25-29 May |
| Mid-year exams | 1-19 Jun |
| Mid-year supplementary exams | about 29 Jun - 7 Jul (read from the layout). **Check** |
| Winter recess | 8-17 Jul |
| Mid-year results; end of semester 1 | 17 Jul |
| Semester 2 starts | 20 Jul |
| Revision week | 5-9 Oct |
| End-of-year exams | 12 Oct - about 6 Nov (end date read from the layout). **Check** |
| Supplementary and deferred exams | 16-24 Nov |
| Year-end results | 8 Dec |
| End of semester 2 and all academic activities | 15 Dec |
| University recess | 23 Dec - 4 Jan 2027 |

During the hackathon (from 23 Oct 2026), SMU students are in end-of-year exams.

Also in the 2026 calendar (read on 10 Oct 2026 for the pack): semester 1 runs 5 Jan to 17 Jul and semester 2 runs
20 Jul to 15 Dec; late registration and course changes close on 13 Feb; courses can be cancelled, and studies
interrupted, until 15 May; graduation ceremonies on 13-15 May and 18 Sep.

## Campus (F1)

One campus: Molotlegi Street, Ga-Rankuwa, Pretoria. Registrar: registrar@smu.ac.za, +27 (0)12 521 4979/4203.
(s-smu-cal-2026 p5)

## Support (F5)

Crisis numbers must be checked by a person before release (CLAUDE.md).

| Need | Contact | Hours | Source |
|---|---|---|---|
| Campus Health and Wellness Centre (free: minor ailments, first aid, Hepatitis B vaccination, HIV counselling, testing and management, peer health education) | 012 521 5735 (Student Affairs also lists 4713) | Mon-Fri 08:00-16:00 | s-smu-health; s-smu-contacts |
| After hours, weekends and emergencies | Campus control for ambulance services, or 079 417 9546 / 6278 | after hours | s-smu-health |
| Centre for Student Counselling and Development (guidance and counselling on relationships, careers, stress, anger and grief; help for first-years settling in) | 012 521 3786; administrator 012 521 4225 | Mon-Fri 08:00-12:00, 13:00-16:00 | s-smu-counselling |
| Student Support Referral Unit (basic life coaching; referrals to the social worker, counselling, the clinical psychologist, the Centre for University Teaching and Learning, Campus Health and Financial Aid; free for registered students) | 012 521 3805; Clinpath Building, room 3L003 | | s-smu-referral |
| Advocacy and Diversity | 012 521 5834 | | s-smu-contacts |
| Student Residences | 012 521 3742 | | s-smu-contacts |
| Student Life and Governance | 012 521 5836 | | s-smu-contacts |
| Sport and Recreation | 012 521 3858 / 4185 | | s-smu-contacts |

Not found: a 24-hour counselling or crisis line, food support, chaplaincy, a careers office (the counselling centre
offers career counselling).

## Fees and funding (F4, F6)

| Fact | Value | Source |
|---|---|---|
| Registration fee | R4 500 for first-years. Students with confirmation letters from NSFAS, public-sector sponsors or listed verified sponsors are ordinarily not expected to pay it; students still waiting for a bursary outcome pay in full | s-smu-fees-2026 p3; s-smu-finance-2026 p2 |
| Early payment | 3% off tuition if the account is settled by 31 May | s-smu-fees-2026 p3 |
| 2026 increases | 7% on tuition, 8% on university-owned accommodation; off-campus residence charged at what the provider charges; transport charged to students in university-owned or leased residences | s-smu-finance-2026 p4 |
| Residence 2026 | Single room R31 476; double room R23 607; Nurses Home R31 871; Residence 1C R57 535; Residence 2B R54 795; Fountain View: Drie Lillies R53 400, Madeira R59 940, Arebeng R59 700; residence admin fee R3 425 | s-smu-fees-2026 p3 |
| Funding | The Financial Aid Office handles NSFAS applications and links to Fundi loans | SMU scholarship and financial aid page |

**First-year totals for 2026** (tuition plus an admin fee of R2 057 and an SRC levy of R1 046; s-smu-fees-2026). In
a data pack these become integer cents.

| Programme, year I | Total |
|---|---|
| MBChB | R90 138 |
| MBChB ECP | R89 179 |
| B Rad (Diagnostic) | R88 079 |
| BSc Physiotherapy | R104 580 |
| BSc Dietetics | R101 005 |
| B Occupational Therapy | R98 860 |
| B Nursing and Midwifery | R140 068 |
| B Speech-Language Pathology | R71 847 |
| B Audiology | R71 847 |
| B Pharm | R115 280 |
| BDS | R90 185 |
| B Dental Therapy | R82 819 |
| B Oral Hygiene | R114 216 |
| BSc Mathematical Sciences, Life Sciences, Environmental Management, Biotechnology | R88 625 each |
| BSc Physical Sciences | R88 147 |
| BSc Occupational and Environmental Health | R89 103 |
| BSc ECP: Mathematical or Physical Sciences | R80 491 each |
| BSc ECP: Life Sciences | R72 927 |

The schedule also lists every later year and the international levies.

## Notes for the data pack

Changes to `smu.yaml` the research supports. Each needs the team's OK:

1. `max_choices: 2` (s-smu-apply-2027).
2. `bsc_y1` requirements: APS 25; English 4, Mathematics 5, Life Sciences 4, Physical Sciences 4, two more at 4
   (s-smu-sst), once the Life Orientation question is settled.
3. `mbchb`: `places: 250`.
4. The MBChB ECP eligibility note: add SMU's population-group restriction in SMU's own words.
5. Add the other programmes above, with places where SMU gives them.
6. Add the route from SMU first year into BDS I (considered; 2 places).
7. Add source ids as above, alongside `s-smu-med`.

Schema needs: Pharmacy's own scale, and BSc and emergency care without Life Orientation (decision 6). Oral Hygiene's
Maths or Maths Lit route with its own APS (decision 1). Every SMU programme stays `selective: true`.

## Gaps and inconsistencies

- SMU's 2027 calendar: not published.
- Life Orientation in the BSc and emergency care APS: unclear.
- Places for Pharmacy, Health Care Sciences, emergency care and BSc: not published on the pages.
- Mid-year supplementary exams and the end of year-end exams: dates read from the calendar layout.
- The general calendar puts the 2027 undergraduate closing date in the 30-31 July rows; the application page says
  Friday 31 July.
- Not found: a 24-hour support line, food support, chaplaincy, a careers office.
- Programmes in the fee schedule but not on the admissions pages: BSc Environmental Management and Toxicology, BSc
  Biotechnology, Nursing Science (phasing out).
