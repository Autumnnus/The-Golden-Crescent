"""Complete the HBC reset at Ontario with an Anishinabe state-scale council."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-hbc-ontario-catalog.json';TARGET=Path(__file__).with_name('card18.json')
COUNTRIES={'VAI':{'name':'Anishinabe Council','name_tr':'Anişinabe Meclisi','color':[103,137,107],'country_type':'unrecognized','tier':'principality','cultures':['algonquian'],'religion':'animist','capital':'STATE_ONTARIO'},'HBC':{'name':'Residual Hudson Bay Jurisdiction','name_tr':'Geçici Hudson Körfezi Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['anglo_canadian'],'religion':'protestant','capital':'STATE_MANITOBA','companies':{'mode':'replace','add':[],'remove':[]}}}
def main():
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','HBC','--out',str(CATALOG)],cwd=ROOT,check=True)
 s=next(x for x in json.loads(CATALOG.read_text())['states'] if x['id']=='STATE_ONTARIO');parts=[]
 local={p for e in s['owners'] if e['tag'] not in {'HBC','ONT'} for p in e['provinces']}
 for e in s['owners']:
  ps=list(dict.fromkeys(p for p in e['provinces'] if not (e['tag'] in {'HBC','ONT'} and p in local)))
  if ps: parts.append({'owner':'VAI' if e['tag'] in {'HBC','ONT'} else e['tag'],'provinces':['x'+p[1:].upper() for p in ps]})
 card={'version':2,'title':'Kart 5G — Anişinabe Ontario Payı','description':'Ontario içindeki HBC ve Britanya Kanada payları Anişinabe meclisine aktarılır; mevcut yerel pay korunur. Böylece birleşik önizlemede HBC veya Ontario sömürge idaresi kalmaz.','countries':COUNTRIES,'states':{'STATE_ONTARIO':{'split':parts,'pops':'drop','buildings':'drop'}},'diplomacy':{'mode':'inherit','reset_countries':['HBC','ONT']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (2 countries, 1 state records)')
if __name__=='__main__':main()
