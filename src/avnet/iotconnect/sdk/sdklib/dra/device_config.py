from array import ArrayType
from pkgutil import get_data
from typing import Final, Callable
import json

from avnet.iotconnect.sdk.sdklib.dra.identity_data import MqttData, MetaData
from .discovery_data import DiscoveryResponseData
from .identity_data import IdentityResponseData, MqttData
from ..util import to_json


# Parses and extracts device configuration from IdentityResponse
# Throws DeviceConfigError if parsing encounters an issue

class DeviceConfigError(Exception):
    def __init__(self, message: str):
        self.msg = message
        super().__init__(message)

class DraDeviceConfig:
    def __init__(self, platform: str = None, env: str = None, cpid: str = None, duid: str = None):
        # TODO: validate args
        self.env = env
        self.cpid = cpid
        self.duid = duid
        self.platform = platform
        self.validate()

    def validate(self):
        # TODO: implement
        pass


class DeviceIdentityData:
    def __init__(self, mqtt: MqttData, metadata: MetaData):
        self.host = mqtt.h
        self.client_id = mqtt.id
        self.username = mqtt.un
        self.topics = mqtt.topics

        self.pf = metadata.pf
        self.is_edge_device = metadata.edge
        self.is_gateway_device = metadata.gtw
        self.protocol_version = str(metadata.v)


class DraDiscoveryUrl:
    method: str = "GET"  # To clarify that get should be used to parse the response
    URL_FORMAT: Final[str] = "%s/api/v2.1/dsdk/cpId/%s/env/%s"

    def get_discovery_url(self, config: DraDeviceConfig):
        if self.base_url is None:
            if config.platform == "az":
                self.base_url = "https://discovery.iotconnect.io"
            elif config.platform == "aws":
                if config.env == "poc":
                    self.base_url = "https://awsdiscovery.iotconnect.io"
                else:
                    self.base_url = "https://consolediscovery.iotconnect.io"
            else:
                raise DeviceConfigError("Invalid platform %s" % config.platform)

        return DraDiscoveryUrl.URL_FORMAT % (self.base_url, config.cpid, config.env)

    def __init__(self, base_url):
        self.base_url = base_url


class DraIdentityUrl:
    URL_FORMAT: Final[str] = "%s/uid/%s"

    def __init__(self, base_url):
        self.base_url = base_url

    method: str = "GET"  # To clarify that get should be used to parse the response

    def get_identity_url(self, config: DraDeviceConfig):
        return DraIdentityUrl.URL_FORMAT % (self.base_url, config.duid)

    def _validate_identity_response(self, ird: IdentityResponseData):
        # TODO: validate and throw DeviceConfigError
        pass


class DraDeviceInfoParser:
    EC_RESPONSE_MAPPING: Final[ArrayType[str]] = [
        "OK – No Error",
        "Device not found. Device is not whitelisted to platform.",
        "Device is not active.",
        "Un-Associated. Device has not any template associated with it.",
        "Device is not acquired. Device is created but it is in release state.",
        "Device is disabled. It’s disabled from broker by Platform Admin",
        "Company not found as SID is not valid",
        "Subscription is expired.",
        "Connection Not Allowed.",
        "Invalid Bootstrap Certificate.",
        "Invalid Operational Certificate."
    ]

    @classmethod
    def _parsing_common(cls, what: str, rd: DiscoveryResponseData | IdentityResponseData):
        """ Helper to parse either discovery or identity response common error fields """

        ec_message = 'not available'
        has_error = False
        if rd.d is not None:
            if rd.d.ec != 0:
                has_error = True
                if rd.d.ec <= len(cls.EC_RESPONSE_MAPPING):
                    ec_message = 'ec=%d (%s)' % (rd.d.ec, cls.EC_RESPONSE_MAPPING[rd.d.ec])
                else:
                    ec_message = 'ec==%d' % rd.d.ec
        else:
            has_error = True

        if rd.status != 200:
            has_error = True

        if has_error:
            raise DeviceConfigError(
                '%s failed. Error: "%s" status=%d message=%s' % (
                    what,
                    ec_message,
                    rd.status,
                    rd.message or "(message not available)"
                )
            )

    @classmethod
    def parse_discovery_response(cls, discovery_response: str) -> str:
        """ Parses discovery response JSON and Returns base URL or raises DeviceConfigError """

        drd: DiscoveryResponseData
        try:
            drd = DiscoveryResponseData.from_json(json.loads(discovery_response))
        except json.JSONDecodeError as json_error:
            raise DeviceConfigError("Discovery JSON Parsing Error: %s" % str(json_error))
        cls._parsing_common("Discovery", drd)

        if drd.d.bu is None:
            raise DeviceConfigError("Discovery response is missing base URL")

        return drd.d.bu

    @classmethod
    def parse_identity_response(cls, identity_response: str) -> DeviceIdentityData:
        ird: IdentityResponseData
        try:
            ird = IdentityResponseData.from_json(json.loads(identity_response))
        except json.JSONDecodeError as json_error:
            raise DeviceConfigError("Identity JSON Parsing Error: %s" % str(json_error))
        cls._parsing_common("Identity", ird)

        return DeviceIdentityData(ird.d.mqtt_data, ird.d.metadata)

