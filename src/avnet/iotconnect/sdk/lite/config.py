import json
import os.path
import re
from dataclasses import dataclass, field
from os import access, R_OK
from typing import Optional

from avnet.iotconnect.sdk.sdklib import filter_init
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
    env: str = field(default=None)
    cpid: str = field(default=None)
    duid: str = field(default=None)
    device_cert_path: str = field(default=None)
    device_pkey_path: str = field(default=None)
    platform: Optional[str] = field(default=None)
    server_ca_cert_path: Optional[str] = field(default=None) # if not specified use system CA certificates in /etc/ssl or whatever it would be in windows
    discovery_url: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.platform not in ("aws", "az"):
            raise DeviceConfigError('DeviceConfig: Platform must be "aws" or "az"')
        if self.discovery_url is None:
            if self.platform == "az":
                self.discovery_url = "https://discovery.iotconnect.io"
            elif self.platform == "aws":
                if self.env == "poc":
                    self.discovery_url = "https://awsdiscovery.iotconnect.io"
                else:
                    # best guess...
                    self.discovery_url = "https://discoveryconsole.iotconnect.io"
        DeviceConfig._validate_file(self.device_cert_path, r"^-----BEGIN CERTIFICATE-----$")
        DeviceConfig._validate_file(self.device_pkey_path, r"^-----BEGIN.*PRIVATE KEY-----$")
        if not os.path.isfile(self.device_pkey_path) or not access(self.device_pkey_path, R_OK):
            raise DeviceConfigError("File %s not accessible" % self.device_pkey_path)


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
            discovery_url=device_config_json.disc,
            device_cert_path=device_cert_path,
            device_pkey_path=device_pkey_path
        )

    @classmethod
    def from_iotc_device_config_json_file(
            cls,
            device_config_json_path: str,
            device_cert_path: str,
            device_pkey_path: str) -> 'DeviceConfig':
        file_content = cls._validate_file(device_config_json_path)
        file_dict = json.loads(file_content)
        pdcj = ProtocolDeviceConfigJson(file_dict)
        return cls.from_iotc_device_config_json(pdcj, device_cert_path=device_cert_path, device_pkey_path=device_pkey_path)

    @classmethod
    def _validate_file(cls, file_name: str, first_line_match_pattern: Optional[str] = None) -> str:
        if not os.path.isfile(file_name) or not access(file_name, R_OK):
            raise DeviceConfigError("File %s not accessible" % file_name)
        file_handle = open(file_name, "r")
        file_content = file_handle.read()
        file_handle.close()
        if file_content is None or 0 == len(file_content):
            raise DeviceConfigError("File %s is empty" % file_name)
        if first_line_match_pattern is not None:
            first_line = file_content.splitlines()[0]
            if not re.search(first_line_match_pattern, first_line):
                raise DeviceConfigError("The file %s does not seem to be valid. Expected the file to start with regex %s" % (file_name, match_pattern))
        file_handle.close()
        return file_content

