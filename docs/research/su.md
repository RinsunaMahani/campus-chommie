# Stellenbosch University (SU): programme list research

Agent draft, 15 Oct 2026. Pack: `backend/data/universities/su.yaml`. Nobody has checked these values yet, so
`release: false` stays.

## Result

73 programmes; 70 with requirements, 3 with `requirements: null`. `points_rules` stays null: SU selects on averages of
your marks, not points, so every SU programme still shows "can't check yet". Each programme keeps its subject
minimums (as percentages, or as NSC levels where an either/or rule needs them) and puts its required average in
extras. `min_points` is null throughout.

## The main problem: the 2027 prospectus couldn't be read

SU's 2027 NSC/IEB prospectus (`su-admissions-booklet-2027.pdf`) and its other 2027 programme documents are on
`files.su.ac.za`. That host's robots.txt answered **403** (an S3 bucket's AccessDenied), so under our rules nothing
was fetched from it. `www.su.ac.za`'s robots.txt allows the pages we'd need, but the pages themselves sent a
Cloudflare "Just a moment..." challenge (403), and we don't get around those. `www.sun.ac.za` and `sun.ac.za` didn't
connect.

So the requirements come from the **2026 prospectus** (NSC/IEB, printed December 2024), the newest edition we could
read. It's on `blogs.sun.ac.za`, whose robots.txt allows everything except WordPress admin paths. Every programme's
extras say the figures are from 2026 and should be checked against 2027.

To check these figures, the newer documents on blogs.sun.ac.za (uploaded March and April 2026 for the 2027 Open Day)
were compared with them. The Science programme brochures, the AgriSciences brochure, the Arts and Social Sciences
pamphlet (63% average), the Data Science and Actuarial Science brochures and the Engineering FAQ all match the 2026
prospectus. The differences are listed under "Check first".

## What was read (all retrieved 15 Oct 2026)

- 2026 Undergraduate Prospectus, NSC or IEB, pages 2 to 15:
  https://blogs.sun.ac.za/open-day/files/2025/02/Prospectus.pdf (source `s-su-prospectus-2026`)
- Faculty of Engineering FAQ, 2027 intake, questions 5 and 9 (BEng selection mark; requirements for the extended
  programmes): https://blogs.sun.ac.za/open-day/files/2026/03/Faculty-FAQ-Eng.pdf (source `s-su-eng-faq-2027`)
- Used to cross-check only, not cited in the pack:
  - International Undergraduate Prospectus 2027:
    https://blogs.sun.ac.za/open-day/files/2026/04/SU-International-booklet.pdf
  - Faculty of Law selection guidelines (for 2027):
    https://blogs.sun.ac.za/open-day/files/2026/04/SU-Faculty-of-Law-Selection-Guidelines.pdf
  - FMHS "Study with us 2026" leaflet: https://blogs.sun.ac.za/open-day/files/2026/04/FMHS-study-with-us-2026.pdf
  - BEd Programme Information 2026:
    https://blogs.sun.ac.za/open-day/files/2026/03/2026-BEd-2026-admission-requirements-ENG.pdf
  - The Science, AgriSciences, Economic and Management Sciences and Engineering brochures and FAQs in
    `blogs.sun.ac.za/open-day/files/2026/03/` and `/2026/04/`
  - The how-to-apply guide for the 2027 intake (already `s-su-howto`).
- The open-day site's WordPress media listing (`/open-day/wp-json/wp/v2/media?search=...`) was used to find the
  files. robots.txt allows it.

## Blocked, so a person should download these in a browser

1. The 2027 NSC/IEB prospectus, the most important:
   https://files.su.ac.za/public/undergraduate-maties/documents/2026-01/su-admissions-booklet-2027.pdf
2. Admission requirements and selection criteria for BEng, 2027:
   https://files.su.ac.za/public/faculty-engineering/documents/2026-03/admission-requirements-beng-2027-eng.pdf
3. The Diploma in Public Accountability prospectus (School of Public Leadership):
   https://files.su.ac.za/public/documents/2025-09/programme-prospectus.pdf
4. The faculties' selection guidelines for 2027, linked from www.su.ac.za > Apply > Undergraduate (behind
   Cloudflare).

## Programmes with `requirements: null`

- `ba_extended`: the prospectus only says that the BA programmes marked # have extended versions and that the
  faculty chooses who takes them. It publishes no separate minimums.
- `bsc_extended`: offered in October or January to applicants in SU's designated categories who don't meet a BSc's
  selection mark. No separate minimums are published.
- `dip_public_accountability`: its own prospectus is on files.su.ac.za, which is blocked. Nothing we could read says
  whether it's open to school-leavers. It's kept because the pack already gives its 15 December closing date. Check
  whether it belongs in scope at all (it may be meant for people already working in the public sector).

## Left out

- Advanced Diploma in Practical Music, the three-year LLB (a second degree), and the PGCE: none is a first
  qualification.
- The Faculty of Military Science's programmes: they're not in the prospectus, and applicants go through the Defence
  Force.
- The race-based categories in the Law, Science and Engineering selection guidelines. CLAUDE.md says we never ask
  about protected characteristics. The pack only says that preference goes to "designated categories" or
  "underserved backgrounds", in SU's own words.

## Approximations

- **Averages aren't checked.** SU's main requirement, the NSC average without Life Orientation, is in extras only.
  The engine has no average rule.
- **"English or Afrikaans" becomes english or other_language.** The app only knows a learner's English and their one
  other language, so `other_language` stands in for Afrikaans (each extras line says so). For the Arts and Social
  Sciences "Home Language 50%, First Additional Language 40%", the pack uses the either/or {english 4, other_language 3}
  or {english 3, other_language 4}. BEd (60% plus 50%), Drama (60% plus 50%) and Law and BDatSci (60%) work the same
  way. SU's percentages in these rules fall on NSC level boundaries (40% = level 3, 50% = 4, 60% = 5, 70% = 6), so
  the levels match the percentages exactly.
- **Rules with HL and FAL thresholds** (for example Economic and Management Sciences: English or Afrikaans Home
  Language 50%, or First Additional Language 70%) are checked at the lowest figure, 50%. The full rule is in extras.
  Actuarial Science, International Business, International Studies, the Sustainable Development diploma and BEng are
  checked on English alone, at the lowest English mark any of their routes allows.
- **AgriSciences extended programmes**: the rule has two combinations, each with an upper bound (Mathematics 55% to
  59.9% with Physical Sciences 50%, or Mathematics 60% with Physical Sciences 45% to 49.9%). The pack checks only
  Mathematics 55% and Physical Sciences 45%. That's a necessary condition, not a sufficient one. The full rule and the
  Wood Products version are in extras.
- **Conditional requirements aren't checked.** Examples: Mathematics 70% for Science students who take first-year
  Mathematics and Physics (60% with the Bio versions), Physical Sciences 50% only if you take Chemistry or Physics,
  Mathematics 60% in LLB or BA (Law) only if you take Economics, and the Socio-Informatics and music Mathematics
  rules. The pack checks the lower figure, or leaves the subject out, and states the rule in extras.
- **The BScFor degree is split into two entries**, because its two fields of study ask different Mathematics and
  Physical Sciences marks.
- **BDatSci** is one programme listed by three faculties, so it has one entry with every focal area.
- **`selective: true` for every programme except the Diploma in Public Accountability** (unknown). SU says all its
  programmes are selection programmes and it has more applicants than places (prospectus, page 2).
- **`places`** is set only where the prospectus gives an exact number (Social Work 100, Visual Arts 60, BEd 125 each,
  BCom Management Sciences ECP about 100, LLB 120, BA Law 55, BCom Law 80, BAccLLB 35). The FMHS "±" numbers are in
  extras.

## Check first

1. **Download the 2027 prospectus** (link 1 above) and compare every average and subject minimum. The 2027
   International booklet hints at changes, though it covers international curricula and may differ from NSC on
   purpose: it asks a 65% average for the BA programmes (2026 NSC prospectus: 63%) and 85% for Actuarial Science and
   International Business (2026 NSC: 80%).
2. **Occupational Therapy and Speech-Language and Hearing Therapy.** The FMHS leaflet uploaded in April 2026 seems to
   ask Mathematics 50% for Occupational Therapy (the prospectus says 40%). It also seems to add Mathematics 50% or
   Mathematical Literacy 80% for Speech therapy. Its two-column layout makes the pairing uncertain, so the pack doesn't
   check Mathematics for either programme and says why in extras. The same leaflet says 280 MBChB places a year (the
   prospectus says about 300).
3. **Law places.** The 2027 Law guidelines give registration targets of 120 (LLB), 50 (BA Law) and 100 for BCom (Law)
   and BAccLLB together. The 2026 prospectus says 120, 55, 80 and 35. The pack uses the prospectus numbers.
4. **BEng language rule.** The prospectus says "Afrikaans Second Additional Language 60%"; the 2027 Engineering FAQ
   says "Afrikaans First Additional Language 60%". The pack doesn't check this part, but the wording in extras should
   follow 2027.
5. **Diploma in Public Accountability**: whether it belongs in scope, and its requirements (link 3).
6. **The Theology extended programme's motivational letter**: the prospectus marks it with a footnote (**) that isn't
   attached to any programme. The pack attaches it to the extended programme, and that should be checked.
