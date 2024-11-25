# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

# This file contains inbound message types

from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ProtocolC2dMessageJson:
    ct: Optional[int] = field(default=None)
    ack: Optional[str] = field(default=None)
    df: Optional[int] = field(default=None)
    f: Optional[int] = field(default=None)

@dataclass
class ProtocolCommandMessageJson:
    ct: Optional[int] = field(default=None)
    cmd: Optional[str] = field(default=None)
    ack: Optional[str] = field(default=None)


@dataclass
class ProtocolOtaUrlJson:
    url: str = field(default=None)
    fileName: str = field(default=None)


@dataclass
class ProtocolOtaMessageJson:
    ct: Optional[int] = field(default=None)
    cmd: Optional[str] = field(default=None)
    sw: Optional[str] = field(default=None)
    hw: Optional[str] = field(default=None)
    ack: Optional[str] = field(default=None)
    urls: List[ProtocolOtaUrlJson] = field(default_factory=list)  # this cannot be optional. It throws off dataclass
