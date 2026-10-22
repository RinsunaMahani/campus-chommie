# Durban University of Technology (DUT): programme research notes

Agent draft, read from DUT's own study guide on 22 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/dut.yaml` keeps `release: false` until a person has compared every one with its source.

## What I read

| Id in the pack | Document | Pages used (printed numbers) |
|---|---|---|
| s-dut-opportunities | [Study Opportunities 2027](https://www.dut.ac.za/wp-content/uploads/2026/06/Study-Opportunities-2027.pdf), published by Student Admissions in May 2026 (175 PDF pages) | p1 (admission rules, points table), p4 (departments' own requirements), and each programme's "Entry Requirements" table: p6-24 (Accounting and Informatics), p26-46 (Applied Sciences), p49-76 (Arts and Design), p79-103 (Engineering and the Built Environment), p106-130 (Health Sciences), p133-155 (Management Sciences) |

The printed page number is the PDF page minus 7 (printed p1 is PDF page 8). The PDF was already downloaded for
this task from DUT's official URL; I made no web requests and opened no other DUT page or the CAO handbook.

Each requirements table has three columns: the National Senior Certificate (NSC), the old Senior Certificate and the
NC(V). Only the NSC column is used. The PDF's extracted text runs the three columns together and drops some cells
(for example, Environmental Health's and Homoeopathy's English and "two more subjects" levels came out blank), so I
rendered pages to images and read them where the text was unclear or a cell was missing: printed p8, 10, 11, 12,
13, 15, 18, 19, 22, 23, 29, 31, 38, 43, 46, 56, 59, 60, 64, 67, 74, 76, 83, 84, 86, 89, 97, 101, 109, 112, 113,
114, 116, 119, 120, 121, 122, 125, 126, 127, 133, 135, 137, 138, 139, 143, 147, 151, 152, 154. The other tables
(among them Somatology p128 and Dental Assisting p130) were read from the text, where every row had its level.

## Points

The pack's `points_rules` (already there) is DUT's own: "NSC levels of achievement are calculated for the top six
subjects, excluding Life Orientation" (p1), levels 1 to 7. Internal Auditing and Taxation say "English and the next
five best results", which is the same count. No programme needed its own rule. Screen Arts and Technology's 36 points
use a weighting of their own (below).

## The programmes

89 programmes, all with requirements; none is `requirements: null`.

- Accounting and Informatics (16): Accounting Bridging Course; Bachelor of ICT, and its Internet of Things degree;
  diplomas in Accounting, Business and Information Management, ICT Applications Development, Internal Auditing and
  Taxation, each with its extended programme; ICT Business Analysis; Library and Information Studies; Management
  Accounting.
- Applied Sciences (13): BAppSc in Biotechnology, Food Science and Technology, Industrial Chemistry and Textile
  Science; Bachelor of Sport Science and Management; diplomas in Analytical Chemistry, Clothing Management, Consumer
  Sciences in Food and Nutrition, Nautical Studies, Shipping and Logistics, Sustainable Horticulture and Landscaping;
  higher certificates in Applied Sciences and Sport Management Science.
- Arts and Design (17): BAppArts in Commercial Photography and in Screen Arts and Technology; BDes in Visual
  Communication Design; six BEd SP & FET Teaching programmes (Economics and Management Sciences, Natural Sciences,
  Languages, and Civil, Electrical and Mechanical Technology, each with its own CAO code); Bachelor of Journalism;
  diplomas in Drama, Fashion Design, Fine Art, Interior Design, Jewellery Design and Manufacture, Language Practice;
  Higher Certificate in Performing Arts Technology.
- Engineering and the Built Environment (13): BEngTech in Chemical, Civil, Electronic, Industrial, Mechanical and
  Power Engineering; BBE in Architecture, Construction Studies, Geomatics, Urban and Regional Planning; diplomas in
  Civil Engineering, Construction Studies, Pulp and Paper Technology.
- Health Sciences (14): Bachelor of Child and Youth Care; BHSc in Chiropractic, Clinical Technology, Emergency Medical
  Care and Rescue, Environmental Health, Homoeopathy, Medical Laboratory Science, Medical Orthotics and Prosthetics,
  Diagnostic Radiography, Diagnostic Sonography, Radiotherapy; Bachelor of Nursing; Diploma in Somatology; Higher
  Certificate in Dental Assisting.
- Management Sciences (16): diplomas in Catering Management, Ecotourism, Hospitality Management, Tourism; the seven
  Management Sciences diplomas (Business Administration and its extended programme, Business Law, Human Resources
  Management, Marketing, Operations Management, Public Relations and Communication Management, Retail Management);
  Public Administration in Disaster and Risk Management, Local Government, Public Management, Supply Chain Management.

**Extended programmes as their own entries (6):** only where the guide gives them a CAO code of their own: Accounting
(DU-D-DA4, DU-P-DA4), Business and Information Management (DU-D-BI4), ICT Applications Development (DU-D-APF),
Internal Auditing (DU-D-DI4), Taxation (DU-D-DT6), Business Administration (DU-P-MB5, see below). They take the
diploma's table. Extended programmes the guide names only by a qualification code (Fashion Design, Fine Art,
Interior Design, Jewellery Design, Homoeopathy, Nursing, Somatology) are a line in the main programme's extras.

**One programme, two campuses:** a programme taught in Durban and Pietermaritzburg under two CAO codes is one entry;
its extras name both campuses. Part-time Operations Management (DU-D-PDY) is a line in extras.

**Points:** 34 programmes have a points minimum from the guide; 55 have `min_points: null` because DUT gives none
(only the subjects are checked, and the extras say how DUT ranks instead).

**Selective (34):** a test, interview, audition, portfolio or fitness evaluation named in the guide, or a fixed number
of offers (Drama 50, Performing Arts Technology 15, Orthotics and Prosthetics 30, set as `places`). "Ranked according
to a points system", "selected in order of merit" and "may include an interview" (Accounting, Internal Auditing,
Management Accounting, Taxation) are not selective; the "may include an interview" is in their extras. Nautical
Studies' SAMSA eyesight test after an offer is in extras, not a selection step.

**Left out:** NC(V), Senior Certificate, N4/N6, Recognition of Prior Learning and mature-age routes; advanced
diplomas and postgraduate study; DUT's "preference will be given to learners from designated groups" line in the
Management Sciences diplomas (not something a learner can act on, and the app never asks about it).

## Choices and approximations

- **English Home Language 3 or First Additional 4** (and HL 4 / FAL 5): `english` at the lower level, with the full
  rule in extras, as in MUT's pack.
- **"Recognised NSC 20-credit subjects" rows** become `additional_minimums`, one level per subject ("And TWO ... 3"
  plus "In addition: ONE ... 3" gives [3, 3, 3]). "Not more than one language" is in extras.
- **Two routes with different counts** (Internal Auditing; Management Accounting): route 1 asks three more subjects
  at 3, route 2 (with Accounting at 4) asks two. The pack uses two, so route 1 is checked one subject short; the
  extras say so.
- **Taxation's "ONE recognised NSC 20-credit subject"** has no level in the table: left out of the check, said in
  extras.
- **Performing Arts Technology:** "Mathematics OR 3 / Mathematical Literacy" with no level for Mathematical
  Literacy: no mathematics rule is checked; the extras give DUT's words.
- **Sports Science** (Sport Science degree, Sport Management certificate) isn't an NSC subject the app knows. The
  pack checks Physical Sciences or Life Sciences (or Mathematics, for the certificate), and the extras say DUT also
  lists Sports Science.
- **"Life Sciences (or recognised equivalent)"** (Horticulture): `life_sciences: 4`, the equivalent in extras.
- **Shipping and Logistics' "Business, Commerce OR Management subject 4"**: one more subject at level 4 in
  `additional_minimums`, the subject type in extras.
- **Urban and Regional Planning's "any two of Geography, History, Life Sciences, Physical Science at 4"**: six
  two-subject options in one choice.
- **Language-specific rules** (BEd Languages: isiZulu or isiXhosa 5; Language Practice: isiZulu or isiXhosa HL 4 or
  FAL 5; Journalism and Drama: another language): `other_language`, with the language named in extras.
- **Engineering ranking:** BEngTech and BBE programmes rank on Mathematics plus Physical Sciences, "subject to a
  minimum combined score of 100%" (Civil: 120%). The schema can't hold a sum of percentages; it's in extras.
- **Screen Arts and Technology's 36 points** triple or double some subjects; the guide doesn't say how many subjects
  count, so it can't be a points rule. `min_points: null`, the weighting in extras.
- **Bachelor's pass:** every degree whose table says "NSC Degree Entry" has "Your NSC must show admission to
  bachelor's degree study" in extras.
- **Accounting Bridging Course** `bridges_to` the Diploma in Accounting (`considered`): the diploma's table accepts
  "a pass in FOUR subjects of the Accounting Bridging Course" in place of the NSC rows.
- **Business Administration's extended programme:** the guide lists qualification code DPMBA1 "(ECP) (PMB)" and a
  third Pietermaritzburg CAO code, DU-P-MB5, without naming it. I took DU-P-MB5 to be the extended programme.
- **Fields** were chosen from the engine's list by the programme's subject; Nautical Studies got `engineering` for
  want of a maritime tag, Textile Science `natural_sciences` and `engineering`.

## Check first (the guide is unclear or disagrees with itself)

1. **"Mathematics OR / Mathematical Literacy OR / Accounting" rows.** Read literally, Accounting is a third option.
   The pack reads it so for the Diploma in Accounting (and its ECP) and Taxation (and its ECP): Mathematics 3,
   Mathematical Literacy 5 or Accounting 4. But Catering Management's identical table adds "Accounting is a
   compulsory Admission Requirement", and for Catering, Hospitality and Tourism (Mathematics 2 or Mathematical
   Literacy 3, which every learner has) Accounting as an option would mean nothing, so the pack makes Accounting 3
   required for those three and says so in Hospitality's and Tourism's extras. Ask DUT which reading is right for
   each.
2. **Drama's points:** the table heading says "Applicants with 22 points or more"; the note under it says
   "Candidates must have achieved a minimum of 24 points". The pack uses 24 and the extras mention both.
3. **Electronic Engineering:** the table lists Technical Mathematics 5 and Technical Sciences 5, but the note says
   neither "will be accepted as a substitute". The pack follows the note (Mathematics and Physical Sciences only).
   The other BEngTech, BBE and engineering diplomas accept them, as their tables say.
4. **Industrial and Power Engineering:** the "Physical Science 4" row has no "OR" before "Technical Science 5" (the
   other engineering tables have one). The pack reads it as either one.
5. **Diploma in Accounting's points:** no minimum in the table; the note says 24-25 points go to the extended
   programme and 26 and above to the three-year diploma. The pack sets 26 and 24.
6. **Somatology and Dental Assisting** tables are headed "NSC Degree Entry" although they're a diploma and a higher
   certificate. The pack doesn't require a bachelor's pass; their extras ask learners to check.
7. **Public Administration** gives its closing date as "30 September 2025", a year earlier than every other page;
   probably a typo for 2026.
8. **Different closing dates:** Chiropractic closed on 15 August 2026, the three radiography degrees on 31 August;
   all others on 30 September 2026. These are in extras; the pack's window still lists only the CAO's two dates
   (31 Aug, 30 Sep), so 15 August could be added to `closes_one_of` or as a `programme_closes` entry.
9. **Names:** Textile Science is "Textile Technology" in the contents; Ecotourism and Tourism are "Ecotourism
   Management" and "Tourism Management" in the contents. The pack uses the programme pages' headings.
10. **Chiropractic** asks for Life Orientation at level 4, which is in `subject_minimums` as the table says.

## What a person should check first

Items 1 to 3 above change who the app says qualifies. Then compare a sample of the tables against the PDF, starting
with the two-route programmes (Internal Auditing, Management Accounting), Consumer Sciences in Food and Nutrition,
Urban and Regional Planning and the BEd Technology programmes, which have the most options.
