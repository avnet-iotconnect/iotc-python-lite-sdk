class DeviceConfigError(Exception):
    def __init__(self, message: str):
        self.msg = message
        super().__init__(message)
