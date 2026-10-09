# Tshwane University of Technology (TUT): research notes

Agent draft, read from TUT's own documents on 9 Oct 2026. Nobody has checked these values yet. A person compares each
one with its source before it goes into `backend/data/universities/tut.yaml` with `release: true` (CLAUDE.md, "Facts:
never invent them"). Anything missing stays `null` and the app shows "Not verified yet".

- **Source** gives a source id from the table below and a page. Use the same ids in `tut.yaml`.
- **Check** marks a value that is ambiguous in the document or that two TUT documents give differently.
- Staff names and personal email addresses are left out on purpose: we keep office numbers and shared addresses. TUT's
  bank account numbers are left out too; the app never handles payments.
- TUT prints "All information in this publication is subject to change without further notice" on both 2027 guides.

## Sources

| Id | Document | Published | Link |
|---|---|---|---|
| s-tut-courses-2027 | 2027 First Year Course Information (20 pages; one table row per programme) | TUT | [PDF](https://www.tut.ac.za/media/tshwane-interim/site-content/documents/First-Year-Course_Information.pdf) |
| s-tut-guide-2027 | 2027 General Information for First Year Enrolment (108 pages) | TUT, printed Jan 2026 | [PDF](https://www.tut.ac.za/media/tshwane-interim/site-content/documents/General-Information-First-Year-Enrolment.pdf) |
| s-tut-cal-2026 | 2026 Academic Core Calendar | approved by Senate 9 Jun and 8 Sep 2025; updated 23 Oct 2025 | [PDF](https://www.tut.ac.za/media/tshwane-interim/site-content/documents/2026-AcademicCore-Calendar.pdf) |
| s-tut-cal-2027 | 2027 Academic Core Calendar | updated 15 Apr 2026 | [PDF](https://www.tut.ac.za/media/tshwane-interim/site-content/documents/2027-Academic-Core-Calendar.pdf) |
| s-tut-rules-2026 | 2026 Prospectus, Part 1: Students' Rules and Regulations | TUT; valid for 2026 | [PDF](https://www.tut.ac.za/media/tshwane-interim/site-content/images/prospectus/Part1_Students_Rules_and_Regulations.pdf) |
| s-tut-fees-2026 | 2026 Prospectus, Part 9: Student Fees | TUT; valid for 2026 | [PDF](https://www.tut.ac.za/media/tshwane-interim/site-content/images/prospectus/PART_9_-Student_Fees.pdf) |

## Applications (F6)

| Fact | Value | Source |
|---|---|---|
| How to apply | Online at www.tut.ac.za, with an email address of your own | s-tut-guide-2027 p7 |
| Applications for 2027 entry open | 1 April 2026 | s-tut-guide-2027 p7; s-tut-cal-2026 |
| Closing dates for 2027 entry | Set per programme: 15 June, 31 July or 30 September 2026. 31 July is also the date for all international applicants. A programme can close earlier once it is full | s-tut-guide-2027 p7; s-tut-cal-2026 |
| **Late applications for 2027 entry** | **14-22 January 2027**, online only (no walk-ins), for programmes that still have space | s-tut-cal-2027 |
| July 2027 intake | Selected programmes; applications close 15 May 2027 | s-tut-cal-2027 |
| Applications for 2028 entry | Open 1 April 2027; close 15 June 2027 (some programmes), 31 July 2027 (other programmes and all international applicants; date read from the calendar layout, **Check**) or 30 September 2027 (January 2028 intake, everything else) | s-tut-cal-2027 |
| Application fee | R240 for 2027; first-time applicants pay it once; not refundable; no cash on any campus | s-tut-guide-2027 p7 |
| Documents | Proof of payment of the fee; certified copy of ID; certified copy of the NSC, or final Grade 11 results if in Grade 12 | s-tut-guide-2027 p7 |
| Grade 11 results | You can apply on Grade 11 or mid-year Grade 12 results and get provisional admission | s-tut-guide-2027 p5 |
| Checking your status | www.tut.ac.za > Study@TUT > Check Your Status, with your ID number | s-tut-guide-2027 p7 |
| Programmes per application | Not stated | - |
| How places are filled | Complete applications are ranked; the top-ranked are selected up to the enrolment plan; first-time entering students get preference; a waiting list fills places of those who don't register. In the eight health sciences bachelor's degrees, at most 5% of places go to applicants who studied at a university before | s-tut-guide-2027, programme pages |

Today (9 Oct 2026) TUT's general closing date has passed, but the January 2027 late window is still ahead.

## Points (APS) rule (F2)

- Life Orientation is not counted, and a subject at level 1 adds nothing. (s-tut-rules-2026 rule 1.2.4;
  s-tut-guide-2027 p5)
- NSC levels: 7 = 80-100%, 6 = 70-79%, 5 = 60-69%, 4 = 50-59%, 3 = 40-49%, 2 = 30-39%, 1 = 0-29%.
  (s-tut-rules-2026 rule 1.2.5)
- TUT needs an NSC with at least six subjects, including English (home or first additional language, at least 3)
  and Mathematics, Technical Mathematics or Mathematical Literacy as the programme requires. Bachelor's degrees need
  four subjects at level 4; diplomas, four at level 3. (s-tut-guide-2027 p5)
- **Not stated: how many subjects count.** A learner with seven subjects besides Life Orientation may score
  differently depending on the answer.
- Mathematics or Mathematical Literacy: Mathematics is compulsory for Science, Engineering and the Built Environment,
  and ICT; Arts accepts Mathematical Literacy; Management Sciences, Economics and Finance, and Humanities take either.
  (s-tut-guide-2027 p8)

## Programmes and minimums (F2)

From s-tut-courses-2027 (pages 5-19), with campuses and extra selection steps from the programme pages in
s-tut-guide-2027. Closing dates are for 2027 entry (2026). 125 rows.

Short forms: **Maths** Mathematics, **Tech Maths** Technical Mathematics, **Maths Lit** Mathematical Literacy, **Phys
Sci** Physical Sciences, **Tech Sci** Technical Sciences. "Maths or Tech Maths 5, or Maths Lit 7" means Maths or Tech
Maths at level 5, or Maths Lit at level 7. Where two APS values appear, the second applies with Maths Lit. "Extra
selection" lists steps beyond ranking by APS.

### Arts and Design (Arts campus; closes 31 July)

| Programme | Years | Subjects | APS | Extra selection |
|---|---|---|---|---|
| Diploma in Commercial Photography | 3 | English 3 | 22 | portfolio, questionnaire |
| Diploma in Fashion Design and Technology | 3 | English 3 | 20 | practical selection project and interview (APS 20+) |
| Diploma in Fine and Applied Arts | 3 | English 3 | 20 | portfolio, questionnaire |
| Diploma in Integrated Communication Design | 3 | English 4 | 24 | departmental assessment |
| Diploma in Interior Design | 3 | English 4 | 22 | departmental assessment; recommended: Civil Technology, Design Studies, Engineering Graphics and Design, Visual Arts |
| Diploma in Jewellery Design and Manufacture | 3 | English 3 | 20 | portfolio, practical selection, interview |
| Diploma in Motion Picture Production | 3 | English 4 | 22 | artistic submission (40%), interview (20%), APS (40%) |
| Diploma in Performing Arts: Dance | 3 | English 4 | 20 | audition or interview per stream (guide p26) |
| Diploma in Performing Arts: Jazz Music | 3 | English 4 | 20 | as above |
| Diploma in Performing Arts: Opera | 3 | English 4 | 20 | as above |
| Diploma in Performing Arts: Technical Theatre and Design | 3 | English 4 | 20 | as above |
| Diploma in Performing Arts: Theatre Arts and Performance | 3 | English 4 | 20 | as above |
| Higher Certificate in Music | 1 | English 3 | 18 | audition and interview |

### Economics and Finance (main campus Ga-Rankuwa)

| Programme | Campus | Years | Closes | Subjects | APS |
|---|---|---|---|---|---|
| Diploma in Accounting | Ga-Rankuwa, Mbombela, Polokwane | 3 | 30 Sep | English 4; Accounting 3, or Maths or Tech Maths 3, or Maths Lit 5 | 22; 24 |
| Diploma in Economics | Ga-Rankuwa | 3 | 31 Jul | English 4; Maths or Tech Maths 3, or Maths Lit 6 | 22; 24 |
| Diploma in Financial Management | Ga-Rankuwa, Mbombela, Polokwane | 3 | 30 Sep | as Accounting | 22; 24 |
| Diploma in Financial Planning | Ga-Rankuwa | 3 | 30 Sep | as Accounting | 22; 24 |
| Diploma in Internal Auditing | Ga-Rankuwa, Mbombela, Polokwane | 3 | 30 Sep | as Accounting | 22; 24 |
| Diploma in Public Finance | Ga-Rankuwa, Mbombela, Polokwane | 3 | 30 Sep | English 4; Accounting 4, or Maths or Tech Maths 3, or Maths Lit 5 | 22 with Maths; 23 with Accounting; 24 with Maths Lit |
| Higher Certificate in Accounting | Ga-Rankuwa | 1 | 30 Sep | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 22; 23 |

For Accounting, Financial Management, Financial Planning and Internal Auditing, the first APS also applies with
Accounting. None of these programmes adds a test.

### Engineering and the Built Environment (Pretoria campus)

| Programme | Campus | Years | Closes | Subjects | APS | Extra selection |
|---|---|---|---|---|---|---|
| Bachelor of Architecture | Pretoria | 4 | 31 Jul | English 4; Maths or Tech Maths 4, or Maths Lit 5 | 25 | departmental assessment |
| Bachelor of Architecture (extended curriculum) | Pretoria | 5 | 31 Jul | as above | 25 | |
| Bachelor of Geomatics | Pretoria | 3 | 31 Jul in the course list, 30 Sep on the programme page. **Check** | English 4; Maths or Tech Maths 5; Phys Sci or Tech Sci 4 | 25 | |
| BEngTech in Chemical Engineering | Pretoria | 3 | 30 Sep | English 4; Maths or Tech Maths 5; Phys Sci or Tech Sci 5 | 28 | |
| BEngTech in Civil Engineering | Pretoria | 3 | 30 Sep | as above | 30 | |
| BEngTech in Electrical Engineering | Pretoria, eMalahleni | 3 | 30 Sep | as above, plus any three more subjects at 4 | 30 | |
| BEngTech in Industrial Engineering | Pretoria | 3 | 30 Sep | English 4; Maths or Tech Maths 5; Phys Sci or Tech Sci 5 | 28 | |
| BEngTech in Materials Engineering in Polymer Technology | Pretoria | 3 | 30 Sep | as above | 28 | |
| BEngTech in Mechanical Engineering | Pretoria | 3 | 30 Sep | as above | 28 | |
| BEngTech in Mechatronic Engineering | Pretoria | 3 | 30 Sep | as above | 28 | |
| BEngTech in Metallurgical Engineering | Pretoria | 3 | 30 Sep | as above | 28 | |
| Diploma in Building Science | Pretoria | 3 | 30 Sep | English 4; Maths or Tech Maths 3; Phys Sci or Tech Sci 3 | 26 | |
| Diploma in Civil Engineering | Pretoria | 3 | 30 Sep | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4 | 26 | |
| Diploma in Electrical Engineering | Pretoria, eMalahleni | 3 | 30 Sep | as Civil Engineering | 26 | |
| Diploma in Geomatics | Pretoria | 3 | 30 Sep | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 3 | 23 | |
| Diploma in Industrial Design | Pretoria | 3 | 31 Jul | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 21 | portfolio |
| Higher Certificate in Construction Engineering: Material Test | Pretoria | 1 | 30 Sep | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 3 | 20 | |
| Higher Certificate in Construction Engineering: Water and Waste | Pretoria | 1 | 30 Sep | as above | 20 | |
| Higher Certificate in Electrical Engineering | Pretoria, eMalahleni | 1 | 30 Sep | as above | 20 | |
| Higher Certificate in Industrial Engineering | Pretoria | 1 | 30 Sep | as above | 20 | |
| Higher Certificate in Mechanical Engineering | Pretoria | 1 | 30 Sep | as above | 20 | |

### Humanities (Soshanguve North and South)

| Programme | Campus | Years | Closes | Subjects | APS | Extra selection |
|---|---|---|---|---|---|---|
| BEd in Foundation Phase Teaching | Soshanguve North | 4 | 31 Jul | a home language offered in the programme 5; first additional language 4; Maths 4, or Maths Lit 5 | 25 | |
| BEd in Intermediate Phase Teaching | Soshanguve North | 4 | 31 Jul | English 4; another home language offered in the programme 4; Maths 4, or Maths Lit 5; Life Sciences and Physical Sciences, or History and Geography, at 4 | 25 | |
| BEd in Senior Phase and FET Teaching: Agriculture | Soshanguve North | 4 | 31 Jul | English 4; Maths, Tech Maths or Maths Lit 4; Agricultural Sciences or Life Sciences 4; Agricultural Technology, Phys Sci or Tech Sci 4 | 24 | |
| BEd SP and FET: Consumer Sciences | Soshanguve North | 4 | 31 Jul | English 4; Maths, Tech Maths or Maths Lit 4; Consumer Studies, Hospitality Studies or Tourism 4 | 24 | |
| BEd SP and FET: Economic and Management Sciences | Soshanguve North | 4 | 31 Jul | English 4; Maths, Tech Maths or Maths Lit 4; Accounting, Business Studies or Economics 4 | 24 | |
| BEd SP and FET: Information Technology | Soshanguve North | 4 | 31 Jul | English 4; "Mathematics or Technical Mathematics or Information Technology" 4 (as printed). **Check** | 24 | |
| BEd SP and FET: Mathematics | Soshanguve North | 4 | 31 Jul | English 4; Maths and Life Sciences, or Maths and Physical Sciences, at 4 | 24 | |
| BEd SP and FET: Physical Education | Soshanguve North | 4 | 31 Jul | English 4; Maths, Tech Maths or Maths Lit 4; Life Sciences 4 | 24 | |
| BEd SP and FET: Sciences | Soshanguve North | 4 | 31 Jul | English 4; Maths 4; Life Sciences or Physical Sciences 4 | 24 | |
| BEd SP and FET: Technology | Soshanguve North | 4 | 31 Jul | English 4; Maths or Tech Maths and/or Civil, Electrical or Mechanical Technology and/or Engineering Graphics and Design and/or Phys Sci or Tech Sci, at 4 (as printed). **Check** | 24 | |
| Diploma in Adult and Community Education and Training: Civil Technology | Soshanguve North | 3 | 31 Jul | English 4; Engineering Graphics and Design, Maths or Tech Maths 3; Civil Technology, Phys Sci or Tech Sci 3; an additional language 3 | 22 | |
| Diploma in ACET: Consumer Sciences | Soshanguve North | 3 | 31 Jul | English 4; Maths or Tech Maths 3, or Maths Lit 4; an additional language 3 | 22 | |
| Diploma in ACET: Electrical and Mechanical | Soshanguve North | 3 | 31 Jul | English 4; Maths or Tech Maths 3; Phys Sci or Tech Sci 3; an additional language 3 | 22 | |
| Diploma in Correctional and Rehabilitation Studies | Soshanguve South | 3 | 15 Jun | English 3; Maths or Maths Lit 3 | 20 | |
| Diploma in Integrated Communication | Soshanguve North | 3 | 31 Jul | English 4 (preference for 5 or more); Maths, Tech Maths or Engineering Mathematics N3 3, or Maths Lit 4 | 20; 21 | selection test (50%), interview (30%), APS (20%) |
| Diploma in Journalism | Soshanguve North | 3 | 31 Jul | English 4 (preference for 5 or more) | 24 | selection test (30%), interview (30%), APS (40%) |
| Diploma in Language Practice | Soshanguve South | 3 | 31 Jul | English 4; another official South African language offered in the programme 5 | 20 | APS 20: TUT potential assessment |
| Diploma in Law | Soshanguve South, Mbombela | 3 | 31 Jul | English 4 | 20 | |
| Diploma in Legal Support | Soshanguve South | 3 | 31 Jul | English 4; any other additional language 3 | 20 | |
| Diploma in Policing | Soshanguve South | 3 | 31 Jul | Not employed in law enforcement: English 3; Maths, Tech Maths or Maths Lit 3. Employed: Senior Certificate or NSC, a relevant NQF 5 or 6 law-enforcement qualification and five years' experience | 20 | |
| Diploma in Public Affairs: Administration of State | Soshanguve South, Mbombela, Polokwane | 3 | 31 Jul | English 3; Maths or Maths Lit 3 | 20 | |
| Diploma in Public Affairs: Local Government | Soshanguve South, Mbombela, Polokwane | 3 | 31 Jul | as above | 20 | |
| Diploma in Traffic Safety and Municipal Police Management | Soshanguve South, Polokwane | 3 | 15 Jun | as Policing | 20 | |

### Information and Communication Technology (Soshanguve South; closes 30 September)

| Programme | Campus | Years | Subjects | APS | Note |
|---|---|---|---|---|---|
| Diploma in Computer Science | Soshanguve South, eMalahleni, Polokwane | 3 | English 4; Maths or Tech Maths 5, or Maths Lit 7 | 26; 28 | |
| Diploma in Computer Science (extended) | Soshanguve South, eMalahleni, Polokwane | 4 | English 3; Maths or Tech Maths 4, or Maths Lit 6 | 23; 25 | waiting list from 21 (Maths) or 24 (Maths Lit) |
| Diploma in Computer Systems Engineering | Soshanguve South | 3 | English 4; Maths or Tech Maths 5; Phys Sci or Tech Sci 4 | 26 | |
| Diploma in Computer Systems Engineering (extended) | Soshanguve South | 4 | English 3; Maths or Tech Maths 4; Phys Sci or Tech Sci 3 | 23 | |
| Diploma in Informatics | Soshanguve South | 3 | English 4; Maths or Tech Maths 5, or Maths Lit 7 | 26; 28 | |
| Diploma in Informatics (extended) | Soshanguve South | 4 | English 3; Maths or Tech Maths 4, or Maths Lit 6 | 23; 25 | |
| Diploma in Information Technology | Soshanguve South | 3 | English 4; Maths or Tech Maths 5, or Maths Lit 7; Phys Sci or Tech Sci 3 | 26; 28 | |
| Diploma in Information Technology (extended) | Soshanguve South | 4 | English 3; Maths or Tech Maths 4, or Maths Lit 6; Phys Sci or Tech Sci 3 | 23; 25 | waiting list as Computer Science (extended) |
| Diploma in Multimedia Computing | Soshanguve South | 3 | English 4; Maths or Tech Maths 5, or Maths Lit 7 | 26; 28 | |
| Diploma in Multimedia Computing (extended) | Soshanguve South | 4 | English 3; Maths or Tech Maths 4, or Maths Lit 6 | 23; 25 | waiting list as Computer Science (extended) |

### Management Sciences (Pretoria campus; closes 30 September)

Many of these programmes admit APS 24 and more. Applicants with 20 to 23 "will be required" (or "may be invited") to
do the TUT potential assessment; the table says which.

| Programme | Campus | Years | Subjects | APS | APS 20-23 |
|---|---|---|---|---|---|
| Diploma in Administrative Information Management | Pretoria, eMalahleni, Polokwane | 3 | English 4; Maths, Tech Maths or Maths Lit 3 | 24 | potential assessment required |
| Diploma in Adventure Tourism Management | Mbombela only | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 24 | potential assessment required |
| Diploma in Casino Resort Management | Pretoria | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 24 | potential assessment required |
| Diploma in Contact Centre Management | Pretoria | 3 | English 4; Maths, Tech Maths or Maths Lit 3 | 24 | potential assessment required |
| Diploma in Credit Management | Pretoria | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4; Accounting 3 | 24 | - |
| Diploma in Ecotourism Management | Mbombela only | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 24 | may be invited |
| Diploma in Entrepreneurship | Pretoria, eMalahleni, Polokwane | 3 | English 4; Maths, Tech Maths or Maths Lit 3 | 24 | - |
| Diploma in Event Management | Pretoria | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 24 | may be invited |
| Diploma in Food Operations Management | Pretoria | 3 | English 3; Maths, Tech Maths or Maths Lit 3 | 24 | potential assessment required |
| Diploma in Hospitality Management | Pretoria | 3 | English 3; Maths, Tech Maths or Maths Lit 3 | 24 | potential assessment required |
| Diploma in Human Resource Management | Pretoria, eMalahleni, Polokwane | 3 | English 4; Maths, Tech Maths or Maths Lit 3 | 24 | - |
| Diploma in Marketing | Pretoria, Mbombela | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 24 | - |
| Diploma in Operations Management | Pretoria | 3 | English 3; Maths or Tech Maths 3, or Maths Lit 5 | 24 | - |
| Diploma in Retail Business Management | Pretoria; also online | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 24 | - |
| Diploma in Sport Management | Pretoria | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 (recommended: Accounting, Business Studies, Economics) | 24 | - |
| Diploma in Supply Chain Management | Pretoria | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 (recommended: commercial subjects) | 24 | - |
| Diploma in Tourism Management | Pretoria | 3 | English 4; Maths or Tech Maths 3, or Maths Lit 4 (recommended: Business Studies, Geography, Hospitality Studies, Travel and Tourism) | 24 | may be invited |
| Diploma in Work Study | Pretoria | 3 | English 3; Maths or Tech Maths 3, or Maths Lit 5 | 24 | - |
| Higher Certificate in Administrative Information Management | online | 1 | English 3 | 20 | no closing date printed |
| Higher Certificate in Contact Centre Management | online | 1 | English 3 | 20 | closes 30 Sep (programme page only) |

### Science (Pretoria and Arcadia campuses)

| Programme | Campus | Years | Closes | Subjects | APS | Extra selection |
|---|---|---|---|---|---|---|
| Diploma in Animal Sciences | Pretoria | 3 | 31 Jul | English 4; Maths or Tech Maths 3; Phys Sci 3 | 19 | potential assessment (40%), APS (60%) |
| Diploma in Crop Production | Pretoria | 3 | 31 Jul | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 19; 20 | admitted from 23; 19 (Maths) or 20 (Maths Lit) to 22 on a waiting list |
| Diploma in Equine Science | Pretoria | 3 | 30 Sep | English 4; Maths or Tech Maths 3; Phys Sci 3 | 19 | potential assessment (40%), APS (60%) |
| Diploma in Horticulture | Pretoria | 3 | 30 Sep | English 4; Maths or Tech Maths 3, or Maths Lit 4; Life Sciences, Phys Sci or Tech Sci 3 | 25; 26 | |
| Diploma in Landscape Technology | Pretoria | 3 | 30 Sep | as Horticulture | 25; 26 | |
| Diploma in Nature Conservation | Pretoria | 3 | 31 Jul | English 4; Maths or Tech Maths 3, or Maths Lit 4 | 24; 25 | |
| Diploma in Wildlife Management | Pretoria | 3 | 31 Jul | as Nature Conservation | 24; 25 | |
| Higher Certificate in Forestry Management | Mbombela only | 2 | 30 Sep | English 3; Maths or Tech Maths 3, or Maths Lit 6 | 18; 21 | academic proficiency test |
| Bachelor of Environmental Health | Pretoria | 4 | 31 Jul | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4; Life Sciences 4; two other subjects 4 | 24 | |
| Bachelor of Nursing | Pretoria | 4 | 15 Jun | English 4; Maths or Tech Maths 4; Life Sciences 4 | 27 | APS 27-29: potential assessment (50% needed); 30+: no test |
| Bachelor of Pharmacy | Arcadia | 4 | 15 Jun | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4; Life Sciences 4; two other subjects 4 | 24 | potential assessment, panel interview; preference from APS 32 |
| Bachelor of Radiography in Diagnostics | Arcadia | 4 | 15 Jun | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4; Life Sciences 4 | 24 | potential assessment (20%), biographical questionnaire, interview (20%), APS (60%) |
| Bachelor of Health Sciences in Biokinetics | Pretoria | 4 | 31 Jul | as Radiography | 24 | selection test (50%) if APS 24+, APS (50%) |
| BHSc in Clinical Technology | Arcadia | 4 | 31 Jul | as Radiography | 24 | potential assessment, then interview |
| BHSc in Medical Laboratory Science | Arcadia | 4 | 15 Jun | as Radiography | 24 | potential assessment, then interview |
| BHSc in Medical Orthotics and Prosthetics | Pretoria | 4 | 15 Jun | as Radiography | 24 | above APS 27: interview, dexterity test and more (APS 40%) |
| BHSc in Veterinary Technology | Arcadia | 4 | 31 Jul | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4; Life Sciences or Agricultural Sciences 4 | 24 | potential assessment (20%), questionnaire (40%), APS (40%) |
| Diploma in Kinesiology and Coaching Science | Pretoria | 3 | 31 Jul | English 3; Maths or Tech Maths 3, or Maths Lit 4; Life Sciences 3 | 24 | |
| Diploma in Somatic Therapy | Arcadia | 3 | 31 Jul | English 4; Maths or Tech Maths 4, or Maths Lit 5; Life Sciences 4 | 22; 23 | APS 22-23: potential assessment and interview; 24+: interview |
| Higher Certificate in Dental Assisting | Pretoria | 1 | 31 Jul | English 4; Maths 3, or Maths Lit 4; any other subjects 3 | 20 | potential assessment, then interview |
| BSc in Industrial Chemistry | Arcadia | 4 | 31 Jul | English 4; Maths 5; Phys Sci 5 | 24 | |
| Diploma in Analytical Chemistry | Arcadia | 3 | 31 Jul | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4 | 21 | considered from 27; 21-26 on a waiting list |
| Diploma in Biotechnology | Arcadia | 3 | 31 Jul | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4; Life Sciences 3 | 24 | |
| Diploma in Environmental Sciences | Arcadia | 3 | 30 Sep | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4 | 24 | |
| Diploma in Fire Technology | Arcadia and distance education | 3 | 31 Jul | Fire and Rescue Services staff only: NSC with bachelor's or diploma endorsement, three years' relevant work and four HAZMAT and Fire Fighter certificates | - | |
| Diploma in Food Technology | Arcadia | 3 | 30 Sep | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4; Life Sciences 3 | 24 | |
| Diploma in Geology | Arcadia | 3 | 31 Jul | English 4; Maths or Tech Maths 4; Phys Sci or Tech Sci 4 | 21 | considered from 24; 21-23 write an academic proficiency test |
| Diploma in Industrial Physics | Arcadia | 3 | 30 Sep | as Geology | 21 | as Geology |
| Diploma in Water Science and Technology | Arcadia | 3 | 30 Sep | as Geology | 21 | |
| Higher Certificate in Resource and Waste Management | Arcadia | 1 | 30 Sep | English 3; Maths or Tech Maths 3, or Maths Lit 6 | 18; 21 | |
| Higher Certificate in Water Treatment | Arcadia | 1 | 30 Sep | English 3; Maths or Tech Maths 3, or Maths Lit 6; Phys Sci or Tech Sci 3 | 18; 21 | |

Somatic Therapy's course row prints "22 (with Mathematics or Technical Sciences)"; Technical Mathematics is probably
meant. **Check.**

## Calendar (F3)

Semesters run in two terms each. Exams for semester modules; year modules' classes continue during the mid-year exams.

| Event | 2026 (s-tut-cal-2026) | 2027 (s-tut-cal-2027) |
|---|---|---|
| Late applications (programmes with space, online only) | 15-23 Jan (2026 entry) | 14-22 Jan (2027 entry) |
| Online registration | 15 Jan - 1 Feb | 14-31 Jan |
| Classes start | 2 Feb | 1 Feb |
| Newcomer orientation | 2-6 Feb | 1-5 Feb |
| Semester 1, term 1 | to 27 Mar | to 25 Mar |
| TUT recess | 30 Mar - 2 Apr | 30 Mar - 2 Apr |
| Semester 1, term 2 | 7 Apr - 30 Jun | 5 Apr - 25 Jun |
| Main exams | 25 May - 12 Jun | 24 May - 11 Jun |
| Supplementary exams (semester modules) | 17-30 Jun | 14-28 Jun |
| TUT recess | 1-10 Jul | 29 Jun - 9 Jul |
| Results published | 3 Jul | 2 Jul |
| Semester 2, term 1 (classes start) | 13 Jul - 18 Sep | 12 Jul - 17 Sep |
| TUT recess | 21-23 Sep (24 Sep Heritage Day, 25 Sep TUT holiday) | 20-23 Sep |
| Semester 2, term 2 | 28 Sep - 4 Dec | 27 Sep - 3 Dec |
| Main exams | 2-20 Nov | 1-19 Nov |
| Supplementary exams | 23 Nov - 4 Dec | 22 Nov - 3 Dec |
| Residences close | 5 Dec | 4 Dec |
| Final results published | 11 Dec | 10 Dec |

TUT's recesses are short (four days in autumn and spring); December to January is the main window for vac work.

## Campuses (F1)

From s-tut-guide-2027 p106.

| Campus | Address | Phone |
|---|---|---|
| Arcadia | 175 Nelson Mandela Drive, Pretoria | 012 382 6377 |
| Arts | Corner Du Toit and Edmund Streets, Pretoria | 012 382 6177 |
| eMalahleni | 19 OR Tambo Street, eMalahleni | 012 382 3100/4/6 |
| Ga-Rankuwa | 2827, Zone 2, Botsi Street, Ga-Rankuwa | 012 382 0500/0840 |
| Mbombela | Madiba Drive, Mbombela | 012 382 3500/3621 |
| Polokwane | Corner Market and Excelsior Streets, Polokwane | 012 382 0700 |
| Pretoria | Staatsartillerie Road, Pretoria West | 012 382 5911 |
| Soshanguve (North and South) | 2 Aubrey Matlala Road, Block K, Soshanguve | 012 382 9000 |

Contact centre: 086 110 2421, general@tut.ac.za, or SMS "TUT", your name, programme and email to 30655. Admission
enquiries: 012 382 5750/5780, admission@tut.ac.za. (p1, p106)

## Support (F5)

From s-tut-guide-2027. Crisis numbers must be checked by a person before release (CLAUDE.md).

| Need | Contact | Hours | Page |
|---|---|---|---|
| Personal counselling line (toll-free) | 0800 68 78 88 | 24 hours | p10 |
| Personal counselling appointments | counselling@tut.ac.za | | p10 |
| Student Development and Support: counselling and therapy, career guidance, study skills, academic support for students with disabilities, English support | all campuses | | p9 |
| Career counselling (free interviews at all sites; full psychometric assessment at some sites, at a cost) | careercounselling@tut.ac.za or assessmentcentre@tut.ac.za; eMalahleni 012 382 3109/10; Ga-Rankuwa 012 382 0701; Mbombela 012 382 3670; Polokwane 012 382 0953; Soshanguve 012 382 9863; Pretoria 012 382 5010/4826/5273 | | p9-10 (the course list p4 gives Mbombela 3672/70 and Pretoria 4394/4826/5075. **Check**) |
| Disability Unit | ptadisability@tut.ac.za, or the disability coordinator at your campus | | p10 |
| Health and Wellness: primary health care, mental health care, sexual and reproductive health, HIV, gender-based violence programme | Director's office 012 382 6611/6613; eMalahleni 012 382 3122; Ga-Rankuwa 012 382 0572; Mbombela 012 382 3691; Polokwane 012 382 0906; Pretoria 012 382 6612; Soshanguve 012 382 9184 | | p13-14 |
| Financial aid | Arcadia 012 382 6295 (finaidarc@tut.ac.za); Arts 012 382 6157 (finaidarts@tut.ac.za); eMalahleni 012 382 3121 (finaidema@tut.ac.za); Ga-Rankuwa 012 382 0797 (finaidgar@tut.ac.za); Mbombela 012 382 3761 (finaidmbom@tut.ac.za); Polokwane 012 382 0976 (finaidpol@tut.ac.za); Pretoria 012 382 4289 (finaidpta@tut.ac.za); Soshanguve North 012 382 9895 (finaidsoshn@tut.ac.za); Soshanguve South 012 382 9272 (finaidsoshs@tut.ac.za) | | p9, p106 |
| NSFAS, as TUT gives it | 08000 67 327; WhatsApp 063 093 5671; info@nsfas.org.za | | p9 |

Not found: food support, chaplaincy.

## Fees and funding (F4, F6)

From s-tut-fees-2026 (valid for 2026) unless shown.

| Fact | Value | Page |
|---|---|---|
| Application fee (2027) | R240, once, not refundable | s-tut-guide-2027 p7 |
| Confirming a place | R1 500 within three days of the acceptance letter, or the place is cancelled; refunded less R220 only if a valid reason stops you registering (for example, failing Grade 12) | p4 |
| First payment at registration | At least R1 500, as the first instalment of tuition (new and returning students) | p4 |
| Residence | No payment to apply; R1 200 advance before residence registration; each semester is 50% of the annual fee | p4 |
| Tuition instalments | Semester 1: 28 Feb, 31 Mar, 30 Apr. Semester 2: 31 Aug, 30 Sep, 31 Oct. Year programmes: nine instalments, 28 Feb to 31 Oct | p5 |
| Residence instalments | Semester 1: 31 Jan, 28 Feb, 31 Mar, 30 Apr. Semester 2: 31 Jul, 31 Aug, 30 Sep, 30 Oct. Year: ten instalments, 1 Jan to 31 Oct (settle by 30 Oct) | p5 |
| Early payment | 5% off class fees paid in full: year programmes by 30 Apr, semester 1 by 28 Feb, semester 2 before 31 Aug; not for NSFAS or TUT financial aid allocations; apply to Student Debtors | p6 |
| Family discount | Class fees only: second student in the household 15%, third and later 25% each | p6 |
| Residence discount | None | p6 |
| Cash | Not accepted for tuition, meals or residence | p4 |
| Tuition per programme | Charged per module and published separately; not found. TUT has an online quotation page (not read) | p4 |

**NSFAS, as stated in TUT's guide** (s-tut-guide-2027 p8-9; confirm at nsfas.org.za):
- **Who it's for:** South African citizens with a combined family income below R350 000 a year (R600 000 for students
  living with a disability). New applicants, including people who passed Grade 12 earlier but never registered at a
  university. Students who have never had NSFAS funding.
- **Each year:** apply online with your own phone number and email. Funded students re-apply each year; continued
  funding depends on academic results, and a gap year means applying again.

## Notes for the data pack

- **Points rule:** Life Orientation excluded; level 1 scores zero (decision 7); the number of subjects counted is
  still to be confirmed.
- **Either/or is the norm.** Almost every row with Mathematics reads "Maths or Tech Maths, or Maths Lit at a higher
  level", often with its own APS. Today's schema fits about 18 rows: the English-only rows and BSc Industrial
  Chemistry. The rest wait for decision 1 (routes with their own APS) and decision 8 (subject keys).
- **Two APS levels.** Where TUT publishes "admitted from X" (Management Sciences 24, Analytical Chemistry 27, Geology
  and Industrial Physics 24, Crop Production 23), the lower number is the minimum and X is a published cut-off:
  `competitive_points`.
- **Selective:** TUT ranks every programme. Proposal: `selective: true` only where TUT adds a test, interview,
  portfolio or audition, or calls the programme highly competitive (decision 9).
- **Out of the course finder:** programmes only for people already employed (Fire Technology; the employed routes of
  Policing and Traffic Safety), shown at most as a note.
- **Bridges:** no published route between extended and mainstream diplomas, or from higher certificates into
  diplomas, was found.
- **`max_choices`:** stays `null`.

## Gaps and inconsistencies

- How many subjects count towards the APS: not stated.
- Programmes per application: not stated.
- Tuition per programme: not found.
- Bachelor of Geomatics closing date: 31 July (course list) or 30 September (programme page).
- Career counselling numbers for Mbombela and Pretoria differ between the two 2027 guides.
- BEd Information Technology and Technology requirements are hard to read as printed; Somatic Therapy prints
  "Technical Sciences" where Technical Mathematics is probably meant.
- 2028 entry: the 31 July 2027 date is read from the calendar layout. The late-application window for 2028 will be
  in the 2028 calendar.
- Not found: food support, chaplaincy.
