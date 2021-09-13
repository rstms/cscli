import secrets
import string
import subprocess
import time

import click

from cscli import MIN_CPU, MIN_DISK, MIN_MHZ, MIN_RAM, PASSWORD_LEN
from cscli.cli import pass_environment


def mkpasswd(length):
    codex = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + "!#%()*+,-./:;<=>@^_"
    )
    return "".join([secrets.choice(codex) for _ in range(length)])


@click.group(name="server")
@click.argument("name", type=str, metavar="SERVER_NAME_OR_UUID")
@pass_environment
def cli(ctx, name):
    """server actions: create list show destroy attach detach start stop ttyopen, ttyclose, shutdown"""
    ctx.server_name = name


@cli.command()
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
@pass_environment
def create(
    ctx, cpu, speed, memory, password, attach_drive, create_drive, boot_cdrom, smp
):
    """create a server resource, optionally create or attach a drive and/or boot cdrom"""
    ctx.output(
        ctx.api.create_server(
            ctx.server_name,
            cpu,
            speed,
            memory,
            password,
            attach_drive,
            create_drive,
            boot_cdrom,
            smp,
        )
    )


@cli.command()
@click.option("-k", "--keep-drives", is_flag=True)
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@pass_environment
def destroy(ctx, keep_drives, force):
    """delete server, optionally preserve drives, always preserve cdroms"""
    server = ctx.api.find_server(ctx.server_name)
    uuid = server["uuid"]
    ctx.confirm(server, "destruction", "server", force)
    if keep_drives:
        drives = None
    else:
        drives = "disks"
    ctx.output(
        ctx.api.server.delete(server["uuid"], drives)
        or f"server {uuid} '{ctx.server_name}' destroyed"
    )


@cli.command()
@pass_environment
def start(ctx):
    """power on"""
    ctx.output(ctx.api.server.start(ctx.api.find_server(ctx.server_name)["uuid"]))


@cli.command()
@pass_environment
def stop(ctx):
    """power off"""
    ctx.output(ctx.api.server.stop(ctx.api.find_server(ctx.server_name)["uuid"]))


@cli.command()
@pass_environment
def shutdown(ctx):
    """ACPI shutdown (soft power switch)"""
    ctx.output(ctx.api.server.shutdown(ctx.api.find_server(ctx.server_name)["uuid"]))


@cli.command()
@pass_environment
def show(ctx):
    """display server attributes"""
    ctx.output(ctx.api.find_server(ctx.server_name))


@cli.command()
@pass_environment
def runtime(ctx):
    """display server runtime data"""
    ctx.output(ctx.api.server.runtime(ctx.api.find_server(ctx.server_name)["uuid"]))


@cli.command()
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
@pass_environment
def tty(ctx, close, exec_command, password):
    """open or close a console TTY port"""
    if close:
        ctx.output(ctx.api.close_tty(ctx.server_name))
    else:
        ret = ctx.api.open_tty(ctx.server_name)
        if ret:
            if exec_command:
                if password:
                    server = ctx.api.find_server(ctx.server_name)
                    pipe = f"echo '{server['vnc_password']}'|"
                else:
                    pipe = ""
                url = ret["console_url"]
                addr, port = (url.split("/")[2]).split(":")
                cmd = f"{pipe}{exec_command} {addr} {port}"
                exit_code = subprocess.call(cmd, shell=True)
                ret = f"subprocess returned {exit_code}"
        ctx.output(ret)


@cli.command()
@click.option("-c", "--close", is_flag=True)
@pass_environment
def vnc(ctx, close):
    """open or close a VNC session"""
    if close:
        ctx.output(ctx.api.close_vnc(ctx.server_name))
    else:
        ctx.output(ctx.api.open_vnc(ctx.server_name))


@cli.command()
@click.option(
    "-s", "--status", type=str, default="started", help="desired server status"
)
@click.option(
    "-t", "--timeout", type=int, default=15, help="timeout in seconds, 0=infinite"
)
@pass_environment
def wait(ctx, status, timeout):
    """wait for server status"""
    server = ctx.api.find_server(ctx.server_name)
    if timeout:
        timeout = time.time() + timeout
    while server["status"] != status:
        server = ctx.api.find_server(ctx.server_name)
        if timeout and time.time() > timeout:
            ctx.error(f"Timeout waiting for server {ctx.server_name} status {status}")
    ctx.output({"uuid": server["uuid"], "status": server["status"]})


@cli.command()
@click.argument("drive", type=str)
@click.option("-c", "--dev-channel", type=str, default="0:0")
@click.option("-d", "--device", type=click.Choice(["virtio", "ide"]), default="virtio")
@pass_environment
def attach(ctx, drive, dev_channel, device):
    """attach drive to server"""
    server = ctx.api.find_server(ctx.server_name)
    attachment = dict(
        drive=ctx.api.find_drive(drive),
        dev_channel=dev_channel,
        device=device,
        boot_order=len(server["drives"]) + 1,
    )
    server.setdefault("drives", []).append(attachment)
    ctx.output(ctx.api.server.update(server["uuid"], server))


@cli.command()
@click.argument("drive", metavar="DRIVE", type=str)
@pass_environment
def detach(ctx, drive):
    """detach drive from server"""
    server = ctx.api.find_server(ctx.server_name)
    drive_uuid = ctx.api.find_drive(drive)["uuid"]
    found = False
    for index, attached_drive in enumerate(server["drives"]):
        if drive_uuid == attached_drive["drive"]["uuid"]:
            del server["drives"][index]
            found = True
            break
    if found:
        ctx.output(ctx.api.server.update(server["uuid"], server))
    else:
        ctx.error(f"server {ctx.server_name} has no attached drive {drive}")


@cli.command()
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
@pass_environment
def nic(ctx, action, config, model, ip, mac, vlan):
    """add, delete, or modify network interfaces"""
    server = ctx.api.find_server(ctx.server_name)
    server.setdefault("nics", [])

    new_nic = {}

    if model:
        new_nic["model"] = model

    if config == "dhcp":
        new_nic["ip_v4_conf"] = dict(conf="dhcp")
    elif config == "static":
        if not ip:
            ctx.error("static config requires --ip option (subscribed IP)")
        # TODO: verify the ip is subscribed and not already assigned
        new_nic["ip_v4_conf"] = dict(conf="static", ip=ip)
    elif config == "manual":
        new_nic["ip_v4_conf"] = dict(conf="manual")
    elif config == "vlan":
        if not vlan:
            ctx.error("vlan config requires --vlan option (subscribed VLAN)")
        # TODO: verify the VLAN is subscribed
        new_nic["vlan"] = vlan
    else:
        ctx.error(f"unknown config type {config}")

    if action == "add":
        server["nics"].append(new_nic)
    else:
        if not mac:
            ctx.error(f"{action} action requires --mac option")

        # find index and nic of server.nics with matching mac address
        matches = [(i, n) for (i, n) in enumerate(server["nics"]) if n["mac"] == mac]
        if len(matches) != 1:
            ctx.error(f"{action} mac addr {mac} not found on server {ctx.server_name}")
        nic_index = matches[0][0]
        if action == "delete":
            del server["nics"][nic_index]
        elif action == "modify":
            new_nic["mac"] = mac
            server["nics"][nic_index] = new_nic
        else:
            ctx.error(f"unknown action {action}")
    ctx.output(ctx.api.server.update(server["uuid"], server))


@cli.command()
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
@pass_environment
def modify(ctx, rename, cpu, speed, memory, password, smp):
    """modify server attributes"""

    server = ctx.api.find_server(ctx.server_name)
    if rename:
        server["name"] = rename
    if cpu or speed:
        server["cpu"] = cpu * speed
        server["smp"] = cpu
    if memory:
        server["mem"] = ctx.api.convert_memory_value(memory)
    if password:
        server["vnc_password"] = password
    if smp:
        server["cpus_instead_of_cores"] = bool(smp == "cpu")
    ctx.output(ctx.api.server.update(server["uuid"], server))
