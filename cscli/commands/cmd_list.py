#!/usr/bin/env python3

import click

from cscli.cli import pass_environment
from cscli.error import ParameterError


@click.command("list", short_help="list resources by type")
@click.argument(
    "resource",
    type=click.Choice(
        ["servers", "drives", "vlans", "ips", "subscriptions", "capabilities"]
    ),
    metavar="RESOURCE_TYPE",
    required=False,
    default=None,
)
@click.option(
    "fmt",
    "--detail",
    flag_value="detail",
    help="detailed JSON output (default)",
)
@click.option(
    "fmt",
    "--json",
    flag_value="detail",
    hidden=True,
    help="detailed JSON output (default)",
)
@click.option("fmt", "--uuid", flag_value="uuid", help="output resource UUIDs")
@click.option(
    "fmt",
    "--brief",
    flag_value="brief",
    help="abbreviated JSON output",
)
@click.option(
    "fmt",
    "--text",
    flag_value="text",
    help="text output",
)
@pass_environment
def cli(ctx, resource, fmt):
    """list resources: servers drives ips venvs capabilities subscriptions"""
    list_map = {
        "servers": ctx.api.list_servers,
        "drives": ctx.api.list_drives,
        "vlans": ctx.api.list_vlans,
        "ips": ctx.api.list_ips,
        "subscriptions": ctx.api.list_subscriptions,
        "capabilities": ctx.api.list_capabilities,
        None: ctx.api.list_all,
    }

    if resource == "capabilities" and fmt not in [None, "detail"]:
        raise ParameterError(f"{resource} cannot be formatted as {fmt}")

    if resource == "subscriptions" and fmt not in [None, "uuid", "detail"]:
        raise ParameterError(f"{resource} cannot be formatted as {fmt}")

    ret = list_map[resource](fmt)
    if fmt == "text":
        click.echo("=" * 79)
        for name, data in ret.items():
            first = True
            for result in data:
                for uuid, lines in result.items():
                    if first:
                        first = False
                    else:
                        click.echo("-" * 79)
                    click.echo(f"{name[:-1]} {uuid}")
                    for line in lines:
                        click.echo("   " + line)
            click.echo("=" * 79)
    elif fmt == "uuid":
        uuids = {}
        for name, data in ret.items():
            uuids[name] = [u for u in [list(d.keys())[0] for d in data] if u]
        ctx.output(uuids)
    else:
        ctx.output(ret)
