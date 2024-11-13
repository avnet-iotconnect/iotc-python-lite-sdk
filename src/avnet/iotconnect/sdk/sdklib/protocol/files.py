from dataclasses import dataclass, field
from typing import Optional

from avnet.iotconnect.sdk.sdklib.util import filter_init


@filter_init
@dataclass
class ProtocolDeviceConfigJson:
    cpid: Optional[str] = field(default=None)
    env: Optional[str] = field(default=None)
    uid: Optional[str] = field(default=None)
    did: Optional[str] = field(default=None)
    disc: Optional[str] = field(default=None)
    ver: Optional[str] = field(default="2.1")
    pf: Optional[str] = field(default="aws")
    at: Optional[int] = field(default=7)          # not sure what this means