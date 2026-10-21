# University of the Free State (UFS): programme research notes

Agent draft, 14 Oct 2026. Nobody has checked these values yet: `backend/data/universities/ufs.yaml` keeps
`release: false` until a person has compared every programme with its source.

## What I read

All from UFS's own site, www.ufs.ac.za, which has no robots.txt (it answers 404), so nothing there is disallowed.
UFS serves curl's own user agent. Page numbers are the printed ones unless I say "PDF page".

- **Undergraduate Prospectus 2027** (`s-ufs-prospectus-2027`), the 2027 intake's own document, linked from
  <https://www.ufs.ac.za/prospective>:
  <https://www.ufs.ac.za/docs/librariesprovider44/undergraduate/ufs---ug-prospectus-2027---jan.pdf?sfvrsn=f3a0f820_1>
  (51 PDF pages of two-page spreads, SHA-256 `8d1cd39f...0cca13b4`). I read the text extract and looked at pictures of
  pages 14 to 39 to check which cell belongs to which row.
  - Page 10: extended curriculum programmes (ECPs): you apply for the mainstream programme and are placed if space allows.
  - Page 11: general notes (English 4 unless stated; non-selection programmes close 30 Sep 2026).
  - Pages 14 and 15 Economic and Management Sciences; 16 and 17 Education; 18 and 19 Health Sciences; 20 Law;
    21 to 33 Natural and Agricultural Sciences; 34 to 38 the Humanities; 39 Theology and Religion.
  - Page 48: two study choices per application; a selection programme must be your first choice. Page 50: the AP (six
    subjects, nothing under 30%, Life Orientation 1 point from 60%); page 51: the closing dates. Page 65: the 2027 fee table,
    which names the extended BCom, BAdmin, BEd, BSc, BA, BSocSci and BDiv.
- **Health Sciences selection documents**, from <https://www.ufs.ac.za/healthselection>: the 2027 MBChB selection rules
  (already in the pack as `s-ufs-rules`), the 2027 BMedSc (Radiation Science) selection rules (`s-ufs-bmedsc-rules-2027`),
  the School of Health and Rehabilitation Sciences selection policy for the 2026 intake (`s-ufs-shrs-policy`, pages 4
  and 5: which programmes take Life Sciences "and/or" Physical Sciences) and the Bachelor of Nursing selection policy
  (`s-ufs-nursing-policy`, amended March 2025).
- **2026 faculty rule books**, the newest published (no 2027 rule books yet), for the ECPs the prospectus doesn't detail:
  Economic and Management Sciences (`s-ufs-rb-ems-2026`, pages 8 and 9), Education (`s-ufs-rb-edu-2026`, pages 26 and
  27), Law (`s-ufs-rb-law-2026`, rule E1.3, PDF page 9), Natural and Agricultural Sciences (`s-ufs-rb-nas-2026`, NAS 2.1
  and 2.2 on pages 21 to 27, section 12.2 on pages 63 to 65), the Humanities (`s-ufs-rb-hum-2026`, PDF pages 49, 61, 73,
  83, 122, 133, 155 and 171) and Theology and Religion (`s-ufs-rb-theo-2026`, PDF page 14).

Not used: UFS's "check what you qualify for" link redirects to gostudy.net, an aggregator whose robots.txt disallows all
agents, and the "undergraduate" link redirects to a Vimeo video, whose robots.txt disallows ClaudeBot. curl followed both
redirects once before I checked; I read neither and deleted both copies. Nothing else was blocked. A 2025
opening-and-closing-dates PDF on UFS's site is out of date (2026 intake).

## What's in the pack

172 programmes, 170 with requirements:

- **From the 2027 prospectus: 152.** Economic and Management Sciences 13, Education 25, Health Sciences 9, Law 1, Natural
  and Agricultural Sciences 86 (Bloemfontein 76, Qwaqwa 10), the Humanities 17, Theology 1.
- **Extended curriculum programmes from the 2026 rule books: 20.** BCom, BCom (Accounting), BCom Management (Qwaqwa),
  BAdmin; the five-year LLB; BAgric, BSc in Agriculture, two BSc groups, Qwaqwa IT, BCIS, Sustainable Food Systems; BA,
  BA (Language Practice), BA (Drama), BA (Fine Arts), BA (Governance), BSocSci; BDiv; and the BEd.

`requirements: null` (2): the **extended BEd** (the fee table names it, but neither the prospectus nor the 2026 Education
rule book gives requirements) and the **extended Bachelor of Sustainable Food Systems** (the 2026 rule book gives
Mathematics 3 in NAS 2.2(d) but Mathematics 2 or Mathematical Literacy 5 in section 12.2).

Left out: the Advanced Diplomas in Music and Opera Studies (they need a Diploma in Music first); Construction Management
and Quantity Surveying by Compact Learning (only for people 22 or older employed in construction); the Higher
Certificate in Theology (no new students from 2026); short learning programmes; postgraduate study; the BSc ECP variants
"Mathematics and Chemistry" and "Mathematics and Finances", which the NAS rule book lists without admission rules.

## Approximations (each has an extras line or a selection note in the pack)

1. **One entry per prospectus row**, as UFS gives each row its own plan code and minimums. You apply for the academic
   programme (for example B4310, Biological Sciences) and choose majors, so the 25 Biological Sciences majors (identical
   minimums) are 25 entries; extras say how to apply. Rows that cover two campuses are one entry, with both in the name.
2. **Named home languages** (Afrikaans, Sesotho, isiZulu) for the BEd specialisations are checked as your other language
   at level 4, with the exact rule in extras. The app can't tell English home language from first additional language.
3. **English at 60% (home) or 65% (additional)** for Journalism, Integrated Organisational Communication, Drama and
   Language Practice is checked as English 5; a first-additional-language learner with 60% to 64% passes the app's check
   but not UFS's. The prospectus writes "Level 6 (60%)" for Journalism and IOC; 60% is level 5.
4. **Health "and/or".** The prospectus marks Dietetics, Occupational Therapy and Biokinetics with an asterisk and the note
   "Life Sciences and/or Physical Sciences are required"; the SHRS policy says "and/or" for exactly these three. So they
   take either science; Physiotherapy and Optometry need both, as in both documents.
5. **Sport Coaching** checks only AP 30 and English 4: the SHRS policy calls its Mathematics and science levels
   recommendations.
6. **BAdmin** checks Mathematics 2, as the prospectus does; the 2026 EMS rule book also accepts Mathematical Literacy 5.
7. **Music** programmes check AP and English; the external grades (Unisa, ABRSM, Trinity) and auditions are in the
   selection notes, and the programmes are marked selective.
8. **ECP AP ranges** ("24 to 27", "25 to 29") are entered as minimums, with the range in extras: the app will also say
   a learner with more meets them. The rule books' rules are 2026's, said so in each programme's extras.
9. **NAS ECPs**: the rule book's admission rules (NAS 2.2) are checked; where its own ECP table (12.2) differs, extras say
   so. Its slip "Physical Science at performance level 3 (50%)" is read as level 3.
10. **Geology** is marked selective from the 2026 rule book (NAS 2.1(b): selection, at most 80 first-years); the 2027
    prospectus only says admission depends on space and results.
11. **Mathematical Sciences**: the prospectus asks Physical Sciences 5 for all four majors; the 2026 rule book asks it
    only when Chemistry, Physics or Agrometeorology is the second major. I used the prospectus.
12. **Education's AP**: the 2026 Education rule book counts only listed subjects (Computer Applications Technology,
    Tourism and Hospitality Studies aren't listed). Not modelled as a points rule (the 2027 prospectus doesn't say it);
    an extras line warns.
13. **Points rule unchanged.** The prospectus (page 50) states the same scale and Life Orientation rule as the pack; no
    programme states a different count, so no programme has its own `points_rules`.
14. **A bridge**: Econometrics to Actuarial Science ("considered"): the prospectus says a third-year Actuarial Science
    space will be made for Econometrics students who excel in their first two years.

## Check first

1. **The 20 extended programmes**: whether UFS runs them in 2027 with the 2026 rules, and whether the app should list
   programmes you reach by placement rather than application.
2. The Health "and/or" reading (item 4) and BAdmin with Mathematical Literacy (item 6).
3. Mathematical Sciences and Physical Sciences 5 (item 11); Geology as selective (item 10).
4. Whether 25 near-identical Biological Sciences entries suit the app, or one entry per academic programme would.

## Also found (outside this brief)

For whoever fills `applications` and `max_choices` (prospectus pages 48 and 51): applications for 2027 opened 1 April
2026; closing dates were 31 May 2026 (MBChB, Occupational Therapy, Optometry, Physiotherapy, Radiation Sciences,
Biokinetics, Dietetics, Sport Coaching), 31 July (Nursing, Social Work, Architecture), 31 August (international
applicants) and 30 September (every non-selection programme and the remaining selection programmes); two study choices
per application.
