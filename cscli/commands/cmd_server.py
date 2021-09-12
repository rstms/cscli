#!/usr/bin/env python3

import subprocess
import time

from .util import confirm, error, output


class Server:
    def __init__(self, name, client):
        self.name = name
        self.client = client

    def create(
        self, cpu, speed, memory, password, attach_drive, create_drive, boot_cdrom, smp
    ):
        """create a server resource, optionally create or attach a drive and/or boot cdrom"""
        output(
            self.client.create_server(
                self.name,
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

    def destroy(self, keep_drives, force):
        """delete server, optionally preserve drives, always preserve cdroms"""
        name = self.name
        server = self.client.find_server(name)
        uuid = server["uuid"]
        confirm(server, "destruction", "server", force)
        if keep_drives:
            drives = None
        else:
            drives = "disks"
        output(
            self.client.server.delete(server["uuid"], drives)
            or f"server {uuid} '{name}' destroyed"
        )

    def start(self):
        """power on"""
        output(self.client.server.start(self.client.find_server(self.name)["uuid"]))

    def stop(self):
        """power off"""
        output(self.client.server.stop(self.client.find_server(self.name)["uuid"]))

    def shutdown(self):
        """ACPI shutdown (soft power switch)"""
        output(self.client.server.shutdown(self.client.find_server(self.name)["uuid"]))

    def show(self):
        """display server attributes"""
        output(self.client.find_server(self.name))

    def runtime(self):
        """display server runtime data"""
        output(self.client.server.runtime(self.client.find_server(self.name)["uuid"]))

    def tty(self, close, exec_command, password):
        """open or close a console TTY port"""
        name = self.name
        if close:
            output(self.client.close_tty(name))
        else:
            ret = self.client.open_tty(name)
            if ret:
                if exec_command:
                    if password:
                        server = self.client.find_server(name)
                        pipe = f"echo '{server['vnc_password']}'|"
                    else:
                        pipe = ""
                    url = ret["console_url"]
                    addr, port = (url.split("/")[2]).split(":")
                    cmd = f"{pipe}{exec_command} {addr} {port}"
                    exit_code = subprocess.call(cmd, shell=True)
                    ret = f"subprocess returned {exit_code}"
        output(ret)

    def vnc(self, close):
        """open or close a VNC session"""
        name = self.name
        if close:
            output(self.client.close_vnc(name))
        else:
            output(self.client.open_vnc(name))

    def wait(self, status, timeout):
        """wait for server status"""
        name = self.name
        server = self.client.find_server(name)
        if timeout:
            timeout = time.time() + timeout
        while server["status"] != status:
            server = self.client.find_server(name)
            if timeout and time.time() > timeout:
                error(f"Timeout waiting for server {name} status {status}")
        output({"uuid": server["uuid"], "status": server["status"]})

    def attach(self, drive, dev_channel, device):
        """attach drive to server"""
        server = self.client.find_server(self.name)
        attachment = dict(
            drive=self.client.find_drive(drive),
            dev_channel=dev_channel,
            device=device,
            boot_order=len(server["drives"]) + 1,
        )
        server.setdefault("drives", []).append(attachment)
        output(self.client.server.update(server["uuid"], server))

    def detach(self, drive):
        """detach drive from server"""
        server = self.client.find_server(self.name)
        drive_uuid = self.client.find_drive(drive)["uuid"]
        found = False
        for index, attached_drive in enumerate(server["drives"]):
            if drive_uuid == attached_drive["drive"]["uuid"]:
                del server["drives"][index]
                found = True
                break
        if found:
            output(self.client.server.update(server["uuid"], server))
        else:
            error(f"server {self.name} has no attached drive {drive}")

    def nic(self, action, config, model, ip, mac, vlan):
        """add, delete, or modify network interfaces"""
        server = self.client.find_server(self.name)
        server.setdefault("nics", [])

        new_nic = {}

        if model:
            new_nic["model"] = model

        if config == "dhcp":
            new_nic["ip_v4_conf"] = dict(conf="dhcp")
        elif config == "static":
            if not ip:
                error("static config requires --ip option (subscribed IP)")
            # TODO: verify the ip is subscribed and not already assigned
            new_nic["ip_v4_conf"] = dict(conf="static", ip=ip)
        elif config == "manual":
            new_nic["ip_v4_conf"] = dict(conf="manual")
        elif config == "vlan":
            if not vlan:
                error("vlan config requires --vlan option (subscribed VLAN)")
            # TODO: verify the VLAN is subscribed
            new_nic["vlan"] = vlan
        else:
            error(f"unknown config type {config}")

        if action == "add":
            server["nics"].append(new_nic)
        else:
            if not mac:
                error(f"{action} action requires --mac option")

            # find index and nic of server.nics with matching mac address
            matches = [
                (i, n) for (i, n) in enumerate(server["nics"]) if n["mac"] == mac
            ]
            if len(matches) != 1:
                error(f"{action} mac addr {mac} not found on server {self.name}")
            nic_index = matches[0][0]
            if action == "delete":
                del server["nics"][nic_index]
            elif action == "modify":
                new_nic["mac"] = mac
                server["nics"][nic_index] = new_nic
            else:
                error(f"unknown action {action}")
        output(self.client.server.update(server["uuid"], server))

    def modify(self, rename, cpu, speed, memory, password, smp):
        """modify server attributes"""

        server = self.client.find_server(self.name)
        if rename:
            server["name"] = rename
        if cpu or speed:
            server["cpu"] = cpu * speed
            server["smp"] = cpu
        if memory:
            server["mem"] = self.client.convert_memory_value(memory)
        if password:
            server["vnc_password"] = password
        if smp:
            server["cpus_instead_of_cores"] = bool(smp == "cpu")
        output(self.client.server.update(server["uuid"], server))
