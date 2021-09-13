#!/usr/bin/env python3

import click

from cscli import MIN_DISK
from cscli.cli import pass_environment


@click.group("drive", short_help="manage drives")
@click.argument("drive", metavar="NAME_OR_UUID", type=str)
@pass_environment
def cli(ctx, drive):
    """actions: create destroy list show modify snapshot upload download"""
    ctx.drive_name = drive


@cli.command()
@click.option("-s", "--size", type=str, default=MIN_DISK)
@click.option("-m", "--media", type=click.Choice(["disk", "cdrom"]), default="disk")
@click.option(
    "-M", "--multimount", type=click.Choice(["enable", "disable"]), default="disable"
)
@click.option(
    "-t", "--storage-type", type=click.Choice(["ssd", "magnetic"]), default="ssd"
)
@pass_environment
def create(ctx, size, media, multimount, storage_type):
    """create a drive resource"""
    ctx.output(
        ctx.api.create_drive(
            ctx.drive_name, size, media, multimount == "enable", storage_type
        )
    )


@cli.command()
@pass_environment
def show(ctx):
    """display drive by name or uuid"""
    ctx.output(ctx.api.find_drive(ctx.drive_name))


@cli.command()
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@pass_environment
def destroy(ctx, force):
    """delete drive by name or uuid"""
    drive = ctx.api.find_drive(ctx.drive_name)
    uuid = drive["uuid"]
    ctx.confirm(drive, "destruction", "drive", force)
    ctx.output(
        ctx.api.drive.delete(drive["uuid"])
        or f"drive {uuid} '{ctx.drive_name}' destroyed"
    )


@cli.command()
@pass_environment
def snapshot(ctx):
    """create drive snapshot"""
    ctx.output(ctx.api.server.snapshot(ctx.api.find_drive(ctx.drive_name)))


@cli.command()
@click.option("-r", "--rename", type=str)
@click.option("-m", "--media", type=click.Choice(["disk", "cdrom"]))
@click.option("-M", "--multimount", type=click.Choice(["enable", "disable"]))
@click.option("-s", "--storage-type", type=click.Choice(["ssd", "magnetic"]))
@pass_environment
def modify(ctx, rename, media, multimount, storage_type):
    """change drive characteristics"""
    ctx.output(
        ctx.api.modify_drive(ctx.drive_name, rename, media, multimount, storage_type)
    )


@cli.command()
@click.option("-s", "--size", type=str, required=True)
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@pass_environment
def resize(ctx, size, force):
    """resize an unmounted drive"""
    drive = ctx.api.find_drive(ctx.drive_name)
    ctx.confirm(drive, "resize", "drive", force)
    ctx.output(ctx.api.resize_drive(drive, size))


@cli.command()
@click.argument("input", metavar="DRIVE_IMAGE", type=click.File("rb"))
@click.option("-m", "--media", type=click.Choice(["disk", "cdrom"]), default="disk")
@click.option(
    "-M", "--multimount", type=click.Choice(["enable", "disable"]), default="disable"
)
@pass_environment
def upload(ctx, input, media, multimount):
    """upload a binary disk image or ISO file"""
    uuid = ctx.api.upload_drive_image(input)
    drive = ctx.api.find_drive(uuid)
    ctx.output(
        ctx.api.modify_drive(drive["uuid"], ctx.drive_name, media, multimount, None)
    )


@cli.command()
@click.argument("image-file", type=click.File("wb"))
@pass_environment
def download(ctx, image_file):
    """download drive image to local file"""
    ctx.output(ctx.api.download(ctx.drive_name, image_file))
