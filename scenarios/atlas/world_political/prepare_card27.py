"""Map Chile's southern direct shares while retaining Santiago for completion."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-chl-catalog.json';TARGET=Path(__file__).with_name('card27.json')
COUNTRIES={'VRI':{'name':'Southern Rivers Assembly','name_tr':'Güney Nehirleri Meclisi','color':[89,136,135],'country_type':'unrecognized','tier':'principality','cultures':['patagonian'],'religion':'animist','capital':'STATE_LOS_RIOS'}}
TARGETS={'STATE_ARAUCANIA':'THL','STATE_LOS_RIOS':'VRI'}
def main():
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','CHL','--out',str(CATALOG)],cwd=ROOT,check=True);by={x['id']:x for x in json.loads(CATALOG.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  s=by[sid];local={p for e in s['owners'] if e['tag']!='CHL' for p in e['provinces']};parts=[]
  for e in s['owners']:
   ps=list(dict.fromkeys(p for p in e['provinces'] if not(e['tag']=='CHL' and p in local)))
   if ps:parts.append({'owner':target if e['tag']=='CHL' else e['tag'],'provinces':['x'+p[1:].upper() for p in ps]})
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 card={'version':1,'title':'Kart 5P — Mapuçe ve Güney Nehirleri','description':'Şilinin Araucanía payı mevcut Mapuçe/yerli düzenine, Los Ríos payı güney nehirleri meclisine geçer. Santiago kart28de ayrı merkez kıyı yönetimine aktarılır.','countries':COUNTRIES,'states':states}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} (1 countries, 2 state records)')
if __name__=='__main__':main()
