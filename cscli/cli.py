import json
import os
import sys

import click
import yaml

from cscli import CloudSigmaClient, __description__, __version__

CONTEXT_SETTINGS = dict(auto_envvar_prefix="CSCLI")


class Environment:
    def __init__(self):
        self.verbose = False
        self.compact = False
        self.fmt = "json"
        self.api = None

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if self.verbose:
            if args:
                msg %= args
            click.echo(msg, file=sys.stderr)

    def output(self, item, status=True):
        if self.compact:
            json_indent = None
            json_separators = [",", ":"]
        else:
            json_indent = 2
            json_separators = [", ", ": "]
        if self.fmt == "yaml":
            out = yaml.dump(item)
        else:
            out = json.dumps(
                dict(status=status, result=item),
                indent=json_indent,
                separators=json_separators,
            )
        click.echo(out)

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
                print(f"filename={filename}")
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"cscli.commands.cmd_{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli


@click.command("cscli", cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.version_option(message=f"{__package__} v{__version__} -- {__description__}")
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
@click.option("-c", "--compact", is_flag=True, help="Output Compact JSON")
@click.option("-y", "--yaml", is_flag=True, help="Output YAML")
@click.option("-j", "--json", is_flag=True, help="Output JSON")
@pass_environment
def cli(ctx, region, username, password, debug, verbose, compact, yaml, json):
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

    ctx.verbose = verbose
    ctx.compact = compact
    if yaml:
        ctx.fmt = "yaml"
    if json:
        ctx.fmt = "json"

    ctx.api = CloudSigmaClient(region, username, password)
