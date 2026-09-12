#!/usr/bin/env python3
"""Automated countdown to activate Codex and press Enter.

Usage:
    python3 tools/auto_continue_codex.py                    # Defaults to 06:35:15
    python3 tools/auto_continue_codex.py --seconds 10       # Test mode: triggers in 10 seconds
    python3 tools/auto_continue_codex.py --time 06:35:30    # Custom target time (HH:MM:SS)
"""

import argparse
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "codex_automation.log"


def log(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


def press_enter_in_codex():
    log("Codex (ChatGPT) uygulaması öne getiriliyor...")
    subprocess.run(
        ["osascript", "-e", 'tell application id "com.openai.codex" to activate'],
        check=False,
    )
    time.sleep(1.0)

    log("Enter (Return) tuşuna basılıyor...")
    subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to key code 36'],
        check=False,
    )
    time.sleep(0.5)

    log("Sistem bildirimi gönderiliyor...")
    notif_script = (
        'display notification "Codex kutusunda Enter tuşuna basıldı ve mesaj gönderildi!" '
        'with title "Codex Otomasyonu" sound name "Glass"'
    )
    subprocess.run(["osascript", "-e", notif_script], check=False)
    log("BAŞARILI: Enter tuşu gönderildi.")


def parse_args():
    parser = argparse.ArgumentParser(description="Codex otomatik Enter basma aracı")
    parser.add_argument(
        "--seconds",
        type=int,
        help="Kaç saniye sonra tetikleneceği (test için, örn: --seconds 10)",
    )
    parser.add_argument(
        "--time",
        type=str,
        default="06:35:15",
        help="Hedef saat HH:MM:SS formatında (varsayılan: 06:35:15)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    now = datetime.datetime.now()

    if args.seconds is not None:
        target = now + datetime.timedelta(seconds=args.seconds)
        log(f"=== TEST MODU BAŞLATILDI ({args.seconds} saniye sonra) ===")
    else:
        try:
            h, m, s = [int(x) for x in args.time.split(":")]
        except ValueError:
            print(f"Hatalı saat formatı: {args.time}. Örnek format: 06:35:15")
            sys.exit(1)

        target = now.replace(hour=h, minute=m, second=s, microsecond=0)
        if target <= now:
            target += datetime.timedelta(days=1)
        log("=== Otomasyon Başlatıldı ===")

    log(f"Hedef an: {target.strftime('%Y-%m-%d %H:%M:%S')}")

    while True:
        now = datetime.datetime.now()
        remaining = (target - now).total_seconds()
        if remaining <= 0:
            break

        hours, rem = divmod(int(remaining), 3600)
        minutes, seconds = divmod(rem, 60)

        # In short/test mode, show every second
        if remaining <= 15:
            print(f"\rKalan süre: {int(remaining)} saniye...  ", end="", flush=True)
            time.sleep(1)
        elif remaining <= 60:
            log(f"Kalan süre: {int(remaining)} saniye")
            time.sleep(5)
        elif remaining <= 900:
            log(f"Kalan süre: {minutes:02d}d {seconds:02d}sn")
            time.sleep(60)
        else:
            log(f"Kalan süre: {hours:02d}s {minutes:02d}d {seconds:02d}sn")
            time.sleep(900)

    print()
    log("Süre doldu! Codex öne getiriliyor ve Enter basılıyor...")
    press_enter_in_codex()


if __name__ == "__main__":
    main()
