# Reused code

Campus Chommie is built by Team PR on its own earlier project, **Akayza** (github.com/MandlaBaloyi/KasiFlow),
© Team PR (Mandla and Rinsuna), all rights reserved. The files listed below were copied from Akayza's `main` branch at
commit `bf8359c` on 9 October 2026, without its git history, and then adapted. The first commit in this repository
(`M0: Akayza foundation, keep list only, unchanged`) holds them exactly as copied, so the history shows what was reused
and every change made since.

Not copied from Akayza: its commerce, informal-trader, supplier and proof features, media uploads (Cloudinary),
geocoding and the location picker, PayFast, PDF documents, seed data and images, its branding, legal text and docs,
and its 24 migrations.

**Permission to reuse Akayza in Campus Chommie**

- [x] Mandla Baloyi confirms: verbal permission given to Rinsuna Mahani, October 2026 (not yet in writing)
- [x] Rinsuna Mahani confirms: 22 October 2026

## From Akayza

| Campus Chommie path | What it does | Changed for Campus Chommie |
|---|---|---|
| `backend/app.py`, `src/__init__.py`, `src/config.py`, `src/extensions.py`, `src/cli.py`, `src/api/` | app factory, config, CLI, the `/api/v1` blueprint and health check | removed features unhooked; renamed |
| `backend/src/core/` | response envelope, stable error codes, base model, route guard | one kind of account; supplier API-key errors removed |
| `backend/src/master_scheduler/` | one scheduler; each feature declares its own jobs | media and orders jobs removed |
| `backend/src/shared/` | audit, cache, constants, email, finance, helpers, idempotency, logging, monitoring, net, notifications, queue, rate limit, scheduling, security, validation | media and geocoding not copied; Akayza-only audit vocabularies, constants, the payment email and business-name validators removed; the per-user rate-limit key moved here from Akayza's credit book |
| `backend/src/domains/identity/` | accounts and consent, sign-up and two-factor sign-in, sessions, password reset, Google sign-in, data export, closing an account | the trader/supplier "dashboard" column removed; 18-or-older confirmation added; a rate limit on every route |
| `backend/src/domains/platform/notifications/` | in-app alerts | one inbox with the account-security alerts (the orders tab and switches removed) |
| `backend/src/domains/security/audit/` | the append-only audit trail | unchanged |
| `backend/migrations/` | migration environment | a fresh baseline (`0001_baseline`), carrying the audit trail's append-only trigger from Akayza's `0004_audit` |
| `backend/scripts/make_env.py`, `backend/scripts/setup_db.sql` | local setup | renamed |
| `backend/tests/` (test setup, `architecture/`, `domains/identity/`, `domains/platform/`, `domains/security/`, `shared/`) | tests | the database only for tests that need it; business-profile tests removed; notification tests rewritten for one inbox |
| `frontend/mobile/` `app.json`, `eas.json`, `package.json`, `tsconfig.json`, `eslint.config.js`, Jest config | app configuration | renamed; Akayza's EAS project removed; location, camera, audio and webview packages removed |
| `frontend/mobile/src/app/` (root layout, `(auth)`, `(legal)`), `src/features/auth/`, `src/features/legal/`, `src/shared/` (api, components, lib, theme) | the app shell, sign-up and sign-in screens, account security, legal screens, UI kit | business onboarding removed; new theme, mark and wordmark; draft legal text; the 18-or-older tick; the tab bar adapted from Akayza's |
| `.github/workflows/ci.yml`, `.gitignore`, `.gitattributes` | CI and repository settings | CI also runs lint, the data validator, engine coverage and a migration check |

## Code that came to Akayza from TruConnect

Akayza's own REUSE.md declared that this code came from **TruConnect** (github.com/Mandla78/TRU-Connect), an earlier
project by Mandla. Campus Chommie keeps it through Akayza, so its author must approve this reuse as well.

- [x] Mandla Baloyi approves reusing the TruConnect-origin code below in Campus Chommie: verbal permission given to
  Rinsuna Mahani, October 2026 (not yet in writing)

| Campus Chommie path | From TruConnect | What it does |
|---|---|---|
| `backend/src/core/` | `src/core/` | response envelope, error classes with stable codes, base model (UUID, timestamps, soft delete) |
| `backend/src/extensions.py` | `src/extensions.py` | Flask extensions created without an app |
| `backend/src/config.py` | `src/config.py` | environment config (rewritten for Akayza, then for Campus Chommie) |
| `backend/src/__init__.py` | `src/__init__.py` | app-factory pattern (rewritten) |
| `backend/src/master_scheduler/` | `src/master_scheduler/` | one scheduler; each feature declares its own jobs |
| `backend/src/shared/finance/` | `src/shared/finance/` | money engine: integer cents, rounding, formatting, allocation |
| `backend/src/shared/idempotency/` | `src/shared/idempotency/` | retried requests land exactly once |
| `backend/src/shared/audit/` | `src/shared/audit/` | typed audit events |
| `backend/src/shared/email/` | `src/shared/email/` | email service with a fake provider for tests (templates not copied) |
| `backend/src/shared/queue/` | `src/shared/queue/` | background worker pool |
| `backend/src/shared/rate_limit/` | `src/domains/security/rate_limit/` | Flask-Limiter wrapper with JSON 429 responses |
| `backend/src/shared/cache/`, `logging/`, `monitoring/`, `security/`, `validation/`, `helpers/`, `constants/`, `notifications/`, `scheduling/` | `src/shared/...` | small shared utilities |
| `backend/tests/architecture/test_finance_boundaries.py` | `tests/architecture/` | fails the build if finance imports a domain |

Reference only, never copied: Akayza wrote its own password-reset page
(`backend/src/domains/identity/auth/api/reset_page.py` and `templates/reset_password_page.html`) after reading
TruConnect's `reset_password_routes.py` and `reset_password_web.html`. **TruConnect stays reference only: no file is
ever copied from it.**

## Campus Chommie's own

- `backend/campus_engine/`, `backend/data/`, `backend/config.yaml`, `backend/scripts/validate_data.py`,
  `backend/tests/engine/`: the engine starter written for Campus Chommie, added on 9 October 2026. The map data in
  `backend/data/maps/` is OpenStreetMap's, under its own licence (below).
- The graduation-cap mark, app icon and splash, the theme colours, the draft Privacy Policy and Terms of Use, and the
  docs.

## Third-party assets worth naming

| What | Licence | Where |
|---|---|---|
| Plus Jakarta Sans (via `@expo-google-fonts/plus-jakarta-sans`) | SIL Open Font License 1.1 | the app's typeface |
| Feather icons (via `@expo/vector-icons`) | MIT | icons in the app |
| OpenStreetMap data: campus outlines, buildings and place names (via the Overpass API) | Open Database License (ODbL) 1.0, © OpenStreetMap contributors; our copy, with the names we add on campus, stays under the ODbL | `backend/data/maps/`, the map API and screen |

Every other library is an ordinary dependency listed in `backend/requirements.txt` and `frontend/mobile/package.json`,
used under its own licence.
