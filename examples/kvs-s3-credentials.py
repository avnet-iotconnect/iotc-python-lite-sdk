# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

import random
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.lite.client import KvsClient, AwsCredentialsProvider, S3Client

@dataclass
class ClassificationData:
    """ Custom metadata that can be tied to S3 uploads in IoTConnect UI """
    classification: Optional[str] = field(default=None)
    confidence: Optional[float]  = field(default=None)

@dataclass
class S3CustomData:
    """ Top level data structure for S3 uploads."""
    cf: ClassificationData = field(default_factory=ClassificationData)

s3_custom_data = S3CustomData()

kvs_client :Optional[KvsClient] = None
s3_client :Optional[S3Client] = None

def print_credentials(provider: AwsCredentialsProvider):
    """
    Example function to print AWS credentials in a format suitable for setting environment variables
    so that aws cli and similar can be used.
    """
    creds = provider.get_credentials()
    # export for Linux with space so that it doesn't record in shell history when pasted
    command = "set" if sys.platform.startswith('win') else " export"
    print(f'{command} AWS_ACCESS_KEY_ID={creds.access_key_id}')
    print(f'{command} AWS_SECRET_ACCESS_KEY={creds.secret_access_key}')
    print(f'{command} AWS_SESSION_TOKEN="{creds.session_token}"')

def check_and_refresh_credentials(provider: AwsCredentialsProvider, what: str = ""):
    """ Example function to check KVS or S3 credentials expiry and refresh if needed."""
    # If provider is none, we already printed a message that the client is not available
    if provider is not None and  provider.get_secs_to_expiry() < 60:
        print(f"Refreshing {what} credentials...")
        provider.obtain_credentials()
        print_credentials(provider)

def on_video_streaming_event(kvsc: KvsClient):
    """
    Example handling of video streaming events / status changes.
    Demonstrates how to ensure that credentials are refreshed.
    NOTE: the handle passed is the same as the kvs_client obtained from Client.get_kvs_client()
    """
    print(f"KVS Video Streaming Status = {kvsc.is_streaming()}")
    if kvsc.is_streaming():
        # make sure to try/catch here to avoid mqtt callback thread crashing and stopping MQTT processing
        try:
            check_and_refresh_credentials(kvsc, "KVS")
        except Exception as e:
            print("Failed to refresh KVS credentials:", e)

def on_disconnect(reason: str, disconnected_from_server: bool):
    print("Disconnected%s. Reason: %s" % (" from server" if disconnected_from_server else "", reason))

def send_telemetry():
    c.send_telemetry({
        'sdk_version': SDK_VERSION,
        'random': random.randint(0, 100)
    })

def upload_file_example(local_path: str = Path(__file__).parent / '../files/sample-s3-upload-image.jpg'):
    print("Account S3 Buckets:")
    print(s3_client.get_buckets())
    print("S3 Credentials:")
    print_credentials(s3_client)

    # Upload the file into the default bucket with some custom metadata
    # The "cf" object is special and will be displayed by /IOTCONNECT UI
    s3_custom_data.cf.classification = "dog"
    s3_custom_data.cf.confidence = random.randint(60, 100) / 100.0

    c.s3_upload(local_path=local_path, custom_values=asdict(s3_custom_data))

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
        print("Auto-start enabled", kvs_client.is_auto_start())

    if s3_client is None:
        print("S3 Client is not available. Make sure you enabled File Support in your device template.")
    else:
        print("S3 credentials as environment variables:")
        s3_client.obtain_credentials()
        print_credentials(s3_client)
        try:
            import boto3 # Quick test to make sure aws-s3 extra is installed
            upload_file_example()
        except ImportError:
            """
            # We can export the variables into a shell that will execute aws cli commands to upload files. Example:
            unix_timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            relative_upload_path = f"{unix_timestamp}-{file_name}"
            cmd = f"aws s3 cp '{file_name}' 's3://{bucket_name}/device-uploads/{c.get_duid()}/{relative_upload_path}'"
            env = os.environ.copy()
            s3_client.get_credentials(env=env)
            print(f"Executing {cmd}...")
        
            try:
                subprocess.run(cmd, shell=True, check=True, env=env)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Failed to execute command. Please ensure that AWS CLI is installed and that the file to upload is in the current directory.")
        
            c.send_file_upload_message(relative_upload_path, {
                'cf': {
                    'classification': 'yorkie',
                    'confidence': 0.700,
                }
            })
            """
            print("AWS S3 support is not installed.")
            print("Install this package with pip install iotconnect-sdk-lite[aws-s3]")
            print("Or set the printed variables in your shell and use aws cli to upload files.")
            print("Then invoke c.send_s3_file_telemetry(...) to notify /IOTCONNECT about the uploaded file.")


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
