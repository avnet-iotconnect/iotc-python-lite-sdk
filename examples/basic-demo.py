from pathlib import Path
from time import sleep

from avnet.iotconnect.sdk.lite import Client
from avnet.iotconnect.sdk.lite.client import DeviceConfig, TelemetryRecord, TelemetryValues

config = DeviceConfig(
    platform="aws",
    cpid="97FF86E8728645E9B89F7B07977E4B15",
    env="poc",
    duid="niktest-gen-ec02",
    device_cert_path="device-cert.pem",
    device_pkey_path="device-pkey.pem"
)

c = Client(config)

c.connect()