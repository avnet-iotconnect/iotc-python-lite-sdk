# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

import json
from dataclasses import dataclass, field
from typing import Optional

from ..util import to_json, filter_init


@filter_init
@dataclass
class ProtocolDiscoveryDJson:
    ec: Optional[int] = field(default=None)
    bu: Optional[str] = field(default=None)
    pf: Optional[str] = field(default=None)
    dip: Optional[int] = field(default=None)
    errorMsg: Optional[str] = None

@filter_init
@dataclass
class IotcDiscoveryResponseJson:
    d: ProtocolDiscoveryDJson = field(default_factory=ProtocolDiscoveryDJson)
    status: Optional[int] = field(default=None)
    message: Optional[str] = field(default=None)


if __name__ == '__main__':
    # unit test
    json_data = '{"d":{"ec":0,"bu":"https://diavnet.iotconnect.io/api/2.1/agent/device-identity/cg/b892c358-e375-4cc3-8841-32e271e26151","log:mqtt":{"hn":"","un":"","pwd":"","topic":""},"pf":"az"},"status":200,"message":"Success"}'
    d = json.loads(json_data)
    response = IotcDiscoveryResponseJson(d)
    print("Json = ", to_json(response))
