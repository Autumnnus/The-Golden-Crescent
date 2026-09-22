"""Remove the last British direct Malaya ports without inventing foreign sovereignty."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card51.json')
def main():
 p=ROOT/'build/political-gbr-malaya-catalog.json'
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','GBR','--out',str(p)],cwd=ROOT,check=True)
 s=next(x for x in json.loads(p.read_text())['states'] if x['id']=='STATE_MALAYA');merged={};order=[];found=False
 for row in s['owners']:
  found|=row['tag']=='GBR';tag='JOH' if row['tag']=='GBR' else row['tag']
  if tag not in merged:merged[tag]=[];order.append(tag)
  merged[tag].extend(row['provinces'])
 if not found:raise RuntimeError('STATE_MALAYA: GBR share missing')
 card={'version':1,'title':'Kart 3E — Malay Boğazında Yerel Egemenlik','description':'Dünya siyasi iskeleti: Malaya’daki üç Britanya doğrudan liman province’i Johor’un mevcut yerel Malay boğaz ağına döner. Mısır/Umman şirketleri için ticaret, borç veya koruma ilişkisi bu harita kartında doğrudan toprak sayılmaz.','countries':{},'states':{'STATE_MALAYA':{'split':[{'owner':x,'provinces':merged[x]} for x in order],'pops':'drop','buildings':'drop'}}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
