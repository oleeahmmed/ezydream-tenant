"""
Development server: default is **Django-Bolt** (fast). Classic Django: ``--use-django-runserver``.

``apps.core`` is listed **before** ``django.contrib.staticfiles`` in ``INSTALLED_APPS``.
Django registers management commands by walking apps in **reverse** order, so this
module's ``runserver`` overwrites ``staticfiles``'s ``runserver``.
"""

from __future__ import annotations

import re
import sys

from django.contrib.staticfiles.management.commands.runserver import (
    Command as StaticfilesRunserverCommand,
)
from django.core.management import CommandError, call_command
from django.core.management.commands.runserver import naiveip_re


class Command(StaticfilesRunserverCommand):
    help = (
        "Starts Django-Bolt in dev mode by default (fast). "
        "Use --use-django-runserver for the classic Django development server."
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--use-django-runserver",
            action="store_true",
            help="Use the classic Django development server (WSGI) instead of Bolt.",
        )

    def handle(self, *args, **options):
        if options.pop("use_django_runserver", False):
            return super().handle(*args, **options)

        addr, port = _parse_addrport(options)
        dev = options.get("use_reloader", True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting Django-Bolt at http://{addr}:{port}/ (dev={'on' if dev else 'off'}) …"
            )
        )
        self.stdout.write(
            self.style.NOTICE(
                "  Tip: python manage.py runserver --use-django-runserver  →  classic Django\n"
            )
        )

        bolt_kwargs = {"host": addr, "port": port}
        if dev:
            bolt_kwargs["dev"] = True
            # django-bolt dev reloader rebuilds argv from sys.argv; if we keep
            # "runserver", the worker becomes ``manage.py runserver --processes 1``,
            # but Django's runserver does not accept --processes → argparse error.
            old_argv = sys.argv[:]
            sys.argv = [old_argv[0], "runbolt", "--host", addr, "--port", str(port), "--dev"]
            try:
                call_command("runbolt", **bolt_kwargs)
            finally:
                sys.argv = old_argv
        else:
            call_command("runbolt", **bolt_kwargs)


def _parse_addrport(options: dict) -> tuple[str, int]:
    """Same rules as Django’s ``runserver`` ``addrport`` positional."""
    addrport = options.get("addrport") or ""
    use_ipv6 = options.get("use_ipv6", False)
    default_addr = "::1" if use_ipv6 else "127.0.0.1"
    default_port = "8000"

    if not addrport:
        return default_addr, int(default_port)

    m = re.match(naiveip_re, addrport)
    if m is None:
        raise CommandError(
            '"%s" is not a valid port number or address:port pair.' % addrport
        )
    addr, _ipv4, _ipv6, _fqdn, port = m.groups()
    if not port.isdigit():
        raise CommandError("%r is not a valid port number." % port)
    if not addr:
        addr = default_addr
    elif _ipv6:
        addr = addr[1:-1]
    return addr, int(port)
