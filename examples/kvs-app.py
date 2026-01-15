# SPDX-License-Identifier: MIT
# Copyright (C) 2026 Avnet

import sys
import time
import random
import subprocess
import signal
import os
import threading
from typing import Optional

from avnet.iotconnect.sdk.lite import Client, DeviceConfig, C2dCommand, C2dMessage, C2dOta, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.sdklib.mqtt import C2dAck

client: Client = None
device_config: DeviceConfig = None
_stream_process: Optional[subprocess.Popen] = None

camera_options = {
    "video": {
        "width": 640,
        "height": 480,
        "framerate": 30
    },
    "verbose": True
}


def extract_and_run_tar_gz(targz_filename: str):
    try:
        subprocess.run(("tar", "-xzvf", targz_filename, "--overwrite"), check=True)
        current_directory = os.getcwd()
        script_file_path = os.path.join(current_directory, "install.sh")
        # If install.sh is found in the current directory, execute it and then delete it
        # so it is not executed automatically again for future packages (may not include an install.sh)
        if os.path.isfile(script_file_path):
            try:
                subprocess.run(['bash', script_file_path], check=True)
                os.remove(script_file_path)
                print(f"Successfully executed install.sh")
                return True
            except subprocess.CalledProcessError as e:
                os.remove(script_file_path)
                print(f"Error executing install.sh: {e}")
                return False
            except Exception as e:
                os.remove(script_file_path)
                print(f"An error occurred: {e}")
                return False
        else:
            print("install.sh not found in the current directory.")
            return True
    except subprocess.CalledProcessError:
        return False


def detect_video_device() -> Optional[str]:
    try:
        devices = [d for d in os.listdir("/dev") if d.startswith("video")]
        if devices:
            devices.sort()
            video_device = f"/dev/{devices[0]}"
            print(f"Detected video device: {video_device}")
            return video_device
        else:
            print("No video devices found in /dev")
            return None
    except Exception as e:
        print(f"Error detecting video device: {e}")
        return None


def start_video_stream(
        stream_name: str,
        access_key: str,
        secret_key: str,
        session_token: str,
        region: str = "us-east-1"
) -> Optional[subprocess.Popen]:
    global _stream_process

    if sys.platform not in ('linux', 'linux2'):
        print("GStreamer video streaming is only supported on Linux")
        return None

    print("Starting GStreamer video stream...")

    # Get camera configuration
    device_port = camera_options.get("deviceport") or detect_video_device()
    if not device_port:
        print("No video device available")
        return None

    video_width = camera_options.get("video", {}).get("width", 640)
    video_height = camera_options.get("video", {}).get("height", 480)
    video_framerate = camera_options.get("video", {}).get("framerate", 30)

    # Build GStreamer command
    gst_command = (
        "gst-launch-1.0 -v "
        f"v4l2src device={device_port} do-timestamp=true ! "
        f"videoconvert ! video/x-raw,format=I420,width={video_width},height={video_height},framerate={video_framerate}/1 ! "
        "x264enc bframes=0 key-int-max=45 bitrate=800 speed-preset=ultrafast tune=zerolatency ! "
        "video/x-h264,stream-format=avc,alignment=au ! "
        f"kvssink stream-name={stream_name} storage-size=512 "
        f"access-key={access_key} secret-key={secret_key} "
        f"session-token={session_token} aws-region={region}"
    )

    if camera_options.get("verbose", False):
        print(f"GStreamer command:\n{gst_command}")

    try:
        _stream_process = subprocess.Popen(
            gst_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
            text=False
        )

        # Start threads to read output
        threading.Thread(
            target=_pipe_reader,
            args=("GSTOUT", _stream_process.stdout),
            daemon=True
        ).start()
        threading.Thread(
            target=_pipe_reader,
            args=("GSTERR", _stream_process.stderr),
            daemon=True
        ).start()

        # Wait a bit and check if process started successfully
        time.sleep(2.0)

        return_code = _stream_process.poll()
        if return_code is not None:
            print(f"GStreamer exited immediately with code {return_code}")
            print("This usually means:")
            print("   - GStreamer is not installed")
            print("   - kvssink plugin is not installed")
            print("   - Video device is not accessible")
            _stream_process = None
            return None

        print("GStreamer process started successfully")
        return _stream_process

    except FileNotFoundError:
        print("GStreamer is NOT installed on this system")
        print("Install with: sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good")
        return None
    except Exception as e:
        print(f"Error starting GStreamer: {e}")
        return None


def stop_video_stream() -> bool:
    global _stream_process

    if sys.platform not in ('linux', 'linux2'):
        print("Stopping GStreamer is only supported on Linux")
        return False

    if _stream_process is None:
        print("No video stream is running")
        return False

    try:
        print("Stopping video stream...")
        os.killpg(os.getpgid(_stream_process.pid), signal.SIGTERM)
        _stream_process = None
        print("Video stream stopped")
        return True
    except Exception as e:
        print(f"Error stopping video stream: {e}")
        return False


def is_streaming() -> bool:
    global _stream_process

    if _stream_process is None:
        return False

    # Check if process is still alive
    if _stream_process.poll() is not None:
        # Process has terminated
        _stream_process = None
        return False

    return True


def _pipe_reader(prefix: str, pipe):
    try:
        for line in iter(pipe.readline, b''):
            decoded = line.decode(errors='replace').rstrip()
            print(f"{decoded}")
    except Exception as e:
        print(f"Error reading pipe: {e}")
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def on_start_stream():
    print("Starting video stream...")

    # Check if KVS is enabled for this device
    if not client.kvs_enabled:
        print("Kinesis Video Streaming is not enabled for this device")
        return

    if is_streaming():
        print("Video stream is already running")
        return

    try:
        print("Fetching AWS credentials...")
        # Get credentials using the endpoint from device identity
        creds = client.get_aws_credentials()

        if creds is None:
            print("Failed to get AWS credentials")
            return

        access_key, secret_key, session_token = creds

        print("Starting GStreamer...")
        process = start_video_stream(
            stream_name=client.client_id,
            access_key=access_key,
            secret_key=secret_key,
            session_token=session_token,
            region="us-east-1"
        )

        if process is None:
            print("Failed to start video stream")
            return

        print("Video stream started successfully")

    except Exception as e:
        print(f"Error starting stream: {e}")
        import traceback
        traceback.print_exc()


def on_stop_stream():
    print("Stopping video stream...")

    if not is_streaming():
        print("No video stream is running")
        return

    if stop_video_stream():
        print("Video stream stopped")
    else:
        print("Failed to stop video stream")


def on_command(msg: C2dCommand):
    print("Received command", msg.command_name, msg.command_args, msg.ack_id)
    if msg.command_name == "file-download":
        if len(msg.command_args) == 1:
            status_message = "Downloading %s to device" % (msg.command_args[0])
            response = requests.get(msg.command_args[0])
            if response.status_code == 200:
                with open('package.tar.gz', 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"File downloaded successfully and saved to package.tar.gz")
            else:
                print(f"Failed to download the file. Status code: {response.status_code}")
            client.send_command_ack(msg, C2dAck.CMD_SUCCESS_WITH_ACK, status_message)
            print(status_message)
            extraction_success = extract_and_run_tar_gz('package.tar.gz')
            print("Download command successful. Will restart the application...")
            print("")
            sys.stdout.flush()
            os.execv(sys.executable, [sys.executable, __file__] + [sys.argv[0]])
        else:
            client.send_command_ack(msg, C2dAck.CMD_FAILED, "Expected 1 argument")
            print("Expected 1 command argument, but got", len(msg.command_args))
    else:
        print("Command %s not implemented!" % msg.command_name)
        if msg.ack_id is not None:
            client.send_command_ack(msg, C2dAck.CMD_FAILED, "Not Implemented")


def on_ota(msg: C2dOta):
    print("Starting OTA downloads for version %s" % msg.version)
    client.send_ota_ack(msg, C2dAck.OTA_DOWNLOADING)
    extraction_success = False
    for url in msg.urls:
        print("Downloading OTA file %s from %s" % (url.file_name, url.url))
        try:
            urllib.request.urlretrieve(url.url, url.file_name)
        except Exception as e:
            print("Encountered download error", e)
            error_msg = "Download error for %s" % url.file_name
            break
        if url.file_name.endswith(".tar.gz"):
            extraction_success = extract_and_run_tar_gz(url.file_name)
            if extraction_success is False:
                break
        else:
            print("ERROR: Unhandled file format for file %s" % url.file_name)
    if extraction_success is True:
        print("OTA successful. Will restart the application...")
        client.send_ota_ack(msg, C2dAck.OTA_DOWNLOAD_DONE)
        print("")
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, __file__] + [sys.argv[0]])
    else:
        print('Encountered a download processing error. Not restarting.')


def on_disconnect(reason: str, disconnected_from_server: bool):
    print(f"Disconnected. Reason: {reason}")
    if is_streaming():
        print("Stopping stream due to disconnect...")
        stop_video_stream()


if __name__ == "__main__":

    try:
        device_config = DeviceConfig.from_iotc_device_config_json_file(
            device_config_json_path="iotcDeviceConfig.json",
            device_cert_path="device-cert.pem",
            device_pkey_path="device-pkey.pem"
        )
    except DeviceConfigError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Register callbacks (matching the framework pattern)
    callbacks = Callbacks(
        command_cb=on_command,
        ota_cb=on_ota,
        disconnected_cb=on_disconnect,
        start_stream_cb=on_start_stream,
        stop_stream_cb=on_stop_stream
    )

    try:
        client = Client(device_config, callbacks)
    except Exception as e:
        print(f"Failed to create client: {e}")
        sys.exit(1)

    print("Connecting to /IOTCONNECT...")
    client.connect()

    if not client.is_connected():
        print("Failed to connect")
        sys.exit(1)

    print("Connected to /IOTCONNECT")

    # Check KVS configuration
    if client.kvs_enabled:
        print(f"\nKinesis Video Streaming is ENABLED")
        print(f"Endpoint: {client.kvs_credential_endpoint}")
        print(f"Auto-start: {client.kvs_auto_start}")
        if client.kvs_auto_start:
            print("Auto-starting stream in 3 seconds...")
            time.sleep(3)
            on_start_stream()  # Call callback directly for auto-start
    else:
        print("\nKinesis Video Streaming is NOT enabled")

    try:
        while True:
            if not client.is_connected():
                print("Connection lost, attempting to reconnect...")
                client.connect()

            client.send_telemetry({
                "random": random.randint(0, 100),
                "streaming": is_streaming()
            })

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nShutting down...")
        if is_streaming():
            print("Stopping video stream...")
            stop_video_stream()
        client.disconnect()
        print("Shutdown successful.")