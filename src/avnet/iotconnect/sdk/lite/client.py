import json
import random
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from json import JSONDecodeError
from ssl import SSLError
from typing import Union, Callable, Optional, Final

from paho.mqtt.client import CallbackAPIVersion, MQTTErrorCode, DisconnectFlags
from paho.mqtt.client import Client as PahoClient
from paho.mqtt.reasoncodes import ReasonCode

from avnet.iotconnect.sdk.sdklib.dra import DraDiscoveryUrl, IotcDiscoveryResponseJson, \
    DraIdentityUrl, IdentityResponseData
from .config import DeviceConfig

# When type "object" is defined in IoTConnect, it cannot have nested objects inside of it.
TelemetryValueObjectType = dict[str, Union[None, str, int, float, bool, tuple[float, float]]]
TelemetryValueType = Union[None, str, int, float, bool, tuple[float, float], TelemetryValueObjectType]
TelemetryValues = dict[str, TelemetryValueType]


class Timing:
    def __init__(self):
        self.t = datetime.now()

    def diff_next(self) -> timedelta:
        now = datetime.now()
        ret = self.diff_with(now)
        self.t = now
        return ret

    def diff_now(self) -> timedelta:
        return datetime.now() - self.t

    def diff_with(self, t: datetime) -> timedelta:
        return t - self.t

    def lap(self, do_print=True) -> timedelta:
        ret = self.diff_next()
        if do_print:
            print("timing: ", ret)
        return ret


class TelemetryValidator(dict[str, TelemetryValueType]):
    # def __init__(self, *args, **kwargs):
    # super(TelemetryValues, self).__init__()
    # self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        def check_primitive_or_latlong(value) -> bool:
            if isinstance(value, (None, str, int, float, bool)):
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

    # def update(self, *args, **kwargs):
    #     print('update', args, kwargs)
    #     for k, v in dict(*args, **kwargs).items():
    #         self[k] = v


@dataclass
class TelemetryRecord:
    values: dict[str, TelemetryValueType]
    timestamp: datetime = None
    unique_id: str = None
    tag: str = None

    def apply_timestamp(self):
        """ Timestamps this TelemetryEntry with the current timestamp """
        self.timestamp = Client.timestamp_now()
        return self


class C2dMessageType:
    # don't use actual enum because we want to allow "unknown" message types
    COMMAND: Final[int] = 0
    OTA: Final[int] = 1
    MODULE_COMMAND: Final[int] = 2
    UNDEFINED: Final[int] = 0xFFFF

    @classmethod
    def parse(cls, value: Union[int, None]) -> int:
        if value is None:
            return C2dMessageType.UNDEFINED
        return value


@dataclass
class IotcC2DMessageJson:
    urls: dict[str, dict[str, str]] = None
    ct: int = None
    cmd: str = None
    sw: str = None
    hw: str = None
    ack: str = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            urls=data.get("urls"),
            ct=data.get("ct"),
            cmd=data.get("cmd"),
            sw=data.get("sw"),
            hw=data.get("hw"),
            ack=data.get("ack")
        )


class C2dMessage:
    def __init__(self, packet: IotcC2DMessageJson):
        self.message_type = C2dMessageType.parse(packet.ct)
        self.ack_id = packet.ack
        if packet.cmd is not None:
            cmd_split = packet.cmd.split()
            self.command_name = cmd_split[0]
            self.command_args = cmd_split[1:]
            self.command_raw = packet.cmd
        else:
            self.command_name = None
            self.command_args = None
            self.command_raw = None


class UserCallbacks:
    connected_cb: Callable = None,
    command_cb: Optional[Callable[[C2dMessage], None]] = None
    ota_cb: Callable = None

    def __init__(
            self,
            connected_cb=None,
            command_cb: Optional[Callable[[C2dMessage], None]] = None,
            ota_cb=None
    ):
        self.connected_cb = connected_cb
        self.command_cb = command_cb
        self.ota_cb = ota_cb


class Client:

    @classmethod
    def timestamp_now(cls) -> datetime:
        """ Returns the UTC timestamp that can be used to stamp telemetry records """
        return datetime.now(timezone.utc)

    def __init__(
            self,
            config: DeviceConfig,
            callbacks: UserCallbacks = None
    ):
        self.config = config
        self.user_callbacks = callbacks
        print(DraDiscoveryUrl(config).get_api_url())
        t = Timing()
        resp = urllib.request.urlopen(urllib.request.Request(DraDiscoveryUrl(config).get_api_url()))
        response_data = IotcDiscoveryResponseJson.from_dict(json.loads(resp.read()))
        t.lap()
        resp = urllib.request.urlopen(DraIdentityUrl(response_data.d.bu).get_uid_api_url(config))
        response_data = IdentityResponseData.from_dict(json.loads(resp.read()))
        t.lap()
        self.mqtt_config = response_data.d.mqtt_data

        self.mqtt = PahoClient(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=self.mqtt_config.id
        )
        # TODO: User configurable with defaults
        self.mqtt.connect_timeout = 10
        self.mqtt.reconnect_delay_set(min_delay=1, max_delay=5)
        self.mqtt.tls_set(certfile=config.device_cert_path, keyfile=config.device_pkey_path)
        self.mqtt.username = self.mqtt_config.un

        self.mqtt.on_message = self.on_mqtt_message
        self.mqtt.on_connect = self.on_mqtt_connect
        self.mqtt.on_disconnect = self.on_mqtt_disconnect
        self.mqtt.on_publish = self.on_mqtt_publish

        self.user_callbacks = callbacks or UserCallbacks()

    def is_connected(self):
        # print('is_connected =', self.mqtt.is_connected())
        return self.mqtt.is_connected()

    def connect(self):
        #got_disconnect = False

        # def on_disconnected_while_connecting(mqttc: PahoClient, obj, flags: DisconnectFlags, reason_code: ReasonCode, properties):
        #     nonlocal got_disconnect
        #     got_disconnect = True

        def wait_for_connection() -> bool:
            # nonlocal got_disconnect
            got_disconnect = False
            connect_timer = Timing()
            print("waiting to connect...")
            while True:
                if self.is_connected():
                    print("MQTT connected")
                    return True
                # if got_disconnect:
                #     return False
                print(str(self.mqtt._state))
                time.sleep(0.5)
                if connect_timer.diff_now().seconds > 20:
                    print("Timed out.")
                    self.disconnect()
                    return False

        if self.is_connected():
            return
        # self.mqtt.on_disconnect = on_disconnected_while_connecting
        for i in range(1, 100):
            try:
                t = Timing()
                mqtt_error = self.mqtt.connect(
                    host=self.mqtt_config.h,
                    port=8883
                )
                if mqtt_error != MQTTErrorCode.MQTT_ERR_SUCCESS:
                    print("TLS connection to the endpoint failed")
                else:
                    print("Awaiting MQTT connection establishment...")
                    self.mqtt.loop_start()
                    if wait_for_connection():
                        print("Connected in %dms" % (t.diff_now().microseconds / 1000))
                        break
                    else:
                        continue

            except (SSLError, TimeoutError) as ex:
                print("Failed to connect to host %s. Exception: %s" % (self.mqtt_config.h, str(ex)))

            backoff_ms = random.randrange(1000, 15000)
            print("Retrying connection... Backing off for %d ms." % backoff_ms)
            # Jitter back off a random number of milliseconds between 1 and 10 seconds.
            time.sleep(backoff_ms / 1000)

        # self.mqtt.on_disconnect = self.on_mqtt_disconnect
        self.mqtt.subscribe(self.mqtt_config.topics.c2d, qos=1)

    def disconnect(self) -> MQTTErrorCode:
        ret = self.mqtt.disconnect()
        print("Disconnected.")
        return ret

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

        iotc_json = Client._to_iotconnect_json(records)
        if not self.is_connected():
            print('Message NOT sent. Not connected!')
        else:
            self.mqtt.publish(
                topic=self.mqtt_config.topics.rpt,
                qos=1,
                payload=iotc_json
            )
            print(">", iotc_json)

    @classmethod
    def _to_iotconnect_json(cls, records: list[TelemetryRecord]) -> str:
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
            # TODO: Validate:
            # if not isinstance(entry.values, TelemetryValues):
            #    # simple dict is fine, but check that the data is valid by converting it to our clas            #    entry.values = TelemetryValues(entry.values)
            t['d'].append(dict(to_iotconnect_data(entry)))
        return json.dumps(t, separators=(',', ':'))

    def _process_c2d_message(self, topic: str, payload: str) -> bool:
        # msg: C2dMessage = None
        try:
            j = json.loads(payload)
            pkt = IotcC2DMessageJson.from_dict(j)
            print("<", pkt)
            msg = C2dMessage(pkt)
            if msg.message_type == C2dMessageType.COMMAND:
                if msg.command_name == 'aws-qualification-start':
                    self._aws_qualification_start(msg.command_args)
                elif self.user_callbacks.command_cb is not None:
                    self.user_callbacks.command_cb(msg)
            elif msg.message_type == C2dMessageType.OTA:
                if self.user_callbacks.ota_cb is not None:
                    self.user_callbacks.ota_cb(msg)
            elif msg.message_type == C2dMessageType.UNDEFINED:
                print("Could not parse message type from message", payload)
            else:
                print("Message type %d is not supported by this client. Message was:", msg.message_type, payload)

        except JSONDecodeError as jde:
            print('Error: Incoming message not parseable: "%s"' % payload)
            return False

    def on_mqtt_connect(self, mqttc: PahoClient, obj, flags, reason_code, properties):
        print("Connected. Reason Code: " + str(reason_code))

    def on_mqtt_disconnect(self, mqttc: PahoClient, obj, flags: DisconnectFlags, reason_code: ReasonCode, properties):
        # print("Disconnected. Reason: %s. Flags: %s" % (str(reason_code), str(flags)))
        print("Disconnected")

    def on_mqtt_message(self, mqttc: PahoClient, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self._process_c2d_message(msg.topic, msg.payload)

    def on_mqtt_publish(self, mqttc: PahoClient, obj, mid, reason_code, properties):
        # print("mid: " + str(mid))
        pass

    def _aws_qualification_start(self, command_args: list[str]):
        t = Timing()

        def log_callback(client, userdata, level, buf):
            print("%d [%s]: %s" % (t.diff_now().microseconds/1000, str(level), buf))
            t.lap(False)

        if len(command_args) >= 1:
            host = command_args[0]
            print("Starting AWS Device Qualification for", host)
            self.mqtt_config.topics.rpt = 'qualification'
            self.mqtt_config.topics.c2d = 'qualification'
            self.mqtt_config.topics.ack = 'qualification'
            self.mqtt_config.h = host
            self.mqtt.on_log = log_callback
            self.disconnect()
            while True:
                if not self.is_connected():
                    print('(re)connecting to', self.mqtt_config.h)
                    self.connect()

                self.send_telemetry({
                    'qualification': 'true'
                })
                time.sleep(5)

        else:
            print("Malformed AWS qualification command. Missing command argument!")
