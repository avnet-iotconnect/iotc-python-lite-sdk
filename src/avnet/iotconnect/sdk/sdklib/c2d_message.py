# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# This file contains definitions related to (inbound or outbound) C2D Messages

from avnet.iotconnect.sdk.lite.client import C2dMessageType
from avnet.iotconnect.sdk.sdklib.protocol.c2d import ProtocolC2dMessageJson, ProtocolCommandMessageJson, ProtocolOtaUrlJson, ProtocolOtaMessageJson

class C2dAck:
    """
    OTA Download statuses
    Best practices for OTA status:
    While the final success of the OTA action should be OTA_DOWNLOAD_DONE, it should be generally sent
    only if we are certain that we downloaded the OTA and the new firmware is up and running successfully.
    The user can store the original ACK ID and only report success only after successfully running with the new firmware.
    While the new firmware is downloading over the network or (if available/applicable) writing to the filesystem, unpacking,
    self-testing etc. the intermediate fine-grained statuses along with an appropriate message can be reported
    with the OTA_DOWNLOAD_FAILED status until DONE or FAILED status is reported.
    The exact steps can be left to the interpretation of the user, given the device's capabilities and limitations.
    """

    CMD_FAILED = 1

    CMD_SUCCESS_WITH_ACK  = 2

    # OTA download was not attempted or was rejected.
    OTA_FAILED = 1

    # An intermediate step during the firmware update is pending.
    OTA_DOWNLOADING = 2

    # OTA download is fully completed. New firmware is up and running.
    OTA_DOWNLOAD_DONE = 3

    # The download itself, self-test, writing the files, or unpacking or running the downloaded firmware has failed.
    OTA_DOWNLOAD_FAILED = 4

    @classmethod
    def is_valid_cmd_status(cls, status: int) -> bool:
        return status in (C2dAck.CMD_FAILED, C2dAck.CMD_SUCCESS_WITH_ACK)

    @classmethod
    def is_valid_ota_status(cls, status: int) -> bool:
        return status in (C2dAck.OTA_FAILED, C2dAck.OTA_DOWNLOADING, C2dAck.OTA_DOWNLOAD_DONE, C2dAck.OTA_DOWNLOAD_FAILED)

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
        cls = C2dMessage  # shorthand
        self.type_description = cls.TYPES.get(packet.ct)
        if self.type_description is None:
            self.type_description = cls.TYPES[cls.UNKNOWN]
            self.type = cls.UNKNOWN
        else:
            self.type = packet.ct # this can be None
        self.is_fatal = self.type in (cls.DEVICE_DELETED, cls.DEVICE_DISABLED, cls.DEVICE_RELEASED, cls.STOP_OPERATION)
        self.needs_refresh = self.type in (cls.DATA_FREQUENCY_CHANGE, cls.REFRESH_ATTRIBUTE, cls.REFRESH_SETTING, cls.REFRESH_EDGE_RULE, cls.REFRESH_CHILD_DEVICE)
        self.heartbeat_operation = None
        if self.type == cls.START_HEARTBEAT:
            self.heartbeat_operation = True
        elif self.type == cls.STOP_HEARTBEAT:
            self.heartbeat_operation = False
        self.frequency = packet.f or packet.df  # pick up frequency with respect to DATA_FREQUENCY_CHANGE or Heartbeat

    def validate(self) -> bool:
        return self.type is not None


class C2dCommand:
    def __init__(self, packet: ProtocolCommandMessageJson):
        self.type = C2dMessageType.COMMAND  # Used for error checking when sending ACKs
        self.ack_id = packet.ack
        if packet.cmd is not None and len(packet.cmd) > 0:
            cmd_split = packet.cmd.split()
            self.command_name = cmd_split[0]
            self.command_args = cmd_split[1:]
            self.command_raw = packet.cmd
        else:
            self.command_name = None
            self.command_args = []
            self.command_raw = ""

    def validate(self) -> bool:
        return self.command_name is not None


class C2dOta:
    class Url:
        def __init__(self, entry: ProtocolOtaUrlJson):
            self.url = entry.url
            self.file_name = entry.fileName

    def __init__(self, packet: ProtocolOtaMessageJson):
        self.type = C2dMessageType.OTA  # Used for error checking when sending ACKs
        self.ack_id = packet.ack
        self.version = packet.sw  # along with OTA superset
        self.hardware_version = packet.hw
        if packet.urls is not None and len(packet.urls) > 0:
            self.urls: list[C2dOta.Url] = [C2dOta.Url(x) for x in packet.urls]
        else:
            # we will let the client handle this case
            self.urls: list[C2dOta.Url] = []

    def validate(self) -> bool:
        if len(self.urls) > 0: return False
        if self.ack_id is None or len(self.ack_id) == 0: return False # OTA must have ack ID
        for u in self.urls:
            if u is None: return False
            if u.file_name is None or len(u.file_name) == 0: return False
            if u.url is None or len(u.url) == 0: return False
        return True
