# University of Mpumalanga (UMP): programme research notes

Agent draft, read from UMP's own website and documents on 13 and 14 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/ump.yaml` keeps `release: false` until a person has compared every one with its source.
Staff names, email addresses and the bank account on UMP's registration page are left out on purpose.

## What I read

| Id in the pack | Document | Used for |
|---|---|---|
| `s-ump-dip-plant-production` to `s-ump-bsw` (22 ids), and `s-ump-aps` for the BEd | Each programme's own page under [Faculties and Schools](https://www.ump.ac.za/Study-with-us/Faculties-and-Schools.aspx), read 14 Oct 2026. The pages show no year or date | Every programme's requirements |
| `s-ump-ug-leaflet` | [Undergraduate Programmes](https://www.ump.ac.za/getattachment/Study-with-us/Application-Process/Online-Applications/Undergraduate-Programmes.pdf.aspx?lang=en-US), an 8-page leaflet. No year printed; the PDF was made on 5 Oct 2023, so probably for the 2024 intake. The Online Applications page no longer links it | Cross-checking the pages (p2 to p7), and two levels the pages leave out (see Approximations) |
| `s-ump-fees-2026` | [2026 Fees Handbook](https://www.ump.ac.za/getattachment/Study-with-us/Fee-Structure/UMP-2026-Fees-Handbook.pdf.aspx?lang=en-US) | Which undergraduate programmes run in 2026 (p8 to p17); the only mention of the Bachelor of Social Sciences (p15) |
| (list only) | The Faculties and Schools menu (94 links), the three faculty pages and the seven school pages | Finding every programme |
| `s-ump-apply` (already in the pack) | [Online Applications](https://www.ump.ac.za/Study-with-us/Application-Process/Online-Applications) | 2027 applications 1 Jun to 30 Nov 2026, two choices |

Nothing was blocked: every page and PDF downloaded with curl. I didn't open the iEnabler application portal. Web
searches limited to ump.ac.za found no 2027 prospectus and no page for the Bachelor of Social Sciences. UMP's Almanac
page is a calendar only, with no admission rules.

The leaflet is laid out in columns, and its extracted text runs one programme into the next (page 4 starts with the
end of the Plant Production diploma). I rendered its pages as images to match each line to its programme.

## The programmes

24 programmes, 23 with requirements. `requirements: null` for the **Bachelor of Social Sciences**: it appears only as a
first-year fee line in the 2026 Fees Handbook (p15), with no programme page and no published requirements.

- Agriculture and Natural Sciences (11): Diplomas in Plant Production, Animal Production, Nature Conservation, and ICT
  in Applications Development; Higher Certificate in ICT in User Support; BAgric in Agricultural Extension and Rural
  Resource Management; BSc, BSc in Agriculture, BSc in Forestry, BSc in Environmental Science; Bachelor of ICT.
- Economics, Development and Business Sciences (12): Bachelor of Administration, BCom (General), Bachelor of
  Development Studies, LLB, Diploma in Entrepreneurship; Higher Certificate in Event Management, Diplomas in
  Hospitality Management and Culinary Arts; BA (General), BA in Media, Communication and Culture, Bachelor of Social
  Work, Bachelor of Social Sciences.
- Education (1): BEd in Foundation Phase Teaching.

Left out: the old Diploma in Hospitality Management (its page says it was phased out at the end of 2023 and new students
take the Revised Curriculum, which is the one in the pack), advanced diplomas, postgraduate programmes, and the NC(V)
and RPL routes.

Selective: none. No page adds a test, interview, portfolio or audition. The LLB page says "There are no special
selection criteria beyond the minimum admission requirements"; its monthly selection (offers, a waiting list, half
the places kept for learners still in matric) is in extras.

Points: every `min_points` is on the pack's university rule (seven subjects, Life Orientation at half). No programme
has its own `points_rules`.

## Approximations

- **BEd:** the subject table asks for the "language of teaching and learning" at 5 and "another recognised language"
  at 4. The pack checks English 5 and `other_language` 4, and an extras line says so. Group B, three subjects at 4, is
  `additional_minimums: [4, 4, 4]`.
- **"Second language"** (BAdmin, BA in Media) and **"Additional Language"** (LLB) are read as `other_language`.
- **"Agriculture"** (Plant Production, Animal Production) is read as Agricultural Sciences.
- **"Two of" rules** (BSc, BSc in Agriculture, BSc in Forestry) are written as every pair of the subjects named.
- **BAgric Extension:** the page gives 28 points with Mathematical Literacy but no level. The pack uses level 6 from
  the leaflet (p6), and an extras line says so.
- **Higher Certificate in Event Management:** the page names Technical Mathematics without a level. The pack uses level
  4 from the leaflet (p2), and says so. "Any three additional vocational subjects: level 2" is
  `additional_minimums: [2, 2, 2]`, with UMP's words in extras.
- **Diploma in Entrepreneurship:** "any of the commerce subjects, such as Business Studies, Economics, Accounting,
  Tourism, among others" is a choice of those four, and extras quotes UMP.
- **Bachelor of Development Studies:** Geography or History at 4 is checked; "one other social or commercial sciences
  subject at level 4" is in extras only.
- **"English Home Language" level 4** (Diplomas in Culinary Arts, Hospitality Management, ICT in Applications
  Development): the pack checks English, home or first additional, at 4, and an extras line asks learners with English
  as a first additional language to check with UMP. The leaflet said "Home or First Additional" for two of them.
- The type of pass (bachelor's, diploma, higher certificate) isn't checked, as in the other packs.

## Check first

1. **Diploma in Hospitality Management (Revised Curriculum):** its admission section starts "The minimum admission
   requirements for the Diploma in Culinary Arts are as follows" and gives 26 points (27 with Mathematical Literacy),
   word for word the Culinary Arts page. The leaflet gave 24 (25). The pack uses 26 and 27, and extras tells the
   learner about the difference.
2. **The year:** no page says which intake it describes, and no 2027 prospectus was found. Seven pages differ from the
   2023 leaflet, so the pages have been updated since, but not necessarily for 2027.
3. **How points are counted:** only the BEd page says how (seven subjects, Life Orientation halved: the pack's
   university rule). The other 22 pages give a minimum APS without the method, and the pack counts them all the same
   way. Ask UMP whether every faculty does.
4. **Bachelor of Social Sciences:** does it take first-years in 2027, and with what requirements?
5. **Diploma in Entrepreneurship and Diploma in Culinary Arts:** both have pages with requirements, but neither is
   named in the 2026 Fees Handbook (its Hospitality Management entry, p14, has a second, unnamed set of fees). Check
   that both take 2027 applications.
6. **BEd:** that UMP's "language of teaching and learning" means English.
7. **Where the pages and the 2023 leaflet differ** (the pack follows the pages):
   - BSc in Agriculture: 32 points, two of Physical Sciences, Life Sciences, Agricultural Sciences or Geography at 4
     (leaflet: 30 points; Life Sciences or Agriculture 4, Physical Sciences 4 and another relevant subject 4).
   - BAgric Extension: one of Physical, Life or Agricultural Sciences at 4, and Life Orientation 4 (leaflet:
     Agriculture or Life Science 4 and Physical Science 4, no Life Orientation).
   - BSc: two of Life Sciences, Physical Sciences or Geography at 4 (leaflet: one).
   - BSc in Environmental Science: Geography 4 plus Life Sciences or Physical Sciences 4 (leaflet: any two of the
     three).
   - Diploma in Nature Conservation: 28 points, Mathematical Literacy 4, Life Sciences 4 required (leaflet: 30 points,
     Mathematical Literacy 3, Life Sciences and Geography recommended).
   - Diploma in ICT in Applications Development: Mathematics or Technical Mathematics 3, or Mathematical Literacy 6
     (leaflet: Mathematics 4).
   - Diploma in Hospitality Management: see 1.

   The other 13 programmes in the leaflet agree with their pages, which sometimes add a detail (the BSW's police
   clearance, the BEd's subject table). The leaflet doesn't have Culinary Arts, Entrepreneurship, the BA in Media,
   Communication and Culture, or the Bachelor of Social Sciences.
