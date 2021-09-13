#!/usr/bin/env python3

import os

import requests

from .error import ParameterError, ResourceNotFound


class CloudSigmaClient(object):
    def __init__(self, region=None, username=None, password=None):

        region = region or os.getenv("CLOUDSIGMA_REGION")
        username = username or os.getenv("CLOUDSIGMA_USERNAME")
        password = password or os.getenv("CLOUDSIGMA_PASSWORD")

        # use hack to pass credentials directly to pycloudsigma module
        # See github issue:
        #   https://github.com/cloudsigma/pycloudsigma/issues/7
        # Initialization workaround adapted from:
        #   http://blog.sourcepole.ch/2016/11/22/manually-initializing-the-pycloudsigma-module/
        # now import (and initialize) the cloudsigma module

        # allow pycloudsigma to read a null config file
        os.putenv("CLOUDSIGMA_CONFIG", "/dev/null")
        import cloudsigma

        # monkeypatch the config values into the module config
        cloudsigma.conf.config.__setitem__(
            "api_endpoint", f"https://{region}.cloudsigma.com/api/2.0/"
        )
        cloudsigma.conf.config.__setitem__(
            "ws_endpoint", f"wss://direct.{region}.cloudsigma.com/websocket"
        )
        cloudsigma.conf.config.__setitem__("username", username)
        cloudsigma.conf.config.__setitem__("password", password)

        # save config values for local image upload
        self.username = username
        self.password = password
        self.upload_endpoint = (
            f"https://direct.{region}.cloudsigma.com/api/2.0/drives/upload/"
        )

        self.config = cloudsigma.conf.config
        self.server = cloudsigma.resource.Server()
        self.drive = cloudsigma.resource.Drive()
        self.vlan = cloudsigma.resource.VLAN()
        self.ip = cloudsigma.resource.IP()
        self.subscription = cloudsigma.resource.Subscriptions()
        self.capabilities = cloudsigma.resource.Capabilites()

        self.list_format = None

    def _get_name(self, uuid, _type):
        if _type == "server":
            server = self.find_server(uuid)
            name = server.get("name")
        elif _type == "drive":
            drive = self.find_drive(uuid)
            name = drive.get("name")
        elif _type == "vlan":
            vlan = self.find_vlan(uuid)
            name = vlan["meta"].get("name")
        elif _type == "ip":
            ip = self.find_ip(uuid)
            name = ip["meta"].get("name")
        elif _type == "subscription":
            name = None
        else:
            raise ParameterError("unknown resource type {_type}")
        return name or f"<unnamed_{_type}>"

    def _format_resource(self, resource, item, list_format):
        if resource == self.server:
            label = "server"
            count = item["smp"]
            speed = int(item["cpu"]) / count
            nics = []
            for nic in item["nics"]:
                mac = nic["mac"]
                if nic["vlan"]:
                    config = "vlan"
                else:
                    config = nic["ip_v4_conf"]["conf"]
                if config == "static":
                    if nic["runtime"]:
                        ip = nic["runtime"]["ip_v4"]["uuid"]
                    else:
                        ip = nic["ip_v4_conf"]["ip"]["uuid"]
                elif config == "dhcp":
                    if nic["runtime"]:
                        ip = nic["runtime"]["ip_v4"]["uuid"]
                    else:
                        ip = "<assigned-on-boot>"
                elif config in ["manual", "vlan"]:
                    ip = "<os-configured>"
                else:
                    raise ParameterError(f"unknown nic conf value {config}")
                nics.append({mac: dict(config=config, ip=ip)})
            if item["cpus_instead_of_cores"]:
                smp_type = "cpu"
            else:
                smp_type = "core"
            data = [
                dict(name=self._get_name(item["uuid"], label)),
                dict(status=item["status"]),
                dict(cpu=f"{count}"),
                dict(clock=f"{speed/1000}Ghz"),
                dict(smp=smp_type),
                dict(memory=self.format_memory_value(item["mem"])),
                dict(
                    drives=[
                        self._get_name(drive["drive"]["uuid"], "drive")
                        for drive in item["drives"]
                    ]
                ),
                dict(nics=nics),
            ]
        elif resource == self.drive:
            label = "drive"
            mounted = item["mounted_on"]
            if len(mounted):
                mounted_on = [
                    self._get_name(server["uuid"], "server") for server in mounted
                ]
            else:
                mounted_on = []
            data = [
                dict(name=self._get_name(item["uuid"], label)),
                dict(size=self.format_memory_value(item["size"])),
                dict(media=item["media"]),
                dict(storage_type=item["storage_type"]),
                dict(mounted=mounted_on),
            ]
        elif resource == self.vlan:
            label = "vlan"
            data = [
                dict(name=self._get_name(item["uuid"], label)),
                dict(description=item["meta"].get("description")),
            ]
        elif resource == self.ip:
            label = "ip"
            data = [
                dict(name=self._get_name(item["uuid"], label)),
                dict(
                    server=[
                        self._get_name(item["server"]["uuid"], "server")
                        if item["server"]
                        else "unassigned"
                    ]
                ),
                dict(description=item["meta"].get("description")),
            ]
        elif resource == self.subscription:
            label = "subscription"
            data = [dict(name=self._get_name(item["uuid"], label)), dict(detail="")]
        else:
            raise ParameterError(f"Unknown resource: {resource}")

        if list_format == "text":
            dlines = [""]
            for dd in data:
                assert (len(dd)) == 1
                for k, v in dd.items():
                    if isinstance(v, list):
                        if k == "nics":
                            dlines.append(f"{k}=[")
                            for vv in v:
                                dlines.append(f"  {vv}")
                            dlines.append("]")
                        elif k == "drives":
                            dlines.append(f"{k}={v}")
                    else:
                        if len(dlines[-1]):
                            dlines[-1] += "  "
                        dlines[-1] += f"{k}={v}"
            longest = max([len(dd) for dd in dlines])
            dlines = [d + (" " * (longest - len(d))) for d in dlines][:longest]

            data = dlines

        return {item["uuid"]: data}

    def _list_resources(self, resource, list_format):
        if resource not in (self.subscription, self.capabilities) and list_format:
            resources = resource.list_detail()
        else:
            resources = resource.list()

        if list_format == "uuid":
            resources = [{i["uuid"]: None} for i in resources]
        elif list_format in ["brief", "text"]:
            resources = [
                self._format_resource(resource, item, list_format) for item in resources
            ]
        elif list_format in ["detail", None]:
            # no post-processing
            pass
        else:
            raise ParameterError(f"unknown list_format {self.list_format}")

        return resources

    def list_all(self, list_format):
        resources = {}
        all_resources = dict(
            servers=self.server, drives=self.drive, vlans=self.vlan, ips=self.ip
        )
        for label, resource in all_resources.items():
            resources[label] = self._list_resources(resource, list_format)
        return resources

    def list_servers(self, list_format):
        return dict(servers=self._list_resources(self.server, list_format))

    def list_drives(self, list_format):
        return dict(drives=self._list_resources(self.drive, list_format))

    def list_vlans(self, list_format):
        return dict(vlans=self._list_resources(self.vlan, list_format))

    def list_ips(self, list_format):
        return dict(ips=self._list_resources(self.ip, list_format))

    def list_subscriptions(self, list_format):
        if list_format not in ["uuid", "detail"]:
            list_format = "detail"
        return dict(subscriptions=self._list_resources(self.subscription, list_format))

    def list_capabilities(self, list_format):
        return dict(capabilities=[self._list_resources(self.capabilities, "detail")])

    def _find_resource(self, resource_lister, _type, name):
        for resource in list(resource_lister("detail").values())[0]:
            if name in [resource.get("name"), resource.get("uuid")]:
                return resource
        raise ResourceNotFound(f"unknown {_type} {name}")

    def find_server(self, name):
        return self._find_resource(self.list_servers, "server", name)

    def find_drive(self, name):
        return self._find_resource(self.list_drives, "drive", name)

    def find_vlan(self, name):
        return self._find_resource(self.list_vlans, "vlan", name)

    def find_ip(self, name=None):
        return self._find_resource(self.list_ips, "ip", name)

    def find_subscription(self, name=None):
        return self._find_resource(self.list_subscriptions, "subscription", name)

    def open_tty(self, name):
        return self.server.open_console(self.find_server(name)["uuid"])

    def close_tty(self, name):
        return self.server.close_console(self.find_server(name)["uuid"])

    def open_vnc(self, name):
        return self.server.open_vnc(self.find_server(name)["uuid"])

    def close_vnc(self, name):
        return self.server.close_vnc(self.find_server(name)["uuid"])

    def convert_memory_value(self, value):
        if value[-1] in ("t", "T"):
            value = float(value[:-1]) * 1024 ** 4
        if value[-1] in ("g", "G"):
            value = float(value[:-1]) * 1024 ** 3
        elif value[-1] in ("m", "M"):
            value = float(value[:-1]) * 1024 ** 2
        elif value[-1] in ("k", "K"):
            value = float(value[:-1]) * 1024
        else:
            value = int(value)
        return int(value)

    def format_memory_value(self, value):
        value = float(value)
        if value >= 1024 ** 4:
            value /= 1024 ** 4
            suffix = "T"
        elif value >= 1024 ** 3:
            value /= 1024 ** 3
            suffix = "G"
        elif value >= 1024 ** 2:
            value /= 1024 ** 2
            suffix = "M"
        elif value >= 1024:
            value /= 1024
            suffix = "K"
        else:
            suffix = ""
        number = "%.1f" % (value)
        if number[-2:] == ".0":
            number = number[:-2]
        return number + suffix

    def map_storage_type(self, storage_type):
        if storage_type == "ssd":
            return "dssd"
        elif storage_type == "magnetic":
            return "zadara"

        raise ParameterError(f"unknown storage_type {storage_type}")

    def create_drive(self, name, size, media, multimount, storage_type):
        return self.drive.create(
            dict(
                name=name,
                size=self.convert_memory_value(size),
                media=media,
                storage_type=self.map_storage_type(storage_type),
                allow_multimount=multimount,
            )
        )

    def modify_drive(
        self, name, rename=None, media=None, multimount=None, storage_type=None
    ):
        drive = self.find_drive(name)
        if rename:
            drive["name"] = rename
        if media:
            drive["media"] = media
        if multimount:
            drive["allow_multimount"] = multimount == "enable"
        if storage_type:
            drive["storage_type"] = storage_type
        return self.drive.update(drive["uuid"], drive)

    def resize_drive(self, drive, size):
        drive["size"] = self.convert_memory_value(size)
        return self.drive.resize(drive["uuid"], drive)

    def create_server(
        self,
        name,
        cpu_count,
        cpu_speed,
        memory,
        password,
        attach_drive,
        create_drive,
        boot_cdrom,
        smp,
    ):
        """create a server, attaching or creating a drive, attaching a boot iso"""

        parameters = dict(
            name=name,
            cpu=cpu_count * cpu_speed,
            smp=cpu_count,
            mem=self.convert_memory_value(memory),
            vnc_password=password,
            cpus_instead_of_cores=bool(smp == "cpu"),
        )
        server = self.server.create(parameters)

        server.setdefault("drives", [])
        if boot_cdrom:
            cdrom = self.find_drive(boot_cdrom)
            if cdrom:
                if cdrom["media"] == "cdrom":
                    server["drives"].append(
                        dict(
                            boot_order=2,
                            dev_channel="0:0",
                            device="ide",
                            drive=cdrom["uuid"],
                        )
                    )
                else:
                    raise ParameterError(
                        f"failed boot cdrom attach; {boot_cdrom} media must be cdrom"
                    )
            else:
                raise ResourceNotFound(
                    f"failed boot cdrom attach; {boot_cdrom} not found"
                )

        if attach_drive:
            drive = self.find_drive(attach_drive)
            if drive["media"] != "disk":
                raise ParameterError(
                    f"failed drive attach; {attach_drive} must be a disk drive"
                )
            elif drive["status"] != "unmounted":
                raise ParameterError(
                    f"failed drive attach; {attach_drive} must be unmounted"
                )
        elif create_drive:
            drive = self.create_drive(
                f"{name}-system", create_drive, "disk", False, "ssd"
            )
        else:
            drive = None

        if drive:
            server["drives"].append(
                dict(
                    boot_order=1,
                    dev_channel="0:0",
                    device="virtio",
                    drive=drive["uuid"],
                )
            )

        # default nic creation is a single public DHCP
        server["nics"] = [
            {
                "ip_v4_conf": {"conf": "dhcp", "ip": None},
                "model": "virtio",
                "vlan": None,
            }
        ]

        return self.server.update(server["uuid"], server)

    def upload_drive_image(self, input_file):
        """upload an image, creating a new drive, and return UUID"""
        s = requests.Session()
        s.auth = (self.config.get("username"), self.config.get("password"))
        s.headers.update({"Content-Type": "application/octet-stream"})
        r = s.post(self.upload_endpoint, data=input_file)
        return r.text.strip()
