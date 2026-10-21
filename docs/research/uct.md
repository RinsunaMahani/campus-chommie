# University of Cape Town (UCT): programme research notes

Agent draft, read and written up 15 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/uct.yaml` keeps `release: false` until a person has compared every programme with its
source.

## Hosts and robots.txt

| Host | robots.txt | Used? |
|---|---|---|
| uct.ac.za | `User-agent: *` disallows only Drupal admin, search, login and oembed paths. It blocks GPTBot, Yandex, ByteDance and FriendlyCrawler completely; nothing about ClaudeBot, Claude-User or anthropic-ai | Yes: every figure in the pack comes from here |
| commerce, ebe, health, humanities, law, science (`.uct.ac.za`) | Same file as uct.ac.za apart from the sitemap line | Read their robots.txt only; no pages were needed |

All fetches used curl's own user agent, one document at a time with a pause. Nothing was blocked.

## What I read

- **2027 Undergraduate Prospectus** (`s-uct-prospectus-2027`),
  <https://uct.ac.za/sites/default/files/media/documents/2027-uct-undergraduate-prospectus-1-april-2026.pdf>,
  linked as "Download the 2027 Undergraduate Prospectus" from
  <https://uct.ac.za/students/prospective-students/undergraduate-prospectus>. 89 pages. Every programme cites it.
  Pages used: 15 to 17 (APS, FPS and WPS), 19 to 22 (NBTs), 23 to 31 (Commerce), 32 to 38 (Engineering & the Built
  Environment), 39 to 47 (Health Sciences, places on page 41), 48 to 58 (Humanities), 59 to 63 (Law), 64 to 70 (Science).
- **2027 Guidelines for admission for holders of the NSC**,
  <https://uct.ac.za/sites/default/files/media/documents/2027-national-senior-certificate-nsc-guidelines-for-admissions.pdf>
  (linked from the NSC requirements page). The same band tables as the prospectus. I used it to check the prospectus,
  not as a cited source; the only difference I used is its "NSC Music 60% or equivalent" for the BMus, quoted in that
  programme's extras.
- **2027 directions for undergraduate applicants** (already `s-uct-directions`), pages 14 to 21: the qualification
  and specialisation codes you apply under (Table A). The programme list follows these codes. It also gives: Commerce's
  four application codes and the automatic fallback from Actuarial Science, BA and BSocSc counting as one qualification,
  the BMus and Geomatics streams, and the BSW limit of 80. Extras that use it say so in words.
- The six "Degrees & diplomas: undergraduate" pages under `uct.ac.za/students/study-uct-degrees-diplomas-*`, to see
  if anything was missing. The Humanities one is out of date (it still lists ACE programmes and a Teacher's Licentiate
  Diploma), and the Commerce one names some specialisations differently from the 2027 prospectus ("Analytics",
  "Finance", "Organisational Psychology"). I followed the 2027 prospectus.

## What's in the pack

34 programmes, all 34 with requirements; 14 marked selective.

- **Commerce 5**, one per application route: all specialisations other than Actuarial Science (Mathematics 60%);
  Computer Science or Statistics and Data Science (Mathematics 70%, chosen after Orientation under the same code);
  Actuarial Science, including Quantitative Finance (Mathematics 80%); and the two Academic Development Programme codes.
- **Engineering & the Built Environment 11**: BAS, Construction Studies, Property Studies, seven BSc (Eng) and Geomatics.
- **Health Sciences 6**: MBChB, Physiotherapy, Occupational Therapy, Audiology, Speech-Language Pathology, and the
  Higher Certificate in Disability Practice, each with its places (240, 70, 70, 37, 40, 30).
- **Humanities 9**: BA, BSocSc, BSocSc PPE, BSW, BA Fine Art, BA Theatre & Performance, BMus, Diploma in Music
  Performance, Diploma in Theatre & Performance.
- **Law 1**: the four-year LLB.
- **Science 2**: the BSc, and the BSc without Physical Sciences (majors restricted to Archaeology, or Environmental &
  Geographical Science, by the prospectus's Note 2).

Left out: the advanced diplomas (Accounting, Actuarial Science, Cosmetic Formulation Science, Adult and Community
Education and Training, Music, Opera, Theatre: all need a degree or diploma first); the Advanced Certificates in
teaching (reserved for WCED-sponsored applicants); the **Higher Certificate in Adult and Community Education and
Training** ("for those who have at least two-years practitioner experience"); the two- and three-year graduate LLB; the
BA specialising in Film and Media Production (selected in the second year of a BA, so it's a line in the BA's extras).
The extended programmes in Humanities, Engineering and Science have no application code of their own (students are
placed in them), so each is an extras line on its parent degree.

## Points and approximations

1. **No points rule.** `points_rules` stays null. UCT's FPS is a sum of percentages (out of 600, 800 for Science,
   900 with NBTs for Health Sciences), and its bands also use a Weighted Points Score that needs UCT's disadvantage
   factor, which the app can't know and must not ask about. Every programme has `min_points: null`; the FPS and WPS
   bands are extras lines, each saying where the counting rule comes from. With no rule, the engine shows every UCT
   programme as "can't check yet", as the brief expects.
2. **Percentages, not levels.** UCT states percentages, so the minimums are `subject_min_percents`. Either/or choices
   only take levels: 60% is exactly level 5 and 70% level 6, so "Mathematics 60% or Mathematical Literacy 70%" and
   "Physical Sciences or Information Technology 60%" are exact. "Physical Sciences or Life Sciences at 65%"
   (Physiotherapy, OT, Audiology, Speech-Language Pathology) is entered as level 5 (60%), with the 65% in extras.
3. **English HL or FAL.** "50% Home Language or 60% First Additional Language" is `english: 50` with the full rule in
   extras (Actuarial Science: 60% or 80%).
4. **The lowest band's subject minimum.** Where a band asks more (Construction Studies Physical Sciences 60% in Band A,
   55% in B and C; Chemical Engineering 75% and 70%; Geomatics 75/70% and 65/60%), the pack uses the B and C figure and
   puts the Band A figure in extras. B and C always asked the same.
5. **"Next three best subjects at 70% (or 60%)"** in Health Sciences is `additional_minimums: [6, 6, 6]` (or `[5, 5, 5]`).
6. **Life Orientation at 50%** is a minimum for every Humanities programme (prospectus page 54, "must be passed at 50%").
7. **Selective**: Health Sciences (the faculty says competition for places is significant), the LLB ("only the best
   applicants will be made an offer"), BAS (portfolio), Fine Art (portfolio), the audition programmes and the BSW
   (interview, 80 places). Commerce, Engineering, Science and the general BA and BSocSc have a guaranteed band, so
   they aren't marked selective.

## Check first

1. **Commerce Computer Science group.** The prospectus says "Computer Science & Statistics and Data Science
   Specialisation" needs Mathematics 70%. I took that to cover the BBusSc in Computer Science, the BBusSc in Statistics
   and Data Science and the BCom in Information Systems and Computer Science. The BCom IS and CS isn't named there.
2. **BMus Music subject.** The prospectus asks for "NSC Music 60% or above"; the NSC guidelines say "or equivalent".
   The pack makes Music 60% a minimum and quotes the guidelines in extras.
3. **Information Technology for the BSc.** The prospectus says IT may replace Physical Sciences for "the major
   combination of Computer Science and Business Computing only"; the guidelines say "for majors in Computer Science
   and Business Computing". The pack uses an either/or choice with that note.
4. **OT, Audiology and SLP NBT Mathematics.** The prospectus exempts Mathematical Literacy applicants "who have
   achieved more than 75%"; the guidelines exempt all Mathematical Literacy applicants. The pack follows the prospectus.
5. **Engineering Band C**: the prospectus says "targeted redress categories", the guidelines "categories 1 and 2". The
   pack says "UCT's redress categories" without naming them.
6. **`max_choices`** (not changed: outside the programmes): the 2027 directions and prospectus say you may choose two
   programmes, and Science applicants give two majors.
