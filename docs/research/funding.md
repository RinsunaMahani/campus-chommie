# Funding: bursaries, merit awards and loans

Research for the funding pack (`backend/data/national/funding.yaml`), read on 10 and 11 Oct 2026 by Rinsuna's coding
agent from each funder's own pages. Nobody has checked these values yet: every source says
`verified_by: "agent draft, needs human check"`, and the pack keeps `release: false` until a person has compared each
value with its source. NSFAS's own notes are in [nsfas.md](nsfas.md).

**Where the funders came from.** Sites that list bursaries (Graduates24, ZABursaries, UniApplyForMe, StudentRoom and
others) only helped us find names. Every fact in the pack comes from the funder's own site or document. A test
(`test_no_fact_comes_from_a_site_that_lists_bursaries`) fails if a listing site ever becomes a source.

**What the app does with them.** `GET /funding` lists every funder with its status today, "N open now, N closing
soon", and filters by field, status, kind and stage. `GET /funding/<id>` gives one funder in full. Each course-finder
choice shows up to five funders whose fields match the programme's, for first-years, usable at that university.
Eligibility is shown in the funder's own words and never asked: the learner decides.

## The funders

Dates are for 2027 funding unless stated. "Seen closed" means the funder's page said applications were closed, with
no dates, when we read it on 11 Oct 2026.

| Funder | Kind | For | Status on 11 Oct 2026 | Sources |
|---|---|---|---|---|
| NSFAS | Bursary (every plan) | Any field; public universities and TVET colleges | Open: 18 Sep to 31 Oct 2026, 23:59 | [nsfas.md](nsfas.md) |
| NSFAS loans (missing middle) | Loan | Households above the NSFAS threshold | How to apply for 2027 not published | Minister's launch speech, 18 Sep 2026 |
| Funza Lushaka (DBE) | Bursary | BEd only; teach a year for every year funded | Open: 1 Oct 2026 to 31 Jan 2027 (re-applications by 30 Nov) | Home page; 2027 application notes (PDF) |
| ISFAP | Bursary | Courses on each partner university's list (UP, TUT and SMU are partners) | Seen closed ("2026 apps have closed for the 2027 intake") | Students page; application portal |
| Thuthuka (SAICA) | Bursary | BCom Accounting (CA stream) | Closed 31 Aug 2026, 23:59 | SAICA's apply page; the fund's portal |
| National Treasury | Bursary | Accounting, economics, finance, law; 3rd year, Honours, Master's | Closed 30 Sep 2026, 12:00 | 2027 advert (PDF) |
| NDMC (CoGTA) | Bursary | Disaster management, fire technology / engineering | Closed 30 Sep 2026, 23:59 | 2027 advert; the bursary portal |
| Reserve Bank (SARB) | Bursary | Undergraduates, any field related to its work; under 30; 70% in June Grade 12 | Closed 30 Sep 2026 | 2027 scheme notice (PDF) |
| Allan Gray Fellowship | Bursary | Grade 12; commerce, science, engineering, law, humanities, arts (not medicine, vet or dentistry); at UP among 11 | Closed 30 Apr 2026, 17:00 | Fellowship page; 2027 application form (PDF) |
| GCRA (Gauteng) | Bursary | Gauteng residents aged 18 to 35, any field | 2026 round closed; 2027 dates not published | The bursary portal and its FAQ |
| Clicks Foundation | Bursary | BPharm, 2nd to 4th year; no obligations | Open: 1 to 31 Oct (every year, says Clicks) | The bursary page |
| CSIR | Bursary | Honours, Master's, doctorate in science, engineering, technology; work back | Closed 15 Sep 2026 | Bursaries page; July 2026 guidelines (PDF) |
| Harmony Gold | Bursary | Communities around its mines; any field (mostly mining) | Seen closed; 2028 opens October 2027 | Opportunities for students |
| Nedbank | Bursary | STEM and green-economy degrees, undergraduate or Honours | Seen closed; 2028 opens in 2027 | Graduates and bursaries |
| EY | Bursary | CA stream; a training contract of at least three years | Closed 30 Sep 2026 (1 Jul to 30 Sep) | Bursary page |
| HWSETA | Bursary | Health; through NSFAS and the university, not direct | Apply through the university | Access to funding; its replies under the 2026/27 advert |
| TUT Bursary and Scholarship Fund | Bursary | TUT students, especially the missing middle | Contact the fund | The fund's page |
| UP FLY@UP Assist | Merit award | First-time UP first-years with an 80%+ average | Automatic: no application | InfoGuide 2026, pp. 14-15 |
| UP funding database | Bursaries through UP | Any UP student | Register through UP | InfoGuide 2026, p. 13 |

## Choices made while building (for Rinsuna to confirm)

- **Field tags are our reading of the funder's words.** Nedbank's "STEM" became natural sciences, engineering,
  computing and mathematics; Allan Gray's "Arts" sits under humanities; HWSETA is tagged health sciences from its
  name. Funders that name no fields (Harmony, the Reserve Bank, ISFAP, GCRA) are "any field". A new tag,
  `disaster_and_fire`, covers the NDMC: no programme in our packs has it yet.
- **Clicks's year.** Clicks says applications run from 1 to 31 October every year and doesn't name the year funded.
  We read October 2026 as the round for 2027.
- **ISFAP is "seen closed",** from its application portal's own message, although listing sites still say it closes
  on 31 October. The portal's welcome text still describes 2025, so check with ISFAP.
- **CSIR is postgraduate only,** following its July 2026 guidelines. Its bursaries page also describes undergraduate
  requirements: check which is right.
- **The Reserve Bank's "how to apply"** points to its bursary page, not to the online form its notice gives (on a
  replit.app address, run by an outside bursary administrator). A person should decide whether the app may show that
  link.
- **UP's FLY@UP amounts are 2026's.** UP's web pages refuse automated reading, so the 2027 amounts on its funding
  page need a person to read them. Each line in the app says "In 2026".
- **Commercial lenders are left out.** UP's InfoGuide lists Fundi (a registered credit provider). The user chose
  non-profit and government loans only, so the pack has NSFAS's loan scheme and no commercial lender.
- **Race and other restricted criteria** (Thuthuka: "Black African or Coloured") are shown in the funder's words,
  never asked and never used to filter. The learner decides.

## Disagreements between official sources

- **NSFAS's closing date.** NSFAS's own page says 31 Oct 2026 at 23:59. The Minister's launch speech (gov.za, 18 Sep
  2026) and SAnews say 18 Nov 2026. The pack keeps NSFAS's own, earlier date until a person checks.
- **Funza Lushaka's age limit.** The home page says first-time applicants must be "30 years or younger"; the 2027
  notes say "below the age of 30" and give a cut-off date. The pack says "under the age of 30", from the notes.

## Not in the pack yet: leads to check on the funders' own pages

Readable pages not found, or no 2027 round published, on 11 Oct 2026:

- **State-owned companies:** Eskom, Transnet (its bursary page loads only in a browser), SANRAL (brochures from 2022
  to 2024 only), Rand Water, Airports Company South Africa.
- **Government:** the Department of Water and Sanitation (2024 form only), the land reform department (its 2027 form
  wouldn't download), MISA (2026 advert only), the Department of Agriculture, provincial health departments
  (Limpopo's nursing college intake is a college route, not a university bursary), City of Tshwane.
- **SETAs:** MICT SETA, BANKSETA, MERSETA and others fund through institutions and employers, like HWSETA.
- **Companies:** Sasol (its site loads only in a browser; its 2027 rounds closed in August and September),
  Anglo American, Sibanye-Stillwater, Exxaro, Implats, Investec (its page refused automated reading), Liberty, Old
  Mutual (its page wouldn't load), PwC, KPMG, Deloitte, Shoprite, Tiger Brands.
- **Foundations:** Studietrust, Moshal, Feenix (a crowdfunding platform for fees, not a loan), the Mastercard
  Foundation Scholars at UP.
- **Universities:** SMU's own bursary page lists only rounds from 2023 and 2024, some through listing sites. Its
  financial aid office is the place to ask; its contact details appeared only in a search result, so check them on
  SMU's registration notices. TUT's undergraduate funding page loads only in a browser.
- **Not funding for fees:** the Allan Gray Postgraduate Fellowship (closes 23 Oct 2026) is an entrepreneurship
  programme that doesn't pay academic fees.

Adding a funder: copy an entry in the pack, cite the funder's own page, run `python scripts/validate_data.py`, and add
a spot check to `tests/engine/test_packs.py` when it has dates.
