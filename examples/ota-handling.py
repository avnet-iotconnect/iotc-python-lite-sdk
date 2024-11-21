# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

import os
import random
import subprocess
import sys
import threading
import time
import urllib.request
from typing import Optional

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.sdklib.c2d import C2dOta

"""
In this demo we demonstrate a simple example of how an OTA could be handled.

We read the list of OTA URLs then and if we see a wheel, we install it. If we see a zip ot a zipped tar, we extract.

Then we restart the process so that it can pick up on newly replaced files.

While we should have more robust handling for all of these steps in production, this example is simplified so 
that 
 
"""

dl_thread: Optional[threading.Thread] = None

# can only exit from main thread, so use this flag or synchronize threads
need_restart = False


def exit_and_restart():
    print("")  # Print a blank line so it doesn't look as confusing in the output.
    sys.stdout.flush()

    # This way to restart the process seems to work reliably.
    # It is best to drive the main application with a runner, like a system service,
    # a cron job or custom simple driver script that keeps restarting the main application python process on exit
    os.execv(sys.executable, [sys.executable, __file__] + [sys.argv[0]])


def subprocess_run_with_print(args):
    print("Running command:", ' '.join(args))
    subprocess.run(args, check=True)


def download(msg: C2dOta):
    global dl_thread
    has_failure = False
    for url in msg.urls:
        print("Downloading OTA file %s from %s" % (msg.urls[0].file_name, msg.urls[0].url))
        try:
            urllib.request.urlretrieve(url.url, url.file_name)
        except Exception as e:
            print("Encountered download error", e)
            has_failure = True
        try:
            if url.file_name.endswith(".whl"):
                # force reinstall may not be the greatest idea, but may help with testing
                subprocess_run_with_print(("python3", "-m", "pip", "install", "--force-reinstall", url.file_name))
            elif url.file_name.endswith(".zip"):
                subprocess_run_with_print(("unzip", "-oqq", url.file_name))
            elif url.file_name.endswith(".tgz") or url.file_name.endswith(".tar.gz"):
                subprocess_run_with_print(("tar", "-zxf", url.file_name))

        except subprocess.CalledProcessError:
            print("ERROR failed to install %s" % url.file_name)
            has_failure = True
    if has_failure:
        print("Encountered a download processing error. Not restarting.")  # In hopes that someone pushes a better update
    else:
        global need_restart
        print("OTA successful. Will restart the application at next main loop iteration...")
        need_restart = True
    dl_thread = None


def on_ota(msg: C2dOta):
    global dl_thread
    if dl_thread is not None:
        print("Received OTA while download is still in progress")
        return

    # We just print the URL. The actual handling of the OTA request would be project specific.
    print("Starting OTA downloads for version %s" % msg.version)
    dl_thread = threading.Thread(target=download, args=[msg])
    dl_thread.start()


try:
    device_config = DeviceConfig.from_iotc_device_config_json_file(
        device_config_json_path="iotcDeviceConfig.json",
        device_cert_path="device-cert.pem",
        device_pkey_path="device-pkey.pem"
    )

    c = Client(
        config=device_config,
        callbacks=Callbacks(
            ota_cb=on_ota,
        )
    )
    while True:
        if not c.is_connected():
            print('(re)connecting...')
            c.connect()
            if not c.is_connected():
                print('Unable to connect. Exiting.')  # Still unable to connect after 100 (default) re-tries.
                sys.exit(2)

        c.send_telemetry({
            'sdk_version': SDK_VERSION,
            'random': random.randint(0, 100)
        })

        if need_restart:
            exit_and_restart()

        time.sleep(10)

except DeviceConfigError as dce:
    print(dce)
    sys.exit(1)

except KeyboardInterrupt:
    print("Exiting.")
    sys.exit(0)
