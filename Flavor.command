#!/bin/sh
FLAVOR_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
cd "$FLAVOR_ROOT" || exit 1
for FLAVOR_PY in "$FLAVOR_ROOT/.venv/bin/python" python3.13 python3.12 python3.11 python3.10 python3 python; do
    if "$FLAVOR_PY" -c 'import sys; assert sys.version_info >= (3,10)' >/dev/null 2>&1; then
        "$FLAVOR_PY" tools/flavor/launch.py "$@"
        FLAVOR_RESULT=$?
        if [ -t 0 ]; then printf '\nKapatmak için Enter… '; read -r FLAVOR_CLOSE; fi
        exit "$FLAVOR_RESULT"
    fi
done
printf '\nPython 3.10+ bulunamadı. Python kurup tekrar açın.\n'
if [ -t 0 ]; then read -r FLAVOR_CLOSE; fi
exit 1
