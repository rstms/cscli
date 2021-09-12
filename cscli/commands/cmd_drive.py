#!/usr/bin/env python3

import click

from .cli import confirm, main, output
from .constants import MIN_DISK


@main.group(name="drive")
@click.argument("drive", metavar="DRIVE", type=str)
@click.pass_context
def drive(ctx, drive):
    """drive actions: create destroy list show modify snapshot upload download"""
    ctx.obj.drive_name = drive


@drive.command()
@click.option("-s", "--size", type=str, default=MIN_DISK)
@click.option("-m", "--media", type=click.Choice(["disk", "cdrom"]), default="disk")
@click.option(
    "-M", "--multimount", type=click.Choice(["enable", "disable"]), default="disable"
)
@click.option(
    "-t", "--storage-type", type=click.Choice(["ssd", "magnetic"]), default="ssd"
)
@click.pass_context
def create(ctx, size, media, multimount, storage_type):
    """create a drive resource"""
    output(
        ctx.obj.create_drive(
            ctx.drive_name, size, media, multimount == "enable", storage_type
        )
    )


@drive.command()
@click.pass_context
def show(ctx):
    """display drive by name or uuid"""
    output(ctx.obj.find_drive(ctx.obj.drive_name))


@drive.command()
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@click.pass_context
def destroy(ctx, force):
    """delete drive by name or uuid"""
    name = ctx.obj.drive_name
    drive = ctx.obj.find_drive(name)
    uuid = drive["uuid"]
    confirm(drive, "destruction", "drive", force)
    output(ctx.obj.drive.delete(drive["uuid"]) or f"drive {uuid} '{name}' destroyed")


@drive.command()
@click.pass_context
def snapshot(ctx):
    """create drive snapshot"""
    output(ctx.obj.server.snapshot(ctx.obj.find_drive(ctx.obj.drive_name)))


@drive.command()
@click.option("-r", "--rename", type=str)
@click.option("-m", "--media", type=click.Choice(["disk", "cdrom"]))
@click.option("-M", "--multimount", type=click.Choice(["enable", "disable"]))
@click.option("-s", "--storage-type", type=click.Choice(["ssd", "magnetic"]))
@click.pass_context
def modify(ctx, rename, media, multimount, storage_type):
    """change drive characteristics"""
    output(
        ctx.obj.modify_drive(
            ctx.obj.drive_name, rename, media, multimount, storage_type
        )
    )


@drive.command()
@click.option("-s", "--size", type=str, required=True)
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@click.pass_context
def resize(ctx, size, force):
    """resize an unmounted drive"""
    drive = ctx.obj.find_drive(ctx.obj.drive_name)
    confirm(drive, "resize", "drive", force)
    output(ctx.obj.resize_drive(drive, size))


@drive.command()
@click.argument("input", metavar="DRIVE_IMAGE", type=click.File("rb"))
@click.option("-m", "--media", type=click.Choice(["disk", "cdrom"]), default="disk")
@click.option(
    "-M", "--multimount", type=click.Choice(["enable", "disable"]), default="disable"
)
@click.pass_context
def upload(ctx, input, media, multimount):
    """upload a binary disk image or ISO file"""
    uuid = ctx.obj.upload_drive_image(input)
    drive = ctx.obj.find_drive(uuid)
    output(
        ctx.obj.modify_drive(drive["uuid"], ctx.obj.drive_name, media, multimount, None)
    )


@drive.command()
@click.argument("output", type=click.File("wb"))
@click.pass_context
def download(ctx, output):
    """download drive image to local file"""
    output(ctx.obj.download(ctx.obj.drive_name, output))
