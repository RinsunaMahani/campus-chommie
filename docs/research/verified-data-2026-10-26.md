# Official data follow-up, 26 October 2026

## Four UJ extended routes resolved

The course pages explicitly say Mathematics **or** Technical Mathematics and Physical Science **or** Technical Science.
This clarifies the separate columns in the 2027 prospectus, without inferring an OR from layout alone.

| Programme | APS | English | Maths or Technical Maths | Physical Science or Technical Science | Official source |
|---|---:|---:|---:|---:|---|
| Construction extended, B6SC0Q | 26 | 4 | 5 | 5 | [Course page](https://www.uj.ac.za/university-courses/bachelor-of-science-in-construction-extended/) |
| Civil Engineering extended, B6CX3Q | 26 | 4 | 4 | 4 | [Course page](https://www.uj.ac.za/university-courses/beng-tech-in-civil-engineering-extended/) |
| Industrial Engineering extended, B6IX2Q | 24 | 4 | 5 | 5 | [Course page](https://www.uj.ac.za/university-courses/beng-tech-in-industrial-engineering-extended/) |
| Mechanical Engineering extended, B6MX2Q | 24 | 4 | 5 | 5 | [Course page](https://www.uj.ac.za/university-courses/beng-tech-in-mechanical-engineering-extended/) |

All thresholds agree with the 2027 prospectus. The Construction page retains 2025 application dates; those dates
were not imported. Only its explicit subject alternatives supplement the matching 2027 threshold table.
Minimums do not guarantee a place. These four records are now assessed, reducing missing requirements from 23 to 19.

## SPU 2027 calendar

The [official calendar landing page](https://www.spu.ac.za/index.php/academic-calendar/) links the
[final 2027 calendar S-2026-51-14](https://www.spu.ac.za/wp-content/uploads/2026/09/S-2026-51-14-2027-Academic-Calendar-FINAL.pdf).
Downloaded and visually checked its single-page table. Added 21 student-facing periods/dates, including registration,
orientation, four teaching blocks, module changes, recesses, examinations and university closure.
Retained the existing 2026 calendar. First-year residence registration is explicitly restricted to residence students.
The tentative NSC results row says 7 January **2026** despite the 2027 calendar heading; it was not imported or silently corrected.
Committee dates are not student examination dates and were not imported.

## Remaining checks

- UJ Geography BEd: the course page lists Maths and Science requirements, while the prospectus's OR layout differs.
  English roles are supported by the app now; the outstanding issue is the subject combination, not language input.
- Four UJ Physical Sciences routes: current course pages corroborate Mathematics 6, but the prospectus footnote
  still gives lower module-dependent values. Geology routes also list Physical Science 4/5. These remain manual
  pending a consistent rule covering the module-dependent cases; a stricter guessed rule could wrongly reject students.
- MUT Community Extension: the current departmental page retains the unclear Agriculture/Consumer Studies/
  Life Sciences combinations; the 2027 CAO wording differs. No inferred combination was imported.
- UMP Social Sciences: the current official search results provide BA General and Social Work, which are distinct
  programmes already covered. Their thresholds were not copied onto the fees-handbook-only Social Sciences entry.
- TUT Foundation Phase and CPUT Senior/FET BEd still need grouped language/elective rules; individual named-language
  support alone does not express these conditions. TUT Technology retains ambiguous subject combinations.
- CPUT Banking, UFH's three rows and UFS Food Systems extended retain their recorded subject-equivalence,
  missing-value or contradictory-rule issues. RU PGCE requires previous qualifications; SU extended programmes and
  UFS extended BEd require faculty placement rather than a fabricated school-leaver threshold.
- Searches did not establish full 2027 teaching calendars for UKZN, UMP, UNIVEN, UFH, UL, UNIZULU or VUT.
  Conferences and application deadlines were not substituted for teaching terms.

The separate SPU APS implementation remains in PR #111. This follow-up starts from main after PR #110 and does
not claim that an open PR has deployed. Official sources are accepted under the owner's existing instruction.

Validation: 591 engine/architecture tests passed, including all four combinations of Maths/Technical Maths and
Physical/Technical Science for each new UJ route, with boundary failures below the published minimums.
The data validator reports zero errors; existing incomplete-pack and map-review warnings remain.
