import random
import sys
import time
from dataclasses import dataclass, asdict

from avnet.iotconnect.sdk.lite import Client
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.client import DeviceConfig, Callbacks, C2dCommand, TelemetryRecord
from avnet.iotconnect.sdk.lite.config import DeviceConfigError

"""
A less elaborate way to specify your device config can be:
device_config = DeviceConfig(
    platform="aws",
    cpid="mycpid",                      # From Settings -> Key Vault in the web UI
    env="poc",                          # From Settings -> Key Vault in the web UI
    duid="my-device",                   # Your device unique ID
    discovery_url="https://url.io"      # (optional, can be inferred from platform) From Settings -> Key Vault in the web UI
    device_cert_path="device-cert.pem", # Path to your device certificate - absolute or relative from you current directory when executing   
    device_pkey_path="device-pkey.pem"  # Path to your device certificate - absolute or relative from you current directory when executing
    )
    or load from iotCeviceConfig.json which you can download by clicking the cog icon at the top right
    of the device info panel:
"""
device_config = DeviceConfig.from_iotc_device_config_json_file("iotcDeviceConfig.json", "device-cert.pem", "device-pkey.pem")

@dataclass
class ExampleAccelerometerData:
    x: float
    y: float
    z: float

acc = {
    'x' : 1,
    'y' : 3
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
    # send structured data
    # make your object inherit from dataclass
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

    # example of sending multiple telemetry records:
    records: list[TelemetryRecord] = []

    records.append(
        TelemetryRecord(
            {'random': random.randint(0, 100)},
            timestamp=Client.timestamp_now()
        )
    )
    time.sleep(1)  # wait some time to use a new timestamp

    records.append(
        TelemetryRecord(
            {'random': random.randint(0, 100)},
            timestamp=Client.timestamp_now()
        )
    )
    c.send_telemetry_records(records)


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
                # c._aws_qualification_start(['t2wlntge8x69qa.deviceadvisor.iot.eu-west-1.amazonaws.com'])

            send_telemetry()
            time.sleep(10)

    except DeviceConfigError as dce:
        print(dce)
        sys.exit(1)

    except KeyboardInterrupt:
        print()
        sys.exit(2)
