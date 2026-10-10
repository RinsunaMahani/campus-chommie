"""
`flask` commands for work that has no screen yet.

    flask seed                     the demo accounts for the judges (fictional
                                   students; the shared password comes from
                                   DEMO_PASSWORD), with their data built on
                                   today's date. Every record goes through the
                                   real services, never raw SQL. Safe to run twice.
"""
from __future__ import annotations

import os

import click
from flask import Flask


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
