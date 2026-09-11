"""Crash daraltma araci: mod icerigini gruplar halinde acip kapatir.

Statik denetim crash'i bulamadiginda tek guvenilir yontem ikiye bolme.
Bu arac icerigi SILMEZ; `_bisect_off/` altina tasir ve geri alir.
`_bisect_off/` Victoria 3'un taradigi bir dizin degildir, oyun gormez.

    python tools/bisect.py durum
    python tools/bisect.py kapat flavor
    python tools/bisect.py ac flavor
    python tools/bisect.py ac hepsi

Harita verisi icin ayri yol var: `world/` kaynaklari kapatilip
`python tools/tgc.py build` tekrar calistirilir; kapatilan bolgeler
vanilla halinde kalir (defaults.unlisted = inherit).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFF = ROOT / "_bisect_off"

# Her grup: oyunun gordugu, mod koküne gore yollar.
GROUPS: dict[str, list[str]] = {
    # Elle yazilmis flavor. Hicbiri harita verisinin on kosulu degil.
    "flavor": [
        "common/journal_entries",
        "common/journal_entry_groups",
        "common/scripted_triggers",
        "common/script_values",
        "common/static_modifiers",
        "common/game_concepts",
        "events",
        "common/history/countries/tgc_journal_entries.txt",
    ],
    # Armalar: 277 arma. Yeni tag'ler varsayilan armaya duser.
    "arms": ["common/coat_of_arms"],
    # Localization ve isim ezmeleri. Eksikse ham anahtar gorunur, crash etmez.
    "loc": [
        "localization/english/replace/tgc_dynamic_names_l_english.yml",
        "localization/turkish/replace/tgc_dynamic_names_l_turkish.yml",
        "localization/english/tgc_concepts_l_english.yml",
        "localization/turkish/tgc_concepts_l_turkish.yml",
        "localization/english/tgc_main_powers_l_english.yml",
        "localization/turkish/tgc_main_powers_l_turkish.yml",
        "localization/english/tgc_minbar_l_english.yml",
        "localization/turkish/tgc_minbar_l_turkish.yml",
    ],
    # Uretilmis diplomasi (vanilla dosya adlarini ezer; kapatinca vanilla doner).
    "diplomasi": ["common/history/diplomacy"],
    # Uretilmis ordular (ayni sekilde vanilla'yi ezer).
    "ordular": ["common/history/military_formations"],
    # Teknoloji ve okuryazarlik ezmeleri.
    "teknoloji": [
        "common/history/countries/tgc_technology.txt",
        "common/history/population",
    ],
    # Uretilmis binalar. replace_paths vanilla'yi kapali tuttugu icin bunlari
    # kapatmak "hic bina yok" demek - state'ler ve pop'lar yerinde kalir.
    "binalar": ["common/history/buildings"],
    # --- HARITA YARISI ---------------------------------------------------
    # Bunlari kapatmak `world/` kaynagini kapatir; ardindan `tgc.py build`
    # calistirilmali. Kapatilan bolgeler vanilla sahipliginde kalir
    # (world/_defaults.yml: unlisted = inherit), yani sonuc TUTARLI bir
    # yari-senaryodur - state, pop, bina ve diplomasi kendiliginden uyumlanir.
    "dogu": [f"world/states/{n}" for n in (
        "08_middle_east.yml", "09_central_asia.yml", "10_india.yml",
        "11_east_asia.yml", "12_indonesia.yml", "13_australasia.yml",
        "14_siberia.yml", "15_russia.yml")],
    "bati": [f"world/states/{n}" for n in (
        "00_west_europe.yml", "01_south_europe.yml", "02_east_europe.yml",
        "03_north_africa.yml", "04_subsaharan_africa.yml", "05_north_america.yml",
        "06_central_america.yml", "07_south_america.yml")],
    # Uretilmis pop'lar. DIKKAT: bunu kapatmak "hic pop yok" demek; kendi
    # basina crash sebebi olabilir, bu yuzden en son denenmeli.
    "poplar": ["common/history/pops"],
}


# Bazi gruplar vanilla dosyalarini AYNI ISIMLE eziyor (diplomasi, ordular).
# Onlari silmek vanilla'nin bozuk halini geri getirir ve testi kirletir; bunun
# yerine ayni isimde BOS ama gecerli bir govde yazilir.
EMPTY_BODY = {
    "diplomasi": "DIPLOMACY = {\n}\n",
    "ordular": "MILITARY_FORMATIONS = {\n}\n",
}


# Ictihat Cagi mezhepleri -> vanilla karsiliklari.
# `dinsiz` komutu bunlari uretilmis dosyalarda yerine koyar ve
# common/religions'i kapatir. Boylece mod TUTARLI kalir (hicbir pop
# tanimsiz bir dine isaret etmez) ama motorda yalnizca vanilla'nin 17 dini olur.
RELIGION_FALLBACK = {
    "mujtahidiyya": "sunni",
    "irfaniyya": "shiite",
    "taklidiyya": "sunni",
    "hikmatiyya": "sunni",
}
RELIGION_PATHS = [
    "common/religions",
    "localization/english/tgc_religions_l_english.yml",
    "localization/turkish/tgc_religions_l_turkish.yml",
]
REWRITE_GLOBS = [
    "common/history/pops/*.txt",
    "common/country_definitions/*.txt",
]


def dinsiz() -> None:
    """Yeni dinleri kaldirir, uretilmis dosyalarda vanilla karsiligini yazar."""
    for rel in RELIGION_PATHS:
        if _move(ROOT / rel, OFF / rel):
            print(f"  kapatildi  {rel}")
    total = 0
    for pattern in REWRITE_GLOBS:
        for file in ROOT.glob(pattern):
            text = original = file.read_text(encoding="utf-8-sig")
            for new, old in RELIGION_FALLBACK.items():
                text = text.replace(f'"{new}"', f'"{old}"').replace(f"= {new}", f"= {old}")
            if text != original:
                file.write_text(text, encoding="utf-8-sig")
                total += 1
    print(f"[dinsiz] {total} uretilmis dosyada din adlari vanilla'ya cevrildi")
    print("         geri almak icin: python tools/daralt.py dinli")


def dinli() -> None:
    for rel in RELIGION_PATHS:
        if _move(OFF / rel, ROOT / rel):
            print(f"  acildi     {rel}")
    print("[dinli] simdi 'python tools/tgc.py build' calistir")


def bosalt(group: str) -> None:
    """Grubu silmeden etkisiz hale getirir: ayni isimde bos govde yazar."""
    body = EMPTY_BODY[group]
    for rel in GROUPS[group]:
        folder = ROOT / rel
        if not folder.is_dir():
            continue
        backup = OFF / (rel + "__dolu")
        if not backup.exists():
            shutil.copytree(folder, backup)
        for file in folder.glob("*.txt"):
            file.write_text(body, encoding="utf-8-sig")
            print(f"  bosaltildi {rel}/{file.name}")


def doldur(group: str) -> None:
    for rel in GROUPS[group]:
        backup = OFF / (rel + "__dolu")
        if backup.exists():
            shutil.rmtree(ROOT / rel, ignore_errors=True)
            shutil.move(str(backup), str(ROOT / rel))
            print(f"  geri alindi {rel}")


def _move(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
    shutil.move(str(src), str(dst))
    return True


def kapat(group: str) -> None:
    moved = 0
    for rel in GROUPS[group]:
        if _move(ROOT / rel, OFF / rel):
            moved += 1
            print(f"  kapatildi  {rel}")
    print(f"[{group}] {moved} oge kapatildi")


def ac(group: str) -> None:
    moved = 0
    for rel in GROUPS[group]:
        if _move(OFF / rel, ROOT / rel):
            moved += 1
            print(f"  acildi     {rel}")
    print(f"[{group}] {moved} oge acildi")


def durum() -> None:
    for name, items in GROUPS.items():
        off = sum(1 for rel in items if (OFF / rel).exists())
        on = sum(1 for rel in items if (ROOT / rel).exists())
        state = "KAPALI" if off and not on else ("acik" if on and not off else "karisik")
        print(f"  {name:12s} {state:8s} (acik {on}, kapali {off})")


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] == "durum":
        durum()
        return 0
    cmd = args[0]
    if cmd == "dinsiz":
        dinsiz()
        return 0
    if cmd == "dinli":
        dinli()
        return 0
    if cmd not in ("ac", "kapat", "bosalt", "doldur"):
        print(__doc__)
        return 2
    names = list(GROUPS) if len(args) > 1 and args[1] == "hepsi" else args[1:]
    fn = {"ac": ac, "kapat": kapat, "bosalt": bosalt, "doldur": doldur}[cmd]
    for name in names:
        if name not in GROUPS:
            print(f"bilinmeyen grup '{name}'. Gruplar: {', '.join(GROUPS)}")
            return 2
        if cmd in ("bosalt", "doldur") and name not in EMPTY_BODY:
            print(f"'{name}' bosaltilamaz (vanilla ezmesi degil); 'kapat' kullan")
            return 2
        fn(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
