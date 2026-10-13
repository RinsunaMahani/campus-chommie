# NSC subjects: research notes

Agent draft, 13 Oct 2026. On 13 Oct Rinsuna asked Find my course to offer every subject, other languages besides
English especially, with related subjects grouped in folders and all languages ticked in one go. She chose the
folders below and the way languages reach the API the same day.

## Sources

- **Department of Basic Education (DBE), CAPS for Grades 10 to 12 (FET phase):**
  [education.gov.za, CAPSFET](https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements(CAPS)/CAPSFET/tabid/570/Default.aspx),
  read 13 Oct 2026. It lists the languages at each level, then every other subject, with a curriculum document for
  each. It also has an entry "SA Sign Language CAPS" for Grades 10 to 12.
- **SAnews (government news agency), 4 Mar 2018:**
  ["Sign Language recognised as a home language"](https://www.sanews.gov.za/south-africa/sign-language-recognised-home-language).
  South African Sign Language "has officially been recognised as a home language in the curriculum" and is "one of
  the examinable subjects for the National Senior Certificate".

## The list

**Home language** and **first additional language**, the same eleven at both levels: Afrikaans, English,
isiNdebele, isiXhosa, isiZulu, Sepedi, Sesotho, Setswana, Siswati, Tshivenda, Xitsonga. South African Sign Language
is a home language only (SAnews, above).

**Second additional language:** Afrikaans, English, French, isiNdebele, isiXhosa, isiZulu, Mandarin, Sepedi, Sesotho,
Setswana, Siswati, Tshivenda, Xitsonga.

**Every other subject:** Accounting, Agricultural Management Practices, Agricultural Sciences, Agricultural
Technology, Business Studies, Civil Technology, Computer Applications Technology, Consumer Studies, Dance Studies,
Design, Dramatic Arts, Economics, Electrical Technology, Engineering Graphics and Design, Equine Studies, Geography,
History, Hospitality Studies, Information Technology, Life Orientation, Life Sciences, Marine Sciences, Maritime
Economics, Mathematical Literacy, Mathematics, Mechanical Technology, Music, Nautical Science, Physical Sciences,
Religion Studies, Sport and Exercise Science, Technical Mathematics, Technical Sciences, Tourism, Visual Arts.

How the page shows two of these:
- **History** is listed only among the Afrikaans documents, as "Geskiedenis (History)".
- **Design** is "Design Studies" among the English documents and "Ontwerp (Design)" among the Afrikaans ones. The app
  keeps "Design", the name the backend's key has always shown.

The page also lists technical-school versions of three subjects: Technical: Civil Technology, Technical: Electrical
Technology and Technical: Mechanical Technology. The picker offers one entry for each subject (see the open
questions).

## In the app

`frontend/mobile/src/features/courseFinder/subjects.ts` holds the list in twelve folders: Languages (home or first
additional language); Mathematics; Sciences; Business and economics; Humanities; Computers; Technology and
engineering; Agriculture; Arts; Consumer, hospitality and tourism; Life Orientation and sport; and Second additional
languages. The folders are the app's own grouping, not the DBE's.

Admission rules name only the keys in `backend/campus_engine/schemas.py` (`SUBJECTS`), so the app sends:

| What the learner picks | What the API gets |
|---|---|
| a subject a rule names (Mathematics, English and 27 more) | its own key |
| one official language besides English, at home or first additional level | `other_language` |
| several of those | the best-marked as `other_language` (on a tie, the first in the folder); the rest as points-only |
| a second additional language, or a subject no rule names (Religion Studies, Marine Sciences...) | `another_subject_1` to `_3`, which count towards points only |

So the API takes at most three points-only subjects and nine subjects in all. The picker greys out anything past
those limits, and a language already chosen at the other level, and says why. When several languages could have
counted, the results say which one did. A test keeps the app's keys and limits in step with the backend's.
