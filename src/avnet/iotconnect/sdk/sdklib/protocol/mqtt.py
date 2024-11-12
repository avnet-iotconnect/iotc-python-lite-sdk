from dataclasses import dataclass, field
from email.policy import default
from typing import Optional

from avnet.iotconnect.sdk.sdklib import filter_init


@filter_init
@dataclass
class ProtocolC2dUrlJson:
    url: Optional[str] = field(default=None)
    fileName: Optional[str] = field(default=None)

@filter_init
@dataclass
class ProtocolC2dMessageJson:
    urls: Optional[list[ProtocolC2dUrlJson]] = field(default_factory=list[ProtocolC2dUrlJson])
    ct: Optional[int] = field(default=None)
    cmd: Optional[str] = field(default=None)
    sw: Optional[str] = field(default=None)
    hw: Optional[str] = field(default=None)
    ack: Optional[str] = field(default=None)
