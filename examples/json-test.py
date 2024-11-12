import json
from dataclasses import dataclass, field

from avnet.iotconnect.sdk.sdklib.util import filter_init


@filter_init
@dataclass
class D:
    ec: int = field(default=None)
    ct: int = field(default=None)

@filter_init
@dataclass
class Main:
    d: D = field(default=None)
    st:int = field(default=None)

data = '{"d":{"ec":0,"ct":200,"meta":{"at":2,"df":60,"cd":"ABCDN8E","gtw":null,"edge":0,"pf":1,"hwv":"","swv":"","v":2.1},"has":{"d":0,"attr":1,"set":0,"r":0,"ota":0},"p":{"n":"mqtt","h":"poc-iotconnect-iothub-017-eu2.azure-devices.net","p":8883,"id":"mydevice","un":"poc-iotconnect-iothub-017-eu2.azure-devices.net/mydevice/?api-version=2018-06-30","topics":{"rpt":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=0&$.ct=application%2Fjson&$.ce=utf-8","flt":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=3&$.ct=application%2Fjson&$.ce=utf-8","od":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=4&$.ct=application%2Fjson&$.ce=utf-8","hb":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=5&$.ct=application%2Fjson&$.ce=utf-8","ack":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=6&$.ct=application%2Fjson&$.ce=utf-8","dl":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&mt=7&$.ct=application%2Fjson&$.ce=utf-8","di":"devices/mydevice/messages/events/cd=7LIBN8E&v=2.1&di=1&$.ct=application%2Fjson&$.ce=utf-8","c2d":"devices/mydevice/messages/devicebound/#","set":{"pub":"$iothub/twin/PATCH/properties/reported/?$rid={version}","sub":"$iothub/twin/PATCH/properties/desired/#","pubForAll":"$iothub/twin/GET/?$rid=0","subForAll":"$iothub/twin/res/#"}}},"dt":"2024-10-25T20:57:57.481Z"},"status":200,"message":"Device info loaded successfully."}'


map = json.loads(data)
print(map)
m = Main(map)
if not m.d:
    print("missing d")
else:
    print(m.d.ec)

print(m.d)
