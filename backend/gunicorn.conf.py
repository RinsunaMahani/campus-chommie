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


def post_worker_init(worker):
    """Read the data packs as the worker starts, not on the first request.

    Each pack is cached once per process. Without this, the first student
    after a wake waits while every pack is parsed. A daemon thread keeps
    /ping and sign-in answering meanwhile."""
    import threading

    def warm():
        from src.domains.catalogue.colleges.repositories import pack_repository as colleges
        from src.domains.catalogue.funding.repositories import pack_repository as funding
        from src.domains.catalogue.maps.repositories import map_repository as maps
        from src.domains.catalogue.universities.repositories import pack_repository as universities

        try:
            universities.all_packs()
            funding.funding_pack()
            colleges.colleges_pack()
            maps.all_maps()
            worker.log.info("data packs: loaded")
        except Exception:  # a broken pack fails CI; here it simply waits for its first request
            worker.log.exception("data packs: preload failed")

    threading.Thread(target=warm, name="pack-preload", daemon=True).start()
