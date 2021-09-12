#!/usr/bin/env python3

import click

from .cli import confirm, error, main, output


@main.group(name="vlan")
@click.argument("name", metavar="VLAN", type=str)
@click.pass_context
def vlan(ctx, name):
    """VLAN actions: create list show modify destroy"""
    ctx.obj.vlan_name = name


@vlan.command()
@click.option("-d", "--duration", type=int, default=1)
@click.option(
    "-u", "--units", type=click.Choice(["hour", "day", "month", "year"]), default="day"
)
@click.option("-a", "--auto-renew", is_flag=True)
@click.pass_context
def create(ctx, duration, units, auto_renew):
    """create a VLAN subscription"""
    if duration > 1:
        units += "s"
    output(ctx.obj.create_vlan(ctx.obj.vlan_name, f"{duration} {units}", auto_renew))


@vlan.command()
@click.pass_context
def show(ctx):
    """display VLAN by name or uuid"""
    output(ctx.obj.find_vlan(ctx.obj.vlan_name))


@vlan.command()
@click.option("-r", "--rename", type=str)
@click.option("-D", "--description", type=str)
# @click.option('-d', '--duration', type=int, default=1)
# @click.option('-u', '--units', type=click.Choice(['hour', 'day', 'month', 'year']), default='day')
# @click.option('-a', '--auto-renew', is_flag=True)
@click.pass_context
def modify(ctx, rename, description):
    """modify VLAN attributes"""
    vlan = ctx.obj.find_vlan(ctx.obj.vlan_name)
    if rename:
        vlan["meta"]["name"] = rename
    if description:
        vlan["meta"]["description"] = description
    # if auto_renew:
    #    error('unimplemented')
    # if duration:
    #    error('unimplemented')
    # if units:
    #    error('unimplemented')
    output(ctx.obj.vlan.update(vlan["uuid"], vlan))


@vlan.command()
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@click.pass_context
def destroy(ctx, force):
    """delete VLAN by name or uuid"""
    name = ctx.obj.vlan_name
    vlan = ctx.obj.find_vlan(name)
    confirm(vlan, "destruction", "VLAN", force)
    error(f"VLAN {name} cannot be deleted while subscribed (verify autorenew status)")
