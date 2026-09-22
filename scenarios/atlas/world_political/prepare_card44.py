"""Distribute Portugal's non-overlapping temporary holdings to local owners."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card44.json')
TARGETS={
 'STATE_ALENTEJO':'VAN','STATE_AZORES':'VAN','STATE_CAPE_VERDE':'VAN',
 'STATE_GUINEA':'KBU','STATE_LOURENCO_MARQUES':'GZA','STATE_MADEIRA':'VAN','STATE_MOCAMBIQUE':'MRV',
 'STATE_NORTH_ANGOLA':'KON','STATE_SENEGAL':'CAY','STATE_SOUTH_ANGOLA':'HRO','STATE_SOUTH_CAMEROON':'DLA','STATE_ZAMBEZIA':'MSK',
}
def main():
 p=ROOT/'build/political-card44-por-catalog.json'
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','POR','--out',str(p)],cwd=ROOT,check=True)
 by={s['id']:s for s in json.loads(p.read_text())['states']};out={}
 for sid,target in TARGETS.items():
  st=by[sid]
  if not any(o['tag']=='POR' for o in st['owners']):raise RuntimeError(f'{sid}: POR share missing')
  if sid=='STATE_SENEGAL' and not any(o['tag']=='FRA' for o in st['owners']):raise RuntimeError(f'{sid}: FRA share missing')
  merged={}
  for o in st['owners']:
   owner=target if o['tag']=='POR' or (sid=='STATE_SENEGAL' and o['tag'] in {'FRA','SIL'}) or (sid=='STATE_SOUTH_CAMEROON' and o['tag']=='SIL') else o['tag']
   merged.setdefault(owner,[]).extend('x'+h[1:].upper() for h in dict.fromkeys(o['provinces']))
  out[sid]={'split':[{'owner':owner,'provinces':list(dict.fromkeys(provinces))} for owner,provinces in merged.items()],'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 1M/4D — Portekiz geçici paylarının yerelleştirilmesi',"description": "POR’un çakışmayan geçici payları ve Senegal’deki Fransız doğrudan payı yerel veya yazılı denizci sahiplerine döner: Atlantik adaları/Alentejo Endülüs’e, Guangdong Yue’ye; Afrika payları state içindeki Kabu, Gaza, Maravi, Kongo, Cayor, Herero, Duala ve Makua temsilcilerine gider. Bombay, Gujarat ve Sunda aynı state’i kullanan kartlarda ayrı birleşir.",'countries':{},'states':out}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
