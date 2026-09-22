"""Freeze every remaining local political border as an explicit Atlas card.

Earlier political cards deliberately changed the large alternate-history
boundaries.  The remaining local polities were inherited from the installed
world, which made the merged preview valid but left their final political
choice implicit.  This generator resolves that gap: it composes every earlier
card, reads the verified final province ownership, then writes every uncovered
state as an explicit map-only split.  It also publishes the human-readable
decision ledger used by the scenario documents.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "card63.json"
PRIOR = ROOT / "build/world-political/pre-card63-preview.json"
CATALOG = ROOT / "build/world-political/pre-card63-catalog.json"
LEDGER = ROOT / "docs/scenario/SIYASI_STATE_KARAR_DEFTERI.md"
NORMALIZED_OWNER = {
    "STATE_ALASKA": "ALK",
    "STATE_EASTERN_HIMALAYAS": "TIB",
    "STATE_INNER_MOROCCO": "MOR",
    "STATE_MAURITANIA": "OUA",
    "STATE_SOMALILAND": "MJT",
    "STATE_TAHITI": "PLY",
    "STATE_TANGANYIKA": "NYM",
    "STATE_TRIPOLI": "TRI",
}


def load_prior_cards() -> list[tuple[str, dict]]:
    return [
        (path.name, json.loads(path.read_text()))
        for path in sorted(HERE.glob("card*.json"))
        if path.name != OUT.name
    ]


def write_prior_preview(cards: list[tuple[str, dict]]) -> set[str]:
    countries: dict[str, dict] = {}
    states: dict[str, dict] = {}
    subject_types: dict[str, dict] = {}
    diplomacy_rows: dict[str, list] = {"subjects": [], "relations": [], "pacts": [], "remove": []}
    resets: list[str] = []
    for filename, card in cards:
        for key, spec in card.get("subject_types", {}).items():
            if key in subject_types and subject_types[key] != spec:
                raise RuntimeError(f"conflicting subject type {key} in {filename}")
            subject_types[key] = spec
        for field, rows in diplomacy_rows.items():
            for row in card.get("diplomacy", {}).get(field, []):
                if row not in rows:
                    rows.append(row)
        resets.extend(card.get("diplomacy", {}).get("reset_countries", []))
        for tag, spec in card["countries"].items():
            if tag in countries and tag not in resets:
                raise RuntimeError(f"duplicate country definition {tag} in {filename}")
            countries[tag] = spec
        for state, spec in card["states"].items():
            if state in states:
                raise RuntimeError(f"duplicate state definition {state} in {filename}")
            states[state] = spec
    resets = list(dict.fromkeys(resets))
    referenced = {
        part["owner"]
        for spec in states.values()
        for part in (spec.get("split") or ([{"owner": spec["owner"]}] if "owner" in spec else []))
    }
    for tag in resets:
        if tag in countries and tag not in referenced:
            del countries[tag]
    prior = {
        "version": 2,
        "title": "Dünya Siyasi Önizlemesi — Kart 63 Öncesi",
        "description": "Kart 63 için doğrulanmış kalan yerel sahiplik girdisi; etkin dünya değildir.",
        "countries": countries,
        "states": states,
        **({"subject_types": subject_types} if subject_types else {}),
        "diplomacy": {"mode": "inherit", "reset_countries": resets, **diplomacy_rows},
    }
    PRIOR.parent.mkdir(parents=True, exist_ok=True)
    PRIOR.write_text(json.dumps(prior, ensure_ascii=False, indent=2) + "\n")
    return set(states)


def owner_text(state: dict, countries: dict[str, dict]) -> str:
    return "; ".join(
        f"`{owner['tag']}` — {countries.get(owner['tag'], {}).get('name', owner['tag'])} "
        f"({len(owner['provinces'])} province)"
        for owner in state["owners"]
    )


def write_document(residual: list[dict], countries: dict[str, dict], normalizations: list[dict]) -> None:
    groups: dict[str, list[dict]] = defaultdict(list)
    for state in residual:
        groups[state["region"]].append(state)
    lines = [
        "# Kesin siyasi state karar defteri",
        "",
        "Bu belge 1836 siyasi önizlemesinde daha büyük kartlar tarafından doğrudan",
        "yeniden çizilmeyen yerel sınırların **kesin** kaydıdır. Her satırdaki",
        "province sahipliği `card63.json`da açık Atlas `split` kaydı olarak üretilir;",
        "buradaki isimler doğrulanmış kurulu oyun/önizleme ülke tanımlarından gelir.",
        "Bir liman hakkı, kültürel etki veya tarihî iddia ikinci bir doğrudan sahip",
        "oluşturmaz. Bu defter siyasi katmanı kapatır; nüfus, ekonomi, hukuk ve",
        "teknoloji verisi içermez.",
        "",
        f"**Kapsam:** {len(residual)} yerel state; bunlar ile diğer doğrudan kartlar birlikte 675/675 kara state'i kapsar.",
        "",
    ]
    for region in sorted(groups):
        lines.extend([f"## {region}", "", "| State | Kesin doğrudan sahiplik |", "|---|---|"])
        for state in sorted(groups[region], key=lambda row: row["id"]):
            lines.append(f"| `{state['id']}` | {owner_text(state, countries)} |")
        lines.append("")
    lines.extend([
        "## Eski çakışmaların tekleştirilmesi",
        "",
        "Kurulu başlangıç verisinde aşağıdaki province'ler birden fazla yerel",
        "sahibe yazılmıştı. Bunlar ortak egemenlik değildir. Kart 63, her state'in",
        "ana yerel yöneticisini seçerek çakışmayı kaldırır; diğer aktörler yalnız",
        "kendilerine özgü province'lerini korur.",
        "",
        "| State | Kesin sahip | Çakışan eski iddia sahipleri | Province |",
        "|---|---|---|---:|",
    ])
    for row in normalizations:
        winner = f"`{row['winner']}` — {countries.get(row['winner'], {}).get('name', row['winner'])}"
        losers = ", ".join(f"`{tag}`" for tag in row["losers"]) or "aynı sahibin yinelenmiş kaydı"
        lines.append(f"| `{row['state']}` | {winner} | {losers} | {row['provinces']} |")
    lines.append("")
    lines.extend([
        "## Uygulama kuralı",
        "",
        "Bir satırın değişmesi ilgili Atlas kartı, bu defter, komşu siyasi belge ve",
        "diplomasi kaydı birlikte güncellenmeden yapılamaz. Böylece mevcut yerel",
        "devletlerin korunması varsayılan vanilla kalıntısı değil, açık senaryo kararıdır.",
        "",
    ])
    LEDGER.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    cards = load_prior_cards()
    covered = write_prior_preview(cards)
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "world", "--scenario", str(PRIOR), "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    catalog = json.loads(CATALOG.read_text())
    residual = [state for state in catalog["states"] if state["id"] not in covered]
    states = {}
    normalizations = []
    for state in residual:
        claims: dict[str, list[str]] = defaultdict(list)
        for owner in state["owners"]:
            for province in owner["provinces"]:
                claims["x" + province[1:].upper()].append(owner["tag"])
        preferred = NORMALIZED_OWNER.get(state["id"])
        assigned: dict[str, list[str]] = defaultdict(list)
        normalized_losers: set[str] = set()
        normalized_count = 0
        for province, owners in claims.items():
            winner = preferred if preferred in owners else owners[0]
            assigned[winner].append("x" + province[1:].upper())
            if len(owners) > 1:
                normalized_count += 1
                normalized_losers.update(tag for tag in owners if tag != winner)
        geometry = {"x" + province[1:].upper() for province in state["provinces"]}
        if set(claims) != geometry:
            raise RuntimeError(f"{state['id']} owner claims do not match state geometry")
        if normalized_count:
            normalizations.append({
                "state": state["id"], "winner": preferred or next(iter(assigned)),
                "losers": sorted(normalized_losers), "provinces": normalized_count,
            })
        parts = [{"owner": tag, "provinces": provinces} for tag, provinces in assigned.items() if provinces]
        if not parts:
            raise RuntimeError(f"{state['id']} has no verified direct owner")
        states[state["id"]] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {
        "version": 2,
        "title": "Kart 6B — Dünya yerel sınır kilidi",
        "description": "Büyük alternatif tarih kartlarının dışında kalan bütün yerel state/province sınırlarını doğrulanmış sahipleriyle açıkça sabitler. Varsayılan vanilla mirası bırakmaz; ekonomi ve nüfus verisi taşımaz.",
        "countries": {},
        "states": states,
        "diplomacy": {"mode": "inherit"},
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    write_document(residual, catalog["countries"], normalizations)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(states)} states) and {LEDGER.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
