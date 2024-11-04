# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/


import json
from typing import Any, Dict, Optional
from ..util import to_json


class IotcMetaDataJson:
    def __init__(self,
                 at: int = -1,
                 df: int = -1,
                 cd: str = None,
                 gtw: str = None,
                 edge: int = 0,
                 pf: int = 1,
                 hwv: str = '',
                 swv: str = '',
                 v: float = 2.1):
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
    def from_dict(cls, data: Dict[str, Any]) -> 'IotcMetaDataJson':
        return cls(
            at=data.get('at'),
            df=data.get('df'),
            cd=data.get('cd'),
            gtw=data.get('gtw'),
            edge=data.get('edge'),
            pf=data.get('pf'),
            hwv=data.get('hwv'),
            swv=data.get('swv'),
            v=data.get('v',)
        )

class HasAttributes:
    def __init__(self, d: int = 0, attr: int = 0, set_: int = 0, r: int = 0, ota: int = 0):
        self.d = d
        self.attr = attr
        self.set = set_
        self.r = r
        self.ota = ota

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HasAttributes':
        return cls(
            d=data.get('d', 0),
            attr=data.get('attr', 0),
            set_=data.get('set', 0),
            r=data.get('r', 0),
            ota=data.get('ota', 0)
        )

# Twin/Shadow topics
class PropertyTopics:
    def __init__(self, pub: str = '', sub: str = '', pub_for_all: str = '', sub_for_all: str = ''):
        self.pub = pub
        self.sub = sub
        self.pubForAll = pub_for_all
        self.subForAll = sub_for_all

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyTopics':
        return cls(
            pub=data.get('pub', ''),
            sub=data.get('sub', ''),
            pub_for_all=data.get('pubForAll', ''),
            sub_for_all=data.get('subForAll', '')
        )

class Topics:
    def __init__(self, rpt: str = '', flt: str = '', od: str = '', hb: str = '', ack: str = '', dl: str = '', di: str = '', c2d: str = '', property_topics: PropertyTopics = None):
        self.rpt = rpt
        self.flt = flt
        self.od = od
        self.hb = hb
        self.ack = ack
        self.dl = dl
        self.di = di
        self.c2d = c2d
        self.property_topics = property_topics if property_topics is not None else PropertyTopics()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topics':
        property_topics_data = data.get('set', {})
        return cls(
            rpt=data.get('rpt', ''),
            flt=data.get('flt', ''),
            od=data.get('od', ''),
            hb=data.get('hb', ''),
            ack=data.get('ack', ''),
            dl=data.get('dl', ''),
            di=data.get('di', ''),
            c2d=data.get('c2d', ''),
            property_topics=PropertyTopics.from_dict(property_topics_data)
        )

class MqttData:
    def __init__(self, n: str = '', h: str = '', p: int = 0, id_: str = '', un: str = '', topics: Topics = None):
        self.n = n
        self.h = h
        self.p = p
        self.id = id_
        self.un = un
        self.topics = topics if topics is not None else Topics()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MqttData':
        return cls(
            n=data.get('n', ''),
            h=data.get('h', ''),
            p=data.get('p', 0),
            id_=data.get('id', ''),
            un=data.get('un', ''),
            topics=Topics.from_dict(data.get('topics', {}))
        )

class DeviceData:
    def __init__(self, ec: int = 0, ct: int = 0, meta: IotcMetaDataJson = None, has: HasAttributes = None, p: MqttData = None, dt: str = ''):
        self.ec = ec
        self.ct = ct
        self.metadata = meta if meta is not None else IotcMetaDataJson()
        self.has = has if has is not None else HasAttributes()
        self.mqtt_data = p if p is not None else MqttData()
        self.dt = dt

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceData':
        return cls(
            ec=data.get('ec', 0),
            ct=data.get('ct', 0),
            meta=IotcMetaDataJson.from_dict(data.get('meta', {})),
            has=HasAttributes.from_dict(data.get('has', {})),
            p=MqttData.from_dict(data.get('p', {})),
            dt=data.get('dt', '')
        )

class IdentityResponseData:
    def __init__(self, d: DeviceData = None, status: int = 0, message: str = 'Success'):
        self.d = d if d is not None else DeviceData()
        self.status = status
        self.message = message

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdentityResponseData':
        return cls(
            d=DeviceData.from_dict(data.get('d', {})),
            status=data.get('status', 0),
            message=data.get('message', 'Success')
        )



if __name__ == '__main__':
    # unit test
    json_data = '{"d":{"ec":0,"ct":200,"meta":{"at":2,"df":60,"cd":"ABCDN8E","gtw":null,"edge":0,"pf":1,"hwv":"","swv":"","v":2.1},"has":{"d":0,"attr":1,"set":0,"r":0,"ota":0},"p":{"n":"mqtt","h":"poc-iotconnect-iothub-017-eu2.azure-devices.net","p":8883,"id":"mydevice","un":"poc-iotconnect-iothub-017-eu2.azure-devices.net/mydevice/?api-version=2018-06-30","topics":{"rpt":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=0&$.ct=application%2Fjson&$.ce=utf-8","flt":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=3&$.ct=application%2Fjson&$.ce=utf-8","od":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=4&$.ct=application%2Fjson&$.ce=utf-8","hb":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=5&$.ct=application%2Fjson&$.ce=utf-8","ack":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=6&$.ct=application%2Fjson&$.ce=utf-8","dl":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=7&$.ct=application%2Fjson&$.ce=utf-8","di":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&di=1&$.ct=application%2Fjson&$.ce=utf-8","c2d":"devices/mydevice/messages/devicebound/#","set":{"pub":"$iothub/twin/PATCH/properties/reported/?$rid={version}","sub":"$iothub/twin/PATCH/properties/desired/#","pubForAll":"$iothub/twin/GET/?$rid=0","subForAll":"$iothub/twin/res/#"}}},"dt":"2024-10-25T20:57:57.481Z"},"status":200,"message":"Device info loaded successfully."}'
    jd = json.loads(json_data)
    response = IdentityResponseData.from_dict(jd)
    print("Json = ", to_json(response))
