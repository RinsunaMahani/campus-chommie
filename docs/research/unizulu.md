# University of Zululand (UNIZULU): programme research notes

Agent draft, read from the CAO's and UNIZULU's own documents on 14 Oct 2026. Nobody has checked these values yet:
`backend/data/universities/unizulu.yaml` keeps `release: false` until a person has compared every one with its source.

## What I read

| Id in the pack | Document | Pages used |
| --- | --- | --- |
| s-unizulu-cao-2027 | [CAO Handbook 2027 Entry](https://www.cao.ac.za/Download/CAO%20HANDBOOK%202027%20Entry%20web.pdf) | printed p13 (dates), 30-32 (points), 35 (campus codes), UNIZULU's rows on p45-47, 52, 60, 67-68, 72, 78, 80, 88, 91, 102, 104, 109, 127-129, 156, 158, 161, 168, 170-177, 180-184, 189, 191, 195 |
| s-unizulu-cao-new-2027 | CAO: [New Programmes Not Listed in the Handbook](https://www.cao.ac.za/download/New_Programmes.html) | UNIZULU's 40 rows (the page builds its table in the browser; I read the list embedded in the page) |
| s-unizulu-brochure-2026 | [Undergraduate Programmes brochure](https://www.unizulu.ac.za/wp-content/uploads/2025/02/2026-Brochure-for-undergraduate.pdf), for the 2026 intake (closing 31 Oct 2025), linked from the [apply page](https://www.unizulu.ac.za/apply/) | p1 (points example), p3-6 (programme tables) |
| s-unizulu-fhss-2026 | [Humanities and Social Sciences Undergraduate Handbook 2026](https://reg.unizulu.ac.za/wp-content/uploads/2026/01/FHSS-Undergrad-Handbook-2026.pdf) | p12-13 (faculty rules), programme entries p17, 32, 38, 43, 50, 56, 61, 70, 79, 85, 94, 103-104, 109, 118, 126, 133, 139 |
| s-unizulu-fsae-2026 | [Science, Agriculture and Engineering Undergraduate Handbook 2026](https://reg.unizulu.ac.za/wp-content/uploads/2026/01/FSAE-Undergraduate-Handbook-2026.cleaned.pdf) | p12 (points), p14-21 (entry rules S1) |
| s-unizulu-fcal-2026 | [Commerce, Administration and Law Handbook 2026](https://reg.unizulu.ac.za/wp-content/uploads/2026/01/FCAL-Handbook-2026.pdf) | p36-41 (admission, points, programmes) |
| s-unizulu-fedu-2026 | [Education Undergraduate Handbook 2026](https://reg.unizulu.ac.za/wp-content/uploads/2026/01/FEDU-Undergraduate-Handbook-2026.pdf) | PDF p19-22 (points, B Ed requirements, intake notes) |
| s-unizulu-rb-2026 | [Richards Bay Campus Handbook 2026](https://reg.unizulu.ac.za/wp-content/uploads/2026/01/2026-Richards-Bay-Campus-Handbook.pdf) | p7 (entry requirements) |
| (cross-check) | The CAO's [Entry Requirement Changes 2027](https://www.cao.ac.za/download/Entry%20Requirement%20Changes%202027%20Entry%20-%2001.10.2027.pdf) and [Closing Date Changes](https://www.cao.ac.za/download/Closing%20Date%20Changes%20-%2029.09.2026.pdf) | one UNIZULU row (B Ed Foundation Phase: Mathematics 3 or Mathematical Literacy 4 replaces Geography and History); the handbook copy I read already has it. No UNIZULU closing-date changes |
| (cross-check) | UNIZULU's [Applying to Study](https://www.unizulu.ac.za/wp-content/uploads/2022/10/ApplyingToStudy.pdf) (2022) and the [admissions policy](https://www.unizulu.ac.za/wp-content/uploads/2018/07/Policy-and-Procedures-on-Admissions.pdf) (s-unizulu-policy) | p1 and p4; policy section 5.4 (p19) |

**robots.txt:** `www.unizulu.ac.za` allows everything (`Allow: /ads.txt`, no disallow); `reg.unizulu.ac.za` and
`www.education.unizulu.ac.za` disallow only `/wp-admin/`; `www.cao.ac.za` and `cao.ac.za` disallow only
`/WebResource.axd`. Nothing I needed was blocked. Not read: the CAO's online programme search (two scripted searches
got an error page, so I stopped), and UNIZULU's "Faculty Handbooks" link (`/faculty-handbooks/`, 404; the handbooks
are on `reg.unizulu.ac.za`). No 2027 document of UNIZULU's own was found: its apply page still links the 2026 brochure.

## Why the CAO is the source

UNIZULU takes applications only through the CAO, and its own "Applying to Study" guide sends applicants to the CAO's
programme list to find its programmes. The CAO's 2027 rows are newer than anything on UNIZULU's site and differ from
its 2026 documents in places (below), so every requirement cites a CAO source; UNIZULU's 2026 brochure and handbooks
are the cross-check, and where they ask for more, an extras line says so and names the document. Each programme's
YAML comment gives its CAO code and page.

## Points

The pack's rule (six subjects, no Life Orientation, levels 1 to 7) is unchanged, and no programme has its own rule:
no faculty says it counts differently. But see "Check first" 1.

## The programmes

185 programmes, all with requirements (none `null`), all from the CAO:

- Commerce, Administration and Law (27): B Com in Accounting Science, in Accounting and (Management Information
  Systems); seven three-year B Com streams; eight four-year B Com Augmented streams; four B Admin streams; LLB; at
  Richards Bay, the Higher Certificate in Accountancy and diplomas in Co-Operatives, Logistics and Transport Management.
- Humanities and Social Sciences (22): 19 degrees at KwaDlangezwa; diplomas in Media Studies, Public Relations
  Management and Tourism Management at Richards Bay.
- Science, Agriculture and Engineering (95): three B Sc Agriculture degrees, two Consumer Science degrees, Nursing
  Science; 36 three-year B Sc two-major streams, 35 B Sc Augmented and 12 B Sc Foundation streams (four years), each a
  separate CAO code; four B Eng degrees and diplomas in Sport and Exercise Technology and Hospitality Management at
  Richards Bay.
- Education (41): Foundation Phase (handbook), and from the CAO's new-programmes page 38 Senior and FET Phase
  combinations and two Intermediate Phase degrees, closing 30 Nov 2026 (said in extras).

Selective (3): BA (Psychology) (interview), BA in Drama, Theatre and Performance (auditions, then an interview),
Bachelor of Social Work (selection interviews). "Preference to first-choice applicants" and "first preference to
those who haven't studied elsewhere" notes are extras, not selection.

Left out: three programmes in UNIZULU's 2026 documents but in neither CAO list for 2027 (the four-year B Com
Augmented in Management Information Systems, the BSc Human Movement Science with Zoology, and the Higher Certificate
in Marketing, which only FCAL's table names; the Richards Bay handbook doesn't); advanced and postgraduate
programmes and the PGCE; and the Senior Certificate, N-certificate, NC(V) and mature-age routes.

## Approximations

- "Engl 4 and five 20 credit subjects": only English is checked; the five are any subjects, counted in the points.
- IsiZulu Home Language at 4 is checked as `other_language: 4`, with a line saying it must be IsiZulu.
- "Engl HL 4/FAL 5" (Social Work) and "HL 4/FAL 3" (Sport and Exercise Technology, B Sc Foundation Botany and
  Microbiology): English at the lower level, the full rule in extras.
- Diploma in Tourism Management: Tourism 4 and "any other four subjects from the listed combination ... at min level
  of 4" is checked as any four other subjects at 4; the list is in extras.
- Diploma in Hospitality Management: "four 20 credit subjects (excl lang) 3" is checked as any four at 3; extras say
  they can't be languages.
- B Eng: Mathematics at 65% (`subject_min_percents`), as the CAO and the FSAE handbook say.
- Names are the CAO's, with its own abbreviations written out ("B Com", "Dip", "SP" for Senior Phase). Four B Ed names
  carry their CAO code, because the CAO gives two codes the same name (see "Check first" 2).

## Check first

1. **The points scale.** It stops at 7 points from 80%, but its own source (the 2018 policy, section 5.4), the 2022
   Applying to Study guide (p4), the FCAL (p37) and FEDU (PDF p20) 2026 handbooks and the brochure's example (p1:
   an additional language at 90% = 8 points, though its own table puts 80-100% at level 7) all give **8 points for
   90-100%**; the CAO's default does too. Only the FSAE handbook
   (p12) stops at 7. Done on 15 Oct: the scale now has `{min_percent: 90, level: 8}`, so FSAE is the one faculty
   whose own table differs.
2. **Duplicate B Ed codes** on the new-programmes page: ZU-M-ILF and ZU-M-ILI share a name (English FAL Senior
   Phase, Geography, Tourism), but ILF also asks for IsiZulu HL 4; ZU-M-ILZ, ZU-M-ILW and ZU-M-IEJ are all English
   FAL, History and Tourism, and ILW asks for no History. ZU-M-ILK (IsiZulu HL FET and Senior Phase, Geography) names no
   English, while the FEDU handbook asks for two languages at 4, one of them English.
3. **The FEDU 2026 handbook** says there was no 2026 intake for the Intermediate Phase and Senior/FET B Eds; the
   CAO's page lists them for 2027. Confirm with UNIZULU that they run.
4. **CAO 2027 against UNIZULU's 2026 documents** (each also in extras): Correctional Studies English 4 (brochure and
   handbook: 5); Tourism Management needs Tourism (not in the 2026 documents); both Consumer Science degrees and
   Hospitality Management, Life Orientation 4 in the 2026 documents only; Political and International Studies,
   English, Geography and History 5 in the handbook (which also says both "30 points" and 26); the FHSS handbook's level
   4 in five subjects (some entries say "level 4 (40-49%)"); Information Science and Library Science, English First
   Additional at 5; B Sc Augmented (Botany and Microbiology) has no Life Sciences in the CAO row; Microbiology or
   Biochemistry with Human Movement Science ask Physical Sciences 4 (CAO) against 3 (FSAE rule S1.3.1(c)).
5. **Nursing:** the 2026 brochure says Mathematics 3 or Mathematical Literacy 4; the CAO and the FSAE handbook (p15,
   p20) say 4 or 6. The pack uses 4 or 6.

## For the coordinator

- Added on 15 Oct: the CAO's dates page (printed p13) says all UNIZULU on-time applications for 2027 close on 31 Oct
  2026, and its new-programmes list gives the 40 new B Eds 30 Nov 2026: the pack's 2027 window now has both. No
  opening date is published, so the app says to check.
- Richards Bay programmes say so in extras; the pack has no campuses yet.
- Not added as bridges: the FSAE handbook's route from the Diploma in Sport and Exercise Technology to the BSc in
  Human Movement Science (p16), and from B Sc (Augmented) modules into the B Eng (p19-20).
- FCAL (p38-39) calls its quotas "extremely strict" and may add interviews or placement tests; not marked selective.
- The pack's header gained one sentence, and a comment above `points_rules` points to "Check first" 1.
