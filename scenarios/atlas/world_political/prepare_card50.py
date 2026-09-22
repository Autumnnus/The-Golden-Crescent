"""Resolve Galicia through Kraków's city polity and the Commonwealth's eastern district."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card50.json')
TARGETS={'STATE_WEST_GALICIA':'KRA','STATE_EAST_GALICIA':'VPL'}
def main():
 p=ROOT/'build/political-aus-galicia-catalog.json'
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','AUS','--out',str(p)],cwd=ROOT,check=True)
 by={s['id']:s for s in json.loads(p.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  merged={};order=[];found=False
  for row in by[sid]['owners']:
   found |= row['tag']=='AUS';tag=target if row['tag']=='AUS' else row['tag']
   if tag not in merged: merged[tag]=[];order.append(tag)
   merged[tag].extend(row['provinces'])
  if not found:raise RuntimeError(f'{sid}: AUS share missing')
  states[sid]={'split':[{'owner':t,'provinces':merged[t]} for t in order],'pops':'drop','buildings':'drop'}
 card={'version':1,'title':'Kart 1O — Kraków ve Galiçya','description':'Dünya siyasi iskeleti: Batı Galiçya Kraków şehir devleti etrafında, Doğu Galiçya Lehistan-Litvanya’nın çok dilli doğu kuşağında kalır. Avusturya kişisel birliği veya Galiçya yönetimi başlangıçta yoktur.','countries':{},'states':states}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
