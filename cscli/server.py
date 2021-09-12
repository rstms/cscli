#!/usr/bin/env python3

import click

@ccs.group(name='server')
@click.pass_context
def server(ctx):
    """server actions: create list show destroy attach start stop shutdown"""
    pass

@server.command()
@click.argument('name', type=str, default='cloudbox', envvar='CCS_NAME')
@click.argument('cpu', type=float, default=1, envvar='CCS_CPU')
@click.argument('memory', type=str, default='1G', envvar='CCS_MEMORY')
@click.argument('vnc-password', type=str, envvar='CCS_VNC_PASSWORD')
@click.option('-a', '--attach_drive', type=str, default=None, envvar='CCS_ATTACH_DRIVE')
@click.option('-c', '--create_drive', type=str, default=None, envvar='CCS_CREATE_DRIVE')
@click.option('-s', '--drive_size', type=str, default='1G', envvar='CCS_DRIVE_SIZE')
@click.option('-i', '--iso', type=str, default=None, envvar='CCS_ISO')
@click.pass_context
def create(ctx, name, cpu, memory, attach_drive, vnc_password, create_drive, drive_size, iso):
    """create a server resource, optionally attach or create a drive, ISO, VLAN"""
    output(ctx.obj.create_server(name, cpu, memory, attach_drive, create_drive, drive_size, iso, vnc_password))

@server.command()
@click.argument('name', type=str, default='cloudbox', envvar='CCS_NAME')
@click.option('-k/-d', '--keep-drives/--delete-drives', is_flag=True)
@click.pass_context
def destroy(ctx, name, keep_drives):
    """delete server, optionally preserve drives, always preserve cdroms"""
    server = ctx.obj.find_server(name)
    uuid = verify(ctx, 'server', server)
    output(ctx.obj.delete_server(uuid, keep_drives))

@server.command()
@click.argument('name', type=str, default='cloudbox', envvar='CCS_NAME')
@click.pass_context
def start(ctx, name):
    """power on"""
    output(ctx.obj.start_server(name))

@server.command()
@click.argument('name', type=str, default='cloudbox', envvar='CCS_NAME')
@click.pass_context
def stop(ctx, name):
    """power off"""
    output(ctx.obj.stop_server(name))

@server.command()
@click.argument('name', type=str, default='cloudbox', envvar='CCS_NAME')
@click.pass_context
def shutdown(ctx, name):
    """ACPI shutdown (soft power switch)"""
    output(ctx.obj.server.shutdown(name))

@server.command()
@click.argument('name', type=str, default='cloudbox', envvar='CCS_NAME')
@click.option('-r', '--runtime', is_flag=True)
@click.pass_context
def show(ctx, name, runtime):
    output(ctx.obj.show_server(name, runtime))

@server.command()
@click.argument('name', type=str, default='cloudbox', envvar='CCS_NAME')
@click.argument('drive', type=str, envvar='CCS_DRIVE')
@click.argument('boot-order', type=int, default=1, envvar='CCS_BOOT_ORDER')
@click.argument('dev-channel', type=str, default='0:0', envvar='CCS_DEV_CHANNEL')
@click.argument('device', type=str, default='virtio', envvar='CCS_DEVICE')
@click.pass_context
def attach(ctx, drive, boot_order, dev_channel, device):
    """attach drive to server"""
    drive = ctx.obj.find_drive(drive)
    if not drive:
        error(f'drive {drive} not found')
    server = ctx.obj.find_server(ctx.obj.uuid)
    if not server:
        error(f'server {ctx.obj.uuid} not found')
    server.setdefault('drives', []).append(
        dict(
            boot_order=boot_order,
            dev_channel=dev_channel,
            device=device,
            drive=drive
        )
    )
    output(ctx.obj.update_server(server))

@server.command()
@click.argument('action', type=click.Choice(['append', 'delete', 'modify']), default='append', envvar='CCS_NIC_ACTION') 
@click.argument('config', type=click.Choice(['dhcp', 'static', 'manual', 'vlan']), default='dhcp', envvar='CCS_NIC_CONFIG')
@click.option('--model', type=str, default=None, envvar='CCS_NIC_MODEL')
@click.option('--ip', type=str, default=None, envvar='CCS_IP')
@click.option('--mac', type=str, default=None, envvar='CCS_MAC')
@click.option('--vlan', type=str, default=None, envvar='CCS_VLAN')
@click.pass_context
def nic(ctx, vlan, ip):
    server = ctx.obj.find_server(ctx.obj.uuid)
    if not server:
        error(f'server {ctx.obj.uuid} not found')

    server.setdefault('nics', [])

    if model:
        new_nic = dict(model=model)
    else:
        new_nic = {}

    if config=='dhcp':
        new_nic['ip_v4_conf']=dict(conf='dhcp')
    elif config=='static':
        if not ip:
            error('static config requires --ip option (subscribed IP)')
        # TODO: verify the ip is subscribed and not already assigned
        new_nic['ip_v4_conf']=dict(conf='dhcp', ip=ip)
    elif config=='manual':
        new_nic['ip_v4_conf']=dict(conf='manual')
    elif config=='vlan':
        if not vlan:
            error('vlan config requires --vlan option (subscribed VLAN)')
        # TODO: verify the VLAN is subscribed
        new_nic['vlan'] = vlan
    else:
        error(f'unknown config type {config}')

    if action == 'append':
        server['nics'].append(new_nic)
    else:
        if not mac:
            error(f'{action} action requires --mac option')

        # find index and nic of server.nics with matching mac address
        matches = [(i,n) for (i,n) in enumerate(server['nics']) if n['mac']==mac]
        if not matches:
            error(f'{action} mac addr {mac} not found on server {ctx.obj.uuid}')
        nic_index = matches[0]
        if action == 'delete':
            del(server['nics'][nic_index])
        elif action == 'modify':
            new_nic['mac'] = mac
            server['nics'][nic_index] = new_nic
        else:
            error(f'unknown action {action}')
    output(ctx.obj.update_server(server))

@server.command()
@click.option('-n', '--name', type=str, default=None, envvar='CCS_NEW_NAME')
@click.option('-c', '--cpu', type=float, default=1, envvar='CCS_CPU')
@click.option('-m', '--memory', type=str, default='1G', envvar='CCS_MEMORY')
@click.option('-p', '--vnc-password', type=str, default=None, envvar='CCS_VNC_PASSWORD')
@click.pass_context
def modify(ctx, name, cpu, memory, vnc_password):
    server = ctx.obj.find_server(ctx.obj.uuid)
    if name:
        server['name'] = name
    if cpu:
        server['cpu'] = cpu * 1000
    if memory:
        server['memory'] = ctx.obj.modify_value(memory)
    if vnc_password:
        server['vnc_password'] = vnc_password
    output(ctx.obj.update_server(server))
