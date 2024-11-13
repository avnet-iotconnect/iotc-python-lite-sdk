# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/


import json
from dataclasses import dataclass, field
from typing import Optional

from avnet.iotconnect.sdk.sdklib.util import filter_init


@filter_init
@dataclass
class ProtocolMetaJson:
    at: Optional[int] = None
    df: Optional[int] = None
    cd: Optional[str] = None
    gtw: Optional[int] = None
    edge: Optional[int] = None
    pf: Optional[int] = None
    hwv: str = field(default="")
    swv: str = field(default="")
    v: float = field(default=0.0)


@filter_init
@dataclass
class ProtocolHasJson:
    d: int = field(default=0)
    attr: int = field(default=0)
    set: int = field(default=0)
    r: int = field(default=0)
    ota: int = field(default=0)


@filter_init
@dataclass
class ProtocolSetJson:
    pub: Optional[str] = None
    sub: Optional[str] = None
    pubForAll: Optional[str] = None
    subForAll: Optional[str] = None


@filter_init
@dataclass
class ProtocolTopicsJson:
    rpt: Optional[str] = None
    flt: Optional[str] = None
    od: Optional[str] = None
    hb: Optional[str] = None
    ack: Optional[str] = None
    dl: Optional[str] = None
    di: Optional[str] = None
    c2d: Optional[str] = None
    set: ProtocolSetJson = field(default_factory=ProtocolSetJson)


@filter_init
@dataclass
class ProtocolIdentityPJson:
    n: Optional[str] = None
    h: Optional[str] = None
    p: int = field(default=0)
    id: Optional[str] = None
    un: Optional[str] = None
    topics: ProtocolTopicsJson = field(default_factory=ProtocolTopicsJson)


@filter_init
@dataclass
class ProtocolIdentityDJson:
    ec: int = field(default=0)
    ct: int = field(default=0)
    meta: ProtocolMetaJson = field(default_factory=ProtocolMetaJson)
    has: ProtocolHasJson = field(default_factory=ProtocolHasJson)
    p: ProtocolIdentityPJson = field(default_factory=ProtocolIdentityPJson)
    dt: Optional[str] = None


@filter_init
@dataclass
class ProtocolIdentityResponseJson:
    d: ProtocolIdentityDJson = field(default_factory=ProtocolIdentityDJson)
    status: int = field(default=0)
    message: str = field(default="")
