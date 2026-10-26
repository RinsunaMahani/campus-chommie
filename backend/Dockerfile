# The backend as a container any host can run (docs/DEPLOY.md). From the repo root:
#   docker build -t campus-chommie-api backend
# Settings come from the host's environment, never from a file in the image.
# The Python release is pinned, so a new one arrives as a reviewed change; Debian's own fixes still arrive each time
# the tag is rebuilt upstream. CI scans the built image and fails on a fixable high or critical flaw (security sweep 3).
FROM python:3.12.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    TZ=Africa/Johannesburg

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
# Compiled once here, not on every start in every process: on a free host's slice of a CPU, compiling our code took
# a quarter of the time it took to load the app.
RUN python -m compileall -q src campus_engine migrations app.py gunicorn.conf.py
# The data packs as JSON, read about ten times faster than the YAML (campus_engine/catalogue.py, CACHE_DIR).
RUN python -c "from campus_engine.catalogue import build_cache; print(build_cache(), 'data packs cached')"

# Never as root.
RUN useradd --create-home --uid 10001 campus
USER campus

EXPOSE 8000

# Docker's own check: is the process up? /ping never touches the database, so a free database can sleep.
# GET /api/v1/health also checks the database, for monitoring.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/api/v1/ping', timeout=4)"

# Migrations first (safe to repeat), then, where the host has no shell for one-off commands (Render's free tier), the
# demo accounts when SEED_DEMO_ON_START=true (also safe to repeat; a failure is logged and the API still starts), all
# in one process (`flask start-up`); then the API. Start one instance at a time (DEPLOY.md).
CMD ["sh", "-c", "flask start-up && exec gunicorn -c gunicorn.conf.py app:app"]
