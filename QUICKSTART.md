## Introduction
This document outlines the steps of setting up the Python Lite SDK
on your PC.

## Prerequisites
The guide uses to a bash shell command prompt. The best way to get bash on
Windows is to install Git for Windows.

Openssl is required as an executable.

Additionally, curl or wget is required to download quickstart.py.
If quickstart.py can be placed in the working directory by other means,
then the requirement can be bypassed.

If you have previously installed the standard [Iotconnect Python SDK](https://github.com/avnet-iotconnect/iotc-python-sdk)
please note that you will not be able to use it alongside the Lite SDK,
unless you install this SDK in a Python virtual environment, as it will upgrade the 
paho-mqtt dependency package.

## Cloud Account Setup
An IoTConnect account is required.  If you need to create an account, a free trial subscription is available.

Select one of the two implementations of IoTConnect:
* [AWS Version](https://subscription.iotconnect.io/subscribe?cloud=aws)  (Recommended)
* [Azure Version](https://subscription.iotconnect.io/subscribe?cloud=azure)  

> **Note:**  Be sure to check any SPAM folder for the temporary password after registering.

See the IoTConnect [Subscription Information](https://github.com/avnet-iotconnect/avnet-iotconnect.github.io/blob/main/documentation/iotconnect/subscription/subscription.md) for more details on the trial.

## IoTConnect Device Template Setup

An IoTConnect *Device Template* will need to be created or imported. This defines the data format the platform should expect from the device.
* Download the pre-made  [Device Template](files/plitedemo-template.json?raw=1) (**must** Right-Click the link, Save As)
 
* **Click** the Device icon and the "Device" sub-menu:  
<img src="https://github.com/avnet-iotconnect/avnet-iotc-mtb-xensiv-example/assets/40640041/57e0b0c8-08ba-4c3f-b33d-489d7d0db568" width=200>
  
* At the bottom of the page, select the "Templates" icon from the toolbar.<br>![image](https://github.com/avnet-iotconnect/avnet-iotconnect.github.io/assets/40640041/3dc0b82c-13ea-4d99-93be-3adf14575709)
* At the top-right of the page, select the "Create Template" button.<br>![image](https://github.com/avnet-iotconnect/avnet-iotconnect.github.io/assets/40640041/33325cbd-4fee-4958-b32a-f28d0d52342c)
* At the top-right of the page, select the "Import" button.<br>![image](https://github.com/avnet-iotconnect/avnet-iotconnect.github.io/assets/40640041/418b999c-58e2-49f3-a3f1-118b16271b26)
* Finally, click the "Browse" button and select the template previously downloaded.

## Device Setup

Download and install the Python Lite SDK:
```shell
curl -sOJ 'https://saleshosted.z13.web.core.windows.net/sdk/python/iotconnect_sdk_lite-0.1.0-py3-none-any.whl'
python3 -m pip install iotconnect_sdk_lite-0.1.0-py3-none-any.whl
```
Execute the quickstart setup with the following line:
```shell
curl -s --output quickstart.sh 'https://raw.githubusercontent.com/avnet-iotconnect/iotc-python-lite-sdk/refs/heads/main/scripts/quickstart.sh' && bash ./quickstart.sh
``` 
Follow the quickstart.sh script prompts.

Successful output form running the quickstart should look like similar to this:
```
(re)connecting...
Awaiting MQTT connection establishment...
waiting to connect...
Connected. Reason Code: Success
MQTT connected
Connected in 572ms
> {"d":[{"d":{"sdk_version":"0.1.0","random":83}}]}
> {"d":[{"d":{"sdk_version":"0.1.0","random":13}}]}
...
```

If sending a command set-user-led with arguments "", you should see output similar to this:
```
Received command set-user-led ['50', '255', '0']
Setting User LED to R:50 G:255 B:0
...
```
