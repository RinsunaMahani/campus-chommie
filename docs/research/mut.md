# Mangosuthu University of Technology (MUT): programme research notes

Agent draft, read from MUT's website and the CAO's documents on 13 and 14 Oct 2026. Nobody has checked these values
yet: `backend/data/universities/mut.yaml` keeps `release: false` until a person has compared every one with its source.

## What I read

| Id in the pack | Document | Pages used (printed numbers) |
|---|---|---|
| s-mut-cao-2027 | [CAO Handbook 2027 Entry](https://www.cao.ac.za/Download/CAO%20HANDBOOK%202027%20Entry%20web.pdf) | p30-32 (how points work); MUT's rows on p47-51, 62, 68-71, 75-77, 92-96, 104, 112-113, 132, 152, 161, 178-179, 181; access routes p204-206 |
| s-mut-admission | [Admission Requirements](https://www.mut.ac.za/admission-requirements/) | the points rule: "the best five subjects", and the point calculation matrix |
| s-mut-prospectus | [Undergraduate prospectus](https://www.mut.ac.za/wp-content/uploads/2026/05/MUT-First-Year-Prospectus-2026.pdf): the file is named 2026, was uploaded in May 2026 and names no intake year | p7 (points), p12-13, 18-19, 24-25 |
| s-mut-ms-2026 | [Faculty of Management Sciences Prospectus 2026](https://www.mut.ac.za/wp-content/uploads/2025/12/2026-Management-Sciences-Prospectus.pdf) | p12-13, 56, 78, 92, 105 |
| s-mut-ahs-2026 | [Faculty of Applied and Health Sciences Prospectus 2026](https://www.mut.ac.za/wp-content/uploads/2025/12/2026-Applied-and-Health-Sciences-Handbook.pdf) | p4, 8, 12, 16, 24-25, 29-35, 42-43, 48, 51, 62, 84 |
| s-mut-eng-2026 | [Faculty of Engineering Prospectus 2026](https://www.mut.ac.za/wp-content/uploads/2025/12/2026-Engineering-Faculty-Prospectus_.pdf) | p8, 20-21, 27-44, 50-51, 64-65, 78, 83-84, 92-96 |
| s-mut-cmqs-2026 | [Construction Management and Quantity Surveying Departmental Prospectus 2026](https://www.mut.ac.za/wp-content/uploads/2026/05/2026-CM-AND-QS-Prospectus.pdf) | p3-4, 15-16, 23 |
| s-mut-rules-2026 | [General Information and Regulations 2026](https://www.mut.ac.za/wp-content/uploads/2026/01/2026-General-Rules-and-Regulation-Handbook-14-Jan-2026.pdf) | p52 (rule G.14) |
| (cross-check) | The CAO's [Entry Requirement Changes 2027](https://www.cao.ac.za/download/Entry%20Requirement%20Changes%202027%20Entry%20-%2001.10.2027.pdf), [Closing Date Changes](https://www.cao.ac.za/download/Closing%20Date%20Changes%20-%2029.09.2026.pdf) and [New Programmes](https://www.cao.ac.za/download/New_Programmes.html) | no MUT rows in any of them |
| (cross-check) | MUT's [apply page](https://www.mut.ac.za/prospective-students/apply/) (s-mut-apply) | faculty minimums, closing dates, second-semester dates |

Nothing was blocked. The apply page's prospectus link (a flipbook at /media/publications-2/) returns 404; the same
prospectus is a PDF on MUT's publications page. The CAO's new-programmes page builds its table in the browser, so I
read the list embedded in the page. Where extracted text came out jumbled (the prospectus tables, CAO pages 69 and 92,
the engineering and construction handbook tables) I rendered the pages as images and read them.

## Points: what MUT says, and what the pack does

- **University rule** (`s-mut-admission`): points "calculated from the best five subjects presented by the prospective
  student", on a matrix of 90-100% = 8, 80-89% = 7, 70-79% = 6, 60-69% = 5, 50-59% = 4, 40-49% = 3, with nothing
  below 40% (`count_from_level: 3`). The prospectus (p7) has the same matrix.
- **Life Orientation** isn't mentioned on that page. MUT's rule G.14 leaves it out of the six subjects it recognises
  for admission, its handbooks leave it out of points ("Total Minimum Points (excluding Life Orientation)", Public
  Management; "25 points excluding Life Orientation", Building), and the CAO handbook (p30-32) adds points "excluding
  LO". The pack leaves it out and says so in the rule's note.
- **Five or six subjects? Ask MUT first.** Everything else points to six: the CAO's default is "the top six subjects,
  excluding Life Orientation"; MUT's IT entries say "the best six subjects excluding Life Orientation"; and most
  programmes list six subjects (English, Accounting, Mathematics and "any 3 subjects level 3", for example). Only the
  two IT diplomas say six in so many words, so only they carry their own `points_rules` (six, no Life Orientation,
  MUT's matrix; cited to the prospectus, p7 and p25). Every other programme uses the five-subject rule, which gives
  fewer points than six would: a fictional learner with 5, 5, 4, 4, 4 and 3 gets 22 on five and 25 on six.

## The programmes

40 programmes; 39 have requirements. They come from the CAO's 2027 handbook, which the 2026 faculty handbooks repeat
closely, except: Civil Engineering and Surveying (and their extended programmes) take 20 points from the engineering
handbook ("In addition the minimum total points must be 20", p36 and p44), and both Building diplomas take their
subjects, 25 points and entrance test from the department's handbook (p15-16).

- Management Sciences (10): Accounting (3 and 4 years), Cost and Management Accounting, Local Government Finance,
  Public Finance and Accounting (3 and 4 years), Human Resource Management, Marketing, Office Management and
  Technology, Public Management.
- Engineering (17): Building, Surveying, Civil, Electrical and Mechanical Engineering, each with its extended
  curriculum programme; Chemical Engineering; access courses in Building, Surveying, Chemical, Civil, Electrical and
  Mechanical Engineering.
- Applied and Health Sciences (13): BSc Environmental Health, BHSc Medical Laboratory Science, Bachelor of Applied
  Science in Nature Conservation; diplomas in Animal Production and Crop Production (each with an extended programme),
  Community Extension, Nature Conservation, Information Technology (and extended), Analytical Chemistry; Access
  Course: Analytical Chemistry.

**`requirements: null` (1): Community Extension.** The CAO says "Engl 4 and Agric Sci 4/ Cons Stud 4, Life Sci and
Geog or Econ and Life Sci 4" (22 points); the AHS handbook (p35) adds Mathematics or Mathematical Literacy at 3 and a
Business Studies with Life Sciences option; the prospectus (p24) asks for level 4 in any one of Agricultural Sciences,
Consumer Studies, Life Sciences, Geography or Economics. They can't be read as one rule. The handbook (p33) also calls
it the Diploma in Agricultural Extension (Science) and Sustainable Food Systems.

Left out: advanced, postgraduate and master's programmes, and the routes for Recognition of Prior Learning, NC(V),
N3 to N6 and the Senior Certificate. The apply page still describes a "Diploma: Biomedical Technology"; neither the
CAO's 2027 handbook nor the 2026 faculty handbook lists it (the faculty offers the BHSc), so it's left out.

Selective (11): the four agriculture diplomas (placement test), both IT diplomas (entrance test and/or ranking),
Medical Laboratory Science (interview and placement tests), Civil Engineering ECP (the CAO's note mentions a
"selection test"), both Building diplomas (entrance test, department handbook p16), and the Diploma in Nature
Conservation (a CV and field experience, AHS handbook p62).

## Approximations and choices

- **Points the CAO doesn't give.** Chemical, Electrical and Mechanical Engineering (with their extended programmes)
  and Analytical Chemistry have no points in the CAO handbook or their faculty handbook. The pack leaves `min_points`
  null, so only their subjects are checked, and extras give the prospectus's general 25 (p7: applicants are "required
  to meet a minimum of 25 points"), which programme rows elsewhere go below.
- **Access courses** (7) are the CAO's "alternative access route programmes": six-month (Building: one-year) bridging
  courses for applicants who don't meet a diploma's requirements. They're in as a first step a school-leaver applies
  for; drop them if they're out of scope. No points are published for them, so `min_points` is null, said in extras. Each
  `bridges_to` its diploma (Chemical also to Analytical Chemistry), marked `considered`: each diploma still selects
  on merit. Electrical ("will gain access", p65) and Mechanical ("for promotion to the S1 level", p96) read closer to
  `by_rule`.
- **"Engl HL 3/FAL 4"** (HR, Marketing, Office Management, Public Management): `english: 3`, the full rule in extras.
- **"Home Lang 4 and FAL 3"** (Electrical and Mechanical access): `english: 3` and `other_language: 3`, the full rule
  in extras. For the other access courses the handbooks add "satisfactory achievement" (4) in the home language: in
  extras.
- **Marketing and Office Management:** "Life Orientation, and any subject at level 1 or 2, isn't considered for
  selection" is in extras, as the handbook words it. The CAO's Marketing note says learners with level 2 or below in
  Life Orientation "and other subjects will not be considered", which may mean they're turned away.
- **Crop Production (ECP):** its CAO row shares Crop Production's merged cells; the AHS handbook (p8) gives the same.
- **Technical Mathematics and Technical Sciences** count wherever the CAO's 2027 rows name them, even where the
  prospectus lists only Mathematics and Physical Science.
- **Second-semester intake:** the CAO lists 31 May 2027 for July entry to Chemical, Civil, Electrical and Mechanical
  Engineering, Surveying, Analytical Chemistry and six access courses. The pack has one window per intake, so this is
  in extras only.

## Check (documents disagree)

1. **Five or six subjects** (above).
2. **The prospectus asks for more** than the CAO and the 2026 handbooks: English First Additional Language 5 and
   Mathematical Literacy 6 (Accounting, Public Finance ECP), Mathematical Literacy 6 (Cost and Management Accounting,
   Local Government Finance), English Home Language 4 or First Additional 5 (Marketing), 25 points with English 4 and
   Mathematics 4 (IT), Mathematics 3 or Mathematical Literacy 4 (IT ECP), Mathematics 4 (Applied Science in Nature
   Conservation). Its HR and agriculture rows don't line up and weren't used. The pack follows the CAO, whose 2027
   changes list has no MUT rows, and says so in extras.
3. **Engineering English:** the extended programmes' tables for Civil and Surveying (p36, 44) say English "4 or 5";
   the regular programmes and the CAO say 4. The pack uses 4.
4. **Building English:** the department table (p15) heads its column "English Home Language"; the CAO and p23 say
   English. The pack uses English 4, Home or First Additional.
5. **Nature Conservation diploma:** the AHS handbook (p62) also asks for two more subjects at level 3; the CAO doesn't.
6. **Environmental Health** takes 3 years in the prospectus, 4 in the CAO and the AHS handbook.
7. **General minimums not applied:** G.14 asks for six subjects at level 3 or better, and the admission page for "a
   minimum of 5 subjects with level 4 pass for diploma study and level 3 for Access Courses"; programme rows contradict
   both (IT ECP takes Mathematics at 2; Accounting takes three subjects at 3).

## For the coordinator

- The pack's header comment changed one sentence: it said MUT has no points rule.
- The prospectus says applications open on 1 March; the apply page (the window's note) says January.
- `points_note` is gone, as the brief asks when a rule is added.
