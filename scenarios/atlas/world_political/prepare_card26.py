"""Complete direct ARG replacement at Buenos Aires."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-arg-ba-catalog.json';TARGET=Path(__file__).with_name('card26.json')
COUNTRIES={'VBC':{'name':'Buenos Aires Civic League','name_tr':'Buenos Aires Kent Birliği','color':[123,132,151],'country_type':'recognized','tier':'principality','cultures':['platinean'],'religion':'catholic','capital':'STATE_BUENOS_AIRES'},'ARG':{'name':'Residual Argentine Jurisdiction','name_tr':'Geçici Arjantin Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['platinean'],'religion':'catholic','capital':'STATE_LA_PAMPA','companies':{'mode':'replace','add':[],'remove':[]}}}
def main():
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','ARG','--out',str(CATALOG)],cwd=ROOT,check=True);s=next(x for x in json.loads(CATALOG.read_text())['states'] if x['id']=='STATE_BUENOS_AIRES');parts=[]
 for e in s['owners']:parts.append({'owner':'VBC' if e['tag']=='ARG' else e['tag'],'provinces':['x'+p[1:].upper() for p in dict.fromkeys(e['provinces'])]})
 card={'version':2,'title':'Kart 5O — Buenos Aires Kent Birliği','description':'Buenos Airesteki son ARG payı kent birliğine geçer; Patagonia yerel payı korunur ve ARG birleşik önizlemede topraksız kalır.','countries':COUNTRIES,'states':{'STATE_BUENOS_AIRES':{'split':parts,'pops':'drop','buildings':'drop'}},'diplomacy':{'mode':'inherit','reset_countries':['ARG']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (2 countries, 1 state records)')
if __name__=='__main__':main()
