"""
Colleges: public TVET colleges and DHET's registers of private colleges and higher education
institutions, served from the national pack (backend/data/national/colleges.yaml) at /api/v1/colleges.

No database tables: like the funding pack, it changes only through a reviewed pull request, and
campus_engine validates it as it loads. Searches and registration checks are never stored or logged.
"""
