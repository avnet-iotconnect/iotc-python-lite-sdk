# SPDX-License-Identifier: MIT
# Copyright (C) 2026 Avnet

from urllib.parse import urlparse
import requests
import subprocess
import signal
import os
import sys
import threading
from typing import Optional

_stream_process: Optional[subprocess.Popen] = None


def get_kvs_config(device_config, verbose=False):
    try:
        props = device_config.to_properties()

        # Step 1: Discovery API call
        discovery_url = f"https://discovery.iotconnect.io/api/v2.1/dsdk/cpId/{props.cpid}/env/{props.env}?pf={props.platform}"
        if verbose:
            print(f"[KVS] Requesting Discovery: {discovery_url}")

        discovery_response = requests.get(discovery_url, timeout=10)
        discovery_data = discovery_response.json()
        base_url = discovery_data["d"]["bu"]

        # Step 2: Sync/Identity API call
        sync_url = f"{base_url}/uid/{props.duid}"
        if verbose:
            print(f"[KVS] Requesting Identity: {sync_url}")

        sync_response = requests.get(sync_url, timeout=10)
        sync_data = sync_response.json()

        vs = sync_data.get("d", {}).get("p", {}).get("vs", {})
        return {
            "enabled": bool(vs),
            "credential_endpoint": vs.get("url"),
            "auto_start": vs.get("as", False)
        }

    except Exception as e:
        if verbose:
            print(f"[KVS] Failed to fetch sync response: {e}")
        return {"enabled": False, "credential_endpoint": None, "auto_start": False}


def get_kinesis_credentials(uid, cacert, devicecert, devicekey, aws_credential_endpoint):
    if not aws_credential_endpoint:
        raise ValueError("AWS credential endpoint is required")

    url = aws_credential_endpoint.strip()
    try:
        p = urlparse(url)
        if p.scheme != "https" or not url.endswith("/credentials"):
            raise ValueError(f"Bad role-alias URL: {url}. URL must use HTTPS and end with '/credentials'")
        if not p.netloc:
            raise ValueError(f"Invalid URL format: {url}. Missing domain name")
    except Exception as e:
        raise ValueError(f"Failed to parse URL '{url}': {e}")

    print("Kinesis creds endpoint (final):", repr(url))
    print("Using Thing name:", uid)

    try:
        response = requests.get(
            url=url,
            cert=(devicecert, devicekey),
            verify=cacert,
            headers={
                "x-amzn-iot-thingname": uid
            },
        )
        res_load = response.json()
        print(res_load)

        if response.status_code == 200:
            return res_load["credentials"]["accessKeyId"], res_load["credentials"]["secretAccessKey"], \
                res_load["credentials"]["sessionToken"]
        else:
            print("Response from IoT: (non 200)", res_load)
            print("Failed in getting Kinesis Device access and Secret key")
            return None

    except requests.RequestException as e:
        print(f"Error obtaining credentials from IoT: {e}")
        return None


def detect_video_device() -> Optional[str]:
    try:
        devices = [d for d in os.listdir("/dev") if d.startswith("video")]
        if devices:
            # Sort to get video0 first
            devices.sort()
            video_device = f"/dev/{devices[0]}"
            print(f"[KVS] Detected video device: {video_device}")
            return video_device
        else:
            print("[KVS] No video devices found in /dev")
            return None
    except Exception as e:
        print(f"[KVS] Error detecting video device: {e}")
        return None


def start_video_stream(
        stream_name: str,
        access_key: str,
        secret_key: str,
        session_token: str,
        camera_options: dict,
        region: str = "us-east-1"
) -> Optional[subprocess.Popen]:
    global _stream_process

    if sys.platform not in ('linux', 'linux2'):
        print("[KVS] GStreamer video streaming is only supported on Linux")
        return None

    print("[KVS] Starting GStreamer video stream...")

    # Get camera configuration
    device_port = camera_options.get("deviceport") or detect_video_device()
    if not device_port:
        print("[KVS] No video device available")
        return None

    video_width = camera_options.get("video", {}).get("width", 640)
    video_height = camera_options.get("video", {}).get("height", 480)
    video_framerate = camera_options.get("video", {}).get("framerate", 30)

    # Video-only pipeline
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
        print(f"[KVS] GStreamer command:\n{gst_command}")

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
        import time
        time.sleep(2.0)

        return_code = _stream_process.poll()
        if return_code is not None:
            print(f"[KVS] GStreamer exited immediately with code {return_code}")
            print("[KVS] This usually means:")
            print("[KVS]   - GStreamer is not installed")
            print("[KVS]   - kvssink plugin is not installed")
            print("[KVS]   - Video device is not accessible")
            _stream_process = None
            return None

        print("[KVS] GStreamer process started successfully")
        return _stream_process

    except FileNotFoundError:
        print("[KVS] GStreamer is NOT installed on this system")
        print(
            "[KVS] Install with: sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good")
        return None
    except Exception as e:
        print(f"[KVS] Error starting GStreamer: {e}")
        return None


def stop_video_stream() -> bool:
    global _stream_process

    if sys.platform not in ('linux', 'linux2'):
        print("[KVS] Stopping GStreamer is only supported on Linux")
        return False

    if _stream_process is None:
        print("[KVS] No video stream is running")
        return False

    try:
        print("[KVS] Stopping video stream...")
        os.killpg(os.getpgid(_stream_process.pid), signal.SIGTERM)
        _stream_process = None
        print("[KVS] Video stream stopped")
        return True
    except Exception as e:
        print(f"[KVS] Error stopping video stream: {e}")
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
            print(f"[KVS-{prefix}] {decoded}")
    except Exception as e:
        print(f"[KVS] Error reading pipe: {e}")
    finally:
        try:
            pipe.close()
        except Exception:
            pass