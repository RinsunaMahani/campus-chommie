# All 26 public universities: research notes

Agent draft, from 13 Oct 2026. On 13 Oct Rinsuna chose to cover all 26 public universities
([USAf's list](https://usaf.ac.za/prospective-students/)), starting with each one's own APS rule and how and when to
apply. Programmes stay at UP, TUT and SMU for now and grow one university at a time. Every value below is an agent
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

## Still to come

- **Batch 2:** UKZN, DUT, MUT and UniZulu (through the Central Applications Office), UFS, CUT and Sol Plaatje.
- **Batch 3:** UCT, Stellenbosch, UWC, CPUT, Nelson Mandela, Rhodes, Fort Hare and Walter Sisulu.
- **UCT and Stellenbosch** rank by a Faculty Points Score and by average percentages, which marks alone don't give
  the engine yet: their packs will say so instead of guessing a number.
