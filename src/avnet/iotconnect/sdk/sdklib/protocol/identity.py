# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/


import json
from dataclasses import dataclass, field
from typing import Optional

from ..util import to_json, filter_init


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


if __name__ == '__main__':
    # unit test
    json_data = '{"d":{"ec":0,"ct":200,"meta":{"at":2,"df":60,"cd":"ABCDN8E","gtw":null,"edge":0,"pf":1,"hwv":"","swv":"","v":2.1},"has":{"d":0,"attr":1,"set":0,"r":0,"ota":0},"p":{"n":"mqtt","h":"poc-iotconnect-iothub-017-eu2.azure-devices.net","p":8883,"id":"mydevice","un":"poc-iotconnect-iothub-017-eu2.azure-devices.net/mydevice/?api-version=2018-06-30","topics":{"rpt":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=0&$.ct=application%2Fjson&$.ce=utf-8","flt":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=3&$.ct=application%2Fjson&$.ce=utf-8","od":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=4&$.ct=application%2Fjson&$.ce=utf-8","hb":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=5&$.ct=application%2Fjson&$.ce=utf-8","ack":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=6&$.ct=application%2Fjson&$.ce=utf-8","dl":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=7&$.ct=application%2Fjson&$.ce=utf-8","di":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&di=1&$.ct=application%2Fjson&$.ce=utf-8","c2d":"devices/mydevice/messages/devicebound/#","set":{"pub":"$iothub/twin/PATCH/properties/reported/?$rid={version}","sub":"$iothub/twin/PATCH/properties/desired/#","pubForAll":"$iothub/twin/GET/?$rid=0","subForAll":"$iothub/twin/res/#"}}},"dt":"2024-10-25T20:57:57.481Z"},"status":200,"message":"Device info loaded successfully."}'
    response = ProtocolIdentityResponseJson(json.loads(json_data))
    print("Json = ", to_json(response))
