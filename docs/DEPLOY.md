# Deploying the backend

How to run the Campus Chommie API on any host that runs a container. Which host is still Rinsuna's choice
(OPEN_QUESTIONS, "Hosting"); nothing here depends on one. The last section says what the app (Expo) and its web
build need from the backend.

## What a host must give it

- **A container runtime**, for the image built from `backend/`.
- **PostgreSQL 16**, with a direct (session) connection. A pooler in transaction mode (some managed databases offer
  one on another port, such as 6543) can't hold the lock that keeps the background jobs to one process.
- **An SMTP account**, for the sign-up and new-phone codes. Production refuses to start without one.
- **An https address** for the API. Password-reset links use it, and phones won't follow plain http.

## Build

From the repo root:

```bash
docker build -t campus-chommie-api backend
```

The image runs as a normal user (not root), holds no `.env` file and no tests, and starts in production mode.

## Settings

Everything comes from the host's environment. Production refuses to start if a required setting is missing or weak.

| Setting | What it is | Required |
|---|---|---|
| `DATABASE_URL` | the PostgreSQL connection, for example `postgresql://user:password@host:5432/campus_chommie` | yes |
| `SECRET_KEY`, `JWT_SECRET_KEY` | two different random strings of 32 characters or more: `python -c "import secrets; print(secrets.token_urlsafe(48))"` | yes |
| `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, `MAIL_REPLY_TO` | the SMTP account that sends the codes (`backend/.env.example` explains each) | yes |
| `APP_BASE_URL` | this API's own https address, without `/api/v1` | yes |
| `PORT` | the port the host sends traffic to; 8000 if not set | no |
| `CORS_ORIGINS` | the web build's https address, if the web build is hosted; comma-separated; `*` and plain http are refused | no |
| `DEMO_PASSWORD` | the demo accounts' shared password, for `flask seed` | for the demo |
| `RATELIMIT_STORAGE_URI` | `memory://` (the default) is right for the one process the image runs; `redis://...` before adding processes or instances | no |
| `BEHIND_CLOUDFLARE` | `true` only when the API is reachable through Cloudflare alone | no |
| `SCHEDULER_ENABLED` | `true` (the default) runs the background jobs in the web process | no |
| `GUNICORN_THREADS` | threads in the one process; 8 if not set | no |
| `WHATSAPP_*` | the WhatsApp bot's settings ("The WhatsApp bot (M6)" below); any of the five secrets missing = bot off | for the bot |

Never put these in the repo, the image or a log. The host's secret settings are the place for them.

## Start

The container runs the migrations (`flask db upgrade`, safe to repeat), then the API (gunicorn, `gunicorn.conf.py`).
When a release brings new migrations, start one instance first and the rest after it.

After the first start, make the demo accounts once (and again whenever `DEMO_PASSWORD` changes), with the host's
one-off command or `docker exec`:

```bash
flask seed
```

## Check it

- **`GET /api/v1/health`** answers 200 with `{"status": "ok", "database": "ok"}` when the API and the database both
  answer; 503 when the database doesn't. Use it to check a deploy by hand.
- **`GET /api/v1/ping`** answers 200 without touching the database. Docker's own health check uses it, and so should
  an uptime pinger that keeps a free host awake: pinging `/health` every few minutes would keep a free database
  awake all month and use up its compute hours.
- **The log** shows `master scheduler: started` in exactly one process. Every other process logs
  `another process runs the jobs`.

## Background jobs

The clean-ups and the demo's daily re-base run inside the web process. Only one process in the whole deployment runs
them: the one holding a PostgreSQL advisory lock. When it stops, the next process to start takes over. A one-off
command (`flask db upgrade`, `flask seed`) never runs them.

The demo's re-base also runs as the scheduler starts. A free host that puts the API to sleep may sleep through
02:00; when the first request wakes it, the demo's dates are put right straight away.

## Growing

The image runs one gunicorn process with threads. The rate limits are counted in that process's memory, so before
running more processes or instances, set `RATELIMIT_STORAGE_URI` to a Redis. The lock keeps the background jobs to
one process either way.

## What is logged

- **Access log:** each request's method, path (never its query string), status, size and time. No IP address.
- **Never logged:** passwords, codes, tokens, reset links, and marks typed into the course finder.

## The app

- **Point the app at the API:** set `EXPO_PUBLIC_API_URL` to `https://<the API's address>/api/v1` and
  `EXPO_PUBLIC_USE_MOCK_API` to `false`. For the installable preview, those go in `eas.json`'s `preview` profile,
  followed by a new build.
- **The web build:** if it's hosted, add its https address to `CORS_ORIGINS`.

## Free hosting: Render and Neon (chosen 20 Oct 2026)

Rinsuna doesn't qualify for Azure for Students, so the hackathon build runs on two free tiers, no card needed. Their
terms, read on their own sites on 20 Oct 2026, are below; free tiers change, so check them again before relying on
them.

- **Neon (the database):** free, no time limit. 1 GB of storage and 100 compute-hours a month per project; the
  database sleeps after 5 minutes idle and wakes on the next query.
  - Create a project in **Frankfurt** (AWS eu-central-1) on **Postgres 16**.
  - Copy the **direct** connection string (connection pooling off), with `?sslmode=require`. That's `DATABASE_URL`.
- **Render (the API):** a free web service from this repo: language **Docker**, root directory `backend`, region
  **Frankfurt**, instance type **Free**. It sleeps after 15 minutes without a request and takes about a minute to
  wake; 750 free hours a month is enough for this one service to run all month. Free services have no shell, no
  one-off jobs and no pre-deploy command, and can't send on ports 25, 465 or 587.
  - Settings (Environment, typed in by Rinsuna; never committed): `FLASK_ENV=production`, `DATABASE_URL`,
    `SECRET_KEY`, `JWT_SECRET_KEY` (Render's **Generate** button makes each), `APP_BASE_URL` (the service's
    `https://….onrender.com` address), `DEMO_PASSWORD`, `SEED_DEMO_ON_START=true`, and the email settings below.
  - **The demo accounts:** with no shell, `flask seed` can't run as a one-off. `SEED_DEMO_ON_START=true` makes the
    container run it after the migrations each time it starts (safe to repeat; it also re-bases the demo data). A
    failed seed is logged and the API still starts.
  - **Keep it awake:** a free pinger (UptimeRobot or cron-job.org) on `GET /api/v1/ping` every 10 minutes. Not
    `/health`: that would keep Neon awake too.
- **Email (Brevo, Rinsuna's OK on 20 Oct 2026):** Render free blocks the ports Gmail needs, so the sign-up codes go
  through Brevo's free SMTP relay (300 emails a day) on port 2525, which Render doesn't block: `MAIL_SERVER` =
  `smtp-relay.brevo.com`, `MAIL_PORT` = `2525`, `MAIL_USE_TLS` = `true`, `MAIL_USERNAME` = the Brevo login it shows,
  `MAIL_PASSWORD` = a Brevo **SMTP key** (not the API key), `MAIL_DEFAULT_SENDER` = a sender address verified in
  Brevo. Without these, production refuses to start; judges still sign in with the demo accounts, which need no code.
- **The app:** the APK's `EXPO_PUBLIC_API_URL` is `https://….onrender.com/api/v1` (README, "An installable Android
  app"), then a new preview build.

### Live since 21 Oct 2026

Set up by Rinsuna as above; every secret is in Render's Environment only.

- **API:** `https://campus-chommie.onrender.com` (Render service `campus-chommie`, Docker, root `backend`, Frankfurt,
  Free). It deploys **`main`** since 21 Oct (it deployed `rinsuna/free-hosting` before). Each start runs the
  migrations, then the demo seed. Checked 21 Oct: `/api/v1/ping` and `/api/v1/health` answer 200, database ok.
  `BEHIND_CLOUDFLARE=true` (Render puts Cloudflare in front of every `onrender.com` service): checked from outside on
  22 Oct, a request carrying its own `CF-Connecting-IP` is refused by Cloudflare (403, error 1000) and
  `X-Forwarded-For` or `True-Client-IP` don't move the rate limit.
- **Web app (since 22 Oct 2026):** `https://campus-chommie-web.onrender.com` (Render static site `campus-chommie-web`,
  branch `main`, root `frontend/mobile`, build `npm ci && npx expo export --platform web --output-dir dist`, publish
  `dist`). Its environment: `NODE_VERSION=22`, `EXPO_PUBLIC_API_URL=https://campus-chommie.onrender.com/api/v1`,
  `EXPO_PUBLIC_USE_MOCK_API=false` (public, not secrets). One rewrite, `/*` to `/index.html`, so an address typed or
  refreshed opens its screen, and three headers on `/*`: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`. The API's `CORS_ORIGINS` names this address. Checked 22 Oct,
  signed out: Funding opens in its groups from the live API, a deep link answers 200, the headers and CORS are in
  place. Rebuilt by Render whenever `main` changes.
- **Database:** Neon project `campus-chommie`, Frankfurt, direct connection with `sslmode=require`.
- **Email:** Brevo SMTP relay on port 2525. The sender is Rinsuna's own verified Gmail address for now: mail that says
  it's from a Gmail address but is sent by another service can land in spam, so send a sign-up code to a Gmail and an
  Outlook inbox to check, and move to a domain sender when there is one.
- **Keep-awake:** cron-job.org job "Campus Chommie Ping", `GET /api/v1/ping` every 10 minutes (SAST).
- **The app:** `eas.json`'s `preview` (the APK) and `production` profiles point at
  `https://campus-chommie.onrender.com/api/v1` with the mock off. That address is public, not a secret.

## The WhatsApp bot (M6)

The bot is off until all five secrets below are in Render's Environment; then `GET /api/v1/me/whatsapp` says
`available: true` and the app's Home → WhatsApp screen offers a link code. Every value goes into Render only, never
into the repo, a chat or a screenshot.

1. **A Meta app.** At developers.facebook.com, create an app for WhatsApp (business type) and add the WhatsApp
   product. Meta gives it a free **test number**.
2. **Who can talk to the test number.** On WhatsApp's API Setup page, add each phone that will use the bot to the
   test number's recipient list and confirm it with the code WhatsApp sends. A test number only talks to the numbers
   on that list (OPEN_QUESTIONS, "WhatsApp test number").
3. **The values Render needs:**

   | Setting | Where it comes from |
   |---|---|
   | `WHATSAPP_PHONE_NUMBER_ID` | API Setup: the test number's "Phone number ID" (not the phone number) |
   | `WHATSAPP_ACCESS_TOKEN` | a **system user** token with `whatsapp_business_messaging` (Business settings → System users). API Setup's temporary token stops after 24 hours |
   | `WHATSAPP_APP_SECRET` | App settings → Basic → App secret |
   | `WHATSAPP_VERIFY_TOKEN` | a random word you make: `python -c "import secrets; print(secrets.token_urlsafe(24))"` |
   | `WHATSAPP_PHONE_KEY` | another random value made the same way (48 characters); it keys the hash numbers are kept as, so changing it unlinks everyone |
   | `WHATSAPP_DISPLAY_NUMBER` | the test number as people dial it, e.g. `+1 555 …` (public, not a secret) |
   | `WHATSAPP_GRAPH_VERSION` | the Graph API version API Setup's sample request uses, e.g. `v23.0` (public) |

4. **Deploy** (Render restarts with the new settings; the migration `0011_whatsapp` runs on start).
5. **The webhook.** In WhatsApp → Configuration: Callback URL `https://campus-chommie.onrender.com/api/v1/webhooks/whatsapp`,
   Verify token = the same `WHATSAPP_VERIFY_TOKEN`, then "Verify and save". Under Webhook fields, subscribe to
   **messages**.
6. **Check it.** In the app: Home → WhatsApp → Link WhatsApp → "Open WhatsApp and send it". The bot answers "Linked."
   Then send `WEEK`, and as a class rep forward an announcement and tap Confirm.

What the bot keeps: a keyed hash of each linked number, a link code's hash for 10 minutes, and hashes of message ids
for 48 hours. It never stores or logs a number, a message, or the access token.

## Google sign-in

Off until the settings below exist. Client IDs are public (not secrets); keep the Google Cloud project's own
secrets out of the repo and chats.

1. **Google Cloud:** a project with the OAuth consent screen set up (app name Campus Chommie, Rinsuna's support
   email, scopes `openid`, `email`, `profile` only). While it's in "Testing", add each tester's Gmail as a test user.
2. **Web client** (OAuth client ID, type "Web application"):
   - Authorized JavaScript origins: `https://campus-chommie-web.onrender.com` (and `http://localhost:8081` for local
     work).
   - Authorized redirect URIs: `https://campus-chommie-web.onrender.com/oauthredirect` (and
     `http://localhost:8081/oauthredirect`).
3. **Android client** (type "Android"): package name `za.campuschommie.app`, and the SHA-1 of the APK's signing key
   (`eas credentials`, Android, the keystore's SHA-1). Its ID isn't put anywhere: Google checks the APK against it.
4. **Settings:**
   - API (Render, `campus-chommie`): `GOOGLE_CLIENT_IDS` = the **web** client ID (the APK asks for tokens issued to
     it too).
   - Web app (Render, `campus-chommie-web`): `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID` = the same web client ID, then a
     rebuild.
   - APK: `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID` in `eas.json`'s `preview` and `production` env, then a new build.
5. **Check it:** Sign in → Continue with Google, on the web and on the APK; a new Gmail is asked to tick the two
   boxes, and a Gmail that already has a password account is asked for the password once.

## Still Rinsuna's to decide

- **A paid host,** if the app outlives the hackathon (the free tiers above sleep and have monthly limits).
- **Error monitoring.** An external service, so Rinsuna agrees to it first (CLAUDE.md).
- **The email sender address**, which needs a domain we don't have yet.
