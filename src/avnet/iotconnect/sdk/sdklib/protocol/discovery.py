# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProtocolDiscoveryDJson:
    ec: Optional[int] = field(default=None)
    bu: Optional[str] = field(default=None)
    pf: Optional[str] = field(default=None)
    dip: Optional[int] = field(default=None)
    errorMsg: Optional[str] = None


@dataclass
class IotcDiscoveryResponseJson:
    d: ProtocolDiscoveryDJson = field(default_factory=ProtocolDiscoveryDJson)
    status: Optional[int] = field(default=None)
    message: Optional[str] = field(default=None)
