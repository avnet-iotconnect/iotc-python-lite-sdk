# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.
import datetime
import os
import random
import shutil
import subprocess
import sys
import time
import uuid
from typing import Optional

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.client import KvsClient, S3Client, AwsCredentialsProvider

kvs_client :Optional[KvsClient] = None

def print_credentials(provider: AwsCredentialsProvider):
    """
    Example function to print AWS credentials in a format suitable for setting environment variables
    so that aws cli and similar can be used.
    """
    creds = provider.get_credentials()
    command = "set" if sys.platform.startswith('win') else "export"
    print(f"{command} AWS_ACCESS_KEY_ID={creds.access_key_id}")
    print(f"{command} AWS_SECRET_ACCESS_KEY={creds.secret_access_key}")
    print(f"{command} AWS_SESSION_TOKEN=\"{creds.session_token}\"")

def check_and_refresh_credentials(provider: AwsCredentialsProvider, what: str = ""):
    """
    Example function to check KVS or S3 credentials expiry and refresh if needed.
    """
    if provider.get_secs_to_expiry() < 60:
        print(f"Refreshing {what} credentials...")
        kvs_client.obtain_credentials()
        print_credentials(provider)

def on_video_streaming_event(kvsc: KvsClient):
    """
    Example handling of video streaming events / status changes.
    Demonstrates how to ensure that credentials are refreshed.
    NOTE: the handle passed is the same as the kvs_client obtained from Client.get_kvs_client()
    """
    print(f"KVS Video Streaming Status = {kvsc.is_streaming}")
    if kvsc.is_streaming:
        check_and_refresh_credentials(kvsc, "KVS")


def on_disconnect(reason: str, disconnected_from_server: bool):
    print("Disconnected%s. Reason: %s" % (" from server" if disconnected_from_server else "", reason))

def send_telemetry():
    c.send_telemetry({
        'sdk_version': SDK_VERSION,
        'random': random.randint(0, 100)
    })

def upload_file_example(file_name="my-file.jpg"):
    bucket_name = None
    for bucket in s3_client.get_buckets():
        # the first bucket that's not customer owned should be the default bucket
        # that can be used to upload files and show then in telemetry UI
        if not bucket.is_customer_owned:
            bucket_name = bucket.bucket_name
    if bucket_name is None:
        print("No suitable S3 bucket found for device uploads.")

    print_credentials(s3_client)
    print("Account S3 Buckets:")
    print(s3_client.get_buckets())
    print("Example with AWS CLI:")
    now = datetime.datetime.now(datetime.timezone.utc)
    upload_file_key = f"{now.strftime('%Y/%m/%d')}/{str(uuid.uuid4())}-{file_name}"
    device_upload_path = f"device-uploads/{c.get_duid()}"
    cmd = f"aws s3 cp my-file.jpg s3://{bucket_name}/{device_upload_path}/{upload_file_key}"
    env = os.environ.copy()
    s3_client.get_credentials(env=env)
    print(f"Executing {cmd}...")
    try:
        subprocess.run(cmd, shell=True, check=True, env=env)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Failed to execute command. Please ensure that AWS CLI is installed and that the file to upload is in the current directory.")
    c.send_telemetry({
        'url': upload_file_key,
        'cf': {
            'classification' : 'device-uploads',
        }
    })


try:
    device_config = DeviceConfig.from_iotc_device_config_json_file(
        device_config_json_path="iotcDeviceConfig.json",
        device_cert_path="device-cert.pem",
        device_pkey_path="device-pkey.pem"
    )

    c = Client(
        config=device_config,
        callbacks=Callbacks(
            disconnected_cb=on_disconnect,
            vs_cb=on_video_streaming_event
        )
    )
    kvs_client = c.get_kvs_client()
    s3_client = c.get_s3_client()

    c.connect()

    if kvs_client is None:
        print("KVS Client is not available. Make sure you enabled Streaming in your device template.")
    else:
        kvs_client.obtain_credentials()
        print("KVS credentials:")
        print_credentials(kvs_client)

    if s3_client is None:
        print("S3 Client is not available. Make sure you enabled File Support in your device template.")
    else:
        print("S3 credentials as environment variables:")
        s3_client.obtain_credentials()
        upload_file_example()

    while True:
        if not c.is_connected():
            print('(re)connecting...')
            c.connect()
            if not c.is_connected():
                print('Unable to connect. Exiting.')  # Still unable to connect after 100 (default) re-tries.
                sys.exit(2)

        # periodically check credentials expiry and refresh if needed
        check_and_refresh_credentials(kvs_client, "KVS")
        check_and_refresh_credentials(s3_client, "S3")

        send_telemetry()
        time.sleep(10)

except DeviceConfigError as dce:
    print(dce)
    sys.exit(1)

except KeyboardInterrupt:
    print("Exiting.")
    sys.exit(0)
