"""Resolve Colombia's interior without making a single replacement republic."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card53.json')
TARGETS={'STATE_ANTIOQUIA':'VSI','STATE_CAUCA':'VCQ','STATE_GUAVIARE':'VOR'}
COUNTRIES={
 'VSI':{'name':'New Ishbiliya','name_tr':'Yeni İşbiliye','color':[91,145,119],'country_type':'recognized','tier':'principality','cultures':['colombian'],'religion':'sunni','capital':'STATE_ANTIOQUIA'},
 'VCQ':{'name':'Cauca Highland Council','name_tr':'Cauca Yüksekova Meclisi','color':[139,119,84],'country_type':'recognized','tier':'principality','cultures':['muisca'],'religion':'catholic','capital':'STATE_CAUCA'},
 'VOR':{'name':'Orinoco River Council','name_tr':'Orinoco Nehir Meclisi','color':[94,133,150],'country_type':'recognized','tier':'principality','cultures':['muisca'],'religion':'animist','capital':'STATE_GUAVIARE'},
}
def main():
 p=ROOT/'build/political-clm-closure-catalog.json';subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','CLM','--out',str(p)],cwd=ROOT,check=True)
 by={x['id']:x for x in json.loads(p.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  merged={};order=[];found=False
  for row in by[sid]['owners']:
   found |= row['tag']=='CLM';tag=target if row['tag']=='CLM' else row['tag']
   if tag not in merged:merged[tag]=[];order.append(tag)
   merged[tag].extend(row['provinces'])
  if not found:raise RuntimeError(f'{sid}: CLM share missing')
  states[sid]={'split':[{'owner':t,'provinces':merged[t]} for t in order],'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 5X — Kolombiya İçinin Yerel Ayrışması','description':'Dünya siyasi iskeleti: Antioquia Yeni İşbiliye kıyı–nehir çekirdeğine, Cauca ve Guaviare ayrı yerel yüksekova/nehir meclislerine geçer; Amazonas’taki CLM payı ilgili Yukarı Amazon kartında mevcut yerel sahibine döner. CLM miras diplomasisi temizlenir.','countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['CLM']}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
