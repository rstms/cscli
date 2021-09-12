#!/usr/bin/env python3

import sys

import click

MIN_CPU = 1
MIN_MHZ = 1000
MIN_RAM = "256M"
MIN_DISK = "512M"

PASSWORD_LEN = 24

from .client import CloudSigmaClient
from .server import Server
from .util import output, error, mkpasswd


@click.group(name="cscli")
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
@click.pass_context
def main(ctx, region, username, password, debug):
    """CLI for CloudSigma

    create, manage, and destroy resources in the cloudsigma region
    """

    ctx.show_default = True
    ctx.auto_envvar_prefix = "CCS_"

    def exception_handler(
        exception_type, exception, traceback, debug_hook=sys.excepthook
    ):
        if debug:
            debug_hook(exception_type, exception, traceback)
        else:
            error(f"{exception_type.__name__}: {exception}")

    sys.excepthook = exception_handler
    ctx.obj = CloudSigmaClient(region, username, password)


@main.group(name="server")
@click.argument("name", type=str, metavar="SERVER")
@click.pass_context
def server(ctx, name):
    """server actions: create list show destroy attach detach start stop ttyopen, ttyclose, shutdown"""
    ctx.obj = Server(name, ctx.obj)


@server.command()
@click.option(
    "-c", "--cpu", metavar="CPU_COUNT", type=int, default=MIN_CPU, help="SMP CPU count"
)
@click.option(
    "-s", "--speed", metavar="CPU_MHZ", type=int, default=MIN_MHZ, help="Mhz per cpu"
)
@click.option(
    "-m",
    "--memory",
    metavar="SIZE",
    type=str,
    default=MIN_RAM,
    help="memory (supports M or G suffix)",
)
@click.option("-p", "--password", type=str, default=mkpasswd(PASSWORD_LEN))
@click.option(
    "-a",
    "--attach-drive",
    metavar="NAME",
    type=str,
    default=None,
    help="drive name or uuid to attach",
)
@click.option(
    "-d",
    "--create-drive",
    metavar="SIZE",
    type=str,
    default=MIN_DISK,
    help="drive size to create",
)
@click.option(
    "-b", "--boot-cdrom", metavar="NAME", type=str, help="boot cdrom drive name or uuid"
)
@click.option(
    "-S",
    "--smp",
    type=click.Choice(["cpu", "core"]),
    help="smp as multi-core or multi-cpu",
)
@click.pass_context
def create(
    ctx, cpu, speed, memory, password, attach_drive, create_drive, boot_cdrom, smp
):
    """create a server resource, optionally create or attach a drive and/or boot cdrom"""
    ctx.obj.create(
        cpu, speed, memory, password, attach_drive, create_drive, boot_cdrom, smp
    )


@server.command()
@click.option("-k", "--keep-drives", is_flag=True)
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@click.pass_context
def destroy(ctx, keep_drives, force):
    """delete server, optionally preserve drives, always preserve cdroms"""
    ctx.obj.destroy(keep_drives, force)


@server.command()
@click.pass_context
def start(ctx):
    """power on"""
    ctx.obj.start()


@server.command()
@click.pass_context
def stop(ctx):
    """power off"""
    ctx.obj.stop()


@server.command()
@click.pass_context
def shutdown(ctx):
    """ACPI shutdown (soft power switch)"""
    ctx.obj.shutdown()


@server.command()
@click.pass_context
def show(ctx):
    """display server attributes"""
    ctx.obj.show()


@server.command()
@click.pass_context
def runtime(ctx):
    """display server runtime data"""
    ctx.obj.runtime()


@server.command()
@click.option("-c", "--close", is_flag=True, help="close the TTY port")
@click.option(
    "-e",
    "--exec",
    "exec_command",
    type=str,
    metavar="COMMAND",
    help="execute COMMAND ADDRESS PORT",
)
@click.option(
    "-p",
    "--password",
    is_flag=True,
    help="pipe vnc_password to stdin of --exec command",
)
@click.pass_context
def tty(ctx, close, exec_command, password):
    """open or close a console TTY port"""
    ctx.obj.tty(close, exec_command, password)


@server.command()
@click.option("-c", "--close", is_flag=True)
@click.pass_context
def vnc(ctx, close):
    """open or close a VNC session"""
    ctx.obj.vnc(close)


@server.command()
@click.option(
    "-s", "--status", type=str, default="started", help="desired server status"
)
@click.option(
    "-t", "--timeout", type=int, default=15, help="timeout in seconds, 0=infinite"
)
@click.pass_context
def wait(ctx, status, timeout):
    """wait for server status"""
    ctx.obj.wait(status, timeout)


@server.command()
@click.argument("drive", type=str)
@click.option("-c", "--dev-channel", type=str, default="0:0")
@click.option("-d", "--device", type=click.Choice(["virtio", "ide"]), default="virtio")
@click.pass_context
def attach(ctx, drive, dev_channel, device):
    """attach drive to server"""
    ctx.obj.attach(drive, dev_channel, device)


@server.command()
@click.argument("drive", metavar="DRIVE", type=str)
@click.pass_context
def detach(ctx, drive):
    """detach drive from server"""
    ctx.obj.detach(drive)


@server.command()
@click.argument("action", type=click.Choice(["add", "delete", "modify"]), default="add")
@click.option(
    "-c",
    "--config",
    type=click.Choice(["dhcp", "static", "manual", "vlan"]),
    default="dhcp",
)
@click.option("-m", "--model", type=str)
@click.option("-i", "--ip", type=str)
@click.option("-m", "--mac", type=str)
@click.option("--vlan", type=str)
@click.pass_context
def nic(ctx, action, config, model, ip, mac, vlan):
    """add, delete, or modify network interfaces"""
    ctx.obj.nic(action, config, model, ip, mac, vlan)


@server.command()
@click.option("-r", "--rename", type=str)
@click.option(
    "-c", "--cpu", metavar="CPU_COUNT", type=int, default=MIN_CPU, help="SMP CPU count"
)
@click.option(
    "-s", "--speed", metavar="CPU_MHZ", type=int, default=MIN_MHZ, help="Mhz per cpu"
)
@click.option("-m", "--memory", type=str)
@click.option("-p", "--password", type=str)
@click.option(
    "-S",
    "--smp",
    type=click.Choice(["cpu", "core"]),
    help="smp as multi-core or multi-cpu",
)
@click.pass_context
def modify(ctx, rename, cpu, speed, memory, password, smp):
    """modify server attributes"""
    ctx.obj.modify(rename, cpu, speed, memory, password, smp)


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


@main.group(name="drive")
@click.argument("drive", metavar="DRIVE", type=str)
@click.pass_context
def drive(ctx, drive):
    """drive actions: create destroy list show modify snapshot upload download"""
    ctx.obj = Drive(drive, ctx)
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
