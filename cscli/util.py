#!/usr/bin/env python3

import json
import secrets
import string
import sys

import click


def output(item, status=True):
    click.echo(json.dumps(dict(status=status, result=item), indent=2))


def error(message):
    output(message, False)
    sys.exit()


def confirm(resource, action, label, force):
    if not force:
        if not click.confirm(
            f"Confirm {action} of {label} {resource['name']} {resource['uuid']}"
        ):
            output(f"{action} averted")
            sys.exit()


def mkpasswd(length):
    codex = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + "!#%()*+,-./:;<=>@^_"
    )
    return "".join([secrets.choice(codex) for _ in range(length)])
