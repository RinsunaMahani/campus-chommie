# Last admission gaps — 26 October 2026

This follow-up starts after the official-source precedence changes: five wholly missing and two partial records. It resolves two full subject rules and enables explicit partial checks for the two CPUT records. One wholly missing record and four partial records remain; these counts must not be presented as zero gaps.

## Resolved subject rules

- **UFH Crop Science (71524, SAQA 101000):** the [current official programme page](https://www.ufh.ac.za/course/bachelor-of-science-agriculture-in-crop-science) explicitly gives English HL/FAL level 4. This fills the blank in the 2027 guide. Maths, Physical Sciences and Life Orientation each require 4; one of Life Sciences, Geography, Agricultural Sciences or IT requires 4; two other subjects require 4. APS 28 remains sourced to the official 2027 guide and must be checked manually using UFH's method.
- **TUT Technology BEd:** the [official 2026 Humanities prospectus](https://www.tut.ac.za/media/tshwane-interim/site-content/images/prospectus/PART_5_Humanities_Prospectus_-2026.pdf), printed pages 179–181, supplies the NSC specialisation prerequisites and six allowed first-year pairs. English 4 and APS 24 are required. One side of the pair needs Civil/Electrical/Mechanical Technology or Physical/Technical Sciences at 4. The other needs EGD or Maths/Technical Maths at 4. This checks existence of at least one valid pair; it does not claim that a Civil Technology mark permits Electrical or Mechanical specialisation. The 2026 source-year caveat remains visible.

## CPUT partial checks

Both use the user-supplied official 2027 prospectus, already recorded as `s-cput-prospectus-2027`.

- **Banking, page 9:** check English 4 and Maths 3 (APS 24) or Maths Literacy 4 (APS 26). The mixed ICT/accounting/commerce/vocational list says **NQF Level 4**, which is not an NSC achievement level. No 50% requirement or IT/CAT equivalence is invented. The extra subject condition and APS method remain explicitly university-assessed.
- **Senior/FET BEd, page 10:** check an offered Home Language at 4 and First Additional Language at 3, from Afrikaans, English and isiXhosa. APS 32 is displayed. Campus language, three-subject and elective conditions still require university assessment. The current official Education application-guidelines URL resolves to a resource page without downloadable guidelines; the course page lists curriculum/fees rather than additional entry rules.

The new `unassessed_conditions` field preserves these as partial requirements. Passing the known checks returns `unverified`, with the missing conditions; failing a definite language/Maths minimum remains `not_yet`. Generic text claiming all subject minimums are met is removed. The readiness report continues to count both as unresolved partial records.

## Remaining external facts

- **UFH BEd Commerce:** the [current official course page](https://www.ufh.ac.za/course/bachelor-of-education-in-senior-phase-and-fet-teaching-commerce) still says “Business management” in its entry requirements. Its description mentions teaching Business Studies, but does not explicitly establish admission-subject equivalence. Accounting plus Economics remains assessable.
- **UFH BEd Science:** the [current official course page](https://www.ufh.ac.za/course/bachelor-of-education-in-senior-phase-and-fet-teaching-science) still says “Computer science”. Neither IT nor CAT equivalence is established. The three named science alternatives remain assessable.
- **UMP Social Sciences:** the official 2026 fees handbook lists the degree, but the [current faculty/programme directory](https://www.ump.ac.za/Study-with-us/Faculties-and-Schools) and searches did not establish an admission table or next intake. Its programme note now names the exact missing facts. BA General and Social Work thresholds are not substituted. A search result for SAQA 120400 belongs to a different institution and was rejected.

Official-source acceptance does not supply values that a source omits. No university was contacted and no deployment was performed.
