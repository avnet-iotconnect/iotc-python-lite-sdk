import json
import os.path
import re
from dataclasses import dataclass, field
from os import access, R_OK
from typing import Optional

from .error import DeviceConfigError
from avnet.iotconnect.sdk.sdklib.protocol.files import ProtocolDeviceConfigJson


@dataclass
class DeviceConfig:
    """
    This dictionary (dataclass) defines your device's configuration settings.
    You can construct an instance on the fly or use the from_iotc_device_config_json_file class method
    to load most of the device configuration's required parameters from the iotcDeviceConfig.json,
    which you can download by clicking the "note and cog" icon in your device's info panel.
    
    Example:

        device_config = DeviceConfig(
            platform="aws",
            cpid="ABCDEFG",
            env="poc",
            duid="my-device",
            device_cert_path="my-device-cert.pem",
            device_pkey_path="my-device-pkey.pem"
        )

    """
    platform: str = field(default=None)
    """The IoTconnect IoT platform - Either "aws" for AWS IoTCore or "az" for Azure IoTHub"""

    env: str = field(default=None)
    """Your account environment. You can locate this in you IoTConnect web UI at Settings -> Key Value"""

    cpid: str = field(default=None)
    """Your account CPID (Company ID). You can locate this in you IoTConnect web UI at Settings -> Key Value"""

    duid: str = field(default=None)
    """Your device unique ID"""

    device_cert_path: str = field(default=None)
    """Path to the device certificate file"""

    device_pkey_path: str = field(default=None)
    """Path to the device private key file"""

    discovery_url: Optional[str] = field(default=None)
    """Platform - either "aws" or "az" (Azure)"""

    server_ca_cert_path: Optional[str] = field(default=None)  # if not specified use system CA certificates in /etc/ssl or whatever it would be in windows
    """
    Optional path the server certificate that will be used to validate the server connection
    against known CA certificate. If not provided, the system Root CA certificate store (located at /etc/ssl/certs on Linux, for example)
    will be used. If provided, they should be the Amazon Root CA1 AWS, and DigiCert Global Root G2 for Azure.    
    Please note that is more secure to pass the actual server CA Root certificate in order to avoid potential MITM attacks.
    On Linux, you can use server_ca_cert_path="/etc/ssl/certs/DigiCert_Global_Root_CA.pem" for Azure,
    or server_ca_cert_path="/etc/ssl/certs/Amazon_Root_CA_1.pem" for AWS    
    """

    def __post_init__(self):
        """ Validate dataclass arguments and try to infoer some, if they are missing """
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
        if self.server_ca_cert_path is not None:
            DeviceConfig._validate_file(self.server_ca_cert_path, r"^-----BEGIN CERTIFICATE-----$")

    @classmethod
    def from_iotc_device_config_json(
            cls,
            device_config_json: ProtocolDeviceConfigJson,
            device_cert_path: str,
            device_pkey_path: str,
            server_ca_cert_path: Optional[str] = None) -> 'DeviceConfig':
        """ Return a class instance based on a json string which is in format of the downloadable iotcDeviceConfig.json"""
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
            device_pkey_path=device_pkey_path,
            server_ca_cert_path=server_ca_cert_path
        )

    @classmethod
    def from_iotc_device_config_json_file(
            cls,
            device_config_json_path: str,
            device_cert_path: str,
            device_pkey_path: str,
            server_ca_cert_path: Optional[str] = None) -> 'DeviceConfig':
        """ Return a class instance based on a downloaded iotcDeviceConfig.json fom device's Info panel in IoTConnect"""
        file_content = cls._validate_file(device_config_json_path)
        file_dict = json.loads(file_content)
        pdcj = ProtocolDeviceConfigJson(file_dict)
        return cls.from_iotc_device_config_json(pdcj, device_cert_path=device_cert_path, device_pkey_path=device_pkey_path, server_ca_cert_path=server_ca_cert_path)

    @classmethod
    def _validate_file(cls, file_name: str, first_line_match_pattern: Optional[str] = None) -> str:
        """ Helper to validate a file - it needs to exist, needs to be readable and (if supplied) the first line has to match the pattern """
        if not os.path.isfile(file_name) or not access(file_name, R_OK):
            raise DeviceConfigError("File %s is not accessible" % file_name)
        file_handle = open(file_name, "r")
        file_content = file_handle.read()
        file_handle.close()
        if file_content is None or 0 == len(file_content):
            raise DeviceConfigError("File %s is empty" % file_name)
        if first_line_match_pattern is not None:
            first_line = file_content.splitlines()[0]
            if not re.search(first_line_match_pattern, first_line):
                raise DeviceConfigError("The file %s does not seem to be valid. Expected the file to start with regex %s" % (file_name, first_line_match_pattern))
        file_handle.close()
        return file_content
