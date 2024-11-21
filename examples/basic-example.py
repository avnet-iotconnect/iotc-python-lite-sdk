# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

import random
import sys
import time
from dataclasses import dataclass, asdict

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, C2dCommand, TelemetryRecord, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.c2d import C2dOta

"""
See minimal.py example for a way to configure the device without the JSON file
You can download the iotcDeviceConfig.json by clicking the cog icon in the upper right of your device's info panel
NOTE: If you do not pass the server certificate, we will use the system's trusted certificate store, if available.
For example, the trusted Root CA certificates from the in /etc/ssl/certs will be used on Linux.
However, it is more secure to pass the actual server CA Root certificate in order to avoid potential MITM attacks.
On Linux, you can use server_ca_cert_path="/etc/ssl/certs/DigiCert_Global_Root_CA.pem" for Azure
or server_ca_cert_path="/etc/ssl/certs/Amazon_Root_CA_1.pem" for AWS
"""


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


def on_command(msg: C2dCommand):
    print("Received command", msg.command_name, msg.command_args)
    if msg.command_name == "set-user-led":
        if len(msg.command_args) == 3:
            print("Setting User LED to R:%d G:%d B:%d" % (int(msg.command_args[0]), int(msg.command_args[1]), int(msg.command_args[2])))
        else:
            print("Expected three command arguments, but got", len(msg.command_args))

def on_ota(msg: C2dOta):
    # We just print the URL. The actual handling of the OTA request would be project specific.
    print("Received OTA request. File: %s Version: %s URL: %s" % (msg.urls[0].file_name, msg.version, msg.urls[0].url))

def on_disconnect(reason: str, disconnected_from_server: bool):
    print("Disconnected%s. Reason: %s" % (" from server" if disconnected_from_server else "", reason))


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
            'x': 33.44,
            'y': 55.6,
            'z': 0.5
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


try:
    device_config = DeviceConfig.from_iotc_device_config_json_file(
        device_config_json_path="iotcDeviceConfig.json",
        device_cert_path="device-cert.pem",
        device_pkey_path="device-pkey.pem"
    )

    c = Client(
        config=device_config,
        callbacks=Callbacks(
            command_cb=on_command,
            ota_cb=on_ota,
            disconnected_cb=on_disconnect
        )
    )
    while True:
        if not c.is_connected():
            print('(re)connecting...')
            c.connect()
            if not c.is_connected():
                print('Unable to connect. Exiting.')  # Still unable to connect after 100 (default) re-tries.
                sys.exit(2)

        send_telemetry()
        time.sleep(10)

except DeviceConfigError as dce:
    print(dce)
    sys.exit(1)

except KeyboardInterrupt:
    print("Exiting.")
    sys.exit(0)
