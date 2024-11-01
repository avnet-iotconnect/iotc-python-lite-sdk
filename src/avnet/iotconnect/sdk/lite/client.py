import json
import random
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

import paho.mqtt.client
from paho.mqtt.client import Client as PahoClient, MQTT_ERR_UNKNOWN
from paho.mqtt.enums import CallbackAPIVersion
from .config import DeviceConfig

from avnet.iotconnect.sdk.sdklib.dra import DraDiscoveryUrl,DiscoveryResponseData, \
    DraIdentityUrl, IdentityResponseData

# When type "object" is defined in IoTConnect, it cannot have nested objects inside of it.
type TelemetryValueObjectType = dict[str, None | str | int | float | bool | tuple[float, float]]
type TelemetryValueType = None | str | int | float | bool | tuple[float, float] | TelemetryValueObjectType


class TelemetryValues(dict[str, TelemetryValueType]):
    def __init__(self, *args, **kwargs):
        super(TelemetryValues, self).__init__()
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        def check_primitive_or_latlong(value) -> bool:
            if isinstance(value, None | str | int | float | bool):
                return True
            elif isinstance(value, list):
                if len(value) != 2:
                    raise ValueError("Not lat/long", key, "=", value)
                else:
                    return True
            return False  # not primitive or latlong

        if not isinstance(key, str):
            raise ValueError("Bad key type")

        if check_primitive_or_latlong(value):
            pass
        elif isinstance(value, dict):
            for k in value:
                if not isinstance(k, str):
                    raise ValueError("Bad key type")
                if not check_primitive_or_latlong(value.get(k)):
                    raise ValueError("Inner dictionary object must not be nested")

        else:
            raise ValueError("Bad type for key", key, type(value))

        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        print('update', args, kwargs)
        for k, v in dict(*args, **kwargs).items():
            self[k] = v





@dataclass
class TelemetryRecord:
    values: TelemetryValues
    timestamp: datetime = None
    unique_id: str = None
    tag: str = None

    def apply_timestamp(self):
        """ Timestamps this TelemetryEntry with the current timestamp """
        self.timestamp = Client.timestamp_now()
        return self

class C2DmessageType(Enum):
    COMMAND = 0
    OTA = 1
    MODULE_COMMAND = 2


@dataclass
class C2DMessagePacket:
    ack: str
    ct: int
    cmd: str
    sw: str
    hw: str
    urls: dict[str, dict[str, str]]


class C2dMessage:
    def __init__(self, packet: C2DMessagePacket):
        self.message_type = packet.ct
        self.ack_id = packet.ack
        cmd_split = packet.cmd.split()
        self.command_name = cmd_split[0]
        self.command_args = cmd_split[1:]

    def apply_timestamp(self):
        """ Timestamps this TelemetryEntry with the current timestamp """
        self.timestamp = Client.timestamp_now()
        return self


class Client:

    @classmethod
    def timestamp_now(cls) -> datetime:
        """ Returns the UTC timestamp that can be used to stamp telemetry records """
        return datetime.now(timezone.utc)

    def __init__(self, config: DeviceConfig):
        self.config = config
        print(DraDiscoveryUrl(config).get_api_url())
        resp = urllib.request.urlopen(urllib.request.Request(DraDiscoveryUrl(config).get_api_url()))
        response_data = DiscoveryResponseData.from_json(json.loads(resp.read()))
        resp = urllib.request.urlopen(DraIdentityUrl(response_data.d.bu).get_uid_api_url(config))
        response_data = IdentityResponseData.from_json(json.loads(resp.read()))
        self.mqtt_config = response_data.d.mqtt_data

        self.mqtt = PahoClient(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=self.mqtt_config.id
        )
        self.mqtt.username = self.mqtt_config.un

        self.mqtt.on_message = self.on_message
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_publish = self.on_publish

        self.mqtt.tls_set(certfile=config.device_cert_path, keyfile=config.device_pkey_path)

    def connect(self):
        while True:
            try:
                mqtt_error = self.mqtt.connect(
                    host=self.mqtt_config.h,
                    port=8883
                )
                if mqtt_error != paho.mqtt.client.MQTT_ERR_SUCCESS:
                    print("Failed to connect")
                else:
                    print("MQTT connected")
                    break # break the loop

            except Exception as ex:
                self._mqtt_status = MQTT_ERR_UNKNOWN
                print("Failed to connect to host %s. Exception: %s" % (self.mqtt_config.h, str(ex)))

            backoff_ms = random.randrange(1000, 15000)
            print("Backing off for %d ms." % backoff_ms)
            # Jitter back off a random number of milliseconds between 1 and 10 seconds.
            time.sleep(backoff_ms / 1000)

        self.mqtt.subscribe(self.mqtt_config.topics.c2d, qos=1)


    def send_telemetry(self, values: dict[str, TelemetryValueType], timestamp: datetime = None):
        """ Sends a single telemetry dataset. 
        If you need gateway/child functionality or need to send multiple value sets in one packet, 
        use the send_telemetry_records() method.
         
        :param TelemetryValues values:
            The name-value telemetry pairs to send. Each value can be
                - a primitive value: Maps directly to a JSON string, number or boolean
                - None: Maps to JSON null,
                - Tuple[float, float]: Used to send a lat/long geographic coordinate as decimal degrees as an
                    array of two (positive or negative) floats.
                    For example, [44.787197, 20.457273] is the geo coordinate Belgrade in Serbia,
                    where latitude 44.787197 is a positive number indicating degrees north,
                    and longitude a positive number as well, indicating degrees east.
                    Maps to JSON array of two elements.
                - Another hash with possible values above when sending an object. Maps to JSON object.
            in case when an object needs to be sent.
        :param datetime timestamp: (Optional) The timestamp corresponding to this dataset.
            If not provided, this will save bandwidth, as no timestamp will not be sent over MQTT.
             The server receipt timestamp will be applied to the telemetry values in this telemetry record.
             Supply this value (using Client.timestamp()) if you need more control over timestamps.
        """

        self.send_telemetry_records([TelemetryRecord(
            values=values,
            timestamp=timestamp
        )])

    def send_telemetry_records(self, records: list[TelemetryRecord]):
        """
        A complex, but more powerful way to send telemetry.
        It allows the user to send multiple sets of telemetry values
        and control the timestamp of each telemetry value set.
        Supports gateway devices with gateway-child relationship by allowing
        the user to set the parent/child unique_id ("id" in JSON)
        and tag of respective parent./child ("tg" in JSON)

        See https://docs.iotconnect.io/iotconnect/sdk/message-protocol/device-message-2-1/d2c-messages/#Device for more information.

        """

        iotc_json = self._to_iotconenct_json(records)
        if not self.mqtt.is_connected():
            print('Message NOT sent. Not connected!')
        else:
            self.mqtt.publish(
                topic=self.mqtt_config.topics.rpt,
                qos=1,
                payload=iotc_json
            )
            print(iotc_json)

    def _to_iotconenct_json(self, records: list[TelemetryRecord]) -> str:
        def to_iotconnect_data(r: TelemetryRecord):
            iotc_record_json = {
                'd': r.values
            }

            if r.timestamp:
                iotc_record_json['dt'] = r.timestamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            if r.unique_id:
                iotc_record_json['id'] = r.unique_id
            if r.tag:
                iotc_record_json['tg'] = r.tag

            return iotc_record_json

        t = {
            'd': []
        }
        for entry in records:
            if not isinstance(entry.values, TelemetryValues):
                # simple dict is fine, but check that the data is valid by converting it to our class
                entry.values = TelemetryValues(entry.values)
            t['d'].append(dict(to_iotconnect_data(entry)))
        return json.dumps(t)

    def _process_c2d_mesage(self, tpic: str, payload: str):
        pass

    def on_connect(self, mqttc: PahoClient, obj, flags, reason_code, properties):
        print("reason_code: " + str(reason_code))

    def on_message(self, mqttc: PahoClient, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self._process_c2d_mesage(msg.topic, msg.payload)

    def on_publish(self, mqttc: PahoClient, obj, mid, reason_code, properties):
        print("mid: " + str(mid))

