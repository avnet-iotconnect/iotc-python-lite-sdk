# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

import urllib.request
from urllib.error import HTTPError, URLError

from avnet.iotconnect.sdk.sdklib.dra import DraDiscoveryUrl, DraDeviceInfoParser, DraIdentityUrl, \
    DeviceIdentityData
from .config import DeviceConfig
from .error import DeviceConfigError


class DeviceRestApi:
    def __init__(self, config: DeviceConfig):
        self.config = config

    def get_identity_data(self) -> DeviceIdentityData:
        try:
            print("Requesting Discovery Data %s..." % DraDiscoveryUrl(self.config).get_api_url())
            resp = urllib.request.urlopen(urllib.request.Request(DraDiscoveryUrl(self.config).get_api_url()))
            discovery_base_url = DraDeviceInfoParser.parse_discovery_response(resp.read())

            print("Requesting Identity Data %s..." % DraIdentityUrl(discovery_base_url).get_uid_api_url(self.config))
            resp = urllib.request.urlopen(DraIdentityUrl(discovery_base_url).get_uid_api_url(self.config))
            identity_response = DraDeviceInfoParser.parse_identity_response(resp.read())
            return identity_response

        except HTTPError as http_error:
            raise DeviceConfigError(http_error)

        except URLError as url_error:
            raise DeviceConfigError(str(url_error))
