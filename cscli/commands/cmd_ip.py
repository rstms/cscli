#!/usr/bin/env python3

import click

from .cli import confirm, error, main, output


@main.group(name="ip")
@click.argument("name", metavar="IP", type=str)
@click.pass_context
def ip(ctx, name):
    """IP commands: create list show modify destroy"""
    ctx.obj.ip_name = name


@ip.command()
@click.option("-d", "--duration", type=int, default=1)
@click.option(
    "-u", "--units", type=click.Choice(["hour", "day", "month", "year"]), default="day"
)
@click.option("-a", "--auto-renew", is_flag=True, envvar="CCS_AUTORENEW")
@click.pass_context
def create(ctx, duration, units, auto_renew):
    """subscribe to a public IP"""
    if duration > 1:
        units += "s"
    output(ctx.obj.create_ip(ctx.obj.ip_name, f"{duration} {units}", auto_renew))


@ip.command()
@click.pass_context
def show(ctx):
    """display IP attributes"""
    output(ctx.obj.find_ip(ctx.obj.ip_name))


@ip.command()
@click.option("-r", "--rename", type=str)
@click.option("-D", "--description", type=str)
# @click.option('-d', '--duration', type=int, default=1)
# @click.option('-u', '--units', type=click.Choice(['hour', 'day', 'month', 'year']), default='day')
# @click.option('-a', '--auto-renew', is_flag=True)
@click.pass_context
def modify(ctx, rename, description):
    """modify IP attributes"""
    ip = ctx.obj.find_ip(ctx.obj.ip_name)
    if rename:
        ip["meta"]["name"] = rename
    if description:
        ip["meta"]["description"] = description
    # if auto_renew:
    #    error('unimplemented')
    # if duration:
    #    error('unimplemented')
    # if units:
    #    error('unimplemented')
    output(ctx.obj.ip.update(ip["uuid"], ip))


@ip.command()
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@click.pass_context
def destroy(ctx, force):
    """delete IP"""
    name = ctx.obj.ip_name
    ip = ctx.obj.find_ip(name)
    confirm(ip, "destruction", "IP", force)
    error(f"IP {name} cannot be deleted while subscribed (verify autorenew status)")
