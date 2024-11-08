from dataclasses import dataclass

@dataclass
class IotcC2dURLJson:
    url: str
    fileName: str

@dataclass
class IotcC2DMessageJson:
    urls: dict[str, dict[str, str]] = None
    ct: int = None
    cmd: str = None
    sw: str = None
    hw: str = None
    ack: str = None

    @classmethod
    def from_dict(cls, data: dict):

        return cls(
            urls=data.get("urls"),
            ct=data.get("ct"),
            cmd=data.get("cmd"),
            sw=data.get("sw"),
            hw=data.get("hw"),
            ack=data.get("ack")
        )
