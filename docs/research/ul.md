# University of Limpopo (UL): programme research notes

Agent draft, 14 Oct 2026. Nobody has checked these values yet: `backend/data/universities/ul.yaml` keeps
`release: false` until a person has compared every programme with its source.

## What I read

All from UL's own official site, www.ul.ac.za. UL's `robots.txt` only disallows `/wp-admin/`, so
prospective student and undergraduate documents are fully allowed.

- **Undergraduate Prospectus 2027** (`s-ul-prospectus-2027`):
  <https://www.ul.ac.za/wp-content/uploads/2025/03/Undergraduate-Prospectus-2027.pdf>
  - General admission rules and statutory requirements:
    - APS counts 6 recognised 20-credit subjects, excluding Life Orientation.
    - Compulsory baseline: Life Orientation at level 3 (40%) and English at level 3 (40%) are required for admission to any undergraduate programme.
    - Standard 1-7 scoring scale (80%+ = 7, down to 0-29% = 1).
    - Section 7 specifies departmental selection tests / additional criteria for:
      - Bachelor of Social Work (BSW)
      - Bachelor of Education in Foundation Phase Teaching (BEd FP)
      - Bachelor of Psychology (BPsych)
      - Medicine (MBChB)
  - Application information:
    - Application handling fee: R200 for South African applicants, R750 for international applicants (non-refundable).
    - Online application via UL student I-Enabler portal.
    - Required documents: Certified copy of ID/passport, Grade 11 final stamped results or Grade 12 statement/matric certificate, academic record and certificate of good conduct (transfers), and USAf foreign exemption certificate (international qualifications).
    - Standard Bank account details published for manual handling fee payments; omitted from code by project policy.
  - Faculty tables across 4 faculties:
    - Faculty of Humanities (20 programmes: 6 Education, 4 Languages & Communication, 10 Social Sciences).
    - Faculty of Management & Law (14 programmes: 3 Accountancy, 10 Economics & Management, 1 Law).
    - Faculty of Science & Agriculture (14 programmes: 4 Physical & Mineral Sciences, 6 Agricultural & Environmental Sciences, 2 Mathematical & Computer Sciences, 2 Molecular & Life Sciences).
    - Faculty of Health Sciences (6 programmes: 1 Medicine, 5 Health Care Sciences).
- **Study with us: University of Limpopo 2027 applications now open** (`s-ul-2027`):
  <https://www.ul.ac.za/study-with-us-university-of-limpopo-2027-application-now-open/>
  - Applications opened 1 April 2026.
  - Closed 30 July 2026 for MBChB and international applicants.
  - Closed 30 September 2026 for general undergraduate applicants.

## What's in the pack

All 54 undergraduate programmes published in the 2027 prospectus:

- **Faculty of Humanities: 20 programmes.**
  - School of Education (6):
    - BEd in Senior Phase & FET Teaching (Languages and Life Orientation) (APS 24)
    - BEd in Senior Phase & FET Teaching (Languages and Social Sciences) (APS 24)
    - BEd in Senior Phase & FET Teaching (Economics and Management Studies) (APS 24)
    - BEd in Senior Phase & FET Teaching (Mathematics, Natural Sciences and Technology) (APS 24)
    - BEd in Foundation Phase Teaching (selective, selection test, APS 24)
    - Postgraduate Certificate in Education (PGCE) (`requirements: null`, postgrad/graduate entry)
  - School of Languages & Communication Studies (4):
    - BA in Contemporary English and Multilingual Studies (APS 24)
    - BA in Language Practice (APS 24)
    - BA in Media Studies (APS 24)
    - BA in Information Studies (APS 23)
  - School of Social Sciences (10):
    - BA (General / Cultural Studies) (APS 23)
    - BA in Criminology and Psychology (APS 23)
    - BA in Psychology (APS 23)
    - Bachelor of Psychology (BPsych) (selective, selection test, APS 25)
    - Bachelor of Social Work (BSW) (selective, selection test, APS 23/25)
    - BA in Political Science (APS 23)
    - BA in Cultural Studies (APS 23)
    - BA in Sociology and Anthropology (APS 23)
    - BA in Development Studies (APS 23)
    - BA in Philosophy (APS 23)

- **Faculty of Management & Law: 14 programmes.**
  - School of Accountancy (3):
    - Bachelor of Accountancy (BAcc - CA stream, 4-year, APS 30)
    - Bachelor of Commerce in Accountancy (BCom Accountancy, 3-year, APS 28)
    - BCom in Accountancy (Extended Curriculum Programme, 4-year, APS 26)
  - School of Economics & Management (10):
    - BCom in Business Management (APS 26)
    - BCom in Economics (APS 26)
    - BCom in Economics (Extended Curriculum Programme, APS 22)
    - BCom in Human Resource Management (APS 26)
    - BCom in Human Resource Management (Extended Curriculum Programme, APS 22)
    - Bachelor of Administration (BAdmin) (APS 26)
    - BAdmin in Local Government (APS 26)
    - Bachelor of Administration (Extended Curriculum Programme, APS 22)
    - Bachelor of Development in Planning and Management (BDev) (APS 26)
    - Bachelor of Development in Planning and Management (Extended, APS 22)
  - School of Law (1):
    - Bachelor of Laws (LLB, 4-year, selective, APS 31)

- **Faculty of Science & Agriculture: 14 programmes.**
  - School of Physical & Mineral Sciences (4):
    - BSc in Physical & Mineral Sciences (Physics & Chemistry stream, APS 26)
    - BSc in Physical & Mineral Sciences (Extended, APS 22)
    - BSc in Geology & Mining (Earth Sciences stream, APS 26)
    - BSc in Geology & Mining (Extended, APS 22)
  - School of Agricultural & Environmental Sciences (6):
    - BSc in Agriculture (Agricultural Economics) (APS 26)
    - BSc in Agriculture (Animal Production) (APS 26)
    - BSc in Agriculture (Plant Production) (APS 26)
    - BSc in Agriculture (Soil Science) (APS 26)
    - BSc in Environmental and Resource Studies (APS 26)
    - BSc in Water and Sanitation Sciences (APS 26)
  - School of Mathematical & Computer Sciences (2):
    - BSc in Mathematical & Computer Sciences (APS 26)
    - BSc in Mathematical & Computer Sciences (Extended, APS 22)
  - School of Molecular & Life Sciences (2):
    - BSc in Life Sciences (APS 26)
    - BSc in Life Sciences (Extended, APS 22)

- **Faculty of Health Sciences: 6 programmes.**
  - School of Medicine (1):
    - MBChB (Bachelor of Medicine & Bachelor of Surgery, 6-year, selective, APS 27, closed 30 July 2026)
  - School of Health Care Sciences (5):
    - BSc in Dietetics (4-year, selective, APS 26)
    - Bachelor of Optometry (BOptom, 4-year, selective, APS 27)
    - BSc in Medical Sciences (4-year, selective, APS 26)
    - Bachelor of Nursing (BNurs, 4-year, selective, APS 26)
    - Bachelor of Pharmacy (BPharm, 4-year, selective, APS 27)

## Approximations and notes

1. **Compulsory Subjects:** UL specifies that Life Orientation (level 3, 40%) and English (level 3, 40%) are compulsory minimums for entry into the University. In addition, programmes set specific higher subject minimums.
2. **Selective Health Sciences:** All programmes in the Faculty of Health Sciences (Medicine and Health Care Sciences) are quota-limited clinical programmes subject to strict selection. They are tagged `selective: true`.
3. **PGCE:** PGCE is an undergraduate capstone/graduate entry certificate requiring an approved bachelor's degree; points are not applicable (`requirements: null`).
4. **Extended Programmes:** 8 extended curriculum programmes (ECP) are offered with duration 4 years and lower points requirements (typically APS 22 vs 26) for candidates who meet the statutory degree endorsement.
