# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

import json
from typing import Any, Dict

from ..util import to_json

class DeviceData:
    def __init__(self, ec: int = 0, bu: str = '', pf: str = ''):
        self.ec = ec
        self.bu = bu
        self.pf = pf

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'DeviceData':
        return cls(
            ec=data.get('ec', 0),
            bu=data.get('bu', ''),
            pf=data.get('pf', '')
        )

class DiscoveryResponseData:
    def __init__(self, d: DeviceData = None, status: int = 0, message: str = 'Success'):
        self.d = d if d is not None else DeviceData()
        self.status = status
        self.message = message


    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'DiscoveryResponseData':
        device_data = DeviceData.from_json(data.get('d', {}))
        return cls(
            d=device_data,
            status=data.get('status', 0),
            message=data.get('message', 'Success')
        )


if __name__ == '__main__':
    # unit test
    json_data = '{"d":{"ec":0,"bu":"https://diavnet.iotconnect.io/api/2.1/agent/device-identity/cg/b892c358-e375-4cc3-8841-32e271e26151","log:mqtt":{"hn":"","un":"","pwd":"","topic":""},"pf":"az"},"status":200,"message":"Success"}'
    d = json.loads(json_data)
    response = DiscoveryResponseData.from_json(d)
    print("Json = ", to_json(response))
