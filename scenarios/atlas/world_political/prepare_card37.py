"""Build the Low Countries and Hanover political correction from catalog ownership."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('card37.json')
TARGETS={'STATE_FLANDERS':'VBT','STATE_WALLONIA':'VLG','STATE_GELRE':'VBT'}
COUNTRIES={
 'VBT': {'name':'Brabant City League','name_tr':'Brabant Kent Birliği','color':[184,137,68],'country_type':'recognized','tier':'principality','cultures':['dutch'],'religion':'catholic','capital':'STATE_FLANDERS'},
 'VLG': {'name':'Liege','name_tr':'Liège Yönetimi','color':[117,117,155],'country_type':'recognized','tier':'principality','cultures':['wallonian'],'religion':'catholic','capital':'STATE_WALLONIA'},
}
def main():
 p=ROOT/'build/political-card37-catalog.json'
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','BEL','--out',str(p)],cwd=ROOT,check=True)
 by={s['id']:s for s in json.loads(p.read_text())['states']}
 states={}
 for sid,target in TARGETS.items():
  state=by[sid]
  states[sid]={
   'split':[{'owner':target if owner['tag']=='BEL' else owner['tag'], 'provinces':['x'+h[1:].upper() for h in dict.fromkeys(owner['provinces'])]} for owner in state['owners']],
   'pops':'drop','buildings':'drop',
  }
 card={'version':2,'title':'Kart 1J — Alçak Ülkeler ve Hannover','description':('Tarihsel Belçika yerine Brabant kent birliği ile Liège yönetimi; Hannover ise Büyük Britanya kişisel birliğinden bağımsız bir Alman aktör olarak kalır. State ölçeği nedeniyle Flanders ve Gelre’deki bütün eski BEL payı Brabant’a, Wallonia’daki pay Liège’e gider.'),'countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['BEL','HAN']}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
