import json
from dataclasses import dataclass
from datetime import datetime, timezone
from multiprocessing.managers import Value
from typing import TypeVar

import paho.mqtt.client

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
            return False # not primitive or latlong

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
class DeviceConfig:
    """
    =param env: Your account environment. You can locate this in you IoTConnect web UI at Settings -> Key Value
    """
    env: str
    cpid: str
    duid: str
    device_cert_path: str
    device_pkey_path: str
    server_ca_cert_path: str = None
    platform: str = "aws"


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



def on_connect(mqttc: paho.mqtt.client.Client, obj, flags, reason_code, properties):
    print("reason_code: " + str(reason_code))


def on_message(mqttc: paho.mqtt.client.Client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mqttc: paho.mqtt.client.Client, obj, mid, reason_code, properties):
    print("mid: " + str(mid))



class Client:

    @classmethod
    def timestamp_now(cls) -> datetime:
        """ Returns the UTC timestamp that can be used to stamp telemetry records """
        return datetime.now(timezone.utc)

    def __init__(self, config: DeviceConfig):
        self.config = config
        self.mqttc = paho.mqtt.client.Client(paho.mqtt.client.CallbackAPIVersion.VERSION2)
        self.mqttc.on_message = on_message
        self.mqttc.on_connect = on_connect
        self.mqttc.on_publish = on_publish



    def connect(self):
        mqtt_error = self.mqttc.connect(
            host="x",
            port=8883
        )

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

        print(self._to_iotconenct_json(records))

    def _to_iotconenct_json(self, records: list[TelemetryRecord]) -> str:
        def to_iotconnect_data(r: TelemetryRecord):
            iotc_record_json = {
                'd' : r.values
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




