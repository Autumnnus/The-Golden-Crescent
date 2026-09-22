"""Replace Spanish Philippines with the atlas' three local political areas."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('card38.json')
TARGETS={'STATE_LUZON':'VTD','STATE_VISAYAS':'VVS','STATE_MINDANAO':'SUL','STATE_WEST_MICRONESIA':'MCR'}
COUNTRIES={
 'VTD': {'name':'Tondo League','name_tr':'Tondo Birliği','color':[161,81,62],'country_type':'recognized','tier':'principality','cultures':['tagalog'],'religion':'catholic','capital':'STATE_LUZON'},
 'VVS': {'name':'Visayan Port League','name_tr':'Visaya Liman Birliği','color':[58,122,160],'country_type':'recognized','tier':'principality','cultures':['visayan'],'religion':'catholic','capital':'STATE_VISAYAS'},
}
def main():
 p=ROOT/'build/political-card38-catalog.json'
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','PHI','--out',str(p)],cwd=ROOT,check=True)
 by={s['id']:s for s in json.loads(p.read_text())['states']}; states={}
 for sid,target in TARGETS.items():
  s=by[sid]
  if not any(o['tag']=='PHI' for o in s['owners']): raise RuntimeError(f'{sid}: PHI share missing')
  parts=[]
  for o in s['owners']:
   # Vanilla assigns xE90347 to both decentralized MND and MGD. The state
   # history itself only claims it for MGD, so retain MGD and drop MND's
   # duplicate copy; Atlas correctly rejects double province assignment.
   provinces=['x'+h[1:].upper() for h in dict.fromkeys(o['provinces'])]
   if sid=='STATE_MINDANAO' and o['tag']=='MND': provinces=[h for h in provinces if h!='xE90347']
   parts.append({'owner':target if o['tag']=='PHI' else o['tag'],'provinces':provinces})
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 3C — Filipinler yerel üçlüsü','description':('İspanyol Filipinler yerine Tondo (Luzon), Visaya liman birliği (orta adalar) ve Sulu (güney) yerel siyasi alanları. Batı Mikronezya’daki PHI payı yerel MCR’ye döner; mevcut Mindanao yerel sahipleri korunur.'),'countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['PHI']}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
