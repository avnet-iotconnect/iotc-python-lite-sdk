import json
import os.path
from dataclasses import dataclass
from os import access, R_OK
from typing import Optional

from avnet.iotconnect.sdk.sdklib.protocol.files import ProtocolDeviceConfigJson


class DeviceConfigError(Exception):
    def __init__(self, message: str):
        self.msg = message
        super().__init__(message)


@dataclass
class DeviceConfig:
    """
    =param env: Your account environment. You can locate this in you IoTConnect web UI at Settings -> Key Value

    """
    env: str
    cpid: str
    duid: str
    device_cert_path: str
    device_pkey_path: str
    platform: str
    server_ca_cert_path: str = None # if not specified use system CA certificates in /etc/ssl or whatever it would be in windows
    _discovery_url: str = None

    def __post_init__(self):
        #todo:
        pass

    @classmethod
    def from_iotc_device_config_json(
            cls,
            device_config_json: ProtocolDeviceConfigJson,
            device_cert_path: str,
            device_pkey_path: str) -> 'DeviceConfig':
        if device_config_json.uid is None or device_config_json.cpid is None or device_config_json.env is None or \
                0 == len(device_config_json.uid) or 0 == len(device_config_json.cpid) or 0 == len(device_config_json.env):
            raise DeviceConfigError("The Device Config JSON file format seems to be invalid. Values for cpid, env and uid are required")
        if device_config_json.ver != "2.1":
            raise DeviceConfigError("The Device Config JSON seems to indicate that the device version is not 2.1, which is the only supported version")
        return DeviceConfig(
            env=device_config_json.env,
            cpid=device_config_json.cpid,
            duid=device_config_json.uid,
            platform=device_config_json.pf,
            device_cert_path=device_cert_path,
            device_pkey_path=device_pkey_path
        )

    @classmethod
    def from_iotc_device_config_json_file(
            cls,
            device_config_json_path: str,
            device_cert_path: str,
            device_pkey_path: str) -> 'DeviceConfig':
        if not os.path.isfile(device_config_json_path) or not access(device_config_json_path, R_OK):
            raise DeviceConfigError("File %s not accessible" % device_config_json_path)

        file_handle = open(device_config_json_path, "r")
        file_content = file_handle.read()
        file_handle.close()
        file_dict = json.loads(file_content)
        pdcj = ProtocolDeviceConfigJson(file_dict)
        return cls.from_iotc_device_config_json(pdcj, device_cert_path=device_cert_path, device_pkey_path=device_pkey_path)

    @property
    def platform(self) -> str:
        return self._platform

    @platform.setter
    def platform(self, v: str) -> None:
        if v not in ("aws", "az"):
            raise DeviceConfigError('DeviceConfig: Platform must be "aws" or "az"')
        self._platform = v

    @property
    def discovery_url(self) -> str:
        if self._discovery_url is not None:
            return self._discovery_url  # cached value
        elif self.platform == "az":
            self._discovery_url = "https://discovery.iotconnect.io"
        elif self.platform == "aws":
            if self.env == "poc":
                self._discovery_url = "https://awsdiscovery.iotconnect.io"
            else:
                # best guess...
                self._discovery_url = "https://discoveryconsole.iotconnect.io"

        return self._discovery_url

    @discovery_url.setter
    def discovery_url(self, v: str) -> None:
        self._discovery_url = v
