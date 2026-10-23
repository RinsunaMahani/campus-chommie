# Campus Chommie

Campus Chommie takes a South African student from choosing a course to graduating.
For applicants, it turns raw matric marks into qualifying programmes across all 26 public universities,
each scored by its own rules, with a three-choice plan and verified bursary deadlines.
For enrolled students, it connects academic deadlines with student money so a heavy test week and
a late allowance are seen coming before they cause a crisis.
Our entry for the FNB App of the Year Hackathon 2026, challenge "Access to higher education".

## Who it's for

- **High school learners (Grades 11–12):** exploring degrees and diplomas without fees, paywalls, or accounts.
- **Prospective applicants:** building realistic backup plans with real application dates and bursaries.
- **First- and second-year university students:** managing tight budgets, allowances, and heavy assessment weeks.
- **Class representatives:** confirming timetable changes and announcements for their class.

## The Five Features

- **F1: University profile:** All 26 South African public universities with verified campus locations, academic calendars, financial aid desks, and local student support.
- **F2: Find my course:** Type marks once; instant eligibility across 26 universities with custom scoring (including APS, UCT FPS, and Stellenbosch formulas); 3-choice pathway plans (goal, bridge route, safe alternative); live intake dates; document checklists; and 24 funding options (NSFAS + 23 bursaries).
- **F3: My week:** Unified student schedule linking university terms with class assessments; 8-week workload indicator (Manageable, Busy, Heavy); class rep announcement verification; target mark tracking with grade projections.
- **F4: My money:** Money runway calculation, daily safe-to-spend figure, life fund buffer responsive to academic load, expected payments tracking with a "two weeks late" allowance buffer toggle, and store-card wallet. No money movement.
- **F5: Alerts and support:** Early warnings when an upcoming heavy academic week collides with a depleted allowance, directly linking the student to verified on-campus counselling, financial aid, or food relief.

## How to try it

- **Live web app:** https://campus-chommie-web.onrender.com (API: https://campus-chommie.onrender.com)
  *(Note: Free hosting may take up to a minute to wake up on the first visit).*
- **Android APK:** Built with EAS; installs on Android 7.0 and newer.
- **Course finder (no account):** Open the app signed out; enter marks and explore programmes immediately.
- **Demo accounts for judges (fictional students, re-based daily):**
  - `naledi.demo@example.com`: first-year at SMU (Ga-Rankuwa); allowance-funded, short money, heavy week ahead.
  - `sipho.demo@example.com`: second-year at UP (Hatfield); self-funded, heavy test week now.
  - `thabo.demo@example.com`: first-year at SMU; class rep with a classmate announcement waiting for verification.
  *(The shared demo password is submitted to judges separately in portal notes; never committed to git).*

## How it's built

- **App (`frontend/mobile`):** Expo / React Native on Android and web. Token-based theme ("Daylight paper" look) with zero hex codes, responsive down to 360 px width.
- **API (`backend/src`):** Python Flask REST API structured into domain modules (identity, student, catalogue, platform, classes) with strict Marshmallow/Pydantic validation schemas.
- **Decision Engine (`backend/campus_engine`):** Pure Python domain engine with zero database or web dependencies, running admission scoring, workload analysis, and financial runway math.
- **Database:** PostgreSQL on Neon (cloud) or Docker (local), with immutable audit triggers.
- **Hosting:** Render (containerized API and web build) and Neon (PostgreSQL with TLS).

## Privacy and security in plain words

- **POPIA first:** The course finder needs no account, runs no database statements, and never stores or logs typed marks.
- **Collect the minimum:** No ID numbers, bank accounts, NSFAS logins, race, religion, or health data. Accounts require confirming age 18 or older and consent.
- **Owner-only data:** Marks, spending, and money are visible exclusively to their owner. No administrator or class rep can view an individual's personal figures.
- **Tested defenses:** 1,434 backend tests and 253 mobile tests pass on every change. 105 automated hostile penetration test attacks (token forgery, IDOR, SQLi, deep JSON, malicious PDFs) pass 105/105. Rate limiting on every endpoint; strict Content-Security-Policy; zero secrets in code.

## Quick start (Local development)

```bash
# Backend (Python 3.12+, PostgreSQL 16)
cd backend && python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt && python app.py

# Mobile / Web (Node 22+)
cd frontend/mobile && npm install && npx expo start --web
```

## Team

- **Rinsuna Mahani** (solo)
