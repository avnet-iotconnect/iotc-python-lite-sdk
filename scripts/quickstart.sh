#!/bin/bash

set -e

function gencert {
  # workaround for Git bash failing with subject formatting error
  export MSYS_NO_PATHCONV=1

  if [ -z "$1" ]; then
    echo Need argument 1
    exit
  fi

  cn=$1
  subj="/C=US/ST=IL/L=Chicago/O=IoTConnect/CN=${cn}"
  days=36500 # 100 years
  ec_curve=prime256v1

  openssl ecparam -name ${ec_curve} -genkey -noout -out ${cn}_ec_key.pem
  openssl req -new -days ${days} -nodes -x509 \
      -subj "${subj}" -key ${cn}_ec_key.pem -out ${cn}_ec_crt.pem
  openssl ec -outform der -in ${cn}_ec_key.pem -out ${cn}_ec_key.der
  openssl x509 -outform der -in ${cn}_ec_crt.pem -out ${cn}_ec_crt.der
}

cat <<END
This script will help guide you through the setup this device with IoTConnect.
END



