"""Transfer the final MEX Bajio share to a city-league, completing the reset."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-mex-bajio-catalog.json';TARGET=Path(__file__).with_name('card20.json')
COUNTRIES={'VBJ':{'name':'Bajio City League','name_tr':'Bajío Kent Birliği','color':[123,126,153],'country_type':'unrecognized','tier':'principality','cultures':['nahua'],'religion':'animist','capital':'STATE_BAJIO'},'MEX':{'name':'Residual Mexican Interior','name_tr':'Geçici Meksika İç Bölgesi','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['nahua'],'religion':'catholic','capital':'STATE_DURANGO','companies':{'mode':'replace','add':[],'remove':[]}}}
def main():
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','MEX','--out',str(CATALOG)],cwd=ROOT,check=True);s=next(x for x in json.loads(CATALOG.read_text())['states'] if x['id']=='STATE_BAJIO');parts=[]
 for e in s['owners']:parts.append({'owner':'VBJ' if e['tag']=='MEX' else e['tag'],'provinces':['x'+p[1:].upper() for p in dict.fromkeys(e['provinces'])]})
 card={'version':2,'title':'Kart 5I — Bajío Kent Birliği','description':'Bajío iç havzasındaki son MEX doğrudan payı kent birliğine aktarılır; birleşik önizlemede MEX topraksız kalır.','countries':COUNTRIES,'states':{'STATE_BAJIO':{'split':parts,'pops':'drop','buildings':'drop'}},'diplomacy':{'mode':'inherit','reset_countries':['MEX']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (2 countries, 1 state records)')
if __name__=='__main__':main()
