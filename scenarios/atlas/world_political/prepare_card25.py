"""Break up direct Argentina shares, retaining Buenos Aires for the completion card."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-arg-catalog.json';TARGET=Path(__file__).with_name('card25.json')
def c(n,tr,col,cu,cap):return {'name':n,'name_tr':tr,'color':col,'country_type':'unrecognized','tier':'principality','cultures':cu,'religion':'animist','capital':cap}
COUNTRIES={'VGN':c('Guarani River League','Guaraní Nehir Birliği',[96,137,107],['guarani'],'STATE_CORRIENTES'),'VPT':c('Pampas Treaty Council','Pampa Antlaşma Meclisi',[138,123,87],['patagonian'],'STATE_LA_PAMPA'),'VTC':c('Tucuman Valley Council','Tucumán Vadi Meclisi',[136,110,123],['quechua'],'STATE_TUCUMAN')}
TARGETS={'STATE_CHACO':'VGN','STATE_CORRIENTES':'VGN','STATE_LA_PAMPA':'VPT','STATE_RIO_NEGRO':'VPT','STATE_SANTA_FE':'VGN','STATE_TUCUMAN':'VTC'}
def main():
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','ARG','--out',str(CATALOG)],cwd=ROOT,check=True);by={x['id']:x for x in json.loads(CATALOG.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  s=by[sid];local={p for e in s['owners'] if e['tag']!='ARG' for p in e['provinces']};parts=[]
  for e in s['owners']:
   ps=list(dict.fromkeys(p for p in e['provinces'] if not(e['tag']=='ARG' and p in local)))
   if ps:parts.append({'owner':target if e['tag']=='ARG' else e['tag'],'provinces':['x'+p[1:].upper() for p in ps]})
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 card={'version':1,'title':'Kart 5N — Guaraní, Pampa ve Tucumán','description':'Dünya siyasi iskeleti: Arjantinin doğrudan Chaco, Corrientes, Pampa, Rio Negro, Santa Fe ve Tucumán payları yerel nehri/otlak/vadi aktörlerine geçer. Buenos Aires kart26da ayrı kent yönetimine aktarılır.','countries':COUNTRIES,'states':states}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (3 countries, {len(states)} state records)')
if __name__=='__main__':main()
