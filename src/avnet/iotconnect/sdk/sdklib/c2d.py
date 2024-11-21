# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

from avnet.iotconnect.sdk.sdklib.protocol.c2d import ProtocolC2dMessageJson, ProtocolC2dCommandJson, ProtocolC2dUrlJson, ProtocolC2dOtaJson


class C2dMessage:
    COMMAND = 0
    OTA = 1
    MODULE_COMMAND = 2
    REFRESH_ATTRIBUTE = 101
    REFRESH_SETTING = 102
    REFRESH_EDGE_RULE = 103
    REFRESH_CHILD_DEVICE = 104
    DATA_FREQUENCY_CHANGE = 105
    DEVICE_DELETED = 106
    DEVICE_DISABLED = 107
    DEVICE_RELEASED = 108
    STOP_OPERATION = 109
    START_HEARTBEAT = 100
    STOP_HEARTBEAT = 111
    UNKNOWN = 9999

    TYPES: dict[int, str, str] = {
        COMMAND: "Command",
        OTA: "OTA Update",
        REFRESH_ATTRIBUTE: "Refresh Attribute",
        REFRESH_SETTING: "Refresh Setting (Twin/Shadow))",
        REFRESH_EDGE_RULE: "Refresh Edge Rule",
        REFRESH_CHILD_DEVICE: "Refresh Child Device",
        DATA_FREQUENCY_CHANGE: "Data Frequency Changed",
        DEVICE_DELETED: "Device Deleted",
        DEVICE_DISABLED: "Device Disabled",
        DEVICE_RELEASED: "Device Released",
        STOP_OPERATION: "Stop Operation",
        START_HEARTBEAT: "Start Heartbeat",
        STOP_HEARTBEAT: "Stop Heartbeat",
        UNKNOWN: "<Unknown Command Received>"
    }

    def __init__(self, packet: ProtocolC2dMessageJson):
        cls = C2dMessage # shorthand
        self.description = cls.TYPES.get(packet.ct)
        if self.description is None:
            self.description = cls.TYPES[cls.UNKNOWN]
            self.type = cls.UNKNOWN
        else:
            self.type = packet.ct
        self.is_fatal = self.type in (cls.DEVICE_DELETED, cls.DEVICE_DISABLED, cls.DEVICE_RELEASED, cls.STOP_OPERATION)
        self.needs_refresh = self.type in (cls.DATA_FREQUENCY_CHANGE, cls.REFRESH_ATTRIBUTE, cls.REFRESH_SETTING, cls.REFRESH_EDGE_RULE, cls.REFRESH_CHILD_DEVICE)
        self.heartbeat_operation = None
        if self.type == cls.START_HEARTBEAT:
            self.heartbeat_operation = True
        elif self.type == cls.STOP_HEARTBEAT:
            self.heartbeat_operation = False
        self.frequency = packet.f or packet.df # pick up frequency with respect to DATA_FREQUENCY_CHANGE or Heartbeat


class C2dCommand:
    def __init__(self, packet: ProtocolC2dCommandJson):
        self.ack_id = packet.ack
        if packet.cmd is not None:
            cmd_split = packet.cmd.split()
            self.command_name = cmd_split[0]
            self.command_args = cmd_split[1:]
            self.command_raw = packet.cmd
        else:
            self.command_name = None
            self.command_args = []
            self.command_raw = ""


class C2dOta:
    class Url:
        def __init__(self, entry: ProtocolC2dUrlJson):
            self.url = entry.url
            self.file_name = entry.fileName

    def __init__(self, packet: ProtocolC2dOtaJson):
        self.ack_id = packet.ack
        self.version = packet.sw # along with OTA superset
        self.hardware_version = packet.hw
        if packet.urls is not None and len(packet.urls) > 0:
            self.urls : list[C2dOta.Url] = [C2dOta.Url(x) for x in  packet.urls]
        else:
            # we will let the client handle this case
            self.urls : list[C2dOta.Url] = []
        if packet.cmd is not None:
            cmd_split = packet.cmd.split()
            self.command_name = cmd_split[0]
            self.command_args = cmd_split[1:]
            self.command_raw = packet.cmd
        else:
            self.command_name = None
            self.command_args = []
            self.command_raw = ""
