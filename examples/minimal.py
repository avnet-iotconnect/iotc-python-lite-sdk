import random
import time

from avnet.iotconnect.sdk.lite import Client
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.client import DeviceConfig, Callbacks, C2dCommand


def on_command(msg: C2dCommand):
    print("Received command", msg.command_name, msg.command_args, msg.ack_id)
    if msg.command_name == "set-user-led":
        if len(msg.command_args) == 3:
            print("Setting User LED to R:%d G:%d B:%d" % (
                int(msg.command_args[0]), int(msg.command_args[1]), int(msg.command_args[2]))
                  )
        else:
            print("Expected three command arguments, but got", len(msg.command_args))


c = Client(
    config=DeviceConfig(
        platform="aws",  # The IoTconnect IoT platform - Either "aws" for AWS IoTCore or "az" for Azure IoTHub
        env="your-environment",  # Your account environment. You can locate this in you IoTConnect web UI at Settings -> Key Value
        cpid="ABCDEFG123456",  # Your account CPID (Company ID). You can locate this in you IoTConnect web UI at Settings -> Key Value
        duid="my-device",  # Your device unique ID
        device_cert_path="path/to/device-cert.pem",  # Path to the device certificate file
        device_pkey_path="path/to/device-pkey.pem"  # Path to the device private key file
    ),
    callbacks=Callbacks(
        command_cb=on_command
    )
)

if __name__ == '__main__':
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
