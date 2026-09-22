from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CAT=ROOT/'build/political-ecu-catalog.json';OUT=Path(__file__).with_name('card29.json')
C={'VQU':{'name':'Kingdom of Quito','name_tr':'Quito Krallığı','color':[123,121,158],'country_type':'recognized','tier':'principality','cultures':['quechua'],'religion':'animist','capital':'STATE_ECUADOR'},'ECU':{'name':'Residual Ecuadorian Jurisdiction','name_tr':'Geçici Ekvador Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['quechua'],'religion':'catholic','capital':'STATE_PASTAZA','companies':{'mode':'replace','add':[],'remove':[]}}}
def main():
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','ECU','--out',str(CAT)],cwd=ROOT,check=True);by={s['id']:s for s in json.loads(CAT.read_text())['states']};states={}
 for sid in ('STATE_ECUADOR','STATE_PASTAZA'):
  s=by[sid];parts=[]
  for e in s['owners']:parts.append({'owner':'VQU' if e['tag']=='ECU' else e['tag'],'provinces':['x'+p[1:].upper() for p in dict.fromkeys(e['provinces'])]})
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 d={'version':2,'title':'Kart 5R — Quito Krallığı','description':'Ekvador ve Pastazadaki doğrulanmış ECU payları Quito Krallığına geçer; Pastazadaki NPU yerel payı korunur. ECU birleşik önizlemede topraksız kalır.','countries':C,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['ECU']}}
 OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('wrote',OUT)
if __name__=='__main__':main()
