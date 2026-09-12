#!/bin/sh
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sh "$project_dir/scripts/tools.sh" "$@"
result=$?
if [ "$result" -ne 0 ] && [ -t 0 ]; then
  printf '\nHata yukarıda. Kapatmak için Enter… '
  read -r ignored
fi
exit "$result"
