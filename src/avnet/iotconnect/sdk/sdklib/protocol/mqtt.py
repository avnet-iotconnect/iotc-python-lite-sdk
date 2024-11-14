# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

from dataclasses import dataclass, field
from typing import Optional

from avnet.iotconnect.sdk.sdklib.util import filter_init


@filter_init
@dataclass
class ProtocolC2dUrlJson:
    url: Optional[str] = field(default=None)
    fileName: Optional[str] = field(default=None)

@filter_init
@dataclass
class ProtocolC2dMessageJson:
    urls: Optional[list[ProtocolC2dUrlJson]] = field(default_factory=list[ProtocolC2dUrlJson])
    ct: Optional[int] = field(default=None)
    cmd: Optional[str] = field(default=None)
    sw: Optional[str] = field(default=None)
    hw: Optional[str] = field(default=None)
    ack: Optional[str] = field(default=None)
