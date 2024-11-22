# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

import random
import time

from avnet.iotconnect.sdk.lite import Client, C2dCommand
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.client import DeviceConfig, Callbacks
from avnet.iotconnect.sdk.sdklib.mqtt import C2dAck


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

c = Client(
    config=DeviceConfig(
        platform="aws",                             # The IoTconnect IoT platform - Either "aws" for AWS IoTCore or "az" for Azure IoTHub
        env="your-environment",                     # Your account environment. You can locate this in you IoTConnect web UI at Settings -> Key Value
        cpid="ABCDEFG123456",                       # Your account CPID (Company ID). You can locate this in you IoTConnect web UI at Settings -> Key Value
        duid="my-device",                           # Your device unique ID
        device_cert_path="path/to/device-cert.pem", # Path to the device certificate file
        device_pkey_path="path/to/device-pkey.pem"  # Path to the device private key file
    ),
    callbacks=Callbacks(
        command_cb=on_command
    )
)

while True:
    if not c.is_connected():
        print('(re)connecting...')
        c.connect()

    # send simple data using a dict initializer
    c.send_telemetry({
        'sdk_version': SDK_VERSION,
        'random': random.randint(0, 100),
        'nested': {
            'a': 'Value A',
            'b': 'Value B'
        }
    })

    time.sleep(10)
