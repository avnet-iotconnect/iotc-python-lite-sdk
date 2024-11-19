# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

from dataclasses import dataclass, field, fields
from typing import Optional, List

from avnet.iotconnect.sdk.sdklib.util import add_from_dict

@add_from_dict
@dataclass
class ProtocolC2dUrlJson:
    url: str = field(default=None)
    fileName: str = field(default=None)

@add_from_dict
@dataclass
class ProtocolC2dMessageJson:
    ct: Optional[int] = field(default=None)
    cmd: Optional[str] = field(default=None)
    sw: Optional[str] = field(default=None)
    hw: Optional[str] = field(default=None)
    ack: Optional[str] = field(default=None)
    urls: List[ProtocolC2dUrlJson] = field(default_factory=list) # this cannot be optional. It throws off dataclass


