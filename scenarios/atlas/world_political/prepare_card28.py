"""Complete Chile reset at Santiago."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-chl-santiago-catalog.json';TARGET=Path(__file__).with_name('card28.json')
COUNTRIES={'VCS':{'name':'Central Chile Civic Assembly','name_tr':'Orta Şili Kent Meclisi','color':[137,110,108],'country_type':'recognized','tier':'principality','cultures':['chilean'],'religion':'catholic','capital':'STATE_SANTIAGO'},'CHL':{'name':'Residual Chilean Jurisdiction','name_tr':'Geçici Şili Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['chilean'],'religion':'catholic','capital':'STATE_LOS_RIOS','companies':{'mode':'replace','add':[],'remove':[]}}}
def main():
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','CHL','--out',str(CATALOG)],cwd=ROOT,check=True);s=next(x for x in json.loads(CATALOG.read_text())['states'] if x['id']=='STATE_SANTIAGO');parts=[]
 for e in s['owners']:parts.append({'owner':'VCS' if e['tag']=='CHL' else e['tag'],'provinces':['x'+p[1:].upper() for p in dict.fromkeys(e['provinces'])]})
 card={'version':2,'title':'Kart 5Q — Orta Şili Kent Meclisi','description':'Santiago merkezi, bağımsız Orta Şili kent meclisine geçer; CHL birleşik önizlemede topraksız kalır.','countries':COUNTRIES,'states':{'STATE_SANTIAGO':{'split':parts,'pops':'drop','buildings':'drop'}},'diplomacy':{'mode':'inherit','reset_countries':['CHL']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (2 countries, 1 state records)')
if __name__=='__main__':main()
