#!/usr/bin/env python3

import click

from .cli import main, output


@main.group(name="list")
@click.option("-d", "--detail", is_flag=True, help="full detailed JSON")
@click.option("-u", "--uuid", is_flag=True, help="uuids only")
@click.option("-h", "--human", is_flag=True, help="human-readable JSON")
@click.option("-t", "--text", is_flag=True, help="text-formatted JSON")
@click.pass_context
def list(ctx, detail, uuid, human, text):
    """list servers drives ips venvs capabilities subscriptions all"""
    ctx.obj.list_format = None
    if detail:
        ctx.obj.list_format = "detail"
    if uuid:
        ctx.obj.list_format = "uuid"
    if human:
        ctx.obj.list_format = "human"
    if text:
        ctx.obj.list_format = "text"


@list.command()
@click.pass_context
def servers(ctx):
    """list servers"""
    output(ctx.obj.list_servers(ctx.obj.list_format))


@list.command()
@click.pass_context
def drives(ctx):
    """list drives"""
    output(ctx.obj.list_drives(ctx.obj.list_format))


@list.command()
@click.pass_context
def vlans(ctx):
    """list VLANs"""
    output(ctx.obj.list_vlans(ctx.obj.list_format))


@list.command()
@click.pass_context
def ips(ctx):
    """list IPs"""
    output(ctx.obj.list_ips(ctx.obj.list_format))


@list.command()
@click.pass_context
def subscriptions(ctx):
    """list subscriptions"""
    output(ctx.obj.list_subscriptions(ctx.obj_list_format))


@list.command()
@click.pass_context
def capabilities(ctx):
    """list capabilities"""
    output(ctx.obj.list_capabilities(ctx.obj.list_format))


@list.command()
@click.pass_context
def all(ctx):
    """list all"""
    output(ctx.obj.list_all(ctx.obj.list_format))
