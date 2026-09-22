"""Replace direct Hudson's Bay Company possession with bounded northern polities."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; CATALOG=ROOT/'build/political-hbc-catalog.json'; TARGET=Path(__file__).with_name('card17.json')
COUNTRIES={
 'VIN':{'name':'Vinland','name_tr':'Vinland','color':[91,132,147],'country_type':'recognized','tier':'principality','cultures':['norwegian','swedish','danish'],'religion':'protestant','capital':'STATE_QUEBEC'},
 'VQC':{'name':'Laurentian Council','name_tr':'Laurentian Meclisi','color':[101,139,115],'country_type':'unrecognized','tier':'principality','cultures':['algonquian'],'religion':'animist','capital':'STATE_QUEBEC'},
 'VCI':{'name':'Interlake Cree Council','name_tr':'Göllerarası Cree Meclisi','color':[111,137,90],'country_type':'unrecognized','tier':'principality','cultures':['cree'],'religion':'animist','capital':'STATE_MANITOBA'},
 'VPC':{'name':'Prairie Cree Council','name_tr':'Ova Cree Meclisi','color':[132,124,83],'country_type':'unrecognized','tier':'principality','cultures':['cree'],'religion':'animist','capital':'STATE_SASKATCHEWAN'},
 'VFC':{'name':'Foothills Council','name_tr':'Etek Dağları Meclisi','color':[118,130,105],'country_type':'unrecognized','tier':'principality','cultures':['cree','athabaskan'],'religion':'animist','capital':'STATE_ALBERTA'},
 'VDE':{'name':'Dene River Council','name_tr':'Dene Nehir Meclisi','color':[90,128,140],'country_type':'unrecognized','tier':'principality','cultures':['athabaskan'],'religion':'animist','capital':'STATE_NORTHWEST_TERRITORIES'},
 'VNU':{'name':'Nunavut Coastal Council','name_tr':'Nunavut Kıyı Meclisi','color':[113,133,166],'country_type':'unrecognized','tier':'principality','cultures':['inuit'],'religion':'animist','capital':'STATE_NUNAVUT'},
 'HBC':{'name':'Residual Hudson Bay Jurisdiction','name_tr':'Geçici Hudson Körfezi Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['anglo_canadian'],'religion':'protestant','capital':'STATE_ONTARIO','companies':{'mode':'replace','add':[],'remove':[]}},
}
TARGETS={'STATE_QUEBEC':'VQC','STATE_MANITOBA':'VCI','STATE_SASKATCHEWAN':'VPC','STATE_ALBERTA':'VFC','STATE_NORTHWEST_TERRITORIES':'VDE','STATE_NUNAVUT':'VNU','STATE_BRITISH_COLUMBIA':'SLS','STATE_YUKON_TERRITORY':'ATB'}
def main():
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','HBC','--out',str(CATALOG)],cwd=ROOT,check=True)
 by={s['id']:s for s in json.loads(CATALOG.read_text())['states']}; states={}
 for sid,target in TARGETS.items():
  state=by[sid]; parts=[];found=False; local={p for e in state['owners'] if e['tag'] not in ({'HBC','QUE'} if sid=='STATE_QUEBEC' else {'HBC'}) for p in e['provinces']}
  for e in state['owners']:
   ps=e['provinces'];
   if e['tag']=='HBC': found=True;ps=[p for p in ps if p not in local]
   owner=target if e['tag']=='HBC' else e['tag']
   if sid=='STATE_QUEBEC' and e['tag']=='QUE': owner='VIN'
   if sid=='STATE_BRITISH_COLUMBIA' and e['tag']=='ORG': owner='SLS'
   if ps: parts.append({'owner':owner,'provinces':['x'+p[1:].upper() for p in ps]})
  if not found:raise RuntimeError(sid)
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 5F — Kuzey Kanada ve HBC Sonrası Ağlar','description':'Dünya siyasi iskeleti: Hudson Körfezi Şirketi payları Laurentian, Cree, Dene, Inuit, Salish ve Athabaskan yerel ağlarına geçer. Vinlandın Quebec kıyı/şehir çekirdeği ayrı Britanya Kanada kartında kuruludur. State ölçeği kıyı istasyonlarını kesin kara egemenliği saymaz; Ontario payı kart18 doğrulama aktarımına ayrılmıştır.','countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['HBC','QUE']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)')
if __name__=='__main__':main()
