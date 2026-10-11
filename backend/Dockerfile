# The backend as a container any host can run (docs/DEPLOY.md). From the repo root:
#   docker build -t campus-chommie-api backend
# Settings come from the host's environment, never from a file in the image.
FROM python:3.12-slim

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

# Never as root.
RUN useradd --create-home --uid 10001 campus
USER campus

EXPOSE 8000

# The host's own check can use GET /api/v1/health too; this one is for Docker itself.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/api/v1/health', timeout=4)"

# Migrations first (safe to repeat), then the API. Start one instance at a time (DEPLOY.md).
CMD ["sh", "-c", "flask db upgrade && exec gunicorn -c gunicorn.conf.py app:app"]
