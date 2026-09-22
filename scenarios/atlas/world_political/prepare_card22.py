"""Split remaining direct Brazilian lands into bounded regional polities."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-brz-catalog.json';TARGET=Path(__file__).with_name('card22.json')
def c(name,tr,color,cult,cap):return {'name':name,'name_tr':tr,'color':color,'country_type':'unrecognized','tier':'principality','cultures':cult,'religion':'animist','capital':cap}
COUNTRIES={'VNR':c('Northeast River Councils','Kuzeydoğu Nehir Meclisleri',[119,139,94],['tupinamba'],'STATE_CEARA'),'VSV':c('Sao Vicente Valley League','São Vicente Vadi Birliği',[111,127,158],['tupinamba'],'STATE_SAO_PAULO'),'VPS':c('Southern Plateau Assemblies','Güney Plato Meclisleri',[121,142,111],['guarani'],'STATE_PARANA'),'VMG':c('Minas Highland Council','Minas Yüksekova Meclisi',[140,112,94],['tupinamba'],'STATE_MINAS_GERAIS'),'VMT':c('Mato Grosso River Council','Mato Grosso Nehir Meclisi',[84,133,135],['guarani'],'STATE_MATO_GROSSO')}
TARGETS={'STATE_CEARA':'VNR','STATE_MARANHAO':'VNR','STATE_PARAIBA':'VNR','STATE_PIAUI':'VNR','STATE_RIO_GRANDE_DO_NORTE':'VNR','STATE_SAO_PAULO':'VSV','STATE_PARANA':'VPS','STATE_SANTA_CATARINA':'VPS','STATE_MINAS_GERAIS':'VMG','STATE_MATO_GROSSO':'VMT'}
def main():
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','BRZ','--out',str(CATALOG)],cwd=ROOT,check=True);by={x['id']:x for x in json.loads(CATALOG.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  s=by[sid];local={p for e in s['owners'] if e['tag']!='BRZ' for p in e['provinces']};parts=[];found=False
  for e in s['owners']:
   ps=list(dict.fromkeys(p for p in e['provinces'] if not(e['tag']=='BRZ' and p in local)))
   if e['tag']=='BRZ':found=True
   if ps:parts.append({'owner':target if e['tag']=='BRZ' else e['tag'],'provinces':['x'+p[1:].upper() for p in ps]})
  if not found:raise RuntimeError(sid)
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 # Mato Grosso's small BOL province share is consolidated here too.
 for part in states['STATE_MATO_GROSSO']['split']:
  if part['owner'] == 'BOL': part['owner'] = 'VMT'
 card={'version':1,'title':'Kart 5K — Brezilya İç Havzaları','description':'Dünya siyasi iskeleti: Fas Brezilyası kıyı şartı dışında kalan BRZ payları kuzeydoğu nehirleri, São Vicente, güney plato, Minas ve Mato Grosso yerel meclislerine geçer. Goiás merkezi kart23te ayrı aktarılır.','countries':COUNTRIES,'states':states}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)')
if __name__=='__main__':main()
