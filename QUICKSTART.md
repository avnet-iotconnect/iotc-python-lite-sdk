## Introduction
This document outlines the steps of setting up the Python Lite SDK
on your PC.

## Prerequisites
The guide uses to a bash shell command prompt. The best way to get bash on
Windows is to install Git for Windows.

Additionally, you will need openssl.

If you have previously installed the standard [Iotconnect Python SDK](https://github.com/avnet-iotconnect/iotc-python-sdk)
please note that you will not be able to use it alongside the Lite SDK unless
you install this SDK in a Python virtual environment, as it will upgrade the 
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

Execute the quickstart setup with the following line:
```shell
curl https://sdk.cloud.google.com | bash
```

TBD Follow the quickstart.sh script