# All 26 public universities: research notes

Agent draft, from 13 Oct 2026. On 13 Oct Rinsuna chose to cover all 26 public universities
([USAf's list](https://usaf.ac.za/prospective-students/)), starting with each one's own APS rule and how and when to
apply. Programmes are at UP, TUT and SMU and, since #32, #33 and wave 3, at VUT, WSU, UMP, MUT, SPU, UFS, UNIZULU, UNIVEN and UL, each with its own note in
this folder (`ufs.md`, `ul.md`, `univen.md`, `unizulu.md`, `vut.md` and so on); the rest follow in waves. Every value below is an agent
draft: `release: false`, each source `verified_by: "agent draft, needs human check"`, and the app shows "Not yet
confirmed by the team" until a person has checked it.

**How each source was read:**
- **Direct:** the page or PDF itself, on the day.
- **Index:** the university's site stops automated readers (UJ sits behind Cloudflare's bot check), so the values
  came from a search engine's copy of the official page. The pack cites the official page; a person should open it
  in a browser to check.

Facts a university doesn't publish are left out (`null`), and the app says "not verified yet". Bank account
numbers in universities' documents are left out on purpose (SECURITY.md).

## Batch 1: Gauteng, Limpopo, Mpumalanga and North West

| University | Points rule | 2027 applications | Fee | Read |
|---|---|---|---|---|
| Wits | best 7 with Life Orientation; levels to 8 (90%+); English and Mathematics add 2 from 60% (10, 9, 8, 7 at 90, 80, 70, 60%); Life Orientation 4, 3, 2, 1 at 90, 80, 70, 60%; under 40% adds nothing; a faculty's required subjects always count | opened in March 2026 (no day given); closed 30 Sep 2026; Health Sciences, Architectural Studies, Audiology, Speech-Language Pathology and BA Film and TV closed 30 Jun 2026 | R100 | direct: [entry requirements](https://www.wits.ac.za/undergraduate/entry-requirements/), [apply](https://www.wits.ac.za/undergraduate/apply-to-wits/), [timelines](https://www.wits.ac.za/undergraduate/apply-to-wits/timelines/) |
| UJ | best 6 without Life Orientation; levels 1 to 7 | 1 Apr to 31 Oct 2026 at 12:00; no late applications; two choices | free | index: [undergraduate](https://www.uj.ac.za/admission-aid/new/), [2026 Science yearbook](https://www.uj.ac.za/wp-content/uploads/2026/02/final-2026-science-apk-undergraduate-yearbook-jan2026.pdf) |
| Unisa | 6 subjects without Life Orientation; levels 1 to 7 (42 at most) | 17 Aug to 9 Oct 2026; up to three qualifications | R160, first-time applicants only | direct: [admission requirements](https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Undergraduate-qualifications/Qualifications/General-admission-requirements), [apply](https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Undergraduate-qualifications/Apply-for-admission), [what's new for 2027](https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Undergraduate-qualifications/Whats-new-for-2027) |
| NWU | 6 without Life Orientation; levels to 8 (90%+) | 1 Jun to 31 Aug 2026; selection programmes closed 30 Jun | R150 | direct: [apply](https://studies.nwu.ac.za/studies/apply); the rule from the [2026 Grade 12 prospectus](https://studies.nwu.ac.za/sites/studies.nwu.ac.za/files/files/undergrad/2025-Grade-12-Prospectus.pdf) via the index (the 2027 one wasn't found); 30 Jun from [NWU's news](https://news.nwu.ac.za/applications-and-admissions-north-west-university-2026) via the index |
| VUT | best 6 without Life Orientation; levels to 8 (90 to 99%) | opened 21 May 2026; closes 30 Sep (2027 requirements) or 30 Oct 2026 (How to apply page): both kept, and the app asks the learner to check; some programmes closed 31 Jul | R110, on the portal | direct: [2027 requirements](https://vut.ac.za/wp-content/uploads/2026/03/2027-Undergraduate-Minimum-Admission-Requirements.pdf), [how to apply](https://vut.ac.za/how-to-apply/) |
| UL | 6 without Life Orientation; levels 1 to 7; Life Orientation at level 3 or more required | 1 Apr to 30 Sep 2026; MBChB and international applicants closed 30 Jul | R200 | direct: [undergraduate studies](https://www.ul.ac.za/admissions/undergraduate-studies/), [2027 applications](https://www.ul.ac.za/study-with-us-university-of-limpopo-2027-application-now-open/) |
| UNIVEN | the 7 highest marks without Life Orientation; each subject scores a tenth of its percentage (75% is 7.5); under 40% adds nothing | 1 May to 30 Sep 2026 | free | direct: [2027 prospectus](https://www.univen.ac.za/wp-content/uploads/2026/09/2027-Univen-Undergraduate-Prospectus.pdf) pages 8 and 9, [how to apply](https://www.univen.ac.za/students/student-support-services/how-to-apply/) |
| UMP | 7: the four compulsory subjects and the three best others; Life Orientation at half; levels 1 to 7 | 1 Jun to 30 Nov 2026; two choices | R200 | direct: [online applications](https://www.ump.ac.za/Study-with-us/Application-Process/Online-Applications), [BEd Foundation Phase page](https://www.ump.ac.za/Study-with-us/Faculties-and-Schools/Faculty-of-Education/School-of-Early-Childhood-Education/Bachelor-of-Education-in-Foundation-Phase-Teaching.aspx) |

**Two new ways of counting** (`campus_engine/points.py`):
- **A subject's own points table** (`subject_points`): Wits's English, Mathematics and Life Orientation; UWC's
  weighted columns come next.
- **Points from the percentage** (`percent_points`): UNIVEN.

**Where the engine is close but not exact** (said in each pack's `note`): UMP always counts the four compulsory
subjects; the engine counts the best six besides Life Orientation, which is the same for a learner with seven
subjects. Wits always counts a faculty's required subjects.

## Batch 2: KwaZulu-Natal, the Free State and the Northern Cape

UKZN, DUT, MUT and UNIZULU take first-time South African applicants through the **Central Applications Office**
([CAO, 2027 entry FAQs](https://cao.ac.za/2027%20Entry%20FAQs.html), direct): R250 if the fee reaches the CAO by
31 Oct 2026, R470 from 1 Nov.

| University | Points rule | 2027 applications | Fee | Read |
|---|---|---|---|---|
| UKZN | 6 without Life Orientation; levels to 8 (90%+); English and Mathematics or Mathematical Literacy always counted; Mathematics Paper 3 never | through the CAO; closed 30 Sep 2026; Medicine 30 Jun (no late applications) | the CAO's | index: UKZN's sites didn't answer from our network on 13 Oct ([selection procedure](https://applications.ukzn.ac.za/selection-procedure/undergraduate-selection-procedure/), [2027 applications](https://applications.ukzn.ac.za/uncategorized/2026-applications/)) |
| DUT | **none yet**: only 90%+ = 8 and 80 to 89% = 7 were read; English and the next five best, without Life Orientation | through the CAO; each programme has its own date (Diagnostic Radiography 31 Aug, Medical Laboratory Science 30 Sep) | the CAO's | index: DUT's site certificate had expired ([Study Opportunities 2027](https://www.dut.ac.za/wp-content/uploads/2026/06/Study-Opportunities-2027.pdf)); dates from the CAO's [entry requirement changes](https://cao.ac.za/download/Entry%20Requirement%20Changes%202027%20Entry%20-%2024.07.2026.pdf) |
| MUT | **none yet**: its pages don't say | through the CAO, MUT first or second; opened January, on time by 30 Sep, late until 30 Nov | the CAO's | direct: [apply](https://www.mut.ac.za/prospective-students/apply/); first-or-second from [how to apply](https://www.mut.ac.za/prospective-students/study-at-mut/how-to-apply-to-mut/) via the index |
| UNIZULU | 6 without Life Orientation; levels 1 to 7; Life Orientation at 40% required | through the CAO; 2027 dates not found | the CAO's | index: [admissions policy](https://www.unizulu.ac.za/wp-content/uploads/2018/07/Policy-and-Procedures-on-Admissions.pdf) (2018, the newest found) |
| UFS | the four compulsory subjects and the best two, levels to 8 (none under 30%), Life Orientation 1 point from 60% | opened 1 Apr 2026; the closing date wasn't found, so no window | not found | direct: [2027 MBChB selection rules](https://www.ufs.ac.za/docs/librariesprovider25/default-document-library/2027-mbchb-selection-rules.pdf?sfvrsn=34af520_0) section 2.2; the scale via the index ([conversion table](https://www.ufs.ac.za/docs/librariesprovider44/default-document-library/conversion-table.pdf?sfvrsn=50268d21_2)) |
| CUT | **none yet**: 30% = 2 up to 90% = 8, Life Orientation at most 1, but how many subjects count isn't said | April to 30 Sep 2026; no late or walk-in applications; two choices | free | direct: [application process](https://www.cut.ac.za/application-process/), [admission points](https://www.cut.ac.za/admission-points-ap); 2027 dates from [Ask CUT](https://askcut.cut.ac.za/support/solutions/articles/103000016975-closing-date-for-cut-online-applications-for-local-and-international-) via the index |
| SPU | **none yet**: levels to 8, Mathematics and a home language add up to 2, Life Orientation 4 to 1, but how many subjects count isn't said, and the bonus needs your home language | open until 31 Oct 2026 | not found | direct: [how to apply](https://www.spu.ac.za/index.php/how-to-apply/), [2026 prospectus](https://www.spu.ac.za/wp-content/uploads/2025/04/2026-Undergraduate-Prospectus.pdf) page 4 |

## Batch 3: the Western and Eastern Cape

| University | Points rule | 2027 applications | Fee | Read |
|---|---|---|---|---|
| UCT | **none**: UCT ranks by a Faculty Points Score its faculties work out their own way | closed 31 Jul 2026; Fine Art portfolios by 31 Aug | R100 (South Africa and SADC) | index: [application procedure](https://uct.ac.za/students/applications-apply-undergraduate-qualifications/application-procedure), [2027 directions](https://uct.ac.za/sites/default/files/media/documents/ug-directions-for-applicants-2027.pdf) |
| Stellenbosch | **none**: selects on averages of your marks, programme by programme | closed 31 Jul 2026; Diploma in Public Accountability 15 Dec; three choices | R100, waived for some schools by quintile | direct: [how to apply, 2027 intake](https://blogs.sun.ac.za/open-day/files/2026/03/How-to-Apply-Undergraduate-programmes-2027-intake.pdf) |
| UWC | 7: English and Mathematics up to 15 (15, 13, 11, 9, 7, 5, 3, 1 from 90% down to 20%), other subjects up to 8, Life Orientation up to 3; nothing under 20% | 1 Apr to 30 Sep 2026; Dentistry and Oral Health 31 Aug; two choices | not found | direct: [APS calculator](https://www.uwc.ac.za/admission-point-score-calculator/south-african-aps-calculator), [undergraduate applications](https://www.uwc.ac.za/admission-and-financial-aid/apply/undergraduate-applications) |
| CPUT | **none yet**: its method wasn't found | each programme its own date: 30 Jun, 31 Jul, 31 Aug or 30 Sep 2026 | free online (R100 on paper) | index: CPUT's site sent an incomplete certificate chain ([apply](https://www.cput.ac.za/study-at-cput/undergraduate/apply)) |
| Nelson Mandela | the Applicant Score: six subjects' percentages added, out of 600, without Life Orientation; quintile 1 to 3 schools add 7 with 50%+ in Life Orientation (not added: we'd have to ask about your school) | Health programmes 30 Jun 2026, early applications 3 Aug, the rest 30 Sep | none for South Africans | index: [applicant score](https://myfuture.mandela.ac.za/Applicant-Score), [closing dates](https://www.mandela.ac.za/Study-at-Mandela/Application/Closing-dates) |
| Rhodes | a tenth of each of six subjects' percentages; Life Orientation not counted (50% required) | 1 Apr to 30 Sep 2026 | R100 | direct: [prospectus](https://www.ru.ac.za/media/rhodesuniversity/content/registrar/documents/information/studentrecruitment/RU_READY_Undergraduate_Prospectus_2026_DIGITAL_A5_Landscape_24pp_18Mar2026.pdf) pages 22 and 23; the fee via the index ([payment of fees](https://www.ru.ac.za/admissiongateway/application/paymentoffees/)) |
| Fort Hare | **none yet**: its table wasn't found (Life Orientation at 50% required) | open until 31 Oct 2026 | R120 | index: [admission](https://www.ufh.ac.za/admission), [apply](https://www.ufh.ac.za/apply/apply-undergraduate) |
| Walter Sisulu | 6 without Life Orientation (English, another language and the four best others; Education counts seven); levels to 8 | 1 Jun to 31 Oct 2026; international applicants 30 Sep | R100 | direct: [2027 brochure](https://wsu.ac.za/media/attachments/2026/05/27/2027-information-brochure-admission-requirements.pdf) page 4, [how to apply](https://www.wsu.ac.za/index.php/en/study-with-us/application-and-registration/how-to-apply-the-process) |

**A third way of counting:** `other_points`, a general table for every subject without its own (UWC). A university
without a points rule says why (`points_note`), and the app shows that instead of a number.

## Open on 13 Oct 2026

UJ (to 31 Oct, 12:00), MUT (late, to 30 Nov), SPU (to 31 Oct), UMP (to 30 Nov), Fort Hare (to 31 Oct) and Walter
Sisulu (to 31 Oct), and possibly VUT (to 30 Oct).
