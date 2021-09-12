import click

@main.group(name='server')
@click.argument('name', type=str, metavar='SERVER')
@click.pass_context
def server(ctx, name):
    """server actions: create list show destroy attach detach start stop ttyopen, ttyclose, shutdown"""
    ctx.obj.server_name = name

@server.command()
@click.option('-c', '--cpu', metavar='CPU_COUNT', type=int, default=MIN_CPU, help='SMP CPU count')
@click.option('-s', '--speed', metavar='CPU_MHZ', type=int, default=MIN_MHZ, help='Mhz per cpu')
@click.option('-m', '--memory', metavar='SIZE', type=str, default=MIN_RAM, help='memory (supports M or G suffix)')
@click.option('-p', '--password', type=str, default=mkpasswd(PASSWORD_LEN))
@click.option('-a', '--attach-drive', metavar='NAME', type=str, default=None, help="drive name or uuid to attach")
@click.option('-d', '--create-drive', metavar='SIZE', type=str, default=MIN_DISK, help="drive size to create")
@click.option('-b', '--boot-cdrom', metavar='NAME', type=str, help="boot cdrom drive name or uuid")
@click.option('-S', '--smp', type=click.Choice(['cpu', 'core']), help='smp as multi-core or multi-cpu')
@click.pass_context
def create(ctx, cpu, speed, memory, password, attach_drive, create_drive, boot_cdrom, smp):
    """create a server resource, optionally create or attach a drive and/or boot cdrom"""
    output(ctx.obj.create_server(ctx.obj.server_name, cpu, speed, memory, password, attach_drive, create_drive, boot_cdrom, smp))

@server.command()
@click.option('-k', '--keep-drives', is_flag=True)
@click.option('-f', '--force', is_flag=True, help='suppress confirmation prompt')
@click.pass_context
def destroy(ctx, keep_drives, force):
    """delete server, optionally preserve drives, always preserve cdroms"""
    name = ctx.obj.server_name
    server = ctx.obj.find_server(name)
    uuid = server['uuid']
    confirm(server, 'destruction', 'server', force)
    if keep_drives:
        drives=None
    else:
        drives='disks'
    output(ctx.obj.server.delete(server['uuid'], drives) or f"server {uuid} '{name}' destroyed")

@server.command()
@click.pass_context
def start(ctx):
    """power on"""
    output(ctx.obj.server.start(ctx.obj.find_server(ctx.obj.server_name)['uuid']))

@server.command()
@click.pass_context
def stop(ctx):
    """power off"""
    output(ctx.obj.server.stop(ctx.obj.find_server(ctx.obj.server_name)['uuid']))

@server.command()
@click.pass_context
def shutdown(ctx):
    """ACPI shutdown (soft power switch)"""
    output(ctx.obj.server.shutdown(ctx.obj.find_server(ctx.obj.server_name)['uuid']))

@server.command()
@click.pass_context
def show(ctx):
    """display server attributes"""
    output(ctx.obj.find_server(ctx.obj.server_name))

@server.command()
@click.pass_context
def runtime(ctx):
    """display server runtime data"""
    output(ctx.obj.server.runtime(ctx.obj.find_server(ctx.obj.server_name)['uuid']))

@server.command()
@click.option('-c', '--close', is_flag=True, help='close the TTY port')
@click.option('-e', '--exec', 'exec_command', type=str, metavar='COMMAND', help='execute COMMAND ADDRESS PORT')
@click.option('-p', '--password', is_flag=True, help='pipe vnc_password to stdin of --exec command')
@click.pass_context
def tty(ctx, close, exec_command, password):
    """open or close a console TTY port"""
    name = ctx.obj.server_name
    if close: 
        output(ctx.obj.close_tty(name))
    else:
        ret = ctx.obj.open_tty(name)
        if ret:
            if exec_command:
                if password:
                    server = ctx.obj.find_server(name)
                    pipe=f"echo '{server['vnc_password']}'|"
                else:
                    pipe=''
                url = ret['console_url']
                addr, port = (url.split('/')[2]).split(':')
                cmd=f"{pipe}{exec_command} {addr} {port}"
                exit_code = subprocess.call(cmd, shell=True)
                ret = f"subprocess returned {exit_code}"
    output(ret)

@server.command()
@click.option('-c', '--close', is_flag=True)
@click.pass_context
def vnc(ctx, close):
    """open or close a VNC session"""
    name = ctx.obj.server_name
    if close: 
        output(ctx.obj.close_vnc(name))
    else:
        output(ctx.obj.open_vnc(name))

@server.command()
@click.option('-s', '--status', type=str, default='started', help='desired server status')
@click.option('-t', '--timeout', type=int, default=15, help='timeout in seconds, 0=infinite')
@click.pass_context
def wait(ctx, status, timeout):
    """wait for server status"""
    name = ctx.obj.server_name
    server = ctx.obj.find_server(name)
    if timeout:
        timeout = time.time() + timeout
    while server['status'] != status:
        server=ctx.obj.find_server(name)
        if timeout and time.time() > timeout:
            error(f'Timeout waiting for server {name} status {status}' )
    output({'uuid': server['uuid'], 'status': server['status']})

@server.command()
@click.argument('drive', type=str)
@click.option('-c', '--dev-channel', type=str, default='0:0')
@click.option('-d', '--device', type=click.Choice(['virtio', 'ide']), default='virtio')
@click.pass_context
def attach(ctx, drive, dev_channel, device):
    """attach drive to server"""
    server = ctx.obj.find_server(ctx.obj.server_name)
    attachment=dict(
        drive=ctx.obj.find_drive(drive),
        dev_channel=dev_channel, 
        device=device,
        boot_order=len(server['drives'])+1
    )
    server.setdefault('drives', []).append(attachment)
    output(ctx.obj.server.update(server['uuid'], server))

@server.command()
@click.argument('drive', metavar='DRIVE', type=str)
@click.pass_context
def detach(ctx, drive):
    """detach drive from server"""
    name = ctx.obj.server_name
    server = ctx.obj.find_server(name)
    drive_uuid = ctx.obj.find_drive(drive)['uuid']
    found=False
    for index, attached_drive in enumerate(server['drives']):
        if drive_uuid == attached_drive['drive']['uuid']:
            del(server['drives'][index])
            found = True
            break
    if found:
        output(ctx.obj.server.update(server['uuid'], server))
    else:
        error(f'server {name} has no attached drive {drive}')


@server.command()
@click.argument('action', type=click.Choice(['add', 'delete', 'modify']), default='add')
@click.option('-c', '--config', type=click.Choice(['dhcp', 'static', 'manual', 'vlan']), default='dhcp')
@click.option('-m', '--model', type=str)
@click.option('-i', '--ip', type=str)
@click.option('-m', '--mac', type=str)
@click.option('--vlan', type=str)
@click.pass_context
def nic(ctx, action, config, model, ip, mac, vlan):
    """add, delete, or modify network interfaces"""
    name = ctx.obj.server_name
    server = ctx.obj.find_server(name)
    server.setdefault('nics', [])

    new_nic={}

    if model:
        new_nic['model'] = model

    if config=='dhcp':
        new_nic['ip_v4_conf'] = dict(conf='dhcp')
    elif config=='static':
        if not ip:
            error('static config requires --ip option (subscribed IP)')
        # TODO: verify the ip is subscribed and not already assigned
        new_nic['ip_v4_conf'] = dict(conf='static', ip=ip)
    elif config=='manual':
        new_nic['ip_v4_conf'] = dict(conf='manual')
    elif config=='vlan':
        if not vlan:
            error('vlan config requires --vlan option (subscribed VLAN)')
        # TODO: verify the VLAN is subscribed
        new_nic['vlan'] = vlan
    else:
        error(f'unknown config type {config}')

    if action == 'add':
        server['nics'].append(new_nic)
    else:
        if not mac:
            error(f'{action} action requires --mac option')

        # find index and nic of server.nics with matching mac address
        matches = [(i,n) for (i,n) in enumerate(server['nics']) if n['mac']==mac]
        if len(matches) != 1:
            error(f'{action} mac addr {mac} not found on server {name}')
        nic_index = matches[0][0]
        if action == 'delete':
            del(server['nics'][nic_index])
        elif action == 'modify':
            new_nic['mac'] = mac
            server['nics'][nic_index] = new_nic
        else:
            error(f'unknown action {action}')
    output(ctx.obj.server.update(server['uuid'], server))

@server.command()
@click.option('-r', '--rename', type=str)
@click.option('-c', '--cpu', metavar='CPU_COUNT', type=int, default=MIN_CPU, help='SMP CPU count')
@click.option('-s', '--speed', metavar='CPU_MHZ', type=int, default=MIN_MHZ, help='Mhz per cpu')
@click.option('-m', '--memory', type=str)
@click.option('-p', '--password', type=str)
@click.option('-S', '--smp', type=click.Choice(['cpu', 'core']), help='smp as multi-core or multi-cpu')
@click.pass_context
def modify(ctx, rename, cpu, speed, memory, password, smp):
    """modify server attributes"""

    server = ctx.obj.find_server(ctx.obj.server_name)
    if rename:
        server['name'] = rename
    if cpu or speed:
        server['cpu'] = cpu * speed
        server['smp'] = cpu
    if memory:
        server['mem'] = ctx.obj.convert_memory_value(memory)
    if password:
        server['vnc_password'] = password
    if smp:
        server['cpus_instead_of_cores']=bool(smp=='cpu')
    output(ctx.obj.server.update(server['uuid'], server))
