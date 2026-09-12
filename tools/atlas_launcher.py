#!/usr/bin/env python3
"""Small cross-platform launcher; defaults to preview, never silently applies it."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
ENV_PYTHON = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def execute(args):
    result = subprocess.run([str(x) for x in args], cwd=ROOT,
                            env={**os.environ, 'PYTHONUTF8': '1'})
    if result.returncode:
        raise RuntimeError(f'İşlem durdu (kod {result.returncode}). Yukarıdaki hata giderilmeden devam edilmedi.')


def environment():
    if sys.version_info < (3, 10):
        raise RuntimeError('Python 3.10 veya daha yenisi gerekiyor. Python kurulumundan sonra Atlas dosyasını tekrar açın.')
    if not ENV_PYTHON.exists():
        print('İlk kullanım: proje için Python ortamı hazırlanıyor…', flush=True)
        execute([sys.executable, '-m', 'venv', ROOT / '.venv'])
    probe = subprocess.run([str(ENV_PYTHON), '-c', 'import numpy, PIL, yaml; import sys; assert sys.version_info >= (3,10)'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if probe.returncode:
        print('Gerekli paketler kuruluyor (ilk kurulum internet gerektirir)…', flush=True)
        execute([ENV_PYTHON, '-m', 'pip', 'install', '-r', ROOT / 'tools/requirements.txt'])
    return ENV_PYTHON


def input_path(value):
    value = value.strip()
    direct = Path(value).expanduser()
    if direct.is_file():
        return direct.resolve()
    try:
        parts = shlex.split(value, posix=os.name != 'nt')
    except ValueError:
        parts = []
    if len(parts) == 1:
        direct = Path(parts[0].strip('"\'')).expanduser()
        if direct.is_file():
            return direct.resolve()
    raise ValueError('Senaryo dosyası bulunamadı. YAML/JSON dosyasını terminale sürükleyip Enter’a basın.')


def menu():
    print('\nThe Golden Crescent — Atlas\n')
    print('  1  Mevcut haritayı aç (Enter)')
    print('  2  YAML/JSON senaryosunu önizle — etkin modu değiştirmez')
    print('  3  Etkin modun kaynak ve üretilen dosyalarını kontrol et')
    print('  4  world/ kaynağını mod dosyalarına derle ve kontrol et')
    print('  5  Kısa rehberi aç')
    print('  0  Çık\n')
    choice = input('Seçim [1]: ').strip() or '1'
    if choice == '0': return 'exit', None
    if choice == '5': return 'guide', None
    if choice == '2':
        return 'atlas', input_path(input('Senaryo dosyasını buraya sürükleyin veya yolunu yazın: '))
    if choice in ('1', '3', '4'):
        return {'1': 'atlas', '3': 'check', '4': 'build'}[choice], None
    raise ValueError('Geçersiz seçim. 0–5 arasında bir sayı kullanın.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario', nargs='?', help='YAML/JSON file to preview')
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true')
    actions.add_argument('--build', action='store_true')
    actions.add_argument('--menu', action='store_true')
    parser.add_argument('--no-browser', action='store_true', help='Prepare without opening the default browser')
    args = parser.parse_args(argv)
    action = 'build' if args.build else 'check' if args.check else 'atlas'
    selected = input_path(args.scenario) if args.scenario else None
    if selected and action != 'atlas':
        raise ValueError('Senaryo dosyası yalnızca önizleme içindir. Etkin derleme kaynağı world/ klasörüdür.')
    if args.menu or (not argv and len(sys.argv) == 1 and sys.stdin.isatty()):
        action, selected = menu()
    if action == 'exit': return 0
    if action == 'guide':
        webbrowser.open((ROOT / 'ATLAS_KISA_REHBER.md').as_uri())
        return 0
    python = environment()
    command = [python, ROOT / 'tools/tgc.py']
    if action in ('check', 'build'):
        if action == 'build': execute(command + ['build'])
        execute(command + ['check'])
        print('\nKontrol tamamlandı.')
        return 0
    destination = ROOT / 'build/maps' / ('atlas_preview.html' if selected else 'atlas_world.html')
    print('\nHarita hazırlanıyor. İlk seferde oyun verileri de okunabilir…', flush=True)
    options = ['--scenario', selected] if selected else []
    execute(command + ['atlas', '--out', destination, *options])
    print(f'\nHazır: {destination}\nBu HTML dosyası daha sonra doğrudan açılabilir; sunucu gerekmez.')
    if not args.no_browser:
        if not webbrowser.open(destination.as_uri()):
            print('Tarayıcı otomatik açılamadı. Yukarıdaki HTML dosyasına çift tıklayın.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError) as exc:
        print(f'\nHata: {exc}', file=sys.stderr)
        raise SystemExit(1)
    except (KeyboardInterrupt, EOFError):
        print('\nİptal edildi.')
        raise SystemExit(130)
