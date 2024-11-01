from time import sleep

from avnet.iotconnect.sdk.lite import Client
from avnet.iotconnect.sdk.lite.client import DeviceConfig, TelemetryRecord, TelemetryValues


values: TelemetryValues = TelemetryValues({
    "temperature": 20.33,
    "empty": None,
    "flag": True,
    "obj": {
        "sensor-type": "infrared",
        "value": 255,
        "location": [41.881832, -87.623177],
    },
    "geo-coordinate": [41.881832, -87.623177],
})

entry1 = TelemetryRecord(values=values, timestamp=Client.timestamp_now())
sleep(0.1)
entry2 = TelemetryRecord(values=values, timestamp=Client.timestamp_now(), unique_id="uid1", tag='uid2')

c.send_telemetry(values)
c.send_telemetry(values, timestamp=Client.timestamp_now())

c.send_telemetry_records([entry1, entry2])

c.send_telemetry({'x': 1})

c.send_telemetry({'x': 2, 'y': None}, timestamp=Client.timestamp_now())

c.connect()
