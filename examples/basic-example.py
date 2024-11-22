# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

import random
import sys
import time
from dataclasses import dataclass, asdict

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, C2dCommand, TelemetryRecord, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.sdklib.mqtt import C2dOta, C2dAck

"""
See minimal.py example for a way to configure the device without the iotcDeviceConfig.json file
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
    print("Received command", msg.command_name, msg.command_args, msg.ack_id)
    if msg.command_name == "set-user-led":
        if len(msg.command_args) == 3:
            status_message = "Setting User LED to R:%d G:%d B:%d" % (int(msg.command_args[0]), int(msg.command_args[1]), int(msg.command_args[2]))
            c.send_command_ack(msg.type, C2dAck.CMD_SUCCESS_WITH_ACK, status_message)
            print(status_message)
        else:
            c.send_command_ack(msg, C2dAck.CMD_FAILED, "Expected 3 arguments")
            print("Expected three command arguments, but got", len(msg.command_args))
    else:
        print("Command %s not implemented!" % msg.command_name)
        if msg.ack_id is not None: # it could be a command without "Acknowledgement Required" flag in the device template
            c.send_command_ack(msg, C2dAck.CMD_FAILED, "Not Implemented")


def on_ota(msg: C2dOta):
    # We just print the URL. The actual handling of the OTA request would be project specific.
    # See the ota-handling.py for more details.
    print("Received OTA request. File: %s Version: %s URL: %s" % (msg.urls[0].file_name, msg.version, msg.urls[0].url))
    # OTA messages always have ack_id, so it is safe to not check for it before sending the ack
    c.send_ota_ack(msg, C2dAck.OTA_DOWNLOAD_FAILED, "Not implemented")


def on_disconnect(reason: str, disconnected_from_server: bool):
    print("Disconnected%s. Reason: %s" % (" from server" if disconnected_from_server else "", reason))


def send_telemetry():
    # Send simple data using a basic dictionary
    c.send_telemetry({
        'sdk_version': SDK_VERSION,
        'random': random.randint(0, 100),
        'accel': {
            'x': 33.44,
            'y': 55.6,
            'z': 0.5
        },
        'lat_long': [34, -43.22233]
    })

    # ...or send structured data. Make sure your object has the @dataclass decorator
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

    # We can update the data by assigning new values to the object before sending it again
    data.temperature = 23.1
    data.accel.x = 0.573
    data.accel.z = 0.002
    c.send_telemetry(asdict(data))

    # Example of sending multiple telemetry records by accumulating data.
    # A use case could be one where we save device power by staying disconnected but periodically waking up to record data,
    # and then we send accumulated data at once (note that there is a limit to maximum IoTConnect packet size)
    records: list[TelemetryRecord] = []

    data.temperature = 34.4
    records.append(TelemetryRecord(asdict(data), timestamp=Client.timestamp_now()))

    time.sleep(2)  # wait some time and the update the record with new sensor readings
    data.temperature = 34.6
    records.append(TelemetryRecord(asdict(data), timestamp=Client.timestamp_now()))

    # multiple records will be sent with different timestamps
    c.send_telemetry_records(records)


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
