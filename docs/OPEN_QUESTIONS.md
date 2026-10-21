# Open questions

Facts we don't have yet and decisions only the team can make. The app shows "Not verified yet" wherever a fact is
missing; nothing here may be guessed. Tick an item and add a line (who, when, the answer or a link) when it's
settled.

## Facts for the data packs (Rinsuna)

- [ ] **SMU admissions:** re-check every value in `backend/data/universities/smu.yaml` against the current prospectus
  (copied from SMU's medicine admissions page on 30 Sep 2026; `verified_by` still says it needs the team's check).
- [ ] **SMU BSc first year:** admission requirements (the pack has `requirements: null`).
- [ ] **SMU maximum choices** per application (`max_choices: null`).
- [ ] **SMU calendar, allowance dates and support contacts** (counselling, crisis lines, financial aid, food support,
  tutoring, chaplaincy, health), each from an official source. Crisis contacts must be verified by a person before
  release.
- [ ] **UP and TUT packs**, from official sources.
- [ ] **Campuses** for each university (needed for F1 and the support screen).
- [ ] **Course finder languages:** which 2 or 3, and the fluent reviewers who sign them off in `docs/translation_review.md`.

## Privacy and legal (both)

- [ ] **Privacy Policy and Terms of Use** are drafts (`0.1-draft`, in `frontend/mobile/src/content/legal/`). They need
  the team's review and a legal professional's check before release. Each must name the information officer and
  contact details (not decided yet).
- [ ] **The audit trail stores personal data.** The reused code (see REUSE.md) records the full email address, IP
  address, user agent and session and device ids with every sign-in event, and keeps them with no deletion rule. The
  brief says audit events contain no personal data. Options: (a) store a keyed hash of the email and a shortened IP,
  (b) keep them for security with a stated retention period and say so in the Privacy Policy, (c) something else.
  Sessions and consent records also keep the IP address and app details.
- [ ] **Retention** for security records and for closed accounts. "Close my account" deactivates it; nothing removes
  a closed account's data yet, and the brief's `DELETE /me` (delete the account and its data) isn't built. The
  Security screen shows "Delete my account and data: Coming soon" until it is.
- [ ] **Email sender.** Placeholders use `example.com` (we own no domain). Which address and inbox send the codes in
  production (`MAIL_DEFAULT_SENDER`, `MAIL_REPLY_TO`)?

## App and accounts (Mandla)

- [ ] **Demo accounts and the email code.** Signing in on a new phone or browser asks for a code sent to the account's
  email, and judges can't read the demo inbox. Decide before M5, for example: the team keeps the demo inbox and
  pre-trusts nothing, or demo accounts (and only they) skip the new-phone code, with tighter rate limits.
- [ ] **Expo and EAS.** The reused app config's EAS project id and owner were removed. Whose Expo account owns Campus Chommie's
  project (`eas init`), and who builds the Android preview?
- [ ] **Package name `za.campuschommie.app`.** Confirm before the first Play Store upload; it can't change after.
- [ ] **App icon, colours and slogan** ("From choosing a course to graduating.") are placeholders drawn for M0:
  keep or replace.
- [ ] **Google sign-in** is hidden until `GOOGLE_READY` (client ids and a native build). When it's switched on,
  Google sign-up must show the 18-or-older tick too (the backend already refuses it without).
- [ ] **Hosting** (brief section 14): which host, and an uptime check on `/api/v1/health`. Rate limits are counted in
  memory, which is right for one server process; more than one needs Redis (`RATELIMIT_STORAGE_URI`).

## Reminders for later milestones

- M3: the first endpoint that takes numbers (money) gets the NaN/Infinity hostile-input test again (it went with
  the reused business-profile tests).
- M3: onboarding brings back an `(onboarding)` route group: 18-or-older confirmation (already recorded at sign-up),
  privacy notice, consent, university and campus. The student profile can read the 18-or-older date from the consent
  records.
- M4: class updates are the first alerts a student could switch off; notification switches come back with them.
