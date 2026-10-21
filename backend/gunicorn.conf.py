"""
gunicorn's settings in the container (Dockerfile): gunicorn -c gunicorn.conf.py app:app

ONE process, with threads. The rate limits are counted in this process's
memory (RATELIMIT_STORAGE_URI), so several processes would each count on
their own; and the scheduled jobs run in one process only anyway
(src/master_scheduler/lock.py). To grow: more threads first; more processes
only once the rate limits are in Redis (docs/DEPLOY.md).

The access log has the method, the path without its query string, the
status, the size and the time taken: never a query string (it can hold an
email or a token) and never the client's IP address.
"""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 1
worker_class = "gthread"
threads = int(os.environ.get("GUNICORN_THREADS", "8"))
timeout = 60
graceful_timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
access_log_format = '"%(m)s %(U)s" %(s)s %(B)s %(L)ss'
