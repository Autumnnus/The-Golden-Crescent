#!/bin/sh
set -eu
bridge_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
for python_bin in python3 python; do
  if command -v "$python_bin" >/dev/null 2>&1; then
    exec "$python_bin" "$bridge_dir/tools.py" "$@"
  fi
done
echo 'Python bulunamadı. Python 3.10+ kurun.' >&2
exit 1
