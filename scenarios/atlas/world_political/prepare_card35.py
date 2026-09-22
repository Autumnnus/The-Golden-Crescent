from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).with_name('card35.json')
def main():
 p=R/'build/political-aus-catalog.json';subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','AUS','--out',str(p)],cwd=R,check=True);by={s['id']:s for s in json.loads(p.read_text())['states']};st={}
 for sid in ('STATE_BOHEMIA','STATE_MORAVIA'):
  s=by[sid];st[sid]={'split':[{'owner':'VBO' if e['tag']=='AUS' else e['tag'],'provinces':['x'+q[1:].upper() for q in dict.fromkeys(e['provinces'])]} for e in s['owners']],'pops':'drop','buildings':'drop'}
 d={'version':1,'title':'Kart 1H — Bohemya Krallığı','description':'Yazılı Alman atlasına göre Bohemya ve Moravya, Avusturyadan ayrı Bohemya Krallığı çekirdeği olarak temsil edilir.','countries':{'VBO':{'name':'Kingdom of Bohemia','name_tr':'Bohemya Krallığı','color':[137,114,151],'country_type':'recognized','tier':'kingdom','cultures':['czech'],'religion':'catholic','capital':'STATE_BOHEMIA'}},'states':st};O.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
