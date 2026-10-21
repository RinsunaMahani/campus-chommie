# Deploying the backend

How to run the Campus Chommie API on any host that runs a container. Which host is still the team's choice
(OPEN_QUESTIONS, "Hosting"); nothing here depends on one. The app (Expo) and its web build are Mandla's; the last
section says what they need from the backend.

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
  answer; 503 when the database doesn't. Point the host's health check, or an uptime monitor, at it. Docker's own
  health check uses it too.
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

## Still the team's to decide

- **The host and the managed PostgreSQL.**
- **Error monitoring.** An external service, so the team agrees to it first (CLAUDE.md).
- **The email sender address**, which needs a domain we don't have yet.
