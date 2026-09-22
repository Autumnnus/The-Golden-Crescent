"""Transfer the final USA capital state to a neutral Potomac city district."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-usa-dc-catalog.json"
TARGET = Path(__file__).with_name("card16.json")
COUNTRIES = {"VDC": {"name": "Potomac Civic District", "name_tr": "Potomac Kent Bölgesi", "color": [135, 135, 135], "country_type": "recognized", "tier": "city_state", "cultures": ["yankee"], "religion": "protestant", "capital": "STATE_DISTRICT_OF_COLUMBIA"}, "USA": {"name": "Residual United States Jurisdiction", "name_tr": "Geçici ABD Yetki Alanı", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["yankee"], "religion": "protestant", "capital": "STATE_ALABAMA", "companies": {"mode": "replace", "add": [], "remove": []}}}
def main() -> None:
 subprocess.run([sys.executable,"scripts/tools.py","atlas","catalog","--region","USA","--out",str(CATALOG)],cwd=ROOT,check=True)
 state=next(s for s in json.loads(CATALOG.read_text())["states"] if s["id"]=="STATE_DISTRICT_OF_COLUMBIA")
 parts=[]
 for entry in state["owners"]:
  if entry["tag"]!="USA": raise RuntimeError("District ownership changed")
  parts.append({"owner":"VDC","provinces":["x" + p[1:].upper() for p in entry["provinces"]]})
 card={"version":2,"title":"Kart 5E — Potomac Kent Bölgesi","description":"ABD sonrası son federal başkent alanı, hiçbir geniş kıta devleti yaratmadan küçük Potomac kent yönetimine geçer.","countries":COUNTRIES,"states":{"STATE_DISTRICT_OF_COLUMBIA":{"split":parts,"pops":"drop","buildings":"drop"}}, "diplomacy":{"mode":"inherit","reset_countries":["USA"]}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+"\n")
 print(f"wrote {TARGET.relative_to(ROOT)} (2 countries, 1 state records)")
if __name__=="__main__": main()
