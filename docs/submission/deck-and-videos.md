# Deck outline and video scripts

For the Sonke submission (due Mon 26 Oct 2026, 23:59): a PDF deck of at most 10 slides, a demo video of 2 minutes, and a 20-second pitch video. Screenshots come from the live hosted app; demo logins are provided on slide 9.

See `docs/submission/video-script.md` for full shot-by-shot video scripts and `docs/submission/judges-guide.md` for the 5-minute judge walkthrough.

---

## Deck (10 slides)

1. **Campus Chommie: from choosing a course to graduating.**
   - Challenge: Access to higher education (FNB App of the Year Hackathon 2026).
   - Team: Rinsuna Mahani (solo).
   - Visual: Clean Campus Chommie monogram on the Daylight paper look.

2. **The problem.**
   - Admission rules and subject prerequisites fragmented across 26 different university websites.
   - Bursary and funding deadlines found too late or missed completely.
   - Once enrolled, students juggle heavy test weeks and an allowance that runs out before payday, with no tool connecting the two.

3. **Find my course.**
   - Type matric marks once; instant eligibility calculation across all 26 public universities in South Africa.
   - Evaluates each university's unique formula: standard APS, UCT Faculty Points Score (FPS, excluding LO), Stellenbosch 6-subject average, and CUT 2–8 scale.
   - Visual: "Where you qualify" cards with university monograms, point scores, and qualifying programme counts.

4. **University by faculty, and the 3-choice plan.**
   - Programmes categorized cleanly by faculty with clear prerequisite checks ("Subjects met" vs "Reach").
   - Realistic three-choice plan: primary goal, bridge pathway, and safer related alternative.
   - Real-time application countdowns, university application fees, and required document checklists.

5. **Funding.**
   - NSFAS and 23 bursary and scholarship options (24 funders in total).
   - Detailed breakdowns: what each covers, who can apply, work-back obligations, and application windows.
   - Bookmark funders to receive automated opening and closing deadline reminders.

6. **The enrolled student side (My week & My money).**
   - **First steps:** Timeline from acceptance to the first lecture.
   - **Home dashboard:** Today tiles showing next class with venue countdown, next due assessment, and remaining money runway; **Do this next** picks the three things that matter most today and says why.
   - **Your week in review:** on the student's check-in day, what they got done, what's coming in the next 7 days, how their marks moved and their spending against their own usual, with an alert that it's ready.
   - **My week:** Monthly calendar with activity dots, 8-week workload indicator (*Manageable*, *Busy*, *Heavy*), class timetables, and class rep announcement verification.
   - **My marks:** Target mark tracking, current standing, and projected final marks with likely ranges.
   - **My money:** Whole-cents runway dial, daily safe-to-spend limit, life fund buffer adapting to academic workload, expected payment tracking with a "two weeks late" allowance buffer toggle, and store-card wallet.
   - **Outdoors:** the centre button opens free and cheap places near campus, each previewed with a slideshow of real photos, its price, hours and "Open in maps".

7. **Alerts and campus support.**
   - Proactive early warnings: combined alert triggers when an upcoming heavy academic week coincides with tightening finances before the next payment.
   - One-tap links directly to verified on-campus student support (counselling, health centre, financial aid office, food relief) with dated official-university sources or recorded human review.
   - Crisis lines require recorded human review or a dated official-university source.

8. **Built honestly and securely.**
   - **Zero invented facts:** Every rule, fee, date, and contact cites its official source URL.
   - **Privacy by design:** Course finder stores no marks and requires no account. Enrolled marks and money are strictly owner-only.
   - **Rigorous verification:** CI runs backend and mobile tests, type checks, data validation, code, dependency and secrets scans; use the current PR run for exact counts.
   - **Hostile penetration tests:** 145 attack scenarios (forged and replayed tokens, other students' data, SQL injection, deep JSON, booby-trapped PDFs, forged Google tokens and WhatsApp messages), all blocked (145/145), after two security sweeps that found and fixed every problem the same day.
   - **Clean APK:** Zero third-party trackers, zero advertising SDKs, zero secrets in code, only essential permissions.

9. **Live demo.**
   - Web App: `https://campus-chommie-web.onrender.com`
   - Demo personas: `naledi.demo@example.com` (short money, heavy week ahead), `sipho.demo@example.com` (heavy test week now), `thabo.demo@example.com` (class rep).
   - Shared demo password provided separately in submission portal notes (never committed).
   - Disclaimer: "Demo data: fictional student."

10. **Architecture and what's next.**
    - Stack: Expo / React Native (Android + web), Python Flask API, pure Python decision engine, PostgreSQL on Neon, hosted on Render.
    - Also built: the WhatsApp bot (class reps confirm tests from WhatsApp; WEEK sends the next 7 days) and Continue with Google.
    - What's next: Resolve the 23 outstanding programme rules, expand 2027 and campus-specific coverage, and verify the released web and Android builds. DHET college-register lookup is already implemented.

---

## Video Scripts Summary

- **20-Second Pitch Video:** Fast 4-beat screen capture highlighting the 26 universities, marks entered once, and connected student week/money (see `docs/submission/video-script.md#1-20-second-pitch-video`).
- **2-Minute Demo Video:** Comprehensive 5-part demo covering Course Finder (0:00–0:48), Funding (0:48–1:04), My Week (1:04–1:20), My Money (1:20–1:36), and Alerts & Support (1:36–2:00) (see `docs/submission/video-script.md#2-2-minute-demo-video-120-seconds`).
