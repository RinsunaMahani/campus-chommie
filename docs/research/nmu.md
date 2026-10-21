# Nelson Mandela University (NMU): programme research notes

Agent draft, read and written up 15 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/nmu.yaml` keeps `release: false` until a person has compared every programme with its
source.

## Hosts and robots.txt

| Host | robots.txt | Used? |
|---|---|---|
| `www.mandela.ac.za` | `User-agent: *` disallows only `/websurvey/`, `/continuingeducation/media/SecureStore` and `/splan/media/SecureStore`. Nothing about ClaudeBot, Claude-User or anthropic-ai | Yes: every figure in the pack comes from here |
| `myfuture.mandela.ac.za` | The same three lines | Read the home page, the Applicant Score page and "Applying to Nelson Mandela University" for links only |

All fetches used curl's own user agent. Nothing was blocked, and no link redirected to another host.

## What I read

- **2027 Nelson Mandela University Undergraduate Guide** (`s-nmu-ug-guide-2027`),
  <https://www.mandela.ac.za/getmedia/c574ec69-1adc-42c0-9075-04525b58202e/MandelaUni-Undergraduate-Guide>, linked as
  "2027 Nelson Mandela University Undergraduate Guide" from
  <https://www.mandela.ac.za/Study-at-Mandela/Discovery/Quick-guides>. 138 pages. It says it was "correct as of April
  2026" (page 8). Every programme cites it. Pages used: 8 to 12 (admission rules, the Applicant Score, extended
  programmes), 18 and 19 (qualification list), 22 to 43 (Business and Economic Sciences), 46 to 49 (Education), 54 to
  73 (Engineering, the Built Environment and Technology), 76 to 87 (Health Sciences), 90 to 103 (Humanities), 106 to
  109 (Law), 112 to 119 (Science), 122 to 133 (George Campus). Each programme in the pack has a `# page` comment.
- **The seven 2027 faculty UG guides and the 2027 George Campus UG guide** (same Quick guides page). Downloaded; they
  carry the same programme tables as the main guide's faculty sections (the Business guide also has the George
  Campus business programmes). A rough check found no AS figure in them that isn't in the main guide, but I didn't
  compare them line by line. I cited the main guide only.
- **Z Card 2027** (same page, a two-page careers-to-qualifications fold-out). I only looked at its list of names to
  check nothing was missing; I didn't compare its figures systematically, and nothing in the pack comes from it.
  Its columns run Mathematics, Mathematical Literacy, Technical Mathematics, a different order from the guide.
- **Qualifications browser** (<https://www.mandela.ac.za/Study-at-Mandela/Discovery/Qualifications>): an ASP.NET
  form that lists programmes only after a postback. I didn't use it; the guide covers the same list.

## How the pack reads NMU's tables

- **Applicant Score (AS).** NMU publishes three AS minimums per programme: with Mathematics, with Technical
  Mathematics and with Mathematical Literacy ("–" where that subject isn't accepted). The pack keeps NMU's rule (six
  subjects' percentages, out of 600, without Life Orientation). `min_points` is the lowest of the three; the other
  routes are options in a Mathematics choice with their own `min_points`. Every such programme has an extras line
  "Applicant Score needed: ...". Where only Mathematics is accepted, the minimum is a `subject_min_percents` figure and
  an extras line says the other two aren't accepted.
- **No subject minimum but different AS.** Music, Visual Art and the two Law Enforcement qualifications set no
  Mathematics mark but still have three AS figures. Their Mathematics choice uses level 1 (any mark), so the right AS
  applies; an extras line says NMU sets no minimum mark.
- **Every requirement has a published AS**, so no programme has `min_points: null` and none has `requirements: null`.

## Approximations

1. **Percentages in either/or rules (32 programmes).** NMU states percentages; the schema's choices only take NSC
   levels. Where NMU's figure is a multiple of ten (30, 40, 50, 60, 70) the level is exact. Where it isn't (35%, 45%,
   55%, 65%, 75%) the option uses the level that contains it (for example 45% is level 3, from 40%), so the app is
   up to 5 points too generous. Each of these programmes has the exact rule and a line saying the app checks from the
   lower figure. Single-subject minimums (for example "Mathematics 65%") are exact `subject_min_percents`.
2. **English Home Language or First Additional Language** (Law, BCom Accounting Science (Law)): `english` at the Home
   Language figure, the lower one, with the full rule in extras.
3. **BEd: "Afrikaans or isiXhosa at 50%".** Entered as `other_language: 50`, with an extras line saying it must be
   Afrikaans or isiXhosa. A learner whose other language is, say, Sesotho will wrongly pass this check.
4. **BA, BA (Media, Communication and Culture), BA (Politics and Economics): "60% in any NSC language"** is an extras
   line only, as the brief asks for "any language".
5. **One entry for several streams.** Bachelor of Visual Art (streams chosen after a generic first year),
   BSc (Computer Science) (five curricula, all 410 and Mathematics 65%), the George Campus BCom General (three pairs of
   majors) and the BA, which the guide describes twice (pages 99 and 102) with the same requirements.
6. **Programmes on both campuses** are listed once with "Also offered on the George Campus". The George Diploma in
   Agricultural Management adds departmental selection (page 122); that's an extras line, and the programme isn't
   marked selective because Gqeberha doesn't add it.
7. **Selective** (28 programmes): where NMU adds an audition, portfolio, interview, departmental selection or limited
   places it calls a selection on merit. The general line on page 8 that "places are limited" isn't counted.

## Left out (not first qualifications a school-leaver can apply for)

- All advanced diplomas, both PGCEs and the Advanced Diploma in Technical and Vocational Teaching.
- Diploma in Operations Management (page 55): part-time only, applicants must be in full-time employment in a
  related field.
- Higher Certificate in Human Settlement Development (page 67): applicants must have worked at least a year in the field.

## Check first

1. **BPharm language rule (page 85).** "NSC achievement rating of at least 50% for Home language or English First
   Additional Language" (the Z Card says "Home language or language of instruction"). It's unclear which home
   language counts, so the pack doesn't check it; the extras line quotes NMU. Ask NMU or read the Health Sciences
   prospectus.
2. **Closing dates.** The pack's application window (from the closing dates page, 13 Oct) says Nursing also closed
   on 30 June 2026. The guide (pages 8 and 10) names only MBChB, BPharm and Radiography for 30 June. I didn't change
   the window; a person should check which is right.
3. **The 32 approximated either/or minimums** (see Approximations 1).
4. **BEd Humanities** (page 48): Mathematics 45%, but 60% if Geography is chosen as a specialisation, and then
   Technical Mathematics and Mathematical Literacy aren't accepted. The pack checks the 45% rule; the Geography rule
   is an extras line.
5. **Pages 108 and 109** repeat some text in the PDF's text layer (the BCom (Law) and LLB columns appear twice). The
   LLB figures read the same in both copies; worth a look at the printed page.
6. **Quintile bonus.** Learners from quintile 1 to 3 schools with 50% or more in Life Orientation get 7 more AS points
   (page 9). The pack's points rule doesn't add them (already noted in its `points_rules.note`).
7. **Spot-check AS figures against the Z Card** for a few programmes; I didn't do it systematically.
