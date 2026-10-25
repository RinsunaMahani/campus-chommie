# CPUT: undergraduate programmes for 2027 (research note)

**24 October update:** the user-supplied 2027 PDF fills 40 of the 44 missing requirement records described below. See [the source review](2027-local-prospectuses.md) for current evidence and unresolved rules. The following notes preserve the earlier online-source audit.

Agent draft, 15 Oct 2026. Pack: `backend/data/universities/cput.yaml`. Nothing here has been checked by a person yet;
`release` stays `false`.

## What was read

| Host | robots.txt | Used |
| --- | --- | --- |
| www.cput.ac.za | Allows everything except Joomla system folders (`/administrator/`, `/api/`, `/components/`, `/modules/` and so on; the site's `/component/...` prospectus link wasn't used). The certificate chain verified normally on 15 Oct (no `-k`). | Yes |
| prospectus.cput.ac.za | Same Joomla rules, then several `User-agent: * / Disallow:` blocks (allow everything). Those blocks also name a sitemap at a bare IP address (`https://196.21.120.9/th/?sitemap.xml`), which looks out of place; worth mentioning to CPUT. | Yes |
| issuu.com, e.issuu.com | robots.txt answers **403** | **No** |

Documents read (all retrieved 15 Oct 2026, curl's own user agent):

1. **CPUT Online Prospectus** (`s-cput-online-prospectus`), https://prospectus.cput.ac.za/. The six faculty lists
   (`index.php/link-to-courses?f=20|60|100|140|180|220`) and every undergraduate course page
   (`index.php/course-details?q=<code>&f=<faculty>`; the code is noted beside each programme in the pack). The course
   pages say their fees are 2026's "and subject to change for 2027", so they are the pages CPUT shows for the 2027 intake.
2. **APS Method 2** (`s-cput-aps-method-2`), the image the engineering course pages show. Some engineering pages point at
   a copy under `/storage/faculties/engineering/online_prospectus/APS Method 2.jpg`, which answers 404; the copy under
   `/images/Faculties/Engineering-and-the-Built-Environment/Documents-and-Resources/APS-Method-2.jpg` works.
3. **Health and Wellness Sciences APS tables** (15 images, `s-cput-aps-<code>`), shown on each health course page. The
   page wraps each image in an Outlook "safelinks" address; I didn't fetch through that host, but took the image's own
   address on www.cput.ac.za from it and fetched that.
4. **Department pages** on www.cput.ac.za/faculties/... (all 52 department pages and their sub-pages were read; only these
   had first-year requirements): Accounting Sciences, Retail Business Management, Unit for Applied Economics and Real
   Estate, and Applied Design (Fashion, Jewellery, Product Design, Visual Communication Design, Design ECP).
5. **2027 supporting documentation** (`s-cput-supporting-docs-2027`, PDF, "Updated: 4 May 2026"): extra documents per
   programme (motivational letters, the sport questionnaire, employment letters).

## What a person should download in a browser

Issuu blocks bots, so these official CPUT documents weren't read. They should fill most of the gaps below:

1. **CPUT 2027 Undergraduate Prospectus**: Issuu document `2027_prospectus` (user `cput6`), embedded on
   https://www.cput.ac.za/study-at-cput/undergraduate/apply/step-1. Most important: it should hold the requirements
   the blank course pages lack, and how each faculty counts its APS.
2. **FBMS 2027 Diploma Prospectus**: Issuu document `2027_fbms_diploma_prospectus`, embedded on
   https://www.cput.ac.za/faculties/fbms/courses/2027-diploma-prospectus. Needed for 24 business programmes.
3. **Faculty of Education application guidelines**: Issuu document `faculty-of-education-application-guidelines`,
   embedded on https://www.cput.ac.za/faculties/fed/resources. Needed for the B Ed in Senior Phase and FET Teaching.

## Programmes: 119, of which 75 have requirements

- Applied Sciences 25, Business and Management Sciences 29, Education 3, Engineering and the Built Environment 27,
  Health and Wellness Sciences 15, Informatics and Design 20 (including four design extended programmes that have a
  department page but no course page).
- **`requirements: null` (44)**: the course page has no admission requirements (or only a heading) and no department
  page gives them. Business: all except Accountancy (and its ECP), Retail Business Management and Real Estate.
  Education: B Ed Senior Phase and FET. Engineering: Clothing and Textile Technology, Construction, Industrial
  Engineering, Mechanical Engineering (with their ECPs) and Mechatronics. Informatics and Design: the three ICT
  diplomas, the ICT higher certificate (its page starts "This programme is offered in collaboration with" and stops),
  Public Relations, Film Production (its page says "The APS is calculated as follows:" and stops), Journalism,
  Photography, Urban and Regional Planning.
- **`min_points: null` (3)**: Real Estate (its page gives no APS) and the two B Ed degrees (CPUT states no APS).

**Left out**: Diploma in Grade R Teaching and Diploma in Early Childhood Care and Education (the 2027 supporting
documents make a letter confirming employment compulsory, so they're for people already working in the field);
Bachelor of Health Sciences in Medical Laboratory Science (articulation), for qualified medical technologists; the
"non-diploma/non-degree" codes (`*0001`, BIO001); advanced diplomas, honours, postgraduate certificates and masters.

## Points

No pack-wide rule: CPUT counts its APS differently by faculty, so `points_rules` stays `null`. I replaced the
`points_note` ("CPUT's points method wasn't found"), which is no longer true.

- **Health and Wellness Sciences** states it on every table: "the percentage score for the 6 highest scoring subjects,
  including the above required subjects (excluding Life Orientation), adding up all the raw scores, and dividing by 10".
  Each of the 15 health programmes therefore carries its own `points_rules` (6 subjects, Life Orientation excluded,
  0.1 point per percent), citing its own table. These are the only CPUT programmes the app can check now.
- **Engineering** uses Method 2: English, Mathematics × 2, Physical Sciences × 2 and the next best subject, as
  percentages, divided by 10. The engine can't express doubled subjects, so these programmes keep their minimums (30 or
  36, maritime ECPs 31) with a line in extras saying how CPUT counts them, and show as "can't check yet".
- **Applied Sciences** says only "All subjects are included in the calculation, except for Life Orientation" (in
  Agriculture's pages), without the scale; **Design** and **Business** pages give a minimum APS without the method. Their
  minimums are recorded on CPUT's own scale, like SPU's pack.

## Approximations

1. **ECP concessions** (Biotechnology, Analytical Chemistry, Marine Science, Chemical, Civil, Computer and Electrical
   Engineering ECPs, Medical Laboratory Science ECP, Emergency Medical Care ECP): CPUT accepts one subject a little
   below the level asked if the others are met, which the schema can't express. The pack keeps the stricter published
   levels and puts the concession in extras.
2. **Ranges**: where CPUT gives an APS range for an ECP (30 to 37, 30 to 34, 27 to 29, 31 to 35), `min_points` is the
   lower end and the range is in extras.
3. **Diploma in Agriculture (ECP)**: its own page is blank. The points (30, or 31 with Technical Mathematics) come from
   the Diploma in Agriculture page, which gives them in brackets; the subjects are copied from that page too.
4. **Bachelor of Food Science and Technology**: "any two other subjects (excluding languages) at level 3" is
   `additional_minimums: [3, 3]`, which can't exclude languages; extras say so.
5. **B Ed Foundation and Intermediate Phase**: "level 4 in four subjects from the subject list" is
   `additional_minimums: [4, 4, 4, 4]`; the language rules are in extras.
6. **Engineering "English (First language)"** is keyed as `english` at the level given, with an extras line.
7. **Names**: CPUT's course pages use abbreviated names ("DIP: CONSUMER SC IN FOOD &NUTRITION(ECP)"). I wrote them out
   in full ("Diploma in Consumer Science in Food and Nutrition (Extended Curriculum Programme)"), using the health
   tables' and department pages' fuller names where they exist. The four design extended programmes are named after
   the department's headings ("ECP Fashion" became "Design Extended Curriculum Programme: Fashion").
8. **Fields**: Nautical Science is tagged `engineering` (there is no maritime tag).
9. **Selective**: all health programmes (each table says places are limited, first choices come first, and gives the
   number of places, recorded as `places`), the B Ed Intermediate Phase (further selection round) and the design
   diplomas (the Design ECP page says the mainstream diplomas add portfolio or entrance test requirements).

## Check first

25 October follow-up: the supplied official 2027 PDF fills 42 of the 44 previously empty requirements.
Banking and Senior/FET BEd remain unresolved. Clothing/Textile routes with unpublished Technical Mathematics
APS return only a subject check. See [the current review](2027-local-prospectuses.md) for the import and
[coverage queue](../DATA_READINESS.md) for current gaps; the list below records the earlier research questions.

1. Download the 2027 prospectus from Issuu (above) and fill the 44 programmes with `requirements: null`, starting with
   Business and Management Sciences.
2. Ask CPUT or read the prospectus for how Applied Sciences, Business and Design count their APS (levels or
   percentages, how many subjects). With that, programmes could get their own rules like the health ones.
3. The design diplomas: the department pages give APS 28 and the subjects, but no portfolio or test for the mainstream
   diploma, while the ECP page says the mainstream has them. Check which applies for 2027.
4. Diploma in Environmental Management (ECP): CPUT's sentence "students may be admitted to the ECP if they have at least
   scored 50% for Geography or Life Sciences, and at least any other subjects except Life Orientation" is garbled; only
   its first half is in the pack.
5. Higher Certificate in Emergency Medical Care: its course page text lists only the old Senior Certificate and NC(V)
   rules; the NSC figures come from the table image on the same page.
6. Whether the Diploma in Early Childhood Care and Education is really closed to school-leavers (its own page says an
   NSC with diploma endorsement is the minimum; the supporting-documents PDF makes an employment letter compulsory).
