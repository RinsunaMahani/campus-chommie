"""
`flask` commands for work that has no screen yet.

    flask seed                     the demo accounts for the judges (fictional
                                   students; the shared password comes from
                                   DEMO_PASSWORD), with their data built on
                                   today's date. Every record goes through the
                                   real services, never raw SQL. Safe to run twice.
    flask start-up                 what the container runs before the server: the
                                   migrations, then (SEED_DEMO_ON_START=true) the
                                   demo accounts, in one process. Loading the app
                                   takes most of a minute on a free host's slice
                                   of a CPU, so it's loaded once, not once per
                                   step (measured 26 Oct 2026, docs/DEPLOY.md).
"""
from __future__ import annotations

import os

import click
from flask import Flask, current_app


def register_cli(app: Flask) -> None:
    @app.cli.command("seed")
    def seed() -> None:
        """Make the demo accounts and build their data on today's date. Safe to run twice."""
        from src.domains.platform.demo.constants import PASSWORD_ENV
        from src.domains.platform.demo.services import demo_service

        password = os.environ.get(PASSWORD_ENV, "")
        if not password:
            raise click.ClickException(
                f"Set {PASSWORD_ENV} in backend/.env first: the demo accounts' shared password. Never commit it."
            )
        try:
            emails = demo_service.seed(password)
        except (demo_service.DemoPasswordError, ValueError) as e:
            raise click.ClickException(str(e)) from None
        click.echo(f"Demo accounts ready, with the password in {PASSWORD_ENV}: " + ", ".join(emails))

    @app.cli.command("start-up")
    def start_up() -> None:
        """The migrations, then the demo accounts when SEED_DEMO_ON_START=true. A failed seed is logged and the
        server still starts; a failed migration stops it."""
        from flask_migrate import upgrade

        from src.domains.platform.demo.constants import PASSWORD_ENV
        from src.domains.platform.demo.services import demo_service

        upgrade()
        if os.environ.get("SEED_DEMO_ON_START") != "true":
            return
        try:
            # Only what's missing or stale: the scheduler's demo re-base runs as the server starts anyway.
            emails = demo_service.seed(os.environ.get(PASSWORD_ENV, ""), rebuild=False)
            click.echo(f"Demo accounts ready, with the password in {PASSWORD_ENV}: " + ", ".join(emails))
        except Exception:  # noqa: BLE001
            current_app.logger.exception("Demo seed failed: the server starts anyway.")
