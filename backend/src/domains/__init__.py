"""domains -- THE BUSINESS. Everything Campus Chommie does lives here.

Organised as AREAS that contain FEATURES:

    identity/          "who you are"          accounts, auth, devices
    platform/          "for everyone"         notifications
    security/          "what happened"        audit

Campus Chommie's own areas (catalogue, pathways, student, classes) are
added the same way as their features are built.

EVERY FEATURE HAS THE SAME FIVE FOLDERS, so learning one teaches all:

    api/            the HTTP routes (URL in, JSON out). Thin: no rules here.
    schemas/        checks what comes in, shapes what goes out (marshmallow)
    services/       THE BUSINESS RULES. The only layer that decides things.
    repositories/   the ONLY layer that talks to the database
    models/         the table definitions (SQLAlchemy)

A request flows:  api -> schemas -> services -> repositories -> models

RULES
  * A feature may use src/shared and src/core freely.
  * A feature talks to ANOTHER feature only through that feature's
    services -- never its repositories or models.
  * src/shared never imports anything from here.

Database schemas (config.DB_SCHEMAS) are a separate idea: they decide
where tables are STORED, not how code is organised.
"""
