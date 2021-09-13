import json
import os
import sys

import click

from cscli import CloudSigmaClient

CONTEXT_SETTINGS = dict(auto_envvar_prefix="CLOUDSIGMA")


class Environment:
    def __init__(self):
        self.verbose = False
        self.api = None

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if self.verbose:
            if args:
                msg %= args
            click.echo(msg, file=sys.stderr)

    def output(self, item, status=True):
        click.echo(json.dumps(dict(status=status, result=item), indent=2))

    def error(self, message):
        self.output(message, False)
        sys.exit()

    def confirm(self, resource, action, label, force):
        if not force:
            if not click.confirm(
                f"Confirm {action} of {label} {resource['name']} {resource['uuid']}"
            ):
                self.output(f"{action} averted")
                sys.exit()


pass_environment = click.make_pass_decorator(Environment, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))


class ComplexCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"cscli.commands.cmd_{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli


@click.command(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.version_option()
@click.option(
    "-u", "--username", type=str, help="override env var CLOUDSIGMA_USERNAME]"
)
@click.option(
    "-p", "--password", type=str, help="override env var CLOUDSIGMA_PASSWORD]"
)
@click.option("-r", "--region", type=str, help="override env var CLOUDSIGMA_REGION]")
@click.option(
    "-d", "--debug", is_flag=True, help="output full stacktrace on runtime error"
)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@pass_environment
@click.pass_context
def cli(ctx, region, username, password, debug, verbose):
    """CLI for the CloudSigma API

    create, modify, operate, and destroy resources on cloudsigma
    """

    def exception_handler(
        exception_type, exception, traceback, debug_hook=sys.excepthook
    ):
        if debug:
            debug_hook(exception_type, exception, traceback)
        else:
            ctx.error(f"{exception_type.__name__}: {exception}")

    sys.excepthook = exception_handler

    ctx.api = CloudSigmaClient(region, username, password, verbose)
