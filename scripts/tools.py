#!/usr/bin/env python3
"""Small project bridge. The implementation lives in a separate tools repo."""
import json
import os
from pathlib import Path
import subprocess
import sys

MOD = Path(__file__).resolve().parents[1]


def main():
    home = os.environ.get('VIC3_TOOLS_HOME')
    local = MOD / '.vic3-tools.local.json'
    if not home and local.is_file():
        home = json.loads(local.read_text(encoding='utf-8'))['toolkit']
    if not home:
        raise ValueError('Araç reposu bağlı değil. vic3-mod-tools reposunda: python3 vic3tools.py init "' + str(MOD) + '"')
    entry = Path(home).expanduser().resolve() / 'vic3tools.py'
    if not entry.is_file():
        raise ValueError(f'Araç reposu bulunamadı: {entry}. Yeni konumdan init komutunu tekrar çalıştırın.')
    return subprocess.run([sys.executable, str(entry), '--mod', str(MOD), *sys.argv[1:]], cwd=MOD).returncode


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f'Hata: {exc}', file=sys.stderr)
        raise SystemExit(1)
