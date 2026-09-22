"""Verify the political diplomacy contract against the final Atlas report."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "build/world-political/final-political-report.json"
OUT = ROOT / "build/world-political/diplomacy-contract-audit.json"
EXPECTED_OVERLORDS = {
    "ADA": "RUM", "ALB": "RUM", "BOS": "RUM", "BUL": "RUM", "ERZ": "RUM", "TRB": "RUM", "VBU": "RUM",
    "HDJ": "EGY", "MOL": "VPL", "KAS": "MUG", "JAI": "MUG", "MEW": "MUG",
    "SHS": "BUR", "CAM": "DAI", "CHP": "SIA", "CMI": "SIA", "LUA": "SIA", "EZO": "JAP", "HAU": "SOK",
    "VNE": "VAN", "VSI": "VAN", "VPI": "VAN", "VMY": "VAN", "VFB": "MOR", "VNI": "VEL", "VVA": "VEL", "VNH": "NET",
}
EXPECTED_RELATIONS = {
    ("EGY", "ACE", 25), ("EGY", "SLW", 20), ("OMA", "JOH", 25), ("OMA", "SUL", 10), ("OMA", "MBS", 10),
    ("DEN", "SWE", 50), ("DEN", "NOR", 50), ("SWE", "NOR", 50), ("DEN", "HOL", 30), ("DEN", "SCH", 30), ("SIA", "DAI", -25),
    ("VEL", "VSC", 50), ("VEL", "VIR", 50), ("VSC", "VIR", 50),
    ("DEN", "VIN", 35), ("SWE", "VIN", 35), ("NOR", "VIN", 35), ("JAP", "RYU", 20), ("YUE", "RYU", 20),
}


def main() -> None:
    report = json.loads(REPORT.read_text())
    actual_overlords = report["diplomacy"]["overlords"]
    actual_relations = {
        (row["actor"], row["target"], row["value"])
        for row in report["diplomacy"]["relations"]
    }
    inherited = [row for row in report["diplomacy"]["pacts"] if row.get("source") == "inherited"]
    payload = {
        "title": "1836 siyasi diplomasi sözleşmesi denetimi",
        "expected_overlords": EXPECTED_OVERLORDS,
        "actual_overlords": actual_overlords,
        "missing_relations": sorted(EXPECTED_RELATIONS - actual_relations),
        "unexpected_relations": sorted(actual_relations - EXPECTED_RELATIONS),
        "inherited_pacts": inherited,
        "passed": actual_overlords == EXPECTED_OVERLORDS and actual_relations == EXPECTED_RELATIONS and not inherited,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={payload['passed']})")
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
