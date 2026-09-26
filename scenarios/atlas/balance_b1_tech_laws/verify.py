"""Audit the B1 candidate report against plan.yml, targets.yml and the tech gates of buildings and methods."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLKIT = Path(os.environ.get("VIC3_TOOLS_HOME") or json.loads(
    (ROOT / ".vic3-tools.local.json").read_text())["toolkit"])
if sys.version_info < (3, 10):
    runtime = TOOLKIT / ".venv/bin/python"
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
os.chdir(ROOT)
from vic3 import mechanics  # noqa: E402

# the protagonists lead, then the rest of the core, the Islamic middle, Europe's top, Europe
ORDER = [("ISF",), ("RUM",), ("EGY",), ("TBR", "VAN", "BSR"), ("MUG", "BGL", "KSG", "MOR"), ("VPL", "SWE"),
         ("FPA", "VEL"), ("HUN", "VMS")]


def main() -> None:
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    prior = json.loads((ROOT / "build/balance/b1-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/b1-candidate/scenario-report.json").read_text())
    data = mechanics.catalog()
    errors = []
    for tag, row in plan["countries"].items():
        techs = report["countries"][tag]["technologies"]
        if len(techs) != row["technologies_after"]:
            errors.append(f"{tag}: {len(techs)} technologies, plan {row['technologies_after']}")
        missing = set((row.get("laws") or {}).get("values", [])) - set(report["countries"][tag]["laws"])
        if missing:
            errors.append(f"{tag}: laws missing {sorted(missing)}")
    counts = {t: len(report["countries"][t]["technologies"]) for t in report["countries"]}
    for higher, lower in zip(ORDER, ORDER[1:]):
        if min(counts[t] for t in higher) < max(counts[t] for t in lower) or \
                (len(higher) == 1 and min(counts[t] for t in higher) == max(counts[t] for t in lower)):
            errors.append(f"technology order: {higher} {[counts[t] for t in higher]} not above {lower} {[counts[t] for t in lower]}")
    for tag, country in prior["countries"].items():
        new = report["countries"][tag]
        if any(new[k] != country[k] for k in ("population", "overlord")) or \
                new["military"]["battalions"] != country["military"]["battalions"] or new["military"]["ships"] != country["military"]["ships"]:
            errors.append(f"{tag}: population, overlord or military size changed")
        if tag not in plan["countries"] and (new["technologies"] != country["technologies"] or new["laws"] != country["laws"]):
            errors.append(f"{tag}: technology or laws changed outside the plan")
    removed = sum(1 for owners in plan["industry"].values() for b in owners.values() for v in b.values() if v == 0)
    before = sum(c["building_levels"] for c in prior["countries"].values())
    after = sum(c["building_levels"] for c in report["countries"].values())
    if before - after != plan["summary"]["levels_removed"]:
        errors.append(f"building levels {before} -> {after}, plan removes {plan['summary']['levels_removed']} ({removed} buildings)")
    gates = 0
    for state, st in report["states"].items():
        for tag, share in st["owners"].items():
            techs = set(report["countries"][tag]["technologies"])
            for b in share["buildings"]:
                need = set(data["buildings"].get(b["type"], {}).get("unlocking_technologies", []))
                bad = [p for p in b["production_methods"]
                       if not set(data["production_methods"].get(p, {}).get("unlocking_technologies", [])) <= techs]
                if (need and not need <= techs) or bad:
                    gates += 1
                    if tag in plan["countries"]:
                        errors.append(f"{state} {tag} {b['type']}: technology gate {sorted(need - techs)} {bad}")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"]]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    result = {"passed": not errors, **plan["summary"], "gate_violations_world": gates,
              "technologies": {t: counts[t] for group in ORDER for t in group}, "errors": errors}
    out = ROOT / "build/balance/b1-verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)} (passed={result['passed']}) {result['technologies']} gates={gates}")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
