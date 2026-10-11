# Other apps and services: what they do and where we differ

For the pitch deck and to steer what we build. Rinsuna tried UniApplyForMe and UniAPS on her phone on 10 Oct 2026
(first section). The rest comes from store listings and the services' own pages, read by an agent the same day.

## Tried first-hand (Rinsuna, 10 Oct 2026)

**UniApplyForMe: very good, and free.** What it does well:
- **Onboarding:** seven steps, one topic per screen, with a progress bar.
  - The steps: NSC or NCV; name and photo; date of birth, gender and race; province and city; school, status
    and matric year; subjects; then a review screen with Edit on every section.
  - The subjects step asks which period the marks are from (Grade 11 final to Grade 12 term 4). It offers the
    full NSC list with language levels and shows the level as you type the mark.
- **Home:** a greeting by name, then:
  - "View my APS"
  - counters (27 universities, 44 colleges)
  - "Upcoming deadlines" cards with a red day count (bursaries closing in 5 and 6 days)
  - a WhatsApp channel for bursary alerts and tips
  - your APS at each university
  - bursaries and universities
- **APS:** "27 universities matched", each university's APS by its own method. The same marks gave 30 at the first
  six listed and 39 at CPUT and UNIVEN.
- **Courses:** 1 844 university courses and 1 106 college programmes, TVET and private. It has a "May qualify only"
  filter, and cards show the minimum APS, the years and "May qualify".
- **Funding:** 280 bursaries, "14 open now" and "2 closing soon", each with days left, fields and a bookmark. An
  "Alternative funding" tab lists a student loan.
- **Institutions:** universities and colleges with photos, type, the application fee or "Free to apply", and a
  "Private higher education" tag.
- **Profile:** editing marks, saved items, a file converter for UNISA's unnamed downloads, and donations ("free for
  every student... help keep it running").

**What it doesn't do, or does in a way we won't:**
- **Nothing after acceptance.** No class deadlines, workload, money or campus support.
- **Selection isn't flagged.** Stellenbosch's BSc Physiotherapy showed "May qualify" against "APS 60+" for 65% in
  every subject. The card says nothing about subject requirements or selection. **To check:** open that card and
  see whether it explains why.
- **It asks for a lot of personal information:**
  - date of birth, gender, race, school and city, and a photo "others will see"
  - race marked "Required for NSFAS and most bursary applications"; NSFAS's own "Who can apply" list doesn't
    mention race ([nsfas.md](nsfas.md))
  - marks kept in a profile, for learners many of whom are under 18
- University logos and campus photos throughout.

**UniAPS: poor.** It bills itself as a companion to "track exams, manage marks, and connect with peers". In practice:
- Marks are entered with sliders and a certificate choice (B, D or H). The home screen shows the average, highest and
  lowest mark.
- It sells "clicks" to spend in the app:
  - from R2,29 for 5 up to R17,99 for 22, or premium from R13,99
  - or earned with "Watch & Earn" videos and a "Daily Karma Reward"
- There's a shopping advert on the home screen.

## What exists (from listings and official pages)

| App or service | What it does | What it doesn't | Source |
|---|---|---|---|
| **UniApplyForMe** (says it's run by a registered non-profit) | As above: APS at every university, courses and college programmes, bursaries with deadlines, NSFAS information | Anything after acceptance; submitting applications (the listings don't say it does) | first-hand; [Google Play analytics](https://www.similarweb.com/app/google/za.org.apply.mobile/) |
| **UniAPS** | Marks and APS behind a paywall of "clicks" and adverts | Free use; plans, funding, support | first-hand; [listing](https://mwm.ai/apps/uniaps/1623573015) |
| **University Qualifications** (iPad; 2 ratings) | Enter your APS, see the courses you qualify for; a prospectus feature and deadline tracking | Per-subject requirements, plans, funding, support | [App Store](https://apps.apple.com/us/app/-/id6535647012) |
| **NSFAS's own app** and myNSFAS | Applying for NSFAS and tracking the application; a third-party guide says it sends payment-date notifications | Courses, admissions, budgeting, studies | [nsfas.org.za](https://www.nsfas.org.za/content/), [third-party guide](https://gauteng.net/nsfas/essential-features-of-the-nsfas-app/) |
| **DHET's Khetha and NCAP** (government) | Career advice by phone (086 999 0123), "please call me" or SMS (072 204 5056) and email; NCAP, a self-help portal | Admissions maths, applications, funding | [helpline](https://careerhelp.org.za/content/career-development-services/career-advice-helpline), [NCAP](https://ncap.careerhelp.org.za/) |
| **FundiConnect's Student Budget Coach** | An AI coach for stretching an allowance, shown as "Coming Soon" | Live use; study workload | [page](https://fundiconnect.co.za/student-budget-coach) |
| **Budgeting apps** (22seven, GoodBudget) | General budgets | Allowance timing, study workload | [guide](https://gauteng.net/nsfas/essential-features-of-the-nsfas-app/) |
| **Bursary and advice sites** (ZABursaries, VarsityWise, GoCareers) | Bursary lists and how-to-apply articles | Official status: they repeat funders' information, sometimes out of date | [ZABursaries](https://www.zabursaries.co.za/bursaries-closing-in-august-2026/), [VarsityWise](https://www.varsitywise.com/posts/how-to-apply-to-south-african-universities-online-) |

## Lessons for our screens (ideas for Mandla)

Learn from their patterns. Don't copy their data, wording or images.

1. **Onboarding:** one topic per screen, a progress bar, and a review screen with Edit before Finish. Ours asks only
   for the 18-or-older confirmation, the privacy notice, consent, university and campus.
2. **A personal home:** greet the student by name, then show the next deadlines as cards with a day count (red within
   7 days).
   - For learners, the plan's deadlines (`plan.apply.deadlines`) fit that pattern.
   - For students, the same cards can carry class deadlines, payment dates and university deadlines, so one design
     runs from Grade 12 to graduation.
3. **Marks entry:**
   - every NSC subject with its language level, mapped to our subject keys plus the "another subject" rows
   - the level shown as the mark is typed
   - "Which period are these marks from?"
4. **Counters and filters:** "N open now, N closing soon", a "Meets the minimum or better" filter, search, saved
   items.
5. **WhatsApp:** their broadcast channel shows learners want alerts there. Ours (M6, from Fri 23 Oct) is a private,
   two-way bot.
6. **Say "free" plainly.**

## What we won't copy

- **Asking race, gender, date of birth, school or city.** Our rules forbid it (CLAUDE.md, "Collect the minimum"),
  POPIA treats race as special personal information, and many learners are under 18. A funder that needs it asks on
  its own form.
- **A public photo** "others will see": we have no social features.
- **University logos and campus photos:** names in text only.
- **Paywalls, adverts and rewards** like UniAPS's "clicks": everything is free, and nothing in the app moves money.
- **"May qualify" on the points alone:** our tiers check subject minimums and either/or routes, mark selection
  programmes "Reach", and give the reasons and source on every card.

## Where we stand out

**Breadth is theirs.** UniApplyForMe covers 27 universities, 44 colleges and 280 bursaries, and shows application
fees. We shouldn't compete on breadth, and the planned 26-university directory would repeat what it
already does well.

**Depth before acceptance:**
- **A plan, not a list:** a goal, a published route in and a safer related choice, with reasons and sources.
- **Applications on today's date,** with NSFAS's countdown.
- **Funding matched to each choice** (built 11 Oct 2026): every choice in a plan shows the bursaries for its fields,
  and the funding list counts "N open now, N closing soon" like UniApplyForMe's. Fewer funders (19 to start), each
  from the funder's own page, with who can apply in the funder's words and nothing asked of the learner.

**After acceptance is the real gap,** and the challenge says it in its own words: "remain supported from acceptance
through graduation". Nobody above does it. The brief's F3 to F5 in the order of a student's year, with two proposed
additions marked *new*:
- **From acceptance to the first lecture** (*new*): accepting the offer (TUT: R1 500 within three days),
  registration dates, orientation, the first day of classes, and NSFAS funding confirmed at registration, all from
  the universities' own calendars and pages.
- **My week:**
  - class deadlines verified by a class rep
  - workload by week
  - the university's own deadlines that cost students marks or a place if missed (*new*): re-mark requests,
    exclusion appeals, module changes, graduation applications
  - marks and what's needed to pass
- **My money:** the runway with "what if the allowance is two weeks late", safe to spend, and the life fund.
- **Alerts and support:** when a heavy week meets short money, say so with actions, and point to campus support with
  verified contacts.

**Privacy for learners under 18:** the course finder needs no account and stores nothing.

**Our honest weaknesses**, to answer before a judge asks:
- **Three universities in depth, not 27:** a pack per university, so coverage grows by adding data, not code.
- **No person has checked our packs yet:** every unchecked pack says so in the app.
- **19 funders, not 280:** each is read on the funder's own page before it goes in, so the list grows slowly
  ([funding](funding.md) lists the leads still to check).

## Graduates24 and bursary websites

- **As leads for us:** useful for finding bursaries and vac work, which we then confirm on the funder's own page.
  Nothing goes into a data pack from them.
- **As links in the app:** a "more opportunities" link points learners at someone else's site, so it needs Mandla's
  OK.
- **Never copy or scrape their listings.**
- **Graduates24 on WhatsApp:** Rinsuna confirmed its channel on 10 Oct 2026:
  https://whatsapp.com/channel/0029Va9MQ0jB4hdYtf0Wml0A ("the latest Internships, Learnerships and Bursaries").
  A link in the app needs Mandla's OK. UniApplyForMe runs its own WhatsApp channel for bursary alerts.
