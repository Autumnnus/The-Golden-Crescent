"""Complete Brazil reset by replacing its Goiás remainder with a central council."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-brz-goias-catalog.json';TARGET=Path(__file__).with_name('card23.json')
COUNTRIES={'VGC':{'name':'Goias Central Council','name_tr':'Goiás Merkez Meclisi','color':[129,128,91],'country_type':'unrecognized','tier':'principality','cultures':['tupinamba'],'religion':'animist','capital':'STATE_GOIAS'},'BRZ':{'name':'Residual Brazilian Interior','name_tr':'Geçici Brezilya İç Bölgesi','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['brazilian'],'religion':'catholic','capital':'STATE_RIO_DE_JANEIRO','companies':{'mode':'replace','add':[],'remove':[]}}}
def main():
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','BRZ','--out',str(CATALOG)],cwd=ROOT,check=True);s=next(x for x in json.loads(CATALOG.read_text())['states'] if x['id']=='STATE_GOIAS');parts=[]
 for e in s['owners']:
  if e['tag']!='BRZ':raise RuntimeError('Goias owner changed')
  parts.append({'owner':'VGC','provinces':['x'+p[1:].upper() for p in dict.fromkeys(e['provinces'])]})
 card={'version':2,'title':'Kart 5L — Goiás Merkez Meclisi','description':'Goiásdaki son BRZ doğrudan payı merkez meclisine geçer. Birleşik önizlemede BRZ topraksızdır.','countries':COUNTRIES,'states':{'STATE_GOIAS':{'split':parts,'pops':'drop','buildings':'drop'}},'diplomacy':{'mode':'inherit','reset_countries':['BRZ']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (2 countries, 1 state records)')
if __name__=='__main__':main()
