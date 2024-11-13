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

## IoTConnect Template Setup

TBD Upload [files/pl-demo.json](files/pl-demo.json)

Pre-made link  [Device Template](https://raw.githubusercontent.com/avnet-iotconnect/iotc-python-lite-sdk/main/files/pl-demo.json) (Right-click, Save As)

## Device Setup

TBD Follow the install.sh script

TBD Follow the quickstart.sh script
