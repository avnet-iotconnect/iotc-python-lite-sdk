# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

from dataclasses import dataclass, field
from typing import Optional, Any

from avnet.iotconnect.sdk.sdklib.util import add_from_dict


@add_from_dict
@dataclass
class ProtocolD2cTelemetryEntryJson:
    d: dict[str, Any] = field(default_factory=dict)
    dt: Optional[str] = field(default=None)
    id: Optional[str] = field(default=None)
    tg: Optional[str] = field(default=None)


@dataclass
class ProtocolD2cTelemetryMessageJson:
    d: list[ProtocolD2cTelemetryEntryJson] = field(default_factory=list[ProtocolD2cTelemetryEntryJson])
    # there is also a top level timestamp which has dubious meaning, so we don't support it
