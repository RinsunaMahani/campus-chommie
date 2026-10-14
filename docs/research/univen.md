# University of Venda (UNIVEN): programme research notes

Agent draft, 14 Oct 2026. Nobody has checked these values yet: `backend/data/universities/univen.yaml` keeps
`release: false` until a person has compared every programme with its source.

## What I read

All from UNIVEN's own official site, www.univen.ac.za. UNIVEN's `robots.txt` only disallows `/wp-admin/`, so
prospective student and undergraduate documents are fully allowed.

- **2027 Undergraduate Prospectus** (`s-univen-prospectus`), 28 pages:
  <https://www.univen.ac.za/wp-content/uploads/2026/09/2027-Univen-Undergraduate-Prospectus.pdf>
  - Pages 7 and 8: Minimum statutory admission requirements, scoring scale for 2027, and required documents.
    - Life Orientation is excluded from APS.
    - Only the 7 subjects with the highest marks are used.
    - Subjects with less than 40% are not included (score 0 points).
    - Percentage points calculation: each subject scores a tenth of its percentage (75% scores 7.5 points).
    - Baseline minimum for degree admission is 26 points.
  - Page 9: Application information:
    - Free application (no application fee).
    - Online application opens 1 May 2026 and closes 30 September 2026.
    - Applicant creates a 5-digit PIN for MyAccess profile.
  - Pages 13 and 14: Faculty of Humanities, Social Sciences and Education programmes (14 programmes).
  - Page 15: Faculty of Health Sciences programmes (7 programmes).
  - Pages 18 and 19: Faculty of Management, Commerce and Law programmes (19 programmes).
  - Pages 23 to 25: Faculty of Science, Engineering and Agriculture programmes (40 programmes).
  - Pages 26 and 27: Faculty contact details.
- **How to apply page** (`s-univen-apply`):
  <https://www.univen.ac.za/students/student-support-services/how-to-apply/>

## What's in the pack

80 programmes, 79 with full requirements and 1 with no published minimum:

- **Faculty of Humanities, Social Sciences and Education: 14 programmes.**
  - Humanities & Social Sciences Stream (12): BA (Media Studies), BA, BA (Development Studies), Bachelor of Indigenous Knowledge Systems, BA in Language Practice, BA (English Language and Literature), BA in International Relations, BA in Youth Development, BA (History), Bachelor of Theology, Higher Certificate in Music, Bachelor of Social Work (selective).
  - Education Stream (2): BEd in Senior Phase and Further Education and Training (with 3 specialisation streams), BEd in Foundation Phase Teaching.
- **Faculty of Health Sciences: 7 programmes.**
  - Degrees (6): Bachelor of Nursing (selective, 38 points), BSc in Nutrition, BSc in Sports and Exercise Science, BSc in Biokinetics (selective), BSc in Recreation and Leisure Studies, Bachelor of Psychology (selective, departmental test).
  - Diploma (1): Diploma in Nursing (selective, 28 points).
- **Faculty of Management, Commerce and Law: 19 programmes.**
  - Management & Commerce Stream (10): BAdmin in Public Administration, BCom in Accounting Sciences (selective, 35 points), BCom in Tourism Management, BCom in Accounting, BCom in Business Information Systems, BCom in Business Management, BCom in Cost and Management Accounting, BCom in Economics, BCom in Human Resource Management, BCom in Industrial Psychology.
  - Law Stream (2): LLB (selective, 38 points, English 60%), BA in Criminal Justice (34 points).
  - Extended Degree Programmes (7): Extended BAdmin, Extended BCom (Accounting), Extended BCom (Business Information Systems), Extended BCom (Business Management), Extended BCom (Cost and Management Accounting), Extended BCom (Economics), Extended BCom (Human Resources Management). APS 28-31 for applicants meeting bachelor endorsement.
- **Faculty of Science, Engineering and Agriculture: 40 programmes.**
  - Diploma (1): Diploma in Freshwater Technology (24 points).
  - BSc Science Stream (13): 13 combinations (Biochemistry & Microbiology, Biochemistry & Biology, Microbiology & Botany, Mathematics & Applied Mathematics, Mathematics & Physics, Mathematics & Statistics, Physics & Chemistry, Chemistry & Mathematics, Chemistry & Biochemistry, Chemistry & Applied Chemistry, Botany & Zoology, Computer Science, Computer Science & Mathematics) each requiring NSC 26 points and level 4 in English, Mathematics, Physical Science and Life Sciences.
  - Environmental Sciences Stream (5): Bachelor of Environmental Sciences, Bachelor of Earth Sciences in Mining and Environmental Geology, Bachelor of Earth Sciences in Hydrology and Water Resources, Bachelor of Urban and Regional Planning (selective), Bachelor of Environmental Sciences in Disaster Risk Reduction.
  - Agriculture Stream (8): BSc in Agriculture (Agricultural Economics, Agribusiness Management, Animal Science, Horticultural Sciences, Plant Production), BSc in Soil Science, BSc in Forestry, BSc in Food Science and Technology.
  - Extended BSc Programmes (13): 13 extended variants of the science stream with APS 24-26 and duration 4 years.

`requirements: null` (1): **Higher Certificate in Music** (the prospectus publishes no points minimum, specifying only NSC certificate + adequate achievement in English).

## Approximations and notes

1. **BEd Senior Phase and FET:** The prospectus describes three elective subject pairs (Maths + Sciences, Commerce, or Humanities/Languages). The pack sets English 4 and min_points 36, and records the three streams in extras.
2. **BEd Foundation Phase Teaching:** Requires level 4 in English, level 4 in an African Language (Tshivenda, Sepedi, or Xitsonga), and either Mathematics 3 (40%) or Mathematical Literacy 4 (50%).
3. **Application Documents:** Verified from prospectus page 8 (ID/passport, Grade 11 final stamped report or Grade 12 statement/matric certificate, academic record for transfer students, SAQA evaluation for international students).
4. **Application Fee:** Free (R0) as confirmed on prospectus pages 8 and 9 and the how-to-apply portal.
