#!/bin/sh
ATLAS_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
exec sh "$ATLAS_ROOT/Atlas.command" "$@"
