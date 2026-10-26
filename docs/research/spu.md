# Sol Plaatje University (SPU): course list research notes

Agent draft, read on 14 Oct 2026 for `backend/data/universities/spu.yaml`. Nobody has checked these values yet:
release stays false until a person has compared each one with its source. Staff names, phone numbers and email
addresses in the prospectus and on the faculty pages are left out on purpose.

## What I read

| Source id | Document | Used for |
|---|---|---|
| s-spu-prospectus-2027 | [SPU 2027 Undergraduate Prospectus](https://indd.adobe.com/view/57eda609-9efc-43e8-b806-791d2e347328), 32 pages | 23 of the 26 programmes |
| s-spu-ems-programmes | [Faculty of Economic and Management Sciences: programmes](https://www.spu.ac.za/index.php/spu-economic-and-management-sciences/) | BCom in Tourism Management, Bachelor of Public Administration |
| s-spu-nas-programmes | [Faculty of Natural and Applied Sciences: programmes](https://www.spu.ac.za/index.php/spu-nas-programmes/) | the BSc stream codes; BSc Physical Sciences (Geology) |
| s-spu-hum-programmes | [Faculty of Humanities: programmes](https://www.spu.ac.za/index.php/faculty-of-hum-programmes/) | one extras line (Court Interpreting's Mathematics) |

Also read to compare, not cited by a programme: the [2026 prospectus PDF](https://www.spu.ac.za/wp-content/uploads/2025/04/2026-Undergraduate-Prospectus.pdf)
(s-spu-prospectus), the [admission requirements page](https://www.spu.ac.za/index.php/admission-requirements-2/)
(its APS table is an image: the same table), the [Education programmes page](https://www.spu.ac.za/index.php/faculty-of-edu-programmes/),
the [science STEM page](https://www.spu.ac.za/index.php/nas-stem-offering/), the [2026 factfile page](https://www.spu.ac.za/index.php/spu-factfile-2026/)
and the [how to apply page](https://www.spu.ac.za/index.php/how-to-apply/) (2027 applications open until 31 Oct 2026).

**How the 2027 prospectus was read.** SPU's site menu (Study@SPU, "2027 Prospectus") links to `https://bit.ly/42LY3gF`,
which passes through an email-security redirect to an Adobe "Publish Online" publication named "SPU 2027
Undergraduate Prospectus". It offers no PDF download and there is no copy on spu.ac.za. I read its text from the
viewer's own search file (`content.json`, next to the pages). Page numbers here are the viewer's; the printed page
numbers are two less (viewer page 7 is printed page 5). Pages: 2 and 3 the programme list; 4 the English rule and
the APS table; 7 to 9 Education; 13 to 16 Economic and Management Sciences; 18 to 20 Humanities; 22 to 28 Natural
and Applied Sciences. Some B.Ed. blocks on pages 7 and 8 have no heading of their own: I placed them from the
viewer's page files and stylesheet (their position on the page), and the 2026 PDF names the same seven with codes
(EDU720, EDU723, EDU724, EDU740 to EDU743).

**What I couldn't read.** SPU's application portal (applications-prod.spu.ac.za) is a sign-in app, so I didn't see
the list of programmes applicants can choose for 2027.

## Programmes (26, all with requirements)

Every programme asks English Home Language at level 4 or English First Additional Language at level 5 (prospectus
page 4), stored as `english: 4` with the full rule in extras.

| Id | Points | Subjects | Source, page |
|---|---|---|---|
| bed_foundation_phase | 30 | Afrikaans, Setswana or isiXhosa 4; Maths 3 or Maths Lit 4 | prospectus 7 |
| bed_intermediate_maths_science | 30 | Afrikaans, Setswana or isiXhosa 4; Maths 4, Physical Sciences 4, Life Sciences 4 | prospectus 7 |
| bed_intermediate_social_sciences | 30 | Afrikaans, Setswana or isiXhosa 4; Geography 4 or History 4 | prospectus 7 |
| bed_sp_fet_science_maths | 30 | Maths 4, Life Sciences 4 | prospectus 8 |
| bed_sp_fet_languages | 30 | Afrikaans or Setswana 4; History 4 if History is an elective | prospectus 8 |
| bed_sp_fet_history_geography | 30 | Afrikaans or Setswana 4; Geography 4 and History 4 | prospectus 8 |
| bed_sp_fet_commerce | 30 | any two of Accounting, Business Studies, Economics at 4 | prospectus 9 |
| hcert_entrepreneurship | 25 | Maths 3 or Maths Lit 4; Accounting, Business Studies or Economics 3 | prospectus 13 |
| dip_retail_business_management | 25 | Maths 3 or Maths Lit 5; Accounting, Business Studies or Economics 4 | prospectus 14 |
| bcom_accounting | 30 | Maths 5, or Maths 4 with Accounting 3 | prospectus 15 |
| bcom_economics | 30 | Maths 5, or Maths 4 with Economics or Business Studies 3 | prospectus 16 |
| bcom_tourism_management | 30 | Maths 3 or Maths Lit 5 | EMS page |
| b_public_administration | 30 | Maths 3 or Maths Lit 4 | EMS page |
| hcert_heritage_studies | 25 | Maths 2 or Maths Lit 3 | prospectus 18 |
| hcert_court_interpreting | 25 | another African language, home 4 or first additional 5 | prospectus 19 |
| ba | 30 | Maths 2 or Maths Lit 3; Geography 4 to major in it | prospectus 20 |
| dip_agriculture | 25 | Maths 3 or Maths Lit 5; Physical Sciences 3; Life Sciences or Agricultural Sciences 3 | prospectus 22 |
| dip_ict_applications_development | 25 | Maths 3 or Maths Lit 5 (CAT or IT recommended) | prospectus 24 |
| b_environmental_science | 30 | Maths 4, Physical Sciences 4, Life Sciences 4 | prospectus 26 |
| bsc_biological_sciences, bsc_mathematical_computer_sciences, bsc_chemistry, bsc_geography, bsc_physics | 30 | Maths 4, Physical Sciences 4, Life Sciences 4 | prospectus 27 |
| bsc_geology | 30 | Maths 4, Physical Sciences 4, Life Sciences 4 | NAS page |
| bsc_data_science | 30 | Maths 5 | prospectus 28 |

Left out, not for school-leavers: the Advanced Diplomas (Management; ICT in Applications Development; School
Leadership and Management), the PGCE, and honours and higher.

## Points

No points rule added, and `points_note` kept. The 2027 table (page 4) is the same as 2026's and the website's: 90-100%
= 8 down to 0-29% = 1; Mathematics and a language taken as a home language add 2 from 60% and 1 at 40-59%; Life
Orientation scores 4, 3, 2, 1 from 90, 80, 70 and 60%. Neither year says how many subjects count. No programme or
faculty says it counts differently, so no programme has its own points rule. Until there is a rule the app shows
every SPU programme as "can't check yet"; the minimums (25 and 30) are on SPU's own scale, bonuses included.

## Approximations

- **"One of Afrikaans, Setswana or isiXhosa at level 4"** (and "Afrikaans or Setswana", "another African language"):
  `other_language: 4` with an extras line naming the languages, as tut.yaml does. The app can't tell which language
  the learner's other language is. Court Interpreting wants level 5 for a first additional language: stored at 4,
  with the full rule in extras.
- **"Any two of Accounting, Business Studies and Economics at level 4"**: one choice with the three pairs.
- **History at level 4 "only if History will be selected as an elective"** (B.Ed. Senior and FET Phase: Languages):
  extras only.
- **The pass type** (bachelor's, diploma or higher certificate admission): extras only; the engine doesn't model it.
- **The BSc** is one degree with three sub-fields in the prospectus, with Chemistry, Geography and Physics under
  Physical Sciences (page 3). The science faculty's page gives each a code of its own (BSC707, BSC708, BSC763 to
  BSC766), so each is listed separately, with the same requirements.
- **Bridges**: page 20 says SPU's Higher Certificates in Heritage Studies and Court Interpreting "will be considered
  for entry" into the BA, with details from the Dean of Humanities. Both are bridges marked `considered`; no added
  years, as none are stated.

## Check first

1. **Three programmes aren't in the 2027 prospectus**: BCom in Tourism Management and Bachelor of Public
   Administration (EMS page) and BSc Physical Sciences (Geology) (science page). The 2026 factfile lists Geology
   under "Future Programmes". Each has an extras line asking the learner to check with SPU. Ask SPU whether they take
   first-years in 2027, and remove them if not.
2. **BCom in Economics**: the prospectus asks Mathematics 5, or Mathematics 4 with Economics or Business Studies 3;
   the EMS page says Mathematics 4 only. The pack follows the prospectus.
3. **Diploma in Retail Business Management**: the EMS page leaves out "at least one of Accounting, Business Studies
   or Economics at level 4". The pack follows the prospectus.
4. **Higher Certificate in Court Interpreting**: the Humanities page adds Mathematics 2 or Mathematical Literacy 3;
   the prospectus doesn't. Shown as an extras line only.
5. **BCom in Tourism Management**: its page asks English at level 4, home or first additional language; the
   prospectus asks every programme for level 5 in English First Additional Language. Both are in its extras.
6. **Points**: ask SPU how many subjects count, whether Mathematical Literacy gets the Mathematics bonus (the table
   says "Mathematics"), and what the Geology table's "additional subjects to contribute to minimum APS total" means.
7. **B.Ed. Senior and FET Phase: History, Social Sciences and Language** is on page 8 (and in 2026 as EDU742), but the
   programme list on page 3 names only three Senior and FET specialisations.
8. **The source address**: the 2027 prospectus is hosted by Adobe, not on spu.ac.za. Confirm it's the one SPU's menu
   links to, and switch to a spu.ac.za PDF if SPU posts one.
9. **Foundation Phase**: 2026 also had a 25-point route with an accredited level 5 ECD qualification; the 2027
   prospectus doesn't. It wasn't for school-leavers, so it's left out.
10. **Geology's English**: its table says "4 (Home Language)" or "5 (1st Language)", which I read as First Additional
    Language, as SPU's general rule says.

## Official APS image supplied on 26 October 2026

Rinsuna supplied `WhatsApp Image 2026-10-25 at 20.27.04.jpeg`, downloaded from the official SPU page.
SHA-256: `39728233b96277c6ab1ae8a72ebb19a755ad2874c6ad90f8d87d9376904c06fd`.
It matches the [image](https://www.spu.ac.za/wp-content/uploads/2018/11/SPU-Admission-calculator-295x300.png)
linked under “Calculating the SPU Admissions Points Score (APS)” on the
[official admissions page](https://www.spu.ac.za/index.php/admission-requirements-2/), checked on 26 October.
That page currently describes admission for 2026; the image does not carry a year.
The new dated official-university source backs `points_how`, not the separate Adobe prospectus's programme rules.

The image confirms the existing scale, Mathematics/Home Language bonuses and Life Orientation scores.
It does not state the number or selection of subjects to sum. The app now accepts optional language roles, so
that former input limitation is removed from the explanation. Total APS remains manual until the subject-count
rule is supported. Search results from third-party calculators are not used to fill the missing official rule.


## Seven-subject source exception accepted on 26 October 2026

Rinsuna supplied the [University Qualifications SPU calculator](https://universityqualifications.co.za/guest/aps/spu)
and explicitly instructed “lets go using this then” after being told it is independent, not an SPU publication.
This supersedes the earlier decision above to leave total APS manual. The exception applies to this calculator,
not to third-party sources generally, and does not verify the separate Adobe prospectus.

The app now counts exactly seven NSC subjects including Life Orientation. SPU's official image corroborates
the base table, Mathematics/Home Language bonuses and Life Orientation scale. The independent calculator
supplies the seven-subject rule. Its citation records the owner's acceptance without claiming official provenance.
Mathematical Literacy and First Additional Language receive no bonus. Home Language bonuses use the selected
language role, including named languages on additional-subject rows. Missing language roles, fewer/more than
seven subjects or missing Life Orientation leave the total uncalculated with an explanation. No best-seven
selection rule is inferred for learners offering extra subjects.

English HL level 4 / FAL level 5 requirements, already present in programme notes, are now enforced by the engine.
NSC achievement levels remain separate from SPU's points (90% is NSC level 7 but eight base APS points).
Other programme-specific language/selection notes and incomplete source provenance remain as recorded above.
