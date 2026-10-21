# University of the Witwatersrand (Wits): programme research notes

Agent draft, read 14 Oct 2026 and written up 15 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/wits.yaml` keeps `release: false` until a person has compared every programme with its
source.

## Hosts and robots.txt

| Host | robots.txt | Used? |
|---|---|---|
| www.wits.ac.za | `User-agent: *` / `Disallow: /admintest/` (served as an RTF file, but that's its content). Nothing about ClaudeBot, Claude-User or anthropic-ai | Yes: every figure in the pack comes from here |
| online.wits.ac.za | `User-agent: *`, disallows only HubSpot preview and preference paths | One page read (Nursing Systems Science), to see who it's for |
| issuu.com and e.issuu.com | Answered **403** ("You are not allowed to access this resource") even for robots.txt, to curl's own user agent | **No**: treated as a block and not worked around |

All fetches used curl's own user agent, one page at a time with a pause.

## What I read

- **Wits's course finder**, one page per programme, at `https://www.wits.ac.za/course-finder/undergraduate/<faculty>/<programme>/`,
  found through the five paginated faculty listings under <https://www.wits.ac.za/undergraduate/academic-programmes/>
  (Commerce, Law and Management 3 pages; Engineering and the Built Environment 3; Health Sciences 2; Humanities 3;
  Science 5): 87 programme pages. Two older links on the index (Ecology and Conservation, Organismal Biology) redirect to
  Applied Ecology and Global Change and Biodiversity in a Changing World, which are already listed.
  Each page's "Entry Requirements" section gives the APS minimum, subject levels and wait-list rule; its facts box gives
  the programme code and the closing date. The pages are kept for the 2027 intake: they give "Application Closing Date:
  30 September 2026" (30 June 2026 for Health Sciences, Architectural Studies, Audiology, Speech-Language Pathology and
  Film and Television), "Applications to study in 2027 will be open from 1 March to 30 September 2026" (part-time), the
  Science NBT "by 31 October 2026", and "Life Orientation (LO) as a teaching major will not be included in 2027" (BEd).
  **Each programme cites its own page** (81 sources, `s-wits-<faculty>-<programme>`), because that page holds the figures.
- <https://www.wits.ac.za/undergraduate/entry-requirements/> (already `s-wits-entry`): the APS table (matches the pack's
  points rule) and "Mathematical Literacy will be considered for LLB, Education and Humanities (except for
  Speech-Language Pathology and Audiology)".
- <https://www.wits.ac.za/undergraduate/apply-to-wits/additional-requirements/>: auditions, portfolios, the BAS exercise,
  NBT dates and job-shadowing certificates.
- <https://www.wits.ac.za/science/undergraduate/biological-sciences-programme/>: the six Biological Sciences pages
  (code SBA11) are streams of one "BSc in the field of Biological Sciences" (APS 43+, English 5, Mathematics 5), and its
  courses are "NOT offered to students who have applied for a BSc General degree".
- <https://www.wits.ac.za/bcom/>: Economics, Finance, Human Resource Management, Information Systems, Insurance and Risk
  Management, Management and Marketing are "BCom Major choices".
- The faculty undergraduate pages and Science's cluster pages (Physical, Earth, Mathematical Sciences), for anything the
  course finder misses: they list nothing more, and no extended or foundation programme.

## What I couldn't read

The **Guide for Undergraduate Applicants 2027** and the **Admission Requirements 2027** are only embedded from Issuu
(`issuu.com/witsmarketing`, documents `guide_for_undergrad_applicants_-_2027` and `admission_requirements_2027`).
Wits's admission requirements page links to "pages 16 to 25" of that guide, faculty by faculty. Issuu refused curl, so
**a person should open both in a browser** at <https://www.wits.ac.za/undergraduate/guide-for-undergraduates/> and
<https://www.wits.ac.za/undergraduate/entry-requirements/admission-requirements-nsc/> and compare them with the pack
(see "Check first"). I found no copy of either on www.wits.ac.za (Wits has no site search at `/search/`).

## What's in the pack

85 programmes, all 85 with requirements; 20 marked selective.

- Commerce, Law and Management 17: BCom (General), Accounting, BAccSc, Financial Sciences, BEconSc, the six BCom majors
  that have pages, Information Systems, PPE, BCom with Law, the four-year LLB, and the part-time BCom and BCom with Law.
- Engineering and the Built Environment 16: nine BSc (Eng) branches, BEngSc (BME), BEngSc in Digital Arts, BSc
  Engineering part-time, BAS, Construction Studies, Property Studies, Urban and Regional Planning.
- Health Sciences 11: three BHSc fields, BCMP, BDS, MBBCh, BNurs, BSc (OT), BOHSc, BPharm, BSc (Physiotherapy).
- Humanities 15: BA, BA part-time, BA part-time with Law, BA with Law, BA Digital Arts, BAFT, BAFA, BMus, Theatre and
  Performance, Social Work, Audiology, Speech-Language Pathology and three BEd phases.
- Science 26: BSc General and 25 fields.

Left out: **Applied Development Economics** (the page says "Entry is at third-year level"); **BHSc in Nursing Systems
Science** (online, "specifically designed for practising nurses": you must be registered with the nursing council and
practising); the **two- and three-year LLB streams** (for graduates); the GEMP and GEPP graduate-entry routes.

No `requirements: null`: every page gives its requirements, or points to another page that does (below).

## Approximations (each has an extras line in the pack)

1. **Minimum and wait-list.** `min_points` is the page's "APS nn+" figure; the wait-list range ("35-37 with English and
   Mathematics at level 6") is an extras line, not a lower route. The part-time BCom's APS is written "38-43": the floor,
   38, is the minimum, with the range in extras.
2. **Health Sciences publishes no APS** for any programme: Wits ranks by a Composite Index (75% the average percentage of
   five named subjects, 25% NBT). So `min_points: null`, `selective: true`, and the index is the selection note.
   "Life Sciences AND/OR Physical Sciences" is an either/or choice; BDS says "AND", so it needs both.
3. **Mathematics and Mathematical Literacy on separate lines** (BA with Law, BA part-time with Law: "Mathematics Level 3",
   "Maths Literacy Level 4") are read as either/or, since a learner takes one or the other; the LLB's wait-list sentence
   says "Mathematics Level 5 OR Maths Literacy Level 6" outright.
4. **Pages that point elsewhere for their figures** cite the page that holds them: Applied Chemistry cites Chemistry ("See
   the entry requirements details outlined in the Chemistry entry"); BSc Archaeology, Geography and Mathematics cite the
   BSc page (their pages send BSc applicants there). For those three I used the BSc General's figures (42+, English 5,
   Mathematics 5); SBA10 Geographical and Archaeological Studies has the same figures.
5. **Majors listed as programmes.** Wits lists six BCom majors (no programme code) and the six Biological Sciences streams
   (one code, SBA11) as separate course-finder entries, so they're separate entries here, each saying how you apply.
   Electrical and Information Engineering share EFA03; the three BHSc fields share MBA05.
6. **Percentages kept as percentages**: BAS (50% in English and Mathematics) and the three Physics programmes (at least 70%
   in Mathematics and Physical Sciences; English "Level 6 or ≥ 70%" is level 6).
7. **Selective (20)**: BAS (exercise and interview), all 11 Health Sciences programmes (Composite Index with the NBT),
   Audiology and Speech-Language Pathology (30 places each, selected on results and NBT), Social Work (60 places, selected
   within school quintiles), Film and Television (portfolio), Fine Arts (questionnaire and portfolio), Music (audition),
   Theatre and Performance (audition), BA Digital Arts (workshop or questionnaire). Not selective: BEd ("preference is
   given to students with higher English results", in extras), engineering (its wait-listing is in extras) and Science
   (the NBT is for support, not selection).
8. **Points rule unchanged.** No page says a programme or faculty counts differently from "the best seven subjects
   including Life Orientation". Health Sciences doesn't use the APS at all, which `min_points: null` covers.
9. **Bridges (considered)**: BEngSc (BME) into the third year of BSc (Eng) Electrical or Information Engineering ("You
   can apply for admission into the third year"), and BEngSc in Digital Arts into the third year of Information
   Engineering ("you may continue").

## Check first

1. **The 2027 Guide and Admission Requirements on Issuu** against the course-finder figures, especially the APS minimums.
2. **Health Sciences NBT date**: programme pages say 17 August; the additional-requirements page says 15 August.
3. **Chemistry with Chemical Engineering** gives two wait-list ranges (40-42 and 40-41).
4. Whether the app should list BCom majors and Biological Sciences streams separately (12 entries), or only the
   degree you apply for.
5. **BEd Senior Phase and FET**: Wits also considers your Grade 12 levels in the subjects you'd teach, without saying
   which levels.
6. Whether **part-time** programmes (BCom, BCom with Law, BA, BA with Law, BSc Engineering) belong in a school-leaver's
   finder: they take NSC applicants and don't require a job, but run in the evenings and exclude NSFAS.

## Also found (outside this brief)

- `backend/tests/engine/test_overview.py` line 42 expects Wits's summary "We haven't added this university's programmes
  yet." and now fails; `tests/domains/catalogue/test_universities_api.py` (programmes == 0) and
  `tests/domains/pathways/test_course_finder_api.py` (the same summary) make the same assumption.
- The pack's 2027 window could list the 30 June closers as `programme_closes` (all Health Sciences programmes, `bas`,
  `b_audiology`, `b_slp`, `baft`); today it's a note.
