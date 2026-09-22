"""Remove the final Spanish placeholder shares after Iberia's borders are settled."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card43.json')
TARGETS={'STATE_AL_RIF':'MOR','STATE_CANARY_ISLANDS':'VAN'}
def main():
 p=ROOT/'build/political-card43-spa-catalog.json'
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','SPA','--out',str(p)],cwd=ROOT,check=True)
 by={s['id']:s for s in json.loads(p.read_text())['states']}; states={}
 for sid,target in TARGETS.items():
  st=by[sid]
  if not any(o['tag']=='SPA' for o in st['owners']):raise RuntimeError(f'{sid}: SPA share missing')
  # Rif's vanilla history duplicates two Spanish port/farm provinces under MOR.
  # Coalesce equal final owners so the political replacement has one owner per province.
  merged={}
  for o in st['owners']:
   owner=target if o['tag']=='SPA' else o['tag']
   merged.setdefault(owner,[]).extend('x'+h[1:].upper() for h in dict.fromkeys(o['provinces']))
  states[sid]={'split':[{'owner':owner,'provinces':list(dict.fromkeys(provinces))} for owner,provinces in merged.items()],'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 1L — İspanyol geçici sahibinin tasfiyesi','description':'Rif eski SPA payı Fas’a, Kanarya Adaları Endülüs’e geçer. İberya’da birleşik İspanya bulunmadığı için geçici SPA ülke tanımı ve devralınan diplomasi temizlenir.','countries':{},'states':states,'diplomacy':{'mode':'inherit','reset_countries':['SPA']}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
