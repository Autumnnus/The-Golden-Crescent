"""Restore Kandy's island sovereignty and remove Ryukyu's military subjection."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).with_name('card40.json')
def main():
 p=ROOT/'build/political-bce-catalog.json'
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','BCE','--out',str(p)],cwd=ROOT,check=True)
 state=next(s for s in json.loads(p.read_text())['states'] if s['id']=='STATE_CEYLON')
 card={'version':2,'title':'Kart 2C/3D — Kandy ve Ryukyu','description':('Kandy Krallığı Sri Lanka’da egemen ada devleti olarak bütün Ceylon province’lerini alır; BCE’nin Cape’deki toprağı değiştirilmez. Ryukyu’nun Japon askerî haraç bağı kaldırılır; yazılı çifte törensel/ticari ilişkiler doğrudan tabiiyet değildir.'),'countries':{'VKN':{'name':'Kingdom of Kandy','name_tr':'Kandy Krallığı','color':[171,118,60],'country_type':'recognized','tier':'kingdom','cultures':['sinhala'],'religion':'theravada','capital':'STATE_CEYLON'}},'states':{'STATE_CEYLON':{'split':[{'owner':'VKN','provinces':['x'+h[1:].upper() for h in dict.fromkeys(o['provinces'])]} for o in state['owners']],'pops':'drop','buildings':'drop'}},'diplomacy':{'mode':'inherit','reset_countries':['RYU']}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
