#!/bin/bash

set -e

this_dir=$(dirname "$0")

pushd "${this_dir}/.." >/dev/null
python3 -m pip install build
python3 -m build .
popd >/dev/null
