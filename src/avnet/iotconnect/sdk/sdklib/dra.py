import json
import urllib.parse
from typing import Final, Union

from avnet.iotconnect.sdk.lite import DeviceConfig, DeviceConfigError
from avnet.iotconnect.sdk.sdklib.protocol.discovery import IotcDiscoveryResponseJson
from avnet.iotconnect.sdk.sdklib.protocol.identity import ProtocolIdentityPJson, ProtocolMetaJson, ProtocolIdentityResponseJson


class DeviceIdentityData:
    def __init__(self, mqtt: ProtocolIdentityPJson, metadata: ProtocolMetaJson):
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
    API_URL_FORMAT: Final[str] = "%s/api/v2.1/dsdk/cpId/%s/env/%s"

    def get_api_url(self) -> str:
        return DraDiscoveryUrl.API_URL_FORMAT % (
            self.config.discovery_url,
            urllib.parse.quote(self.config.cpid, safe=''),
            urllib.parse.quote(self.config.env, safe='')
        )

    def __init__(self, config: DeviceConfig):
        self.config = config


class DraIdentityUrl:
    UID_API_URL_FORMAT: Final[str] = "%s/uid/%s"

    def __init__(self, base_url):
        self.base_url = base_url

    method: str = "GET"  # To clarify that get should be used to parse the response

    def get_uid_api_url(self, config: DeviceConfig) -> str:
        return DraIdentityUrl.UID_API_URL_FORMAT % (
            self.base_url,
            urllib.parse.quote(config.duid, safe='')
        )

    def _validate_identity_response(self, ird: ProtocolIdentityResponseJson):
        # TODO: validate and throw DeviceConfigError
        pass


class DraDeviceInfoParser:
    EC_RESPONSE_MAPPING = [
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
    def _parsing_common(cls, what: str, rd: Union[IotcDiscoveryResponseJson, ProtocolIdentityResponseJson]):
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

        drd: IotcDiscoveryResponseJson
        try:
            drd = IotcDiscoveryResponseJson(json.loads(discovery_response))
        except json.JSONDecodeError as json_error:
            raise DeviceConfigError("Discovery JSON Parsing Error: %s" % str(json_error))
        cls._parsing_common("Discovery", drd)

        if drd.d.bu is None:
            raise DeviceConfigError("Discovery response is missing base URL")

        return drd.d.bu

    @classmethod
    def parse_identity_response(cls, identity_response: str) -> DeviceIdentityData:
        ird: ProtocolIdentityResponseJson
        try:
            ird = ProtocolIdentityResponseJson(json.loads(identity_response))
        except json.JSONDecodeError as json_error:
            raise DeviceConfigError("Identity JSON Parsing Error: %s" % str(json_error))
        cls._parsing_common("Identity", ird)

        return DeviceIdentityData(ird.d.p, ird.d.meta)

