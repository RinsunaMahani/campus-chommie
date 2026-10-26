# Release follow-up — 26 October 2026

This is the current queue; older checklists in HANDOVER and OPEN_QUESTIONS also contain historical decisions.
Source acceptance is resolved: dated official university/funder/government/venue publications are sufficient.
Incomplete packs stay unreleased, and contradictory facts remain unresolved.

## Completed in PR #106 and the follow-up branch

- Combined latest main (through PR #105) with the data/language changes, preserving the week-review and Outdoors work.
- Twelve additional programme rules and named-language Home/First Additional checks; marks remain transient.
- Calendar, support and activity entries at all 26 universities, with mixed calendar years explicitly reported.
- Added five contacts from official CPUT/UFH publications: 98 total. Every listed campus has at least one service
  or central telephone contact, not necessarily an on-site office or every service category.
- Added 15 UJ 2027 academic periods from its official indexed PDF and three CUT 2027 registration/change windows from its current page.
- SPU's user-supplied APS table matched its official image. The subject-count rule is still absent, so no guessed total.
- Updated submission claims: college-register lookup is built, official-source acceptance replaces universal
  human sign-off, and test totals must refer to a dated run rather than a permanent promise.

## Checks and remaining work

| Area | Evidence and next step |
|---|---|
| PR status | PR #106 merged with passing CI while this follow-up was being tested. Further support/calendar/documentation changes are on `rinsuna/release-data-followup`, integrated with main through PR #109. |
| Public availability | On 26 October the API `/api/v1/ping` and web root both returned HTTP 200. Public `/universities` returned 26 institutions and `/colleges` returned a total of 357 entries, both with success envelopes. This verifies public reads, not authenticated journeys or deployment of the PR. |
| Android/web release | After merge, confirm deployed revisions, build an updated APK and exercise course finder, sign-in, week, money, support and account deletion/export with test accounts. No deployment or account changes were performed during this follow-up. |
| Google sign-in | Implementation and public web client ID exist. Confirm production backend audience, web origins and Android signing fingerprint through an actual sign-in on each platform. Do not publish secrets. |
| WhatsApp | Implementation exists. Meta credentials, recipient eligibility, webhook verification and LINK/WEEK/rep confirmation need a live test with an authorised account/number. No messages were sent. |
| Programme rules | Of the 19 records remaining after PR #112, eight now have complete subject rules, two have partial rules and four have documented university-assessed routes. Five still lack usable requirements; seven including partial records need clarification. Official-source precedence choices are recorded in research/official-source-precedence-2026-10-26.md; DATA_READINESS lists the current gaps. |
| Calendar/activity coverage | Added 21 SPU 2027 entries from the final official calendar. Other 2027 calendars, allowance schedules and campus-local activities remain partial. |
| SPU provenance | Official APS image accepted; separately hosted Adobe prospectus still needs its exact official-link provenance confirmed. |
| Privacy/legal | Audit records still include email/IP and an append-only database guard prevents ordinary deletion. Retention requires an explicit policy and a designed migration/job, not merely a scheduled DELETE. Privacy/Terms still need legal review. |
| Ownership | Confirm the expected written rights transfer before changing LICENSE or REUSE permissions. |
| Translations | Choose languages and obtain fluent review before exposing translations. Language-subject assessment is already supported and is a separate feature. |
| Submission | Record/export the final videos and deck using the released build. Scripts and guides are preparation, not proof those artefacts were submitted. |

No production database, credentials or personal student records were accessed. Public HTTP checks do not establish
whether Google or WhatsApp is configured; that status must not be inferred from empty local defaults.

## Local validation

Before main advanced through PR #109, the combined branch passed 1,673 backend tests (two existing Flask-Migrate deprecation warnings),
40 mobile suites / 305 tests, TypeScript, Expo lint and the web production export.
After the final UJ/CUT calendar additions, all 596 affected engine, architecture, catalogue and support tests passed.
The data validator reports zero errors; incomplete-pack and OSM review warnings remain.
GitHub CI must also pass on the pushed revision before merge.

After integration with main through PR #109: 574 engine/architecture checks and 29 affected API checks passed.
The API checks were rerun after restarting the isolated test database; the initial connection errors were environmental.
