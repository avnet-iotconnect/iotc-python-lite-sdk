import random
import sys
import time
from dataclasses import dataclass, asdict

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, C2dCommand, TelemetryRecord, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION

# See telemetry-minimal.py example for a way to configure the device without the JSON file
# You can download the iotcDeviceConfig.json by clicking the cog icon in the upper right of your device's info panel
device_config = DeviceConfig.from_iotc_device_config_json_file("iotcDeviceConfig.json", "device-cert.pem", "device-pkey.pem")


@dataclass
class ExampleAccelerometerData:
    x: float
    y: float
    z: float


acc = {
    'x': 1,
    'y': 3
}


@dataclass
class ExampleSensorData:
    temperature: float
    humidity: float
    accel: ExampleAccelerometerData


def on_command(msg: C2dCommand):
    print("Received command", msg.command_name, msg.command_args)
    if msg.command_name == "set-user-led":
        if len(msg.command_args) == 3:
            print("Setting User LED to R:%d G:%d B:%d" % (int(msg.command_args[0]), int(msg.command_args[1]), int(msg.command_args[2])))
        else:
            print("Expected three command arguments, but got", len(msg.command_args))


def send_telemetry():
    # send structured data make sure your object has the @dataclass decorator
    data = ExampleSensorData(
        humidity=30.43,
        temperature=22.8,
        accel=ExampleAccelerometerData(
            x=0.565,
            y=0.334,
            z=0,
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
        'random': random.randint(0, 100),
        'accel': {
            'x': 'Value A',
            'y': 'Value 3',
            'obj': {
                'o': 2
            }
        },
        'latlng': [34, -43.22233]
    })

    # example of sending multiple telemetry records by accumulating data:
    records: list[TelemetryRecord] = []

    data.temperature = 34.4
    records.append(TelemetryRecord(asdict(data), timestamp=Client.timestamp_now()))

    time.sleep(1)  # wait some time and the update the record
    data.temperature = 34.6
    records.append(TelemetryRecord(asdict(data), timestamp=Client.timestamp_now()))
    c.send_telemetry_records(records)
    # multiple records will be sent with different timestamps


if __name__ == '__main__':
    try:
        c = Client(
            config=device_config,
            callbacks=Callbacks(
                command_cb=on_command
            )
        )
        while True:
            if not c.is_connected():
                print('(re)connecting...')
                c.connect()

            send_telemetry()
            time.sleep(10)

    except DeviceConfigError as dce:
        print(dce)
        sys.exit(1)

    except KeyboardInterrupt:
        print()
        sys.exit(2)
