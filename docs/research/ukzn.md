# University of KwaZulu-Natal (UKZN): programme research notes

Agent draft, read from UKZN's and the CAO's own documents on 22 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/ukzn.yaml` keeps `release: false` until a person has compared every one with its source.

## What I read

| Id in the pack | Document | Pages used |
| --- | --- | --- |
| s-ukzn-prospectus-2027 | [Undergraduate Prospectus 2027](https://applications.ukzn.ac.za/wp-content/uploads/2026/05/2027-Undergrad.pdf) ("correct at the date of publication, May 2026"), linked from the [prospectus page](https://applications.ukzn.ac.za/prospectus/) as "undergraduate/latest" | printed p10-11 (closing dates), p13-14 (entrance rules), p15-17 (the APS), p18 (campus letters), p20-24 (the programme tables, "The following programmes are available in 2027"), p25 (no NBT), p26-27 (selection), p29-32 (access programmes), p81-91 (Agriculture, Engineering and Science), p93-103 (Health Sciences), p105-115 (Humanities), p117-124 (Law and Management Studies) |
| s-ukzn-cao-2027 | [CAO Handbook 2027 Entry](https://www.cao.ac.za/Download/CAO%20HANDBOOK%202027%20Entry%20web.pdf) | UKZN's rows on printed p45-46, 60, 67-68, 74, 81-82, 88-89, 102, 109, 111, 127-128, 152-154, 156-158, 168-169, 175, 177, 181, 183-184, 197, and the access routes on p207 |
| s-ukzn-selection | [Undergraduate selection procedure](https://applications.ukzn.ac.za/selection-procedure/undergraduate-selection-procedure/) (already in the pack) | re-read for the points rule |

The prospectus tables are merged-cell tables, so I read them from page images as well as from the PDF's text; the
CAO handbook's rows were read the same way. Printed page numbers are the ones in the comments in the pack (the PDF's
page is the printed page plus 8 for the prospectus, plus 12 for the CAO handbook).

**robots.txt:** `applications.ukzn.ac.za` answered this time (it refused an honest user agent on 14 Oct): it disallows
only `/wp-admin/`. `ukzn.ac.za/robots.txt` is a 404. `www.cao.ac.za` disallows only `/WebResource.axd`. I used curl's
own user agent, one request at a time. Not read: the college handbooks on saa.ukzn.ac.za (the prospectus points to
them for detail; not needed for first-year entry).

## Why UKZN's prospectus is the source

It is UKZN's own document for the 2027 intake, newer than the pack's earlier sources and dated May 2026. Every
requirement cites it. The CAO handbook was read row by row as a cross-check; where the two differ, the pack follows
the prospectus and an extras line says what the CAO says (all differences are listed below).

## Points

The pack's rule (six subjects, Life Orientation not counted, 8 points for 90-100%) matches UKZN: the selection page
says "performance levels (1-8) for the six subjects ... excluding Life Orientation", and the prospectus (p15-17) says
"UKZN will recognise academic excellence by awarding eight points to a subject with a performance level of 90-100%"
and that the maximum APS is 48 (p26). Not changed. One oddity: the prospectus's own table under that sentence (p17)
stops at 7 points for 80-100%; the sentence, the selection page and the 48 maximum all say 8, so the pack keeps 8.
No programme counts points its own way (Medicine ranks on an average percentage, so it has no points minimum).

## The programmes

66 programmes, all with requirements (none `null`), all citing the prospectus:

- **College of Agriculture, Engineering and Science (29):** seven B Sc in Engineering degrees (Agricultural,
  Chemical, Civil, Computer, Electrical, Electronic, Mechanical), the B Sc in Land Surveying, the Bachelor of
  Architectural Studies; seven agriculture degrees (six B Sc in Agriculture specialisations: Agricultural
  Economics, Agricultural Plant Sciences, Agribusiness, Plant Pathology, Soil Science, Animal and Poultry Science,
  plus the Bachelor of Agricultural Management); the B Sc Life and Earth Sciences and Mathematics streams, nine
  focused B Sc degrees (GIS and Earth Observation, Applied Chemistry, Chemistry and Chemical Technology, Computer
  Science and IT, Crop and Horticultural Science, Environmental Science, Environmental and Earth Science, Geological
  Science, Marine Biology), the B Sc Augmented Programme and the B Sc Engineering Access Programme.
- **College of Health Sciences (13):** Audiology, Speech-Language Therapy, Dental Therapy, Medical Science
  Innovation and Entrepreneurship, Occupational Therapy, Optometry, Oral Hygiene, Pharmacy, Physiotherapy, Dietetics
  and Human Nutrition, Sport Science, Nursing and MBChB.
- **College of Humanities (14):** three B Ed degrees (Foundation, Intermediate, Senior and FET Phase); BA (General
  Studies), BA in Music, BA in Music (Foundation), B Soc Sc (General Studies), B Soc Sc in Geography and Environmental
  Management, in Housing, and in Government, Business and Ethics, Bachelor of Social Work, BA in Philosophy, Politics
  and Law, BA in Visual Art, and the B Soc Sc Extended Curriculum.
- **College of Law and Management Studies (10):** LLB full-time and part-time, Bachelor of Administration, Bachelor
  of Business Administration, two Bachelor of Business Science degrees (Finance, Investment Science), B Com, B Com
  in Accounting and both four-year B Com Extended Curriculum programmes.

A qualification offered on two campuses (each with its own CAO code) is one programme; its extras name the campuses
and its comment gives both codes. Faculty names are the colleges as the tables' headings write them.

**Selective (5):** Architectural Studies (portfolio, essay and questionnaire "influence" selection), the Engineering
Access Programme (personal circumstances, aptitude tests, possible interview), BA in Music and BA in Music
(Foundation) (auditions), and MBChB (ranked on an average percentage, with target groups). Not marked selective:
"choices 1 to 3 only" (Health Sciences) and "choice 1 only" (Nursing), quintile rules and preferences, and Sport
Science's "preference ... to applicants who show a keen interest in sport" (its selection "will be based on academic
achievement"); each is an extras line.

**Left out:** the BA International Studies (KN-P-ABI) and the "B Sc Generic Degree" (KN-P-BG4, KN-W-BG4), which are
in the CAO handbook but not in UKZN's 2027 tables; the programmes the prospectus's college sections still name but
its 2027 tables don't (B Sc Biological Sciences KN-P-BSN/KN-W-BSN, Environmental Science (Grassland Science)
KN-P-BES, Industrial and Applied Biotechnology KN-P-SII, the Bachelor of Agriculture KN-P-BAG/KN-P-BAC at Cedara,
and the diplomas in Music Performance and Jazz, which have no requirements printed); the higher certificate into
the BBA (the "CBA"), which the BBA entry mentions without a code; the PGCE and postgraduate programmes; and the
Senior Certificate, NC(V) and mature-age routes.

## Choices and approximations

- **Minimum points** are the bottom of each table's "APS range" (48-30 gives 30). The Extended Curriculum's range
  reads "20/27"; 20 is used (p108: "scores ranging from 20 to 27").
- **Three blank APS cells** (p21: Soil Science, Animal and Poultry Science, and the Life and Earth Sciences stream):
  28 from the prospectus's own p88, which gives 28 for the B Sc in Agriculture and the Life and Earth Sciences stream
  (the CAO also gives 28 for both agriculture rows). Each has a comment.
- **Life Orientation 4** is checked wherever UKZN's table asks for it (all but the B Soc Sc in Housing and Medical
  Science, Innovation and Entrepreneurship, whose rows don't name it).
- **Engineering and Land Surveying:** "Maths and Phys Sci 5 (pass with at least 65%)" is checked as 65% in each
  (`subject_min_percents`); 65% is already level 5.
- **The College of Humanities' "one of ... at level 5"** (eight programmes: BA and B Soc Sc General Studies,
  Geography and Environmental Management, Social Work, Philosophy Politics and Law, Visual Art, Government Business
  and Ethics, and Architectural Studies in a version without Mathematics): "any lang HL/FAL 5" includes English, so
  English sits in every option (English 5, or English 4 with another listed subject at 5). Religion Studies isn't a
  subject the app knows; extras say so.
- **isiZulu at level 4** (B Ed Foundation Phase) is checked as `other_language: 4`, with a line saying it must be
  isiZulu.
- **LLB "Engl HL 5/FAL 6":** English is checked at 5; extras give the full rule.
- **MBChB:** "Engl, Life Sci, Maths and Phys Sci 5" checked at level 5 (p96 says 60% in each, the same thing); the 65%
  aggregate and the ranking are extras. `min_points: null`, since the table gives "N/A".
- **Not checked, words in extras:** B Ed Intermediate Phase's "Level 5 in any two of Math, Math Lit, Technology, Life
  Science, Physical Science" (UKZN doesn't say which subjects count as Technology), and B Ed Senior and FET Phase's
  "L5 in any two NSC subjects pertaining to the package selected".
- **B Soc Sc (Housing):** the table reads "NSC-Deg with Eng and, Maths L4"; checked as English 4 and Mathematics 4.
- **Names** write out the tables' abbreviations ("B Sc Eng: Civil" is "Bachelor of Science in Engineering (Civil)").
- **Applications:** MBChB's 30 June 2026 closing date is now a `programme_closes` entry in the 2027 window (the
  window's note already said so).

## Where UKZN's prospectus and the CAO handbook differ

The pack follows UKZN's prospectus in each case, and the programme's extras say what the CAO says.

Programme codes (13):

1. In the prospectus but not in the CAO handbook (8): B Sc Life and Earth Sciences stream (KN-P/W-BS2), Mathematics
   stream (KN-P/W-BS3), Applied Chemistry (KN-W-BSR), Chemistry and Chemical Technology (KN-P-SIK), Crop and
   Horticultural Science (KN-P-SIH), Environmental and Earth Science (KN-P-EES), Marine Biology (KN-W-BSM), and B Soc
   Sc Geography and Environmental Management (KN-H/P-SGE). The CAO lists a "B Sc Generic Degree" (KN-P-BG4, KN-W-BG4,
   28 points, Mathematics 4) that UKZN's tables don't.
2. Spelled differently (5): Soil Science KN-P-BS1 (CAO: KN-P-BSI); Engineering Access KN-H-UNT (CAO: KN-H-UNP);
   Medical Science, Innovation and Entrepreneurship KN-W-BMS-IE (CAO: KN-W-MSI); BA in Music Foundation KN-H-BMX on
   p23 and KN-H-BAMUS4 on p31 (CAO: KN-H-AMF); B Ed Senior and FET KN-E-BSN/FET (CAO: KN-E-FET).

Requirements (10):

1. **B Sc Engineering Access:** UKZN 28 points, Mathematics and Physical Sciences 4; CAO 33 points, same subjects.
2. **B Sc Computer Science and IT:** UKZN 30 points, Mathematics 5; CAO 28, Mathematics 4.
3. **B Sc GIS and Earth Observation:** UKZN 30 points, Mathematics 5; CAO 28, Mathematics 4.
4. **Bachelor of Administration:** UKZN 26 points (table and p120); CAO 28.
5. **B Soc Sc (Housing):** UKZN English and Mathematics 4; CAO English and Life Orientation 4 and one of the
   humanities subjects at 5.
6. **B Ed Foundation Phase:** UKZN isiZulu 4 and Mathematical Literacy 4 or Mathematics 3; CAO any other official
   language 4 and Mathematics or Mathematical Literacy 4.
7. **B Ed Intermediate Phase:** UKZN's list of subjects for "level 5 in two" is shorter than the CAO's (which adds
   Information Technology, the technology subjects, Computer Applications Technology, Engineering Graphics and
   Design "or any other NSC subjects").
8. **Medical Science, Innovation and Entrepreneurship:** the CAO also asks for Life Orientation 4.
9. **BA in Music:** the CAO also asks for one of the humanities subjects at 5.
10. **B Soc Sc Extended Curriculum:** the CAO says quintile 1 to 3 schools (UKZN: 1 and 2) and also asks for one of
    the humanities subjects at 5.

## Conflicts inside UKZN's prospectus

- B Ed Intermediate Phase: the table (p23) asks for level 5 in two of five subjects; the Education page (p106) says
  "Mathematics is Level 4 and Mathematical Literacy Level 5". The pack uses the table's words in extras and checks
  neither.
- Architectural Studies sits in the College of Agriculture, Engineering and Science's table (p20) and section (p81),
  but the College of Humanities' list of qualifications (p107) names it too. The pack uses the table.
- Dietetics and Human Nutrition sits in the Health Sciences table (p22) and section (p102), and in Agriculture,
  Engineering and Science's list (p91). The pack uses the table.
- The points table (p17) stops at 7; the sentence above it gives 8 for 90-100% (see "Points").
- Medicine "does not consider international applications" (p10) while p96 describes SADC applicants sent by their
  ministries; the pack says nothing about international applicants.

## What a person should check first

1. **The CAO codes in "Where UKZN's prospectus and the CAO handbook differ".** A learner applies through the CAO
   with a code: if the B Sc streams and the other eight codes really aren't on the CAO's list for 2027, the app
   points learners at programmes they can't choose. Ask UKZN or the CAO which codes are live (the CAO's online
   programme search was not used).
2. **The Engineering Access Programme:** 28 or 33 points, KN-H-UNT or KN-H-UNP.
3. **The ten requirement differences** above, especially Computer Science and IT and GIS (UKZN's prospectus asks for
   more than the CAO), and B Admin and the Engineering Access Programme (UKZN asks for less).
4. **The three blank APS cells** (Soil Science, Animal and Poultry Science, Life and Earth Sciences): 28 is from p88.
5. **B Ed Intermediate and Senior/FET Phase** subject rules, which the app doesn't check.
6. **The humanities "one of" rule** as encoded: English 5 alone meets it (as "any lang HL/FAL 5" reads).
