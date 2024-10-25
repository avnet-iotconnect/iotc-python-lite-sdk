# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

import json
from typing import Any, Dict, Optional

class MetaData:
    def __init__(self, at: int = 0, df: int = 0, cd: str = '', gtw: Optional[str] = None, edge: int = 0, pf: int = 1, hwv: str = '', swv: str = '', v: float = 2.1):
        self.at = at
        self.df = df
        self.cd = cd
        self.gtw = gtw
        self.edge = edge
        self.pf = pf
        self.hwv = hwv
        self.swv = swv
        self.v = v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'MetaData':
        return cls(
            at=data.get('at', 0),
            df=data.get('df', 0),
            cd=data.get('cd', ''),
            gtw=data.get('gtw'),
            edge=data.get('edge', 0),
            pf=data.get('pf', 1),
            hwv=data.get('hwv', ''),
            swv=data.get('swv', ''),
            v=data.get('v', 2.1)
        )

class HasAttributes:
    def __init__(self, d: int = 0, attr: int = 0, set_: int = 0, r: int = 0, ota: int = 0):
        self.d = d
        self.attr = attr
        self.set = set_
        self.r = r
        self.ota = ota

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'HasAttributes':
        return cls(
            d=data.get('d', 0),
            attr=data.get('attr', 0),
            set_=data.get('set', 0),
            r=data.get('r', 0),
            ota=data.get('ota', 0)
        )

class Topics:
    def __init__(self, rpt: str = '', flt: str = '', od: str = '', hb: str = '', ack: str = '', dl: str = '', di: str = '', c2d: str = '', set_: Dict[str, str] = None):
        self.rpt = rpt
        self.flt = flt
        self.od = od
        self.hb = hb
        self.ack = ack
        self.dl = dl
        self.di = di
        self.c2d = c2d
        self.set = set_ if set_ is not None else {}

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Topics':
        set_topics = data.get('set', {})
        return cls(
            rpt=data.get('rpt', ''),
            flt=data.get('flt', ''),
            od=data.get('od', ''),
            hb=data.get('hb', ''),
            ack=data.get('ack', ''),
            dl=data.get('dl', ''),
            di=data.get('di', ''),
            c2d=data.get('c2d', ''),
            set={k: v for k, v in set_topics.items()}
        )

class P:
    def __init__(self, n: str = '', h: str = '', p: int = 0, id_: str = '', un: str = '', topics: Topics = None):
        self.n = n
        self.h = h
        self.p = p
        self.id = id_
        self.un = un
        self.topics = topics if topics is not None else Topics()

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'P':
        return cls(
            n=data.get('n', ''),
            h=data.get('h', ''),
            p=data.get('p', 0),
            id_=data.get('id', ''),
            un=data.get('un', ''),
            topics=Topics.from_json(data.get('topics', {}))
        )

class DeviceData:
    def __init__(self, ec: int = 0, ct: int = 0, meta: MetaData = None, has: HasAttributes = None, p: P = None, dt: str = ''):
        self.ec = ec
        self.ct = ct
        self.meta = meta if meta is not None else MetaData()
        self.has = has if has is not None else HasAttributes()
        self.p = p if p is not None else P()
        self.dt = dt

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'DeviceData':
        return cls(
            ec=data.get('ec', 0),
            ct=data.get('ct', 0),
            meta=MetaData.from_json(data.get('meta', {})),
            has=HasAttributes.from_json(data.get('has', {})),
            p=P.from_json(data.get('p', {})),
            dt=data.get('dt', '')
        )

class ResponseObject:
    def __init__(self, d: DeviceData = None, status: int = 0, message: str = 'Success'):
        self.d = d if d is not None else DeviceData()
        self.status = status
        self.message = message

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ResponseObject':
        return cls(
            d=DeviceData.from_json(data.get('d', {})),
            status=data.get('status', 0),
            message=data.get('message', 'Success')
        )

# Example JSON
json_data = '{"d":{"ec":0,"ct":200,"meta":{"at":2,"df":60,"cd":"7LIBN8E","gtw":null,"edge":0,"pf":1,"hwv":"","swv":"","v":2.1},"has":{"d":0,"attr":1,"set":0,"r":0,"ota":0},"p":{"n":"mqtt","h":"poc-iotconnect-iothub-017-eu2.azure-devices.net","p":8883,"id":"avtds-avr-mchp-sn0123EE7A14329D3D01","un":"poc-iotconnect-iothub-017-eu2.azure-devices.net/avtds-avr-mchp-sn0123EE7A14329D3D01/?api-version=2018-06-30","topics":{"rpt":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/events/cd=7LIBN8E&v=2.1&mt=0&$.ct=application%2Fjson&$.ce=utf-8","flt":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/events/cd=7LIBN8E&v=2.1&mt=3&$.ct=application%2Fjson&$.ce=utf-8","od":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/events/cd=7LIBN8E&v=2.1&mt=4&$.ct=application%2Fjson&$.ce=utf-8","hb":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/events/cd=7LIBN8E&v=2.1&mt=5&$.ct=application%2Fjson&$.ce=utf-8","ack":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/events/cd=7LIBN8E&v=2.1&mt=6&$.ct=application%2Fjson&$.ce=utf-8","dl":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/events/cd=7LIBN8E&v=2.1&mt=7&$.ct=application%2Fjson&$.ce=utf-8","di":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/events/cd=7LIBN8E&v=2.1&di=1&$.ct=application%2Fjson&$.ce=utf-8","c2d":"devices/avtds-avr-mchp-sn0123EE7A14329D3D01/messages/devicebound/#","set":{"pub":"$iothub/twin/PATCH/properties/reported/?$rid={version}","sub":"$iothub/twin/PATCH/properties/desired/#","pubForAll":"$iothub/twin/GET/?$rid=0","subForAll":"$iothub/twin/res/#"}}},"dt":"2024-10-25T20:57:57.481Z"},"status":200,"message":"Device info loaded successfully."}'

# Parse JSON
data = json.loads(json_data)

# Create ResponseObject from JSON data
response = ResponseObject.from_json(data)

print(response)
print(response.d.meta.cd)  # Example access to nested attribute
