from dataclasses import dataclass, field


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
    server_ca_cert_path: str = None
    _discovery_url: str = None

    @property
    def platform(self) -> str:
        return self._platform

    @platform.setter
    def platform(self, v : str) -> None:
        if v not in ("aws", "az"):
            raise DeviceConfigError('DeviceConfig: Platform must be "aws" or "az"')
        self._platform = v

    @property
    def discovery_url(self) -> str:
        if self._discovery_url is not None:
            return self._discovery_url # cached value
        elif self.platform == "az":
            self._discovery_url= "https://discovery.iotconnect.io"
        elif self.platform == "aws":
            if self.env == "poc":
                self._discovery_url = "https://awsdiscovery.iotconnect.io"
            else:
                # best guess...
                self._discovery_url = "https://consolediscovery.iotconnect.io"

        return self._discovery_url

    @discovery_url.setter
    def discovery_url(self, v : str) -> None:
        self._discovery_url = v
