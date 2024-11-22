# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

import os
import random
import sys
import time

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, Callbacks, DeviceConfigError, C2dMessage
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION

"""
In this demo we demonstrate a way to provide your own way of handling of IoTConnect special events
or not yet implemented event features (like Module Command).

While on_ota and on_command callbacks are a preferred way to handle commands, 
one can also choose to implement their own. 

Most of the event examples in this demo deal with cases where:
- Device is deleted
- Device template updated or changed
- Device setting (Twin/Shadow) changed

While not demonstrating some practical examples, the demo shows the general mechanism
and may expand in the future when/if extra features are added to the SDK.

"""

# can only exit from main thread, so use these flags
need_exit = False
need_restart = False


def exit_and_restart():
    print("")  # Print a blank line so it doesn't look as confusing in the output.
    sys.stdout.flush()

    # This way to restart the process seems to work reliably.
    # It is best to drive the main application with a runner, like a system service,
    # a cron job or custom simple driver script that keeps restarting the main application python process on exit
    os.execv(sys.executable, [sys.executable, __file__] + [sys.argv[0]])


def on_stop_message(msg: C2dMessage, message_dict: dict):
    global need_exit
    print("Received stop message (%s). Exiting cleanly at next main loop iteration..." % msg.type_description)
    need_exit = True


def on_restart_message(msg: C2dMessage, message_dict: dict):
    global need_restart
    print("Received stop restart (%s). Restarting at next loop iteration..." % msg.type_description)
    need_restart = True


print("Starting the Advanced C2D Generic Message Handling Demo")

try:
    device_config = DeviceConfig.from_iotc_device_config_json_file(
        device_config_json_path="iotcDeviceConfig.json",
        device_cert_path="device-cert.pem",
        device_pkey_path="device-pkey.pem"
    )

    c = Client(
        config=device_config,
        callbacks=Callbacks(
            # some examples of messages that can be handled by restarting or exiting the process
            generic_message_callbacks={
                C2dMessage.DEVICE_DELETED: on_stop_message,
                C2dMessage.DEVICE_DISABLED: on_stop_message,
                C2dMessage.DEVICE_RELEASED: on_stop_message,
                C2dMessage.STOP_OPERATION: on_stop_message,  # Typically a template change (the template pulldown on the device info page)
                C2dMessage.REFRESH_ATTRIBUTE: on_restart_message,  # Template attributes added/removed/changed
                C2dMessage.REFRESH_SETTING: on_restart_message
            }
        )
    )
    while True:
        if not c.is_connected():
            print('(re)connecting...')
            c.connect()
            if not c.is_connected():
                print('Unable to connect. Exiting.')  # Still unable to connect after 100 (default) re-tries.
                sys.exit(2)
        if need_exit:
            sys.exit()

        if need_restart:
            exit_and_restart()

        c.send_telemetry({
            'sdk_version': SDK_VERSION,
            'random': random.randint(0, 100)
        })
        time.sleep(10)

except DeviceConfigError as dce:
    print(dce)
    sys.exit(1)

except KeyboardInterrupt:
    print("Exiting.")
    sys.exit(0)
