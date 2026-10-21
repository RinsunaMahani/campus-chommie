# Walter Sisulu University (WSU): programme research notes

Agent draft, 13 and 14 Oct 2026. Nobody has checked these values yet: `backend/data/universities/wsu.yaml` keeps
`release: false` until a person has compared every programme with the brochure.

## What I read

- **WSU's 2027 Undergraduate Information Brochure & Admission Requirements** (28 pages, uploaded 27 May 2026 going by
  its address): <https://wsu.ac.za/media/attachments/2026/05/27/2027-information-brochure-admission-requirements.pdf>.
  Source id `s-wsu-brochure-2027`. It is the 2027 intake's own document. I read its text extract (made 13 Oct 2026),
  downloaded my own copy at 00:00 on 14 Oct (byte-identical, SHA-256 `02aefaa8...646c86d`), and looked at pictures of
  pages 4, 5, 7, 9, 10, 13, 14, 17, 20, 21, 23 and 26 to 28 to check which cell of each table belongs to which row.
  - Page 3: general rules (a diploma needs a diploma endorsement, a degree a bachelor's endorsement). Not modelled.
  - Pages 4 and 5: the APS (already in the pack). Page 5's worked example: for the BEd in Foundation Phase Teaching,
    Life Orientation counts too, "to make 7 subjects in total".
  - Pages 6 and 7 Economic and Financial Sciences; 8 to 10 Education; 11 to 14 Engineering, Built Environment and IT;
    15 to 17 Law, Humanities and Social Sciences; 18 to 21 Management and Public Administration Sciences; 22 and 23
    Medicine and Health Sciences; 24 to 28 Natural Sciences.
- Nothing was blocked. I didn't read the faculty prospectuses the brochure points to (Health Sciences selection
  criteria; rules for the old Senior Certificate, NC(V) and international results).

## What's in the pack

105 programmes, every one with requirements (none `null`): Economic and Financial Sciences 9, Education 10,
Engineering, Built Environment and IT 16, Law, Humanities and Social Sciences 21, Management and Public Administration
Sciences 21, Medicine and Health Sciences 5, Natural Sciences 23. Each extended curriculum programme (ECP) is its own
programme, as WSU gives each its own code.

Left out: advanced diplomas and postgraduate programmes. The Bachelor of Social Sciences row also names codes W66005
and W66006, which the faculty's list of qualifications doesn't name; the pack has the 14 named streams instead.

## Approximations (each has a comment in the pack, and extras tell the learner)

1. **Education counts seven subjects.** Page 5 says so for Foundation Phase. For the Senior Phase and FET programmes I
   followed the faculty-wide rule we already had (the pack's points note): six of their nine requirement lists (with
   the Creative Arts English ECP) name seven subjects whose minimums add up to the APS asked (Creative Arts History:
   4+4+4+4+8 = 24); the other three name six. So each
   Education programme has its own `points_rules` (WSU's scale, seven subjects, Life Orientation counted), and an
   extras line says so. Without it the app would count six subjects and compare them with a seven-subject minimum.
2. **"Any other N subjects totalling X APS"** (all Education programmes) is only in extras: the app can't check it.
3. **Named languages.** "Any other African language", "isiXhosa" and "isiXhosa or Sesotho" are checked as the learner's
   other language, with the exact rule in extras (as TUT's pack does). The app can't tell which language it is.
4. **"Any other language"** (Versatile Broadcasting, Journalism, Public Relations and its ECP) isn't a subject the app
   knows, so it counts among the additional subjects (three at the level asked), with the rule in extras.
5. **ECPs that take "one level below in ONE subject"** (Building Technology, Civil, Electrical, Mechanical, the four ICT
   diplomas) list every way of doing that as options. Building Technology's text says both "a rating of 3" and "one
   level below", which differ for Technical Mathematics (asked at 5) and Physical Sciences (asked at 3): I used the
   stricter reading (Technical Mathematics 4; Physical Sciences not lowered).
6. **"Two technical subjects from the list"** (BEd Technical and Vocational Education): all 28 pairs of WSU's eight
   subjects. **"3 for two majors and 4 for the third"** (BSc ECPs): the three ways.
7. **A level and a percentage that disagree**: I check the level both readings share and an extras line says to ask
   WSU. BA (English): English "5 (50-59%)", checked at 4. Diploma in Consumer Science: Physical Sciences "4 (40-49%)",
   checked at 3 (its ECP asks 3 and is "as for main-stream"). Diploma in Pest Management: Physical Sciences
   "3 (30-39%)", checked at 2.
8. **Analytical Chemistry ECP** lists English at 3 but also says "as for main-stream" (English 4): I used the 3 listed.
9. **Psychology and Social Work** say "an achievement in any two subjects as follows". Psychology: any two of English,
   an African language and Life Sciences at 4. Social Work lists four lines under that heading (the last is "any other
   three subjects"), so I read it as any two of English 4, an African language 5 and Life Sciences 4, plus three other
   subjects at 4. The app may count the African language as one of the three, which WSU wouldn't.
10. **Environmental Studies** accepts "Agriculture": read as Agricultural Sciences. Its ECP gives no English minimum.
11. **"Three relevant school subjects"** (Hospitality, Tourism): checked as any three at level 3.
12. **Selective**: Fashion and Fine Art (an evaluation confirms final placement) and the five Health Sciences
    programmes ("additional selection criteria"). The Creative Arts BEds audition only applicants without Music, so
    they aren't marked selective; extras say it.

Small slips in the brochure, noted in the pack: the Local Government Finance row says "one of the three options" but
lists two; page 23 labels the MBChB row W65005 (page 22 gives W65006); the BEd Creative Arts English ECP (W62023) is
on page 9 but not in page 8's list.

## Check first

1. Whether every Education programme counts seven subjects (item 1). If the Senior Phase and FET programmes count six,
   delete their `points_rules`.
2. Psychology and Social Work (item 9).
3. The level and percentage disagreements (items 7 and 8) and Building Technology's ECP (item 5).
4. The schema has no campus per programme: WSU's four campuses are far apart, and the brochure's tables say where each
   programme runs, if the app wants to show it.
