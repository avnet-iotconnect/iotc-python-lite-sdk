#!/bin/bash

# ----------- I M P O R T A N T ------------
# Run this script first to build the package and process the README.md
# before posting the package to PyPi or anywhere else.
# IMPORTANT: If anything fails along the way, review the original README.md for any problems
# and roll it back if needed before checking it in.

set -e

this_dir=$(dirname "$0")
pushd "${this_dir}/.." >/dev/null


REPO_URL="https://github.com/avnet-iotconnect/iotc-python-lite-sdk"
VERSION_FILE="src/avnet/iotconnect/sdk/lite/__init__.py"
README_PATH="README.md"
README_PATH_WORK="README.work.md"
README_PATH_BKP="README.bak.md"

# Make a backup of the original README.
cp "${README_PATH}" "${README_PATH_BKP}"

# Prepare the new (work) README
python3 <<EOF
import re
from pathlib import Path

# Do not import this directly in order to avoid possible import errors.
# Just locate the actual version and exex it.
with open("${VERSION_FILE}", "r") as f:
    for line in f:
        if '__version__ ' in line:
            exec(line)
            break
print("Package version is", __version__)

repo_url = "${REPO_URL}"
readme_path = Path("${README_PATH}")
README_PATH_WORK = Path("${README_PATH_WORK}")

with readme_path.open("r", encoding="utf-8") as file:
    content = file.read()

content = re.sub(
    r'\[([^\]]+)\]\((?!http)([^)]+)\)',
    lambda match: f"[{match.group(1)}]({repo_url}/blob/v{__version__}/{match.group(2)})",
    content,
)

heading="""
> This document is reformatted to better viewing as a standalone document.
> We recommend visiting this [GitHub v{} link]({}) for best experience.

""".format(__version__, f"$REPO_URL/blob/v{__version__}/")

with README_PATH_WORK.open("w", encoding="utf-8") as file:
    file.write(heading)
    file.write(content)
EOF

echo "README prepared at $README_PATH_WORK"

# Build the package using the temporary README
cp "${README_PATH_WORK}" "${README_PATH}"
python3 -m pip install build
python3 -m build

# Cleanup
# Restore README from backup
cp "${README_PATH_BKP}" "${README_PATH}"

popd >/dev/null