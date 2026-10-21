# Deck outline and video scripts (draft)

For the Sonke submission (due Mon 26 Oct 2026, 23:59): a PDF deck of at most 10 slides, a demo video of at most 90
seconds, and a 20-second pitch video on Sat 24 Oct. Screenshots come from the hosted app once it's live; the demo
login goes on slide 9.

## Deck (10 slides)

1. **Campus Chommie: from choosing a course to graduating.** Challenge: Access to higher education. Team Blue Tag,
   Rinsuna Mahani. The CC icon on the forest wallpaper.
2. **The problem.** Three lines from the canvas: rules on 26 websites, funding found too late, a heavy week and an
   allowance that runs out with nobody connecting them.
3. **Find my course.** Marks once, then points at every university counted its own way; screenshot of "Where you
   qualify" with the monograms and counts.
4. **A university, by faculty, and the plan.** Screenshot of the faculty sections, then the three-choice plan with
   "What you can still do now".
5. **Funding.** NSFAS and 23 funders: what each covers, who can apply, dates; saved funders and reminders.
   Screenshot of a funder page.
6. **If you're accepted, then the student side.** The steps to the first lecture. Home opens on **Do this next**: the
   app looks at the week, the money and what's due, and picks the three things that matter most today, saying why.
   My week: the whole year as month, week, 3-day or day, with classes read from the university's own timetable PDF,
   tests, exams and the student's own plans ("Find a time" spots the gaps). My money: runway, safe to spend, "can I
   afford this?", payday plan, goals with fee dates, "two weeks late". The store-card wallet keeps loyalty cards on
   the phone.
7. **Alerts and support.** The combined alert (heavy week and short money) pointing to campus counselling and
   financial aid; crisis lines only once verified.
8. **Built honestly and securely.** Every fact cites its official source; no ID, bank or NSFAS details; marks and
   money owner-only; the course finder stores nothing. 1,416 backend tests and 175 app tests on every change, with
   code, dependency and secrets scans. We attacked it ourselves: 105 attacks (forged tokens, other students' data,
   hostile input, booby-trapped PDFs), three problems found and fixed the same day, 105 of 105 now blocked. The APK:
   no trackers, no secrets, only the permissions it needs.
9. **Demo.** APK link; demo login: `naledi.demo@example.com` (or Sipho, Thabo) and the demo password; the demo video
   link. "Demo data: fictional student."
10. **Architecture and what's next.** Expo app (Android and web), Flask API, Python decision engine, PostgreSQL;
    hosted on Render and Neon. Next: all 26 universities checked by a person, TVET and private colleges, the WhatsApp
    bot.

## Demo video (at most 90 seconds)

| Time | Show | Say |
|---|---|---|
| 0 to 10 s | Welcome screen, CC icon | "Campus Chommie takes a South African student from choosing a course to graduating." |
| 10 to 30 s | Type marks, then "Where you qualify" | "Type your marks once. See your points at every university, each counted its own way, and how many programmes you meet." |
| 30 to 45 s | Tap a university: faculties, then plan | "Programmes by faculty, a three-choice plan, and what you can still apply for today." |
| 45 to 55 s | Funding, then a funder | "NSFAS and 23 funders: what they cover, who can apply, and when." |
| 55 to 75 s | Sign in as Naledi: Home alert, Week, Money with "two weeks late" | "Once enrolled: your week and your money together. A heavy week and a late allowance? You see it coming." |
| 75 to 90 s | Support, then the end card | "Campus support, one tap away. Every fact sourced. Your data stays yours." |

## Pitch video (20 seconds, Sat 24 Oct)

About 50 words, spoken calmly (2.5 words a second). Film the phone screen; no faces needed. Text on screen in the
app's own type, large enough to read on a phone.

| Time | Show | Say |
|---|---|---|
| 0 to 5 s | The 26 universities list scrolling fast | "Twenty-six universities. Twenty-six ways of counting points." |
| 5 to 10 s | Type marks, "Where you qualify" fills in | "Type your marks once: see where you qualify, and what funds it." |
| 10 to 16 s | Sign in as Naledi: Home's "Do this next", then Money's runway | "Once you're in, it thinks ahead: a heavy week, an allowance running late, what to do first." |
| 16 to 20 s | End card: Campus Chommie, the tagline, Team Blue Tag | "Campus Chommie. From choosing a course to graduating." |

On screen at the end: "Demo data: fictional student."
