#!/bin/bash

set -e

# workaround for Git bash failing with subject formatting error for openssl
export MSYS_NO_PATHCONV=1


function check_sdk {
  if ! python3 -c 'from avnet.iotconnect.sdk.lite import Client' > /dev/null; then
    echo "The Python Lite SDK was not found. Please see instructions on how to install it at https://github.com/avnet-iotconnect/iotc-python-lite-sdk." >&2
  fi
}

function check_python_version {
  ver=$(python3 -c 'import sys; v=sys.version_info; print("%02d.%02d" % (v.major, v.minor))')
  if [[ "${ver}" > "03.07" ]]; then
    return 0
  else
    echo "Python version should be greater or equal to 3.7" >&2
    return 1
  fi
}

function has {
  if [ -z "$1" ]; then
    echo "Need argument 1" >&2
    exit 128
  fi
  if ! command -v "$1" &> /dev/null; then
    echo "Error: ${1} was not found. Please make sure to install it." >&2
    return 1
  fi
  return 0
}

function askyn {
  if [ -z "$1" ]; then
    echo "Need argument 1" >&2
    exit 128
  fi
  while true; do
    read -rp "$1 [y/n]: " answer
    if [[ "${answer}" =~ ^[yY]$ ]]; then
      return 0
    elif [[ "${answer}" =~ ^[nN]$ ]]; then
      return 1
    else
      echo "Please answer 'y' or 'n'."
    fi
  done
}

function gencert {
  if [ -z "$1" ]; then
    echo "Need argument 1" >&2
    exit 128
  fi

  cn=$1
  subj="/C=US/ST=IL/L=Chicago/O=IoTConnect/CN=${cn}"
  days=36500 # 100 years
  ec_curve=prime256v1

  openssl ecparam -name ${ec_curve} -genkey -noout -out "${cn}-pkey.pem"
  openssl req -new -days ${days} -nodes -x509 \
      -subj "${subj}" -key "${cn}-pkey.pem" -out "${cn}-cert.pem"

  echo "X659 credentials are now generated as ${cn}-cert.pem and ${cn}-pkey.pem."
}

has python3 || exit 3
has openssl || exit 4
has curl || exit 5

check_python_version || exit 5
check_sdk || exit 6


if [[ -f "device-cert.pem" && -f "device-pkey.pem" ]]; then
  if askyn "It seems that the device certificate and key already exist. Do you want to overwrite them?"; then
    gencert "device"
  fi
  # else just proceed
else
  gencert "device"
fi

cat <<END
---- IoTconnect Python Lite SDK Quickstart ----
This script will help guide you through the setup this device with IoTConnect.
Ensure that you have read the guide at https://github.com/avnet-iotconnect/iotc-python-lite-sdk on how to install the lite SDK before proceeding.
If you area already familiar with IoTconnect you can follow these simple steps:
- Create the device template by uploading TBD link to template.
- Create a new device and:
  - Select your Entity and the newly created template.
  - Click the "Use my certificate" radio button.
- Copy and paste the certificate that will be printed, including the BEGIN and END lines into the Certificate Text field.
END

read -rp "ENTER to print the certificate and proceed:"
cat device-cert.pem

cat <<END
- Click the "Save & View" button.
- Click the "Paper and Cog" icon at top right to download your device configuration file.
END

if [[ -f "iotcDeviceConfig.json" ]]; then
  askyn "It seems that the iotcDeviceConfig.json already exists. Do you want to overwrite it?" || ( print "Exiting..."; exit 2 )
fi

cat <<END
Open the downloaded file in a text editor and paste the content into this terminal and hit ENTER to add the last line.
END

echo > iotcDeviceConfig.json
while true; do
  read -r line
  echo "${line}" >> iotcDeviceConfig.json
  if [[ "${line}" == "}" ]]; then
    break
  fi
done

echo "Downloading quickstart.py... (TBD)"
cp ../examples/quickstart.py .

cat <<END
If you are connecting via a serial terminal, ensure that the content of iotcDeviceConfig.json matches what you pasted (type "cat iotcDeviceConfig.json" at the prompt to view it).
In some cases, pasting text into a serial terminal can cause it to skip characters. If using TeraTerm on Windows, enter a 10ms "Transmit delay" for both lines and characters in the Settings -> Serial Port dialog.
The Quickstart setup is complete.
You can now run this command on the command line to execute the Quickstart demo:
python3 quickstart.py
END

