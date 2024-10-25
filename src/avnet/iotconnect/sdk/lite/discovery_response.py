# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

import json
from typing import Any, Dict

class LogMQTT:
    def __init__(self, hn: str = '', un: str = '', pwd: str = '', topic: str = ''):
        self.hn = hn
        self.un = un
        self.pwd = pwd
        self.topic = topic

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'LogMQTT':
        return cls(
            hn=data.get('hn', ''),
            un=data.get('un', ''),
            pwd=data.get('pwd', ''),
            topic=data.get('topic', '')
        )

class DeviceData:
    def __init__(self, ec: int = 0, bu: str = '', log_mqtt: LogMQTT = None, pf: str = ''):
        self.ec = ec
        self.bu = bu
        self.log_mqtt = log_mqtt if log_mqtt is not None else LogMQTT()
        self.pf = pf

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'DeviceData':
        log_mqtt_data = data.get('log:mqtt', {})
        log_mqtt = LogMQTT.from_json(log_mqtt_data)
        return cls(
            ec=data.get('ec', 0),
            bu=data.get('bu', ''),
            log_mqtt=log_mqtt,
            pf=data.get('pf', '')
        )

class ResponseObject:
    def __init__(self, d: DeviceData = None, status: int = 0, message: str = 'Success'):
        self.d = d if d is not None else DeviceData()
        self.status = status
        self.message = message

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ResponseObject':
        device_data = DeviceData.from_json(data.get('d', {}))
        return cls(
            d=device_data,
            status=data.get('status', 0),
            message=data.get('message', 'Success')
        )

# Example JSON
json_data = '{"d":{"ec":0,"bu":"https://diavnet.iotconnect.io/api/2.1/agent/device-identity/cg/b892c358-e375-4cc3-8841-32e271e26151","log:mqtt":{"hn":"","un":"","pwd":"","topic":""},"pf":"az"},"status":200,"message":"Success"}'

# Parse JSON
data = json.loads(json_data)

# Create ResponseObject from JSON data
response = ResponseObject.from_json(data)
def get_json(obj):
  return json.loads(
    json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
  )
print("Json = ", get_json(response))
