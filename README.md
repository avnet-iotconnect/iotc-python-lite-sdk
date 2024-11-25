# Introduction
This project is the IoTConnect Python Lite Client (SDK)
that aims for a modern, intuitive and robust interface to connect your
Linux, Windows or MacOS devices to the Avnet IoTConnect platform.

The project supports IoTConnect Device Protocol 2.1 devices. 
The project requires Python 3.9 or newer and provides
a set of features for most common IoTConnect use cases.

If you need support for older Pyton, Protocol 1.0, Properties (Shadow/Twin)
Offline or HTTP Client along with other features like Gateway/Child support
you should check out the standard
[Iotconnect Python SDK](https://github.com/avnet-iotconnect/iotc-python-sdk) repository.

# Licensing

This python package is distributed under the [MIT License](LICENSE.md).

# Installing

The quickest way to get started with the project is to follow the [QUICKSTART.md](QUICKSTART.md) document.

# Using the Client

Using this client to communicate to IoTConnect involves the following steps:
- Get familiar with the client API by examining documentation at [client.py](src/avnet/iotconnect/sdk/lite/client.py)
- Initialize the client with either:
  - iotcDeviceConfig.json (downloaded from the device *Info* panel) - see the [basic-example](examples/basic-example.py)
  - Explicit parameters to the constructor - see the [minimal example](examples/minimal.py).
- Optionally, configure your own Client settings (log verbosity, timeouts etc.) and pass those to the constructor.
- Optionally, pass callbacks for C2D message and OTA (see the [basic-example](examples/basic-example.py)) or even your own [custom message handler](examples/c2d-special-event-handling.py) to the constructor 
  - While actual download and application replacement mechanism would depend on how your application runs
    (via a system service, cron or other method) a simple OTA download and install method is shown in the [ota-handling](examples/ota-handling.py) example.  
- Optionally, pass a callback for the MQTT disconnect event and handle it according to your application requirements.  
- Call Client.connect(). The call should block until connected based on timeout retry settings.
- Call Client.send_telemetry() at regular intervals. Verify that the client is connected with Client.is_connected()
