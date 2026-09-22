"""Build the deliberately narrow Moroccan Brazil coast core."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-brz-catalog.json';TARGET=Path(__file__).with_name('card21.json')
COUNTRIES={'BRZ':{'name':'Residual Brazilian Interior','name_tr':'Geçici Brezilya İç Bölgesi','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['brazilian'],'religion':'catholic','capital':'STATE_GOIAS','companies':{'mode':'replace','add':[],'remove':[]}},'VFB':{'name':'Moroccan Brazil Coastal Charter','name_tr':'Fas Brezilyası Kıyı Şartı','color':[141,105,69],'country_type':'recognized','tier':'principality','cultures':['maghrebi'],'religion':'sunni','capital':'STATE_PERNAMBUCO'}}
TARGETS={'STATE_PERNAMBUCO':'VFB','STATE_BAHIA':'VFB','STATE_RIO_DE_JANEIRO':'VFB'}
def main():
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','BRZ','--out',str(CATALOG)],cwd=ROOT,check=True);by={x['id']:x for x in json.loads(CATALOG.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  s=by[sid];parts=[]
  for e in s['owners']:
   if e['tag']!='BRZ':raise RuntimeError(f'{sid} changed owner')
   parts.append({'owner':target,'provinces':['x'+p[1:].upper() for p in dict.fromkeys(e['provinces'])]})
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 card={'version':1,'title':'Kart 5J — Fas Brezilyası Kıyı Çekirdeği','description':'Dünya siyasi iskeleti: Fas Brezilyası yalnız Recife–Bahia kıyı çekirdeği ile ayrı Rio liman ağını alır. BRZnin Amazon, iç yayla ve güney sahiplikleri bu karta dahil değildir; bunlar yerel siyaset kartlarında ayrıştırılacaktır.','countries':COUNTRIES,'states':states}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (2 countries, {len(states)} state records)')
if __name__=='__main__':main()
