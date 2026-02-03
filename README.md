# Introduction
This project is the /IOTCONNECT Python Lite Client (SDK)
that aims for a modern, intuitive and robust interface to connect your
Linux, Windows or MacOS devices to the Avnet IoTConnect platform.

The project supports /IOTCONNECT Device Protocol 2.1 devices. 
The project requires Python 3.9 or newer and provides
a set of features for most common /IOTCONNECT use cases.

If you need support for older Pyton, both Protocol 1.0 and 2.1, Properties (Shadow/Twin)
Offline or HTTP Client along with other features like Gateway/Child support
you should check out the standard
[iotconnect-python-sdk](https://github.com/avnet-iotconnect/iotc-python-sdk) repository.

See the [iotc-python-lite-sdk-demos](https://github.com/avnet-iotconnect/iotc-python-lite-sdk-demos) repository for implementation examples.

# Licensing

This python package is distributed under the [MIT License](LICENSE.md).

# Installing

The quickest way to get started with the project is to follow the [QUICKSTART.md](QUICKSTART.md) document.

# Using the Client

Using this client to communicate to /IOTCONNECT involves the following steps:
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

# Development and Testing

Please ensure to review the [CONTRIBUTING.md](CONTRIBUTING.md) document for detailed guidelines before making changes to the project.

To set up for development:
- Ensure to use a modern IDE like PYCharm Community Edition or VSCode so that typing hints
    will be properly recognized. This will ensure that problems are caught early or typing issues
    are not causing a burden for future development.
- Clone this repository locally.
- Create a new development branch.
- Install the local repo as editable package with development dependencies:
```bash
pip3 install -e .[dev]
```
- If needing to make changes to the iotc-python-sdk-lib, clone that repository as well and install it as editable package:
```bash
pip3 install -e path/to/iotc-python-sdk-lib
```
- When done with changes, submit a pull request for this and/or the iotc-python-sdk-lib repository as needed.
