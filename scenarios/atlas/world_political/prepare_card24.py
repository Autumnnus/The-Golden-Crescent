"""Build a broad Bolivia/Charcas regional political break-up."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-bol-catalog.json';TARGET=Path(__file__).with_name('card24.json')
def c(name,tr,color,cult,cap):return {'name':name,'name_tr':tr,'color':color,'country_type':'unrecognized','tier':'principality','cultures':cult,'religion':'animist','capital':cap}
COUNTRIES={'VAM':c('Upper Amazon Councils','Yukarı Amazon Meclisleri',[75,133,126],['amazonian'],'STATE_ACRE'),'VAK':c('Atacama Coastal Council','Atacama Kıyı Meclisi',[139,117,84],['quechua'],'STATE_ANTOFAGASTA'),'VLP':c('La Paz Highland Council','La Paz Yüksekova Meclisi',[119,125,151],['quechua'],'STATE_LA_PAZ'),'VKC':c('Charcas Kingdom','Charcas Krallığı',[142,111,131],['quechua'],'STATE_POTOSI'),'VSB':c('Santa Cruz River Assembly','Santa Cruz Nehir Meclisi',[93,136,111],['guarani'],'STATE_SANTA_CRUZ'),'BOL':{'name':'Residual Bolivian Jurisdiction','name_tr':'Geçici Bolivya Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['quechua'],'religion':'catholic','capital':'STATE_MATO_GROSSO','companies':{'mode':'replace','add':[],'remove':[]}}}
TARGETS={'STATE_ACRE':'VAM','STATE_AMAZONAS':'VAM','STATE_ANTOFAGASTA':'VAK','STATE_JUJUY':'VKC','STATE_LA_PAZ':'VLP','STATE_POTOSI':'VKC','STATE_SANTA_CRUZ':'VSB'}
def main():
 subprocess.run([sys.executable,'scripts/tools.py','atlas','catalog','--region','BOL','--out',str(CATALOG)],cwd=ROOT,check=True);by={x['id']:x for x in json.loads(CATALOG.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  s=by[sid];local={p for e in s['owners'] if e['tag']!='BOL' for p in e['provinces']};parts=[];found=False
  for e in s['owners']:
   ps=list(dict.fromkeys(p for p in e['provinces'] if not(e['tag']=='BOL' and p in local)))
   if e['tag']=='BOL':found=True
   if ps:parts.append({'owner':target if e['tag']=='BOL' or (sid=='STATE_AMAZONAS' and e['tag']=='CLM') else e['tag'],'provinces':['x'+p[1:].upper() for p in ps]})
  if not found:raise RuntimeError(sid)
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 # Jujuy also contains ARG's share; keep all ownership changes for the state
 # in this card rather than producing competing overlays.
 for part in states['STATE_JUJUY']['split']:
  if part['owner'] == 'ARG': part['owner'] = 'VKC'
 card={'version':2,'title':'Kart 5M — Charcas ve Yukarı Andlar','description':'Dünya siyasi iskeleti: Bolivyanın doğrudan payları Charcas/Potosí, La Paz, Atacama, Santa Cruz ve yukarı Amazon meclislerine dağıtılır; Amazonas’taki Kolombiya payı da mevcut Yukarı Amazon meclislerine döner. Mato Grossodaki küçük BOL payı, aynı statei yöneten Brezilya iç kartında devredilir; böylece birleşik önizlemede BOL topraksız kalır.','countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['BOL']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)')
if __name__=='__main__':main()
