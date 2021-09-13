#!/usr/bin/env python3

import click

from cscli.cli import pass_environment


@click.command("list", short_help="list resources by type")
@click.argument(
    "resource",
    type=click.Choice(
        ["servers", "drives", "vlans", "ips", "subscriptions", "capabilities", "all"]
    ),
    default="all",
)
@click.option(
    "-d",
    "--detail",
    "output-format",
    flag_value="detail",
    help="output full detailed JSON",
)
@click.option(
    "-u", "--uuid", "output-format", flag_value="uudi", help="output uuids only"
)
@click.option(
    "-h",
    "--human",
    "output-format",
    flag_value="human",
    help="output human-readable JSON",
)
@click.option(
    "-t",
    "--text",
    "output-format",
    flag_value="text",
    help="output text-formatted JSON",
)
@pass_environment
def cli(ctx, resource, output_format):
    """list servers drives ips venvs capabilities subscriptions all"""
    list_map = {
        "servers": ctx.api.list_servers,
        "drives": ctx.api.list_drives,
        "vlans": ctx.api.list_vlans,
        "ips": ctx.api.list_ips,
        "subscriptions": ctx.api.list_subscriptions,
        "capabilities": ctx.api.list_capabilities,
        "all": ctx.api.list_all,
    }
    ctx.output(list_map[resource](output_format))
