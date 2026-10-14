# Rhodes University (RU): programme research notes

Agent draft, 14 Oct 2026. Nobody has checked these values yet: `backend/data/universities/ru.yaml` keeps
`release: false` until a person has compared every programme with its source.

## What I read

All from Rhodes's own official site, www.ru.ac.za. Rhodes's `robots.txt` specifies `Allow: /`, so
prospective student and undergraduate documents are fully accessible.

- **RU Ready: Undergraduate Prospectus** (`s-ru-prospectus`), 24 pages:
  <https://www.ru.ac.za/media/rhodesuniversity/content/registrar/documents/information/studentrecruitment/RU_READY_Undergraduate_Prospectus_2026_DIGITAL_A5_Landscape_24pp_18Mar2026.pdf>
  - Pages 6 to 8: Minimum statutory admission requirements and APS calculation.
    - APS calculation: Divide the percentage achieved in each of your 6 best subjects by 10, then add them up (e.g. 78% gives 7.8 points; maximum 60 points).
    - Life Orientation is excluded from the APS calculation, but a subminimum of Level 4 (50%) in Life Orientation is required across all faculties.
    - Automatic provisional acceptance: Offered to applicants with 45+ points (40+ for BCom/BEcon).
    - Dean's discretion: Offered to applicants with 34-44 points depending on the faculty and space availability.
    - Extended Studies Programme: 4-year extended degrees for students from disadvantaged backgrounds with 34-37 points.
  - Pages 11 to 18: Faculty degree tables (16 undergraduate programmes across 6 faculties).
  - Pages 22 and 23: Application information:
    - Online application opens 1 April 2026 and closes 30 September 2026.
    - Applications portal: ross.ru.ac.za / www.ru.ac.za/admissiongateway.
    - Required documents: Certified copy of ID or passport, Grade 11 final results or Grade 12 Term 2 report / NSC statement.
- **Payment of fees: application** (`s-ru-fees`):
  <https://www.ru.ac.za/admissiongateway/application/paymentoffees/>
  - Application handling fee: R100 (non-refundable).

## What's in the pack

All 16 undergraduate degree qualifications across Rhodes University's 6 faculties:

- **Faculty of Commerce: 4 programmes.**
  - Bachelor of Business Science (BBusSc) (4-year, APS 38-44 discretion, 45+ provisional offer, English 4, Mathematics 6).
  - Bachelor of Commerce (BCom) (3-year, APS 34-39 discretion, 40+ provisional offer, English 4, Mathematics 4).
  - Bachelor of Economics (BEcon) (3-year, APS 34-39 discretion, 40+ provisional offer, English 4, Mathematics 4).
  - Bachelor of Commerce (Extended Studies Programme) (4-year, APS 34-37, Mathematics 4).

- **Faculty of Humanities: 6 programmes.**
  - Bachelor of Arts (BA) (3-year, APS 34-44 discretion, 45+ provisional offer, English HL 60% or FAL 65%).
  - Bachelor of Social Science (BSocSc) (3-year, APS 34-44 discretion, 45+ provisional offer, English HL 60% or FAL 65%).
  - Bachelor of Fine Arts (BFA) (4-year, selective, portfolio required, APS 34-44 discretion, 45+ provisional offer, English HL 60% or FAL 65%).
  - Bachelor of Music (BMus) (4-year, selective, audition required, APS 34-44 discretion, 45+ provisional offer, English HL 60% or FAL 65%).
  - Bachelor of Journalism (BJourn) (4-year, selective, APS 34-44 discretion, 45+ provisional offer, English HL 60% or FAL 65%).
  - Bachelor of Arts / Social Science (Extended Studies Programme) (4-year, APS 34-37, English HL 60% or FAL 65%).

- **Faculty of Education: 2 programmes.**
  - Bachelor of Education in Foundation Phase Teaching (4-year, APS 39-43 discretion, 44+ provisional offer, English 4, Mathematics 3 or Mathematical Literacy 4).
  - Postgraduate Certificate in Education (PGCE) (1-year capstone, requires bachelor's degree, `requirements: null`).

- **Faculty of Law: 1 programme.**
  - Bachelor of Laws (LLB) (4-year, selective direct entry, APS 40-44 discretion, 45+ provisional offer, English HL 5 or FAL 6, Mathematics 4 or Mathematical Literacy 5).

- **Faculty of Pharmacy: 1 programme.**
  - Bachelor of Pharmacy (BPharm) (4-year, selective, APS 40-44 discretion with Maths 5 / Life Sci 5 / Physical Sci 5; 45+ provisional offer with Maths 6 / Life Sci 6 / Physical Sci 6).

- **Faculty of Science: 2 programmes.**
  - Bachelor of Science (BSc) (3-year, APS 39-44 discretion, 45+ provisional offer, English HL 60% or FAL 65%, Mathematics 4, Physical Sciences 5 or Life Sciences 5).
  - Bachelor of Science in Information Systems (BSc InfoSys) (3-year, APS 40-44 discretion, 45+ provisional offer, English 5, Mathematics 4, Physical Sciences 5).

## Approximations and notes

1. **Dean's Discretion vs Provisional Offer:** In accordance with Campus Chommie engine semantics, `min_points` captures the minimum score for consideration (the Dean's discretion threshold), while `competitive_points` captures the automatic provisional offer score (typically 45, or 40 for BCom/BEcon).
2. **Life Orientation Rule:** Rhodes requires at least 50% (level 4) in Life Orientation for admission into any faculty, but Life Orientation is excluded from the six subjects counted toward the APS.
3. **Collegiate Flexibility:** Rhodes uses general degree qualifications (BA, BSocSc, BSc, BCom) under which students select from over 30 majors.
