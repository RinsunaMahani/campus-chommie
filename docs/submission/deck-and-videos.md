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
   - **Home dashboard:** Today tiles showing next class with venue countdown, next due assessment, and remaining money runway.
   - **My week:** Monthly calendar with activity dots, 8-week workload indicator (*Manageable*, *Busy*, *Heavy*), class timetables, and class rep announcement verification.
   - **My marks:** Target mark tracking, current standing, and projected final marks with likely ranges.
   - **My money:** Whole-cents runway dial, daily safe-to-spend limit, life fund buffer adapting to academic workload, expected payment tracking with a "two weeks late" allowance buffer toggle, cheap things nearby, and store-card wallet.

7. **Alerts and campus support.**
   - Proactive early warnings: combined alert triggers when an upcoming heavy academic week coincides with tightening finances before the next payment.
   - One-tap links directly to verified on-campus student support (counselling, health centre, financial aid office, food relief) with human-checked contact details.
   - Crisis lines displayed only once verified by a person.

8. **Built honestly and securely.**
   - **Zero invented facts:** Every rule, fee, date, and contact cites its official source URL.
   - **Privacy by design:** Course finder stores no marks and requires no account. Enrolled marks and money are strictly owner-only.
   - **Rigorous verification:** 1,434 backend tests and 253 mobile tests pass on every change.
   - **Hostile penetration tests:** 105 automated attack scenarios (token replay, IDOR, SQL injection, deep JSON, malicious PDFs) all blocked (105/105 pass).
   - **Clean APK:** Zero third-party trackers, zero advertising SDKs, zero secrets in code, only essential permissions.

9. **Live demo.**
   - Web App: `https://campus-chommie-web.onrender.com`
   - Demo personas: `naledi.demo@example.com` (short money, heavy week ahead), `sipho.demo@example.com` (heavy test week now), `thabo.demo@example.com` (class rep).
   - Shared demo password provided separately in submission portal notes (never committed).
   - Disclaimer: "Demo data: fictional student."

10. **Architecture and what's next.**
    - Stack: Expo / React Native (Android + web), Python Flask API, pure Python decision engine, PostgreSQL on Neon, hosted on Render.
    - What's next: Human verification sign-off across all 26 university data packs, integration with DHET's TVET and private colleges register, and the WhatsApp bot.

---

## Video Scripts Summary

- **20-Second Pitch Video:** Fast 4-beat screen capture highlighting the 26 universities, marks entered once, and connected student week/money (see `docs/submission/video-script.md#1-20-second-pitch-video`).
- **2-Minute Demo Video:** Comprehensive 5-part demo covering Course Finder (0:00–0:48), Funding (0:48–1:04), My Week (1:04–1:20), My Money (1:20–1:36), and Alerts & Support (1:36–2:00) (see `docs/submission/video-script.md#2-2-minute-demo-video-120-seconds`).
