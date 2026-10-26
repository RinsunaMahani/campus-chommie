# How to Judge Campus Chommie in 5 Minutes

Welcome, judges! Campus Chommie tackles the **"Access to higher education"** challenge by supporting a South African student end-to-end: from discovering viable degrees before enrollment to navigating academic deadlines, budgeting, and campus wellbeing until graduation.

* **Live Web App:** https://campus-chommie-web.onrender.com
* **Backend API Health Check:** https://campus-chommie.onrender.com/api/v1/health
* **Demo Accounts:** (Shared password provided in portal notes; never committed)
  * `naledi.demo@example.com` (First-year at SMU, Ga-Rankuwa; allowance-funded, short money, heavy week ahead)
  * `sipho.demo@example.com` (Second-year at UP, Hatfield; self-funded, heavy test week now)
  * `thabo.demo@example.com` (First-year at SMU; class representative with announcement verification panel)

*(Note: Free hosting may take ~30–60 seconds to wake up on first load).*

---

### Minute 1: The Course Finder (Signed Out — No Account Required)
1. Open the live web app in any browser. Tap **"Find my course"** directly from the landing page.
2. Enter sample matric marks (e.g., English HL: 80%, Mathematics: 85%, Physical Sciences: 82%, Life Sciences: 78%) and tap **"See where you qualify"**.
3. **What to look for:**
   * **26 Universities:** Instant evaluation across every public university in South Africa.
   * **Individual Point Formulas:** Look at Stellenbosch (6-subject average 79.2%), UCT (475 Faculty Points Score out of 600, LO excluded), and CUT (2–8 point scale).
   * Tap an institution (e.g. Stellenbosch or UP) to see programmes grouped by faculty, with explicit prerequisite feedback ("Subjects met" vs "Reach").
   * Tap a programme to see a generated **three-choice plan** (primary goal, route-in bridge, and safer related alternative) with live application countdowns and verified bursary recommendations.

### Minute 2: Sign in as Naledi & Home Dashboard
1. Tap **Sign in** from the header or menu and enter `naledi.demo@example.com` with the demo password.
2. **What to look for:**
   * **Fictional Data Disclaimer:** Gold banner stating *"Demo data: fictional student"*.
   * **Privacy First:** In strict compliance with POPIA, the app does not store or display personal names; headers show the verified institution (*"SMU · Sefako Makgatho Health Sciences University"*).
   * **Immediate Clarity:** Look at the 3-card TODAY row:
     * *Next class:* In 3 days (ANA201 in Demo lecture hall A).
     * *Next due:* BCH111 Quiz 3 in 2 days.
     * *Money lasts:* 12 days (R610 balance).
   * **Do This Next:** Dynamic priority queue highlighting what matters most today.

### Minute 3: My Week & Timetable Synchronization
1. Tap the **Week** tab in the bottom navigation.
2. **What to look for:**
   * **Workload Strip:** An 8-week lookahead categorizing each week as *Manageable*, *Busy*, or *Heavy*. Week of Mon 26 Oct is flagged as **Heavy** (1 test + 1 assignment within 48h).
   * **Timetable Accuracy:** Scroll to Monday 08:00 to verify `ANA201 Lecture, 08:00–09:40, Demo lecture hall A` matches Home's "Next class" exactly.
   * **My Marks:** Open assessment tracking to see target marks vs current standing (e.g. ANA201 current 66.3% towards target 60%).

### Minute 4: My Money (Zero Money Movement)
1. Tap the **Money** tab in the bottom navigation.
2. **What to look for:**
   * **Runway Dial:** Shows 12 days remaining based on R610 balance and R40/day essential spending.
   * **Life Fund Buffer:** Reserve set aside for emergencies, which automatically adjusts its status based on the student's academic stress.
   * **"Two Weeks Late" Toggle:** Tap the toggle to simulate an allowance delay; the runway recalculates immediately so students can plan ahead safely.
   * **Cheap Things Nearby:** Sourced free and low-cost activities accessible from the Ga-Rankuwa area; check travel distance and costs.

### Minute 5: Alerts, Support & Class Rep Workflow
1. Return to **Home** and tap the proactive alert (*"Heavy week and short money"*).
2. **What to look for:**
   * **Verified Campus Support:** Opens directly to real SMU support desks (Student Counselling Unit, Student Support Referral Unit in Clinpath 3L003, Campus Health, Financial Aid, and Community Garden food relief) with human-verified phone numbers and locations.
3. Switch account to `thabo.demo@example.com` (or view class rep panel):
   * Open BCH111 to see the **Class Rep Panel** with a classmate's raw chat message ("BCH111 quiz 5 is on Friday at 10:00 in Lab C3").
   * Tap to see how the engine parses unformatted text into structured event fields ready for the rep to confirm.

---

### Technical & Architectural Integrity
* **CI checks** backend and mobile tests, types, data, dependencies and secrets; see the current PR run for exact counts.
* **145 hostile security tests**, all blocked (forged and replayed tokens, other students' data, SQL injection, deep JSON, booby-trapped PDFs, forged Google tokens and WhatsApp messages), after two security sweeps.
* **Zero Inventory of Facts:** Every admission rule, closing date, fee, and contact cites its official source URL.
* **Zero Hex Codes / 360 px Responsive:** Token-based styling; verify narrow-screen wrapping on the current release build.
