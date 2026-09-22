"""Resolve the remaining Prussian shares without re-creating a unified Prussia."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('card49.json')
TARGETS={
 'STATE_BRUNSWICK':'BRA',
 'STATE_EAST_PRUSSIA':'VPD',
 'STATE_WEST_PRUSSIA':'VPL',
 'STATE_LOWER_SILESIA':'VBO',
 'STATE_UPPER_SILESIA':'VBO',
}
COUNTRIES={'VPD':{'name':'Baltic Prussian Duchy','name_tr':'Baltık Prusya Dükalığı','color':[102,130,151],'country_type':'recognized','tier':'principality','cultures':['north_german'],'religion':'protestant','capital':'STATE_EAST_PRUSSIA'}}
def main():
 p=ROOT/'build/political-pru-closure-catalog.json'
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','PRU','--out',str(p)],cwd=ROOT,check=True)
 by={s['id']:s for s in json.loads(p.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  merged={};order=[];found=False
  for row in by[sid]['owners']:
   found |= row['tag']=='PRU'; owner=target if row['tag']=='PRU' else row['tag']
   if owner not in merged: merged[owner]=[];order.append(owner)
   merged[owner].extend(row['provinces'])
  if not found: raise RuntimeError(f'{sid}: PRU share missing')
  states[sid]={'split':[{'owner':x,'provinces':merged[x]} for x in order],'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 1N — Prusya Kalıntısının Kapanışı','description':'Dünya siyasi iskeleti: Prusya birleşmesi gerçekleşmez. Batı Prusya Lehistan-Litvanya Baltık koridoruna, Doğu Prusya bağımsız Baltık Prusya Dükalığına, Silezya Bohemya’ya ve Brunswick’teki küçük pay yerel Brunswick yönetimine gider. PRU miras diplomasisi temizlenir.','countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['PRU']}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
