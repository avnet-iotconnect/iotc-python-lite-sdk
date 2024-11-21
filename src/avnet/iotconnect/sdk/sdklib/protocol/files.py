# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProtocolDeviceConfigJson:
    cpid: Optional[str] = field(default=None)
    env: Optional[str] = field(default=None)
    uid: Optional[str] = field(default=None)
    did: Optional[str] = field(default=None)
    disc: Optional[str] = field(default=None)
    ver: Optional[str] = field(default="2.1")
    pf: Optional[str] = field(default="aws")
    at: Optional[int] = field(default=7)  # authentication type, but ignored for now
