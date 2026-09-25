"""Verify the city-anchor candidate changes exactly the reviewed provinces."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def owner_map(world: dict) -> dict[tuple[str, str], str]:
    result = {}
    for state, spec in world["states"].items():
        for part in spec.get("split", []):
            for province in part["provinces"]:
                key = state, province
                if key in result:
                    raise AssertionError(f"duplicate province: {key}")
                result[key] = part["owner"]
    return result


def main() -> None:
    original = yaml.safe_load((ROOT / "build/city-anchors/source.yml").read_text())
    candidate = yaml.safe_load((ROOT / "build/city-anchors/candidate.yml").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    before, after = owner_map(original), owner_map(candidate)
    assert before.keys() == after.keys(), "province set changed"
    expected = {(m["state"], m["province"]): (m["from"], m["to"]) for m in plan["moves"]}
    actual = {key: (before[key], after[key]) for key in before if before[key] != after[key]}
    assert len(expected) == len(plan["moves"]) == 8, "duplicate planned province"
    assert actual == expected, f"unexpected ownership changes: {actual}"
    for move in plan["moves"]:
        spec = index["states"][move["state"]]
        assert move["province"] in spec["provinces"], move
        assert move["province"] in {spec[key] for key in ("city", "port", "farm", "mine", "wood")}, move
    assert original["countries"] == candidate["countries"]
    assert original["subject_types"] == candidate["subject_types"]
    assert original["diplomacy"] == candidate["diplomacy"]
    for state in original["states"]:
        a, b = original["states"][state], candidate["states"][state]
        assert a.keys() == b.keys(), state
        assert {k: v for k, v in a.items() if k != "split"} == {k: v for k, v in b.items() if k != "split"}, state
        if "split" in a:
            assert [p["owner"] for p in a["split"]] == [p["owner"] for p in b["split"]], state
            for left, right in zip(a["split"], b["split"]):
                assert {k: v for k, v in left.items() if k != "provinces"} == {k: v for k, v in right.items() if k != "provinces"}, state
    prior_report = json.loads((ROOT / "build/world-political/active-political-report.json").read_text())
    new_report = json.loads((ROOT / "build/scenarios/city-anchor-candidate/scenario-report.json").read_text())
    assert prior_report["diplomacy"] == new_report["diplomacy"]
    assert sum(s["population"] for s in prior_report["states"].values()) == sum(s["population"] for s in new_report["states"].values())
    assert all(s["population"] > 0 for s in new_report["states"].values())
    assert all(c["population"] > 0 for c in new_report["countries"].values())
    assert new_report["validation"] == "passed"
    print(f"passed: {len(actual)} hub province moves in {len(Counter(s for s, _ in actual))} states; population and diplomacy conserved")


if __name__ == "__main__":
    main()
