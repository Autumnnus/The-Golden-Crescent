"""Separate the documented local Panama isthmus from the Colombian remnant."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card52.json')
COUNTRIES={'VIT':{'name':'Isthmian Council','name_tr':'Kıstak Meclisi','color':[107,145,133],'country_type':'recognized','tier':'principality','cultures':['muisca'],'religion':'catholic','capital':'STATE_PANAMA'}}
def main():
 p=ROOT/'build/political-clm-panama-catalog.json';subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','CLM','--out',str(p)],cwd=ROOT,check=True)
 s=next(x for x in json.loads(p.read_text())['states'] if x['id']=='STATE_PANAMA');parts=[]
 for row in s['owners']:parts.append({'owner':'VIT' if row['tag']=='CLM' else row['tag'],'provinces':row['provinces']})
 if not any(row['tag']=='CLM' for row in s['owners']):raise RuntimeError('Panama no longer has CLM share')
 card={'version':1,'title':'Kart 5W — Panama Kıstağı Meclisi','description':'Dünya siyasi iskeleti: Panama’daki Kolombiya doğrudan payı yerel Kıstak Meclisi’ne geçer. Geçiş vergisi ve dış liman sözleşmeleri toprak egemenliği değildir; sonraki diplomasi katmanında kurulacaktır.','countries':COUNTRIES,'states':{'STATE_PANAMA':{'split':parts,'pops':'drop','buildings':'drop'}}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
