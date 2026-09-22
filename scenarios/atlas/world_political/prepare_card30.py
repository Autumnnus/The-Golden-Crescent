from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).with_name('card30.json')
C={'VCU':{'name':'Kingdom of Cusco','name_tr':'Cusco Krallığı','color':[135,109,137],'country_type':'recognized','tier':'kingdom','cultures':['quechua'],'religion':'animist','capital':'STATE_AREQUIPA'}}
def load(t):
 p=R/f'build/political-{t.lower()}-catalog.json';subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region',t,'--out',str(p)],cwd=R,check=True);return {x['id']:x for x in json.loads(p.read_text())['states']}
def main():
 n=load('NPU');s=load('SPU');states={}
 for src,sid,tag in [(n,'STATE_CAJAMARCA','NPU'),(s,'STATE_AREQUIPA','SPU'),(s,'STATE_TARAPACA','SPU')]:
  x=src[sid];parts=[]
  for e in x['owners']:parts.append({'owner':'VCU' if e['tag']==tag else e['tag'],'provinces':['x'+p[1:].upper() for p in dict.fromkeys(e['provinces'])]})
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 d={'version':2,'title':'Kart 5S — Cusco Krallığı Çekirdeği','description':'Cusco Krallığı, oyun başkenti temsili olarak Arequipa ile güney Peru yüksek havzası, Tarapacá ve Cajamarca paylarında kurulur. Lima kıyısıyla ilişkisi toprak devri değil sözleşmeli ticarettir; Ica ile Pastaza yerel sahipliğinde kalır. Eski Güney Peru başlangıç kaydı temizlenir.','countries':C,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['SPU']}};O.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('wrote',O)
if __name__=='__main__':main()
