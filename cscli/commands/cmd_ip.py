#!/usr/bin/env python3

import click

from cscli.cli import pass_environment


@click.group(name="ip", short_help="manage ip addresses")
@click.argument("name", metavar="IP", type=str)
@pass_environment
def cli(ctx, name):
    """IP commands: create list show modify destroy"""
    ctx.ip_name = name


@cli.command()
@click.option("-d", "--duration", type=int, default=1)
@click.option(
    "-u", "--units", type=click.Choice(["hour", "day", "month", "year"]), default="day"
)
@click.option("-a", "--auto-renew", is_flag=True, envvar="CCS_AUTORENEW")
@pass_environment
def create(ctx, duration, units, auto_renew):
    """subscribe to a public IP"""
    if duration > 1:
        units += "s"
    ctx.output(ctx.api.create_ip(ctx.ip_name, f"{duration} {units}", auto_renew))


@cli.command()
@pass_environment
def show(ctx):
    """display IP attributes"""
    ctx.output(ctx.api.find_ip(ctx.ip_name))


@cli.command()
@click.option("-r", "--rename", type=str)
@click.option("-D", "--description", type=str)
# @click.option('-d', '--duration', type=int, default=1)
# @click.option('-u', '--units', type=click.Choice(['hour', 'day', 'month', 'year']), default='day')
# @click.option('-a', '--auto-renew', is_flag=True)
@pass_environment
def modify(ctx, rename, description):
    """modify IP attributes"""
    ip = ctx.api.find_ip(ctx.ip_name)
    if rename:
        ip["meta"]["name"] = rename
    if description:
        ip["meta"]["description"] = description
    # if auto_renew:
    #    ctx.error('unimplemented')
    # if duration:
    #    ctx.error('unimplemented')
    # if units:
    #    ctx.error('unimplemented')
    ctx.output(ctx.api.ip.update(ip["uuid"], ip))


@cli.command()
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@pass_environment
def destroy(ctx, force):
    """delete IP"""
    name = ctx.ip_name
    ip = ctx.api.find_ip(name)
    ctx.confirm(ip, "destruction", "IP", force)
    ctx.error(f"IP {name} cannot be deleted while subscribed (verify autorenew status)")
