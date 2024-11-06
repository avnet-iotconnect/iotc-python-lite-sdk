import random
import time
from dataclasses import dataclass, asdict

import avnet.iotconnect.sdk.lite
from avnet.iotconnect.sdk.lite import Client
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.client import DeviceConfig, UserCallbacks, C2dMessage, TelemetryRecord

device_config = DeviceConfig(
    platform="aws",
    cpid="97FF86E8728645E9B89F7B07977E4B15",
    env="poc",
    duid="python-lite-sdk01",
    device_cert_path="device-cert.pem",
    device_pkey_path="device-pkey.pem"
)

@dataclass
class ExampleAccelerometerData:
    x: float
    y: float
    z: float

@dataclass
class ExampleSensorData:
    temperature: float
    humidity: float
    accel: ExampleAccelerometerData

def on_command(msg: C2dMessage):
    print("Received command", msg.command_name, msg.command_args)
    if msg.command_name == "set-user-led":
        if len(msg.command_args) == 3:
            print("Setting User LED to R:%d G:%d B:%d" % (int(msg.command_args[0]), int(msg.command_args[1]), int(msg.command_args[2])))
        else:
            print("Expected three command arguments, but got", len(msg.command_args))

c = Client(
    config=device_config,
    callbacks=UserCallbacks(
        command_cb=on_command
    )
)
if __name__ == '__main__':
    while True:
        if not c.is_connected():
            print('(re)connecting...')
            c.connect()
            # c._aws_qualification_start(['t2wlntge8x69qa.deviceadvisor.iot.eu-west-1.amazonaws.com'])


        # send structured data
        # make your object inherit from dataclass
        data = ExampleSensorData(
            humidity=30.43,
            temperature=22.8,
            accel=ExampleAccelerometerData(
                x = 0.565,
                y = 0.334,
                z = 0,
            )
        )
        c.send_telemetry(asdict(data))

        # we can update the data update
        data.temperature = 23.1
        data.accel.x = 0.573
        data.accel.z = 0.002
        c.send_telemetry(asdict(data))

        # send simple data using a dict initializer
        c.send_telemetry({
            'sdk_version': SDK_VERSION,
            'random' : random.randint(0,100),
            'accel' : {
                'x' : 'Value A',
                'y' : 'Value 3',
                'obj' : {
                    'o': 2
                }
            },
            'latlng' : [34, -43.22233]
        })

        # example of sending multiple telemetry records:
        records: list[TelemetryRecord]= []

        records.append(
            TelemetryRecord(
                {'random': random.randint(0, 100)},
                timestamp=Client.timestamp_now()
            )
        )
        time.sleep(1) # wait some time to use a new timestamp

        records.append(
            TelemetryRecord(
                {'random': random.randint(0, 100)},
                timestamp=Client.timestamp_now()
            )
        )
        c.send_telemetry_records(records)

        time.sleep(10)
