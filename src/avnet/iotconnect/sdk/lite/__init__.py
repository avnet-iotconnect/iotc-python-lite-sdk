__version__ = '1.1.0'

# redirect these imports so that the user code is not affected by any changes in file organization
from .client import Client, ClientSettings, Callbacks
from .config import DeviceConfig
from .client import Client, ClientSettings, Callbacks

# redirect these imports so that the user code is not affected by any changes in file organization
from avnet.iotconnect.sdk.sdklib.mqtt import C2dCommand, C2dOta, C2dAck, C2dMessage, TelemetryRecord
from avnet.iotconnect.sdk.sdklib.error import DeviceConfigError
