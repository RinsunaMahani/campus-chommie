# Vaal University of Technology (VUT): programme research notes

Agent draft, read from VUT's own website and documents on 13 and 14 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/vut.yaml` keeps `release: false` until a person has compared every one with its source.

## What I read

| Id in the pack | Document | Pages used |
|---|---|---|
| s-vut-requirements | [2027 Undergraduate Minimum Admission Requirements](https://vut.ac.za/wp-content/uploads/2026/03/2027-Undergraduate-Minimum-Admission-Requirements.pdf), a two-page poster | p1: Applied and Computer Sciences, Management Sciences. p2: Human Sciences, Engineering and Technology (Tables 1 to 4) |
| s-vut-facs-prospectus-2026 | [Faculty of Applied and Computer Sciences Prospectus 2026](https://vut.ac.za/wp-content/uploads/2026/01/Faculty-of-Applied-and-Computer-Sciences-Prospectus-info-2026.pdf) | PDF p10, 16, 18, 24-25, 30, 34, 40 (printed page numbers are one lower) |
| s-vut-fhs-prospectus-2026 | [Faculty of Human Sciences Prospectus](https://vut.ac.za/wp-content/uploads/2026/03/Prospectus-Faculty-of-Human-Sciences-2025.pdf): the file is named 2025, its cover lists a 2026 edition | PDF p3, 7, 9, 32-34, 53-54, 60-62, 86-109 (printed one lower) |
| (names only) | [Faculty of Engineering and Technology Prospectus 2026](https://vut.ac.za/wp-content/uploads/2026/07/Prospectus-2026-FET-FINAL_18-June-2026.pdf) | PDF p3-4 (qualification names and codes), p20-24 (admission) |
| (names only) | [Faculty of Management Sciences Prospectus 2026](https://vut.ac.za/wp-content/uploads/2026/01/Faculty-of-Management-Sciences-Prospectus-info-2026.pdf) | PDF p2-3 (contents), p10, 15, 20, 24, 32, 38 |
| (cross-check) | VUT's four programme pages: [applied and computer sciences](https://vut.ac.za/applied-and-computer-sciences-programme/), [engineering](https://vut.ac.za/engineering-programmes-vaal-university-of-technology/), [human sciences](https://vut.ac.za/human-sciences-programmes-vaal-university-of-technology/), [management sciences](https://vut.ac.za/management-sciences-programmes-vaal-university-of-technology/) | the same values as the poster, except where listed under "Check" |
| (background) | [2025 General Prospectus](https://vut.ac.za/wp-content/uploads/2026/01/2025-GENERAL-PROSPECTUS.pdf) | PDF p10: departments select on merit, and selection "may include interviews, selection and/or placement tests" |

Nothing was blocked: every page and PDF downloaded with curl. I didn't open the application portal.

The poster's text extracts cleanly, but page 2 is laid out in boxes and the extracted text puts some boxes under the
wrong heading (Safety Management and Policing, Public Relations and Tourism). I rendered both pages as images to match
each box to its programme, then checked every box against VUT's faculty web pages, which give one slide per programme.

## The programmes

49 programmes, all with requirements; none has `requirements: null`. Faculty prospectuses list the same first
qualifications as the poster, so nothing is missing from it.

- Applied and Computer Sciences (8): Analytical Chemistry, Agricultural Management, Biotechnology, Environmental
  Science, Non-Destructive Testing, Information Technology and its extended programme; BHSc Medical Laboratory Science.
- Management Sciences (8): Cost and Management Accounting, Financial Information Systems, Internal Auditing, Human
  Resource Management, Logistics, Marketing, Retail Business Management, Sport Management.
- Human Sciences (14): Fashion, Fine Art, Graphic Design, Photography, Food Service Management, Public Relations
  Management, Tourism Management, Ecotourism Management, Legal Assistance, Labour Law, Safety Management, Policing;
  BEd in Senior Phase and FET Teaching; Bachelor of Communication Studies.
- Engineering and Technology (19): nine engineering diplomas (Chemical, Civil, Industrial, Mechanical, Metallurgical,
  and Electrical Engineering in Computer Systems, Electronic, Power and Process Control), the same nine as 4-year
  extended programmes, and Operations Management.

Left out: advanced and postgraduate diplomas, and the routes for NC(V), N3 to N6 and mature-age applicants.

Selective (6): the four Visual Arts diplomas (practical interview and portfolio, on the poster), Medical Laboratory
Science (job shadowing and placement testing, on the poster), and Communication Studies (an interview, in the faculty
prospectus, PDF p54).

## Approximations

- **BEd:** the poster asks for "Language of Teaching & Learning 4". The faculty prospectus (PDF p9) names English, so
  the pack has English 4 and says so in extras.
- **Agricultural Management:** "Agriculture/Life Science 3/3" is read as Agricultural Sciences or Life Sciences at 3.
  An extras line asks learners with another agriculture subject to check with VUT.
- **"Other Language" and "Additional Language"** are read as `other_language` (Public Relations, Legal Assistance,
  Labour Law, Policing, Communication Studies).
- **Food Service Management:** VUT's list for the other subject also names Hotel and Catering, which aren't NSC
  subjects; the choice holds the five NSC ones and extras gives VUT's full list.
- **"One other subject 4"** (HR, Logistics, Marketing, Retail, Sport) is `additional_minimums: [4]`.
- **Analytical Chemistry:** "Any other 3 subjects 9" is in extras only; the schema can't hold a total for some subjects.
- **Engineering:** the NSC tables name Mathematics and Physical Sciences only. Table 4, for NC(V) applicants, also
  names Technical Mathematics, and Technical Sciences for Electrical Engineering; the mainstream diplomas say so in
  extras and ask the learner to check with VUT.

## Check (documents disagree, or the app can't count it)

1. **Internal Auditing:** Mathematical Literacy 6 and 23 points on the poster and in the 2026 faculty prospectus
   (PDF p15); the web page shows 5. The pack uses 6.
2. **Extended Operations Management:** the engineering web page's extended table lists it; the poster and the 2026
   prospectus list only the nine engineering diplomas. Not added.
3. **Names:** the poster says "Logistics and Supply Chain Management" and "Human Resources Management"; the 2026
   faculty prospectus says "Diploma in Logistics" and "Human Resource Management". The pack uses the prospectus names.
4. **Older values in the faculty prospectuses** differ from the 2027 poster (the pack follows the poster): Analytical
   Chemistry also accepted Technical Science; Safety Management gave 21 points either way; the BEd text says 23 or 26
   points while its own table says 22 or 24.
5. **Points below 30%:** the engineering prospectus (PDF p21) gives 0 points for a subject under 30%; the human
   sciences prospectus (PDF p7) gives 1, as the pack does. The points rule is unchanged; a person should decide
   (`count_from_level: 2` would give 0).
6. **Bonus points aren't counted.** The 2026 prospectuses add up to 2 points for Visual Arts (Mathematics, Physical
   Science, EGD or Art, when 21 or 22 isn't reached), and points for Mathematics and Physical Sciences at level 5 or
   more in Analytical Chemistry and Biotechnology. For engineering they're used only to rank applicants. The app may
   show some learners 1 or 2 points short of what VUT would count.
7. **Testing band:** the human sciences prospectus says applicants "meet the minimum APS or fall within the testing
   band", without giving the band.

## What a person should check first

1. The page-2 boxes on the poster against the pack (Human Sciences especially), since the text came out of order.
2. Whether NSC learners with Technical Mathematics or Technical Sciences can enter the engineering diplomas.
3. The Logistics name and the Internal Auditing Mathematical Literacy level.
4. Points under 30%, and whether bonus points count towards the minimum anywhere.
