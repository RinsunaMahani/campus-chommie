# NSFAS: research notes

Agent draft, read from NSFAS's own website on 10 Oct 2026. Nobody has checked these values yet. A person compares each
one with its source before `backend/data/national/funding.yaml` gets `release: true` (CLAUDE.md, "Facts: never invent
them"). Anything missing stays `null` and the app shows "Not verified yet".

- **Source** gives a source id from the table below. `funding.yaml` uses the same ids.
- **Check** marks a value that two places give differently.
- We never ask learners about income, disability or family circumstances. The pack shows NSFAS's own words, and the
  learner decides whether to apply.

## Sources

| Id | Page | Link |
|---|---|---|
| s-nsfas-apply-2027 | NSFAS 2027 Applications: how to apply | [page](https://nsfas.org.za/content/how-to-apply.html) |
| s-nsfas-home-2027 | NSFAS 2027 Applications (home page) | [page](https://www.nsfas.org.za/content/) |

## Applications for 2027 funding

| Fact | Value | Source |
|---|---|---|
| Opens | 18 September 2026 | both |
| Closes | 31 October 2026 at 23:59 South African time | both |
| Late applications | None: "Late applications cannot be accepted"; "Nothing can be submitted after this date" | s-nsfas-apply-2027 |
| Fee | Free: "No application fee", "There is no fee at any stage" | both |
| Where | myNSFAS (my.nsfas.org.za) or the official NSFAS app; "no one needs to apply on your behalf" | both |
| Steps | 1. Create a myNSFAS profile with your South African ID number, cellphone number and email address (an OTP activates it). 2. Fill in personal and household information, give consent, upload documents; you can save and finish later. 3. Submit, save the reference number and track the status on myNSFAS | both |
| Uploads | PDF or JPEG, up to 20 MB each, clear and readable; phone photos are fine if every corner shows and the text can be read | both |
| Missing information | 30 working days to answer a request for more information | s-nsfas-home-2027 |
| Outcome | "Funding eligible": funding is confirmed once you register at a public university or TVET college. "Unsuccessful": the reason shows on myNSFAS, and you can appeal within the appeal window | s-nsfas-apply-2027 |
| Application drives | Provincial drives from 5 to 24 October 2026, with venues on the home page's map | s-nsfas-home-2027 |
| Contact | Toll-free 08000 67327 (the home page writes it 0800 067 327), USSD \*134\*67327#, info@nsfas.org.za; fraud reports to speakup@nsfas.org.za | both |

Today (10 Oct 2026) NSFAS's 2027 window is open for 21 more days. It is the one application in the course finder's
plans that a Grade 12 learner can still make for 2027.

## Who can apply

From s-nsfas-home-2027, "Who can apply":
- South African citizens studying or planning to study at a public university or TVET college
- SASSA grant recipients
- Students from households earning up to R350 000 a year
- Students with disabilities from households earning up to R600 000 a year

TUT's 2027 guide (p8) gives the same amounts. NSFAS's policies page lists eligibility criteria only up to 2025, and the home
page links to "the full criteria". The how-to page has its own four-question eligibility check ("Nothing you enter is
stored or sent anywhere"). The app links to NSFAS instead of asking any of this.

## Documents

Forms, all printed, filled in by hand in capital letters and black ink, with no correction fluid and no electronic
signatures (s-nsfas-home-2027):
- **Consent form (APP2027):** everyone. Signed by the applicant (two signature blocks) and by every parent, legal
  guardian or spouse on the application. Without it the application can't be submitted.
- **Declaration form:** applicants aged 34 or younger; confirms parent or guardian details. **Check:** the home page
  also describes it as needed only when the declared people don't match Home Affairs records.
- **Disability annexure:** completed with a medical practitioner, merged into one file with the medical report.
- **Orphan or vulnerable child declaration:** applicants under 18; completed by a social worker.

By circumstance (s-nsfas-home-2027): ID or birth certificate (everyone); payslips, a UIF statement or an affidavit
when a parent, guardian or spouse earns an income; nothing for SASSA grants (checked with SASSA); death certificates;
a divorce decree or settlement agreement; a marriage certificate and the spouse's ID; proof of legal guardianship from
a court; a retrenchment letter.

**The eight most common reasons a document is sent back** (s-nsfas-apply-2027): a cut-off corner or edge; a blurry,
dark or glaring image; a missing or electronic signature; pencil or coloured ink; correction fluid or an uninitialled
change; last year's form; one page of a two-page form; names or ID numbers that don't match the ID.

## Warnings NSFAS gives

- "Never pay anyone to apply. NSFAS will never ask for your password or OTP." (both)
- "Use nsfas.org.za and my.nsfas.org.za only. Check the spelling in the address bar before you sign in."
  (s-nsfas-apply-2027)
- "Ignore WhatsApp forwards, social media accounts and agents offering to speed up your application or upload
  documents on your behalf." (s-nsfas-home-2027)

## Gaps and inconsistencies

- **WhatsApp number.** The how-to page's header says "WhatsApp 0800 067 327" (the toll-free number); TUT's 2027 guide
  gives 063 093 5671. Left out of the pack until a person checks.
- **Portal links.** The how-to page's own links to myNSFAS are misspelt `httpss://my.nsfas.org.za`; the page text and
  the home page give `my.nsfas.org.za`, which the pack uses.
- **Reference numbers.** The how-to page's demonstration tracker uses "2027 followed by six digits"; not used in the
  pack, since it may describe only the demonstration.
- **2028 funding:** not published.
- **Allowance amounts and payment dates for 2027:** not researched yet (needed for the money features, F4).
