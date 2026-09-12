#!/usr/bin/env python3
"""Dependency bootstrap and short interactive menu; no Atlas dependency."""
import os
from pathlib import Path
import shlex
import subprocess
import sys
import webbrowser

ROOT=Path(__file__).resolve().parents[2]


def main():
    if sys.version_info<(3,10):raise RuntimeError('Python 3.10+ gerekiyor.')
    python=ROOT/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if not python.exists():subprocess.run([sys.executable,'-m','venv',str(ROOT/'.venv')],check=True)
    if subprocess.run([str(python),'-c','import yaml, PIL'],capture_output=True).returncode:
        subprocess.run([str(python),'-m','pip','install','-r',str(ROOT/'tools/flavor/requirements.txt')],check=True)
    args=sys.argv[1:]
    if not args:
        print('\nFlavor Studio — Hikâye masası\n\n1  Örnek diyagramı aç (Enter)\n2  Kendi planını önizle\n3  Kısa rehberi aç\n0  Çık\n')
        choice=input('Seçim [1]: ').strip() or '1'
        if choice=='0':return 0
        if choice=='3':webbrowser.open((ROOT/'tools/flavor/README.md').as_uri());return 0
        if choice=='1':args=['preview',str(ROOT/'tools/flavor/examples/academy.yml'),'--open']
        elif choice=='2':
            value=input('Plan dosyasını sürükle veya yolunu yaz: ').strip()
            path=Path(value).expanduser()
            if not path.is_file():
                parts=shlex.split(value,posix=os.name!='nt')
                if len(parts)!=1:raise ValueError('Tek bir YAML/JSON dosyası seçin.')
                path=Path(parts[0].strip('\'"')).expanduser()
            if not path.is_file():raise ValueError('Plan dosyası bulunamadı.')
            args=['preview',str(path.resolve()),'--open']
        else:raise ValueError('0–3 arasında seçim yapın.')
    return subprocess.run([str(python),str(ROOT/'tools/flavor/flavor.py'),*args],cwd=ROOT,env={**os.environ,'PYTHONUTF8':'1'}).returncode


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as exc:print(f'Hata: {exc}',file=sys.stderr);raise SystemExit(1)
    except (KeyboardInterrupt,EOFError):print('İptal edildi.');raise SystemExit(130)
