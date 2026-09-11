#!/usr/bin/env python
"""Read a Victoria 3 minidump and say what actually crashed.

The logs do not name the cause of a load crash. The minidump does. This is the
tool that found the decentralized-buildings crash: the exception was not a null
dereference but a *write* to a valid array base at a fixed offset — that is,
valid data written somewhere that cannot hold it.

    python tools/crashinfo.py                 newest crash under Documents
    python tools/crashinfo.py <path.dmp>      a specific dump
    python tools/crashinfo.py --list          list the crash folders

Read the output in this order:
  1. ExceptionCode 0xC0000005 is an access violation.
  2. operation: `write` narrows the cause to something the mod *added*;
     `read` usually means something the mod *removed*.
  3. rva is the crash site inside victoria3.exe. The same rva across runs means
     the same bug, however different the symptoms look.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

CRASH_ROOT = (Path.home() / "OneDrive" / "Documents" / "Paradox Interactive"
              / "Victoria 3" / "crashes")
CRASH_ROOT_ALT = (Path.home() / "Documents" / "Paradox Interactive"
                  / "Victoria 3" / "crashes")

MDMP = 0x504D444D
STREAM_THREAD_LIST = 3
STREAM_MODULE_LIST = 4
STREAM_MEMORY_LIST = 5
STREAM_EXCEPTION = 6
STREAM_SYSTEM_INFO = 7

EXCEPTION_NAMES = {
    0xC0000005: "ACCESS_VIOLATION",
    0xC000001D: "ILLEGAL_INSTRUCTION",
    0xC0000094: "INTEGER_DIVIDE_BY_ZERO",
    0xC0000095: "INTEGER_OVERFLOW",
    0xC00000FD: "STACK_OVERFLOW",
    0xC0000374: "HEAP_CORRUPTION",
    0xE06D7363: "C++ EXCEPTION (thrown, not a memory fault)",
}

ACCESS_KIND = {0: "read", 1: "write", 8: "execute (DEP)"}

# Offsets of the general purpose registers inside an AMD64 CONTEXT record.
X64_GPR = [
    ("rax", 0x78), ("rcx", 0x80), ("rdx", 0x88), ("rbx", 0x90),
    ("rsp", 0x98), ("rbp", 0xA0), ("rsi", 0xA8), ("rdi", 0xB0),
    ("r8", 0xB8), ("r9", 0xC0), ("r10", 0xC8), ("r11", 0xD0),
    ("r12", 0xD8), ("r13", 0xE0), ("r14", 0xE8), ("r15", 0xF0),
    ("rip", 0xF8),
]


class Dump:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        sig, _ver, n_streams, dir_rva = struct.unpack_from("<IIII", self.data, 0)
        if sig != MDMP:
            raise SystemExit(f"{path} is not a minidump (bad signature)")
        self.streams: dict = {}
        for i in range(n_streams):
            stype, size, rva = struct.unpack_from("<III", self.data, dir_rva + i * 12)
            self.streams[stype] = (size, rva)

    def string(self, rva: int) -> str:
        (length,) = struct.unpack_from("<I", self.data, rva)
        return self.data[rva + 4:rva + 4 + length].decode("utf-16-le", "replace")

    # -- streams ----------------------------------------------------------
    def exception(self):
        if STREAM_EXCEPTION not in self.streams:
            return None
        _, rva = self.streams[STREAM_EXCEPTION]
        thread_id, _pad = struct.unpack_from("<II", self.data, rva)
        base = rva + 8
        code, flags, _rec, address, n_params, _pad2 = struct.unpack_from(
            "<IIQQII", self.data, base)
        params = struct.unpack_from("<15Q", self.data, base + 32)[:n_params]
        ctx_size, ctx_rva = struct.unpack_from("<II", self.data, base + 32 + 15 * 8)
        return {
            "thread_id": thread_id, "code": code, "flags": flags,
            "address": address, "params": list(params),
            "context": (ctx_size, ctx_rva),
        }

    def modules(self) -> list:
        if STREAM_MODULE_LIST not in self.streams:
            return []
        _, rva = self.streams[STREAM_MODULE_LIST]
        (count,) = struct.unpack_from("<I", self.data, rva)
        out = []
        entry = rva + 4
        for _ in range(count):
            base, size, _cksum, _stamp, name_rva = struct.unpack_from(
                "<QIIII", self.data, entry)
            out.append({"base": base, "size": size,
                        "name": self.string(name_rva)})
            entry += 108        # sizeof(MINIDUMP_MODULE)
        return out

    def registers(self, exc) -> dict:
        size, rva = exc["context"]
        if not size or rva + 0x100 > len(self.data):
            return {}
        return {name: struct.unpack_from("<Q", self.data, rva + off)[0]
                for name, off in X64_GPR}


def _module_for(modules: list, address: int):
    for m in modules:
        if m["base"] <= address < m["base"] + m["size"]:
            return m
    return None


def report(path: Path) -> int:
    d = Dump(path)
    exc = d.exception()
    mods = d.modules()
    print(f"dump      {path}")
    print(f"          {path.stat().st_size / 1024 / 1024:.1f} MB, "
          f"{len(mods)} modules loaded")
    if not exc:
        print("\nno exception stream: this dump did not record a fault")
        return 1

    code = exc["code"]
    name = EXCEPTION_NAMES.get(code, "unknown")
    print(f"\nexception 0x{code:08X}  {name}")
    print(f"address   0x{exc['address']:016X}")

    main = _module_for(mods, exc["address"])
    if main:
        rva = exc["address"] - main["base"]
        print(f"module    {Path(main['name']).name}  base=0x{main['base']:016X}")
        print(f"rva       0x{rva:X}      <-- the same rva means the same bug")
    else:
        print("module    (crash address is not inside any loaded module)")

    if code == 0xC0000005 and len(exc["params"]) >= 2:
        kind = ACCESS_KIND.get(exc["params"][0], f"code {exc['params'][0]}")
        target = exc["params"][1]
        print(f"\noperation {kind}")
        print(f"target    0x{target:016X}")
        if target < 0x10000:
            print("          near-null: a pointer that was never set "
                  "(something the mod removed)")
        else:
            print("          a valid-looking address: data written past the end "
                  "of an array")
            print("          the engine allocated for. This is the shape of the "
                  "decentralized-")
            print("          buildings crash - check what the mod *added* for a "
                  "country type")
            print("          that vanilla never gives that content to.")

    regs = d.registers(exc)
    if regs:
        print("\nregisters")
        items = list(regs.items())
        for i in range(0, len(items), 4):
            print("  " + "  ".join(f"{k}=0x{v:016X}" for k, v in items[i:i + 4]))
        if code == 0xC0000005 and len(exc["params"]) >= 2:
            target = exc["params"][1]
            near = [(k, v) for k, v in regs.items()
                    if v and abs(target - v) < 0x100000 and k != "rip"]
            if near:
                print("\n  registers close to the faulting address (likely the "
                      "array base and index):")
                for k, v in sorted(near, key=lambda kv: abs(target - kv[1])):
                    print(f"    {k}=0x{v:016X}   offset {target - v:+d}")
    return 0


def find_dumps() -> list:
    roots = [r for r in (CRASH_ROOT, CRASH_ROOT_ALT) if r.is_dir()]
    dumps = [p for r in roots for p in r.rglob("*.dmp")]
    return sorted(dumps, key=lambda p: p.stat().st_mtime, reverse=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dump", nargs="?", help="path to a .dmp file")
    ap.add_argument("--list", action="store_true", help="list known crash dumps")
    args = ap.parse_args(argv)

    if args.list:
        dumps = find_dumps()
        if not dumps:
            print(f"no crash dumps under {CRASH_ROOT}")
            return 1
        for p in dumps:
            import datetime
            when = datetime.datetime.fromtimestamp(p.stat().st_mtime)
            print(f"{when:%Y-%m-%d %H:%M}  {p}")
        return 0

    if args.dump:
        path = Path(args.dump)
        if not path.exists():
            raise SystemExit(f"no such file: {path}")
    else:
        dumps = find_dumps()
        if not dumps:
            print(f"no crash dumps found under {CRASH_ROOT}")
            print("(that is good news: the game has not crashed)")
            return 0
        path = dumps[0]
        print(f"newest of {len(dumps)} dump(s)\n")
    return report(path)


if __name__ == "__main__":
    sys.exit(main())
