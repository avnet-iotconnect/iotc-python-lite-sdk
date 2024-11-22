__version__ = '0.1.1'

from .error import DeviceConfigError
from .config import DeviceConfig
from .client import Client, ClientSettings, Callbacks

# redirect these imports so that the user code is not affected by any changes in file organization
from avnet.iotconnect.sdk.sdklib.mqtt import C2dCommand, C2dOta, C2dAck, C2dMessage, TelemetryRecord
