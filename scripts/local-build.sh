#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# Run this script to build and debug this package locally

set -e

this_dir=$(dirname "$0")

pushd "${this_dir}/.." >/dev/null
python3 -m build .
popd >/dev/null
