"""Audit the M1b candidate: literacy inputs reach target - school boost and nothing else moves."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIELDS = ("technology", "laws", "institutions")
TOLERANCE = 0.006


def without_literacy(spec: dict) -> dict:
    spec = json.loads(json.dumps(spec))
    for share in spec["population"]["by_owner"].values():
        share.pop("literacy")
    spec.pop("industry", None)
    return spec


def main() -> None:
    build = ROOT / "build/mechanics"
    source = yaml.safe_load((build / "m1b2-source.yml").read_text())
    candidate = yaml.safe_load((build / "m1b-candidate.yml").read_text())
    prior = json.loads((build / "m1b2-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/m1b-candidate/scenario-report.json").read_text())
    targets = yaml.safe_load((HERE / "targets.yml").read_text())["countries"]
    m1 = yaml.safe_load((HERE.parent / "mechanics_m1_institutions/plan.yml").read_text())["countries"]
    m1b = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    audit = json.loads((build / "m1b-audit.json").read_text())
    fixes, inputs = audit["method_fixes"], audit["inputs"]
    fixed = {tuple(row.split(":")[0].split("/")[:2]) for row in fixes}
    errors = []
    for field in ("version", "subject_types", "diplomacy"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    lit = defaultdict(lambda: [0, 0.0])
    for state, old in source["states"].items():
        new = candidate["states"][state]
        if without_literacy(old) != without_literacy(new):
            errors.append(f"{state}: non-literacy state fields changed")
        old_ind, new_ind = old.get("industry") or {}, new.get("industry") or {}
        for tag in set((old_ind.get("by_owner") or {})) | set((new_ind.get("by_owner") or {})):
            if (old_ind.get("by_owner") or {}).get(tag) != (new_ind.get("by_owner") or {}).get(tag) and (state, tag) not in fixed:
                errors.append(f"{state}/{tag}: unplanned industry change")
        if {k: v for k, v in old_ind.items() if k != "by_owner"} != {k: v for k, v in new_ind.items() if k != "by_owner"}:
            errors.append(f"{state}: industry scale changed")
        for tag, share in new["population"]["by_owner"].items():
            if tag not in old["population"]["by_owner"]:
                continue  # moved by a later political transfer (political_p2_corrections)
            lit[tag][0] += share["total"]
            lit[tag][1] += share["total"] * share["literacy"]
    for tag in set(source["countries"]) | set(candidate["countries"]):
        old, new = source["countries"].get(tag, {}), candidate["countries"].get(tag, {})
        keep = lambda d: {k: v for k, v in d.items() if k not in FIELDS}
        if keep(old) != keep(new):
            errors.append(f"{tag}: non-institutional country fields changed")
        if tag not in m1 and tag not in m1b and old != new:
            errors.append(f"{tag}: unplanned country changed")
    for tag, goal in targets.items():
        reached = lit[tag][1] / lit[tag][0]
        if abs(reached - inputs[tag]["input"]) > TOLERANCE or inputs[tag]["target"] != goal["target"]:
            errors.append(f"{tag}: literacy input {reached:.3f} vs {inputs[tag]['input']}")
        country, before = report["countries"][tag], prior["countries"][tag]
        if country["population"] != before["population"]:
            errors.append(f"{tag}: population changed")
        if country["building_levels"] != before["building_levels"]:
            errors.append(f"{tag}: building levels changed")
    for tag, row in m1.items():
        if set(report["countries"][tag]["laws"]) != set(row["laws"]):
            errors.append(f"{tag}: M1 laws differ {sorted(set(report['countries'][tag]['laws']) ^ set(row['laws']))}")
        if not set(row["add_technologies"]) <= set(report["countries"][tag]["technologies"]):
            errors.append(f"{tag}: M1 technologies missing")
    for tag, row in m1b.items():
        country = report["countries"][tag]
        if not set(row["new_laws"]) <= set(country["laws"]):
            errors.append(f"{tag}: M1b laws missing {sorted(set(row['new_laws']) - set(country['laws']))}")
        if not set(row["add_technologies"]) <= set(country["technologies"]):
            errors.append(f"{tag}: M1b technologies missing")
        if not set(prior["countries"][tag]["technologies"]) <= set(country["technologies"]):
            errors.append(f"{tag}: technologies lost")
    for tag, country in prior["countries"].items():
        if tag not in m1 and tag not in m1b and report["countries"][tag]["laws"] != country["laws"]:
            errors.append(f"{tag}: non-target laws changed")
    if report["validation"] != "passed" or report["diplomacy"] != prior["diplomacy"]:
        errors.append("report validation or diplomacy differs")
    bands = defaultdict(lambda: [0, 0.0, 0.0])
    for tag, goal in targets.items():
        bands[goal["band"]][0] += lit[tag][0]
        bands[goal["band"]][1] += lit[tag][1]
        bands[goal["band"]][2] += lit[tag][0] * goal["target"]
    result = {"passed": not errors, "countries": len(targets), "m1": len(m1), "m1b": len(m1b),
              "method_fixes": len(fixes),
              "band_literacy": {band: {"input": round(v[1] / v[0], 3), "expected": round(v[2] / v[0], 3)}
                                for band, v in sorted(bands.items())}, "errors": errors}
    (build / "m1b-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/mechanics/m1b-verification.json (passed={result['passed']}) {result['band_literacy']}")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
