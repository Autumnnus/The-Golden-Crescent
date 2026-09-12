#!/bin/sh
# macOS: Finder'da çift tıklayın. Linux/macOS terminal: ./Atlas.sh
ATLAS_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
cd "$ATLAS_ROOT" || exit 1
for ATLAS_PY in "$ATLAS_ROOT/.venv/bin/python" python3.13 python3.12 python3.11 python3.10 python3 python; do
    if "$ATLAS_PY" -c 'import sys; assert sys.version_info >= (3, 10)' >/dev/null 2>&1; then
        "$ATLAS_PY" tools/atlas_launcher.py "$@"
        ATLAS_RESULT=$?
        if [ -t 0 ]; then
            printf '\nKapatmak için Enter… '
            read -r ATLAS_CLOSE
        fi
        exit "$ATLAS_RESULT"
    fi
done
printf '\nPython 3.10+ bulunamadı. Python kurup Atlas.command dosyasını tekrar açın.\n'
if [ -t 0 ]; then read -r ATLAS_CLOSE; fi
exit 1
