import random
import time

from avnet.iotconnect.sdk.lite import Client
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.client import DeviceConfig, Callbacks, C2dCommand

device_config = DeviceConfig(
    platform="aws",
    cpid="97FF86E8728645E9B89F7B07977E4B15",
    env="poc",
    duid="python-lite-sdk01",
    device_cert_path="device-cert.pem",
    device_pkey_path="device-pkey.pem"
    )


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
    config=device_config,
    callbacks=Callbacks(
        command_cb=on_command
    )
)

if __name__ == '__main__':
    while True:
        if not c.is_connected():
            print('(re)connecting...')
            c.connect()
            # c._aws_qualification_start(['t2wlntge8x69qa.deviceadvisor.iot.eu-west-1.amazonaws.com'])
            # c._aws_qualification_start(["tab0656391t2wlntge8x69qa.deviceadvisor.iot.eu-west-1.amazonaws.com"])


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
