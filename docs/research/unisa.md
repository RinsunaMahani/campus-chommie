# University of South Africa (Unisa): course list research notes

Agent draft, read on 15 Oct 2026 for `backend/data/universities/unisa.yaml`. Nobody has checked these values yet:
release stays false until a person has compared each one with its source. Staff names, phone numbers, email
addresses and banking details on the qualification pages are left out on purpose.

## What I read

All from `www.unisa.ac.za`. Its `robots.txt` returns 404 (no file), so nothing is disallowed for any user agent.
I used curl's own user agent and waited between requests.

| Source id | Page | Used for |
|---|---|---|
| s-unisa-all-qualifications | [All qualifications](https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Undergraduate-qualifications/Qualifications/All-qualifications) | the list of qualifications by level (448 links) |
| s-unisa-q-&lt;code&gt;[-&lt;stream&gt;] (167) | each qualification's own page under All qualifications | the "APS/AS" figure and the "Qualification admission requirements" text of every programme |
| s-unisa-2027 | [2027 Unisa application information](https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Undergraduate-qualifications/Whats-new-for-2027) | "The minimum APS score differs from college to college, and from qualification to qualification. Please refer to each qualification" |
| s-unisa-admission | [General admission requirements](https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Undergraduate-qualifications/Qualifications/General-admission-requirements) | the APS rule already in the pack (six 20-credit subjects, no Life Orientation, 42 at most), unchanged |
| s-unisa-rules-2026 | [2026 Unisa Rules for Students](https://www.unisa.ac.za/static/myunisa/Content/Learner%20support%20&%20regions/Documents/Unisa%20Student%20Rules_2026.pdf), page 2, rule 1 | "The university provides tuition in English" (see approximations) |

I found the rules PDF's address through a web search limited to unisa.ac.za, then downloaded and read the PDF itself
from Unisa. Also read, not cited by a programme: the [Apply for admission](https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Undergraduate-qualifications/Apply-for-admission)
page ("I meet the minimum academic points score (APS) for my qualification(s) of choice") and the FAQ page.

The qualification pages carry no date. The general admission page (last modified 7 Aug 2026) and the 2027 page speak
of the 2027 academic year, and applications for 2027 are closed (17 Aug to 9 Oct 2026), so these are the pages
applicants used for 2027.

**A fetching note, not a block.** Unisa's web firewall answered "Request Rejected" for the 322 page addresses that
contain an en dash ("(90093 – FIP)") because my first pass sent the dash unencoded. Sending the same addresses
percent-encoded, as a browser does, returned every page (HTTP 200). Nothing was blocked; the source URLs in the pack
are the percent-encoded ones.

## Programmes (167, all with requirements)

19 higher certificates, 29 diplomas and 119 bachelor's degrees. Every `min_points` is the qualification page's
"APS/AS" value, on the pack's APS scale. None has `requirements: null`.

- **Bachelor of Arts (99311).** Unisa lists the BA (General) and 215 pairs of majors as separate pages of one
  qualification. All 216 ask the same (APS 20, 50% in the language of teaching and learning), so the pack has one
  `ba` entry citing the BA (General) page. One major page (Psychology & Arabic, PSA) shows "APS/AS: 0" with the same
  text: a page error, not used.
- **Streams kept separately** where Unisa gives each its own page: the three Higher Certificate in Education streams,
  the BCom specialisations, the six Consumer Science streams, the three Intermediate Phase and 27 Senior Phase and FET
  BEd subject combinations (they differ: Mathematics 50%, Mathematics and Physical Sciences 50%, Mathematics 50% or
  Mathematical Literacy 60%, or language only), the 16 BSc major pairs and the Agricultural Science, Environmental
  Management and Life Sciences streams.
- **Left out:** the Diploma in Explosives Management (98222), because Unisa requires pre-approval and "proof of current
  employment in the explosives industry" (only for people already working in the field); advanced certificates,
  advanced diplomas, postgraduate certificates and the postgraduate diploma.
- **Selective (5 kinds):** the Bachelor of Social Work and the Higher Certificate in Social Auxiliary Work ("a
  selection qualification", testimonials, police clearance), the BA in Visual Multimedia Arts and the two BEd Art
  combinations (a portfolio and a permission letter from the Department of Art and Music).

Each requirement keeps only the NSC route. The Senior Certificate, NC(V), N4, higher-certificate and RPL routes on the
pages are left out (a school-leaver applies with an NSC), except the N4 line for the engineering diplomas, kept in
extras.

## Approximations

1. **"The language of teaching and learning" stored as English.** Almost every page asks a percentage in "the language
   of teaching and learning" without naming it. Unisa's 2026 Rules for Students (rule 1) say "The university provides
   tuition in English", so it is stored as `english`, with an extras line quoting Unisa's words. Pages that name
   English (engineering diplomas, BA Psychology, BSW) are stored as they say.
2. **Percentages as NSC levels.** Every percentage on the pages falls on an NSC level boundary (30% = 2, 40% = 3,
   50% = 4, 60% = 5, 70% = 6), so they are stored as levels.
3. **Pass type in extras.** Higher certificates: an NSC; diplomas: "Diploma endorsement"; degrees: "Degree endorsement".
   The engine doesn't check the pass type.
4. **BSc Physical Sciences.** The science pages ask 50% in Physical Sciences or Technical Sciences "if any Physics or
   Chemistry modules form part of the curriculum". I made it a requirement only where the major itself is Chemistry
   or Physics (9 of the 98801 pairs and Environmental Management: Chemistry); everywhere else it is an extras line.
   Life Sciences and Agricultural Science curricula may well include Chemistry: not checked.
5. **BSW "60% for a further four content subjects"** is stored as `additional_minimums: [5, 5, 5, 5]`; whether Unisa
   counts Life Orientation as a content subject isn't stated.
6. **APS/AS is the minimum.** The qualification pages label the figure only "APS/AS"; the 2027 page and the Apply page
   call it the minimum APS for each qualification, which is how it is stored. No programme has its own points rule.

## Check first

1. That "APS/AS" on a qualification page is the minimum APS for 2027 (and what "AS" stands for).
2. The English mapping (approximation 1), and the BSc Physical Sciences split (approximation 4).
3. Unisa's 2027 page says places are limited and that selection uses "a calculation of your individual points score",
   which also weighs the school attended and other personal factors Unisa lists. The app can only check the published
   minimums, so meeting them doesn't mean a place; the pack's `how` line already says so.
4. The 2027 page still says "you will not automatically be accepted to study through Unisa in 2019" in one sentence
   (an old line beside the 2027 one); harmless, but a sign the pages are updated piecemeal.
5. The Diploma in Adult and Community Education and Training (90189) is kept as a school-leaver option because its
   NSC route asks only a diploma pass and 40%: confirm it isn't meant for people already teaching adults.
6. The Diploma in Mining Engineering's extra "Engineering and Technology or Computer subject" (extras only).
