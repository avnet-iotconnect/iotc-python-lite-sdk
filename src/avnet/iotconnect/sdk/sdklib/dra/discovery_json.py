# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

import json
from typing import Any, Dict

from ..util import to_json

class IotcDeviceJson:
    def __init__(self, ec: int = 0, bu: str = '', pf: str = ''):
        self.ec = ec
        self.bu = bu
        self.pf = pf

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IotcDeviceJson':
        return cls(
            ec=data.get('ec', -1),
            bu=data.get('bu', ''),
            pf=data.get('pf', '')
        )

class IotcDiscoveryResponseJson:
    def __init__(self,
                 d: IotcDeviceJson = IotcDeviceJson(),
                 status: int = -1,
                 message: str = None):
        self.d = d
        self.status = status
        self.message = message

    @classmethod
    def from_json(cls, json_str: str) -> 'IotcDiscoveryResponseJson':
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IotcDiscoveryResponseJson':
        device_data = IotcDeviceJson.from_dict(data.get('d', {}))
        return cls(
            d=device_data,
            status=data.get('status', -1),
            message=data.get('message')
        )

if __name__ == '__main__':
    # unit test
    json_data = '{"d":{"ec":0,"bu":"https://diavnet.iotconnect.io/api/2.1/agent/device-identity/cg/b892c358-e375-4cc3-8841-32e271e26151","log:mqtt":{"hn":"","un":"","pwd":"","topic":""},"pf":"az"},"status":200,"message":"Success"}'
    d = json.loads(json_data)
    response = IotcDiscoveryResponseJson.from_dict(d)
    print("Json = ", to_json(response))
