"""Dismantle MEX's northern and regional direct holdings, retaining Bajio as validation anchor."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];CATALOG=ROOT/'build/political-mex-catalog.json';TARGET=Path(__file__).with_name('card19.json')
def c(name,tr,color,cult,cap):return {'name':name,'name_tr':tr,'color':color,'country_type':'unrecognized','tier':'principality','cultures':cult,'religion':'animist','capital':cap}
COUNTRIES={
 'VBP':c('Baja Coastal Council','Baja Kıyı Meclisi',[92,132,151],['nahua'],'STATE_BAJA_CALIFORNIA'),
 'VCL':c('California Valley League','Kaliforniya Vadi Birliği',[110,142,109],['nahua'],'STATE_CALIFORNIA'),
 'VSO':c('Sonoran Council','Sonora Meclisi',[146,121,80],['nahua'],'STATE_SONORA'),
 'VNP':c('Northern Plateau Council','Kuzey Plato Meclisi',[133,116,88],['apache'],'STATE_CHIHUAHUA'),
 'VDR':c('Durango Highland Council','Durango Yüksekova Meclisi',[119,126,104],['nahua'],'STATE_DURANGO'),
 'VGR':c('Guerrero Coastal Council','Guerrero Kıyı Meclisi',[78,137,138],['nahua'],'STATE_GUERRERO'),
 'VOA':c('Oaxaca Assembly','Oaxaca Meclisi',[142,108,112],['zapotec','mixtec'],'STATE_OAXACA'),
 'VJL':c('Jalisco Lake League','Jalisco Göl Birliği',[129,139,79],['nahua'],'STATE_JALISCO'),
 'VZA':c('Zacatecas Mining Council','Zacatecas Maden Meclisi',[133,113,133],['nahua'],'STATE_ZACATECAS'),
 'VSR':c('Rio Grande River Council','Rio Grande Nehir Meclisi',[99,130,149],['nahua'],'STATE_RIO_GRANDE'),
 'MEX':{'name':'Residual Mexican Interior','name_tr':'Geçici Meksika İç Bölgesi','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['nahua'],'religion':'catholic','capital':'STATE_BAJIO','companies':{'mode':'replace','add':[],'remove':[]}},
}
TARGETS={'STATE_ARIZONA':'APC','STATE_BAJA_CALIFORNIA':'VBP','STATE_CALIFORNIA':'VCL','STATE_CHIHUAHUA':'VNP','STATE_DURANGO':'VDR','STATE_GUERRERO':'VGR','STATE_JALISCO':'VJL','STATE_NEVADA':'BNN','STATE_NEW_MEXICO':'APC','STATE_OAXACA':'VOA','STATE_RIO_GRANDE':'VSR','STATE_SINALOA':'VSO','STATE_SONORA':'VSO','STATE_TEXAS':'COM','STATE_UTAH':'UTE','STATE_ZACATECAS':'VZA'}
def main():
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','MEX','--out',str(CATALOG)],cwd=ROOT,check=True);by={x['id']:x for x in json.loads(CATALOG.read_text())['states']};states={}
 for sid,target in TARGETS.items():
  s=by[sid];local={p for e in s['owners'] if e['tag']!='MEX' for p in e['provinces']};parts=[];found=False
  for e in s['owners']:
   ps=list(dict.fromkeys(p for p in e['provinces'] if not(e['tag']=='MEX' and p in local)))
   if e['tag']=='MEX':found=True
   if ps:parts.append({'owner':target if e['tag']=='MEX' else e['tag'],'provinces':['x'+p[1:].upper() for p in ps]})
  if not found:raise RuntimeError(sid)
  states[sid]={'split':parts,'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 5H — Meksika İç ve Kuzey Yerel Ağları','description':'Dünya siyasi iskeleti: Meksika Cumhuriyetinin kalan doğrudan payları Baja, Kaliforniya, Sonora, kuzey plato, yüksekova ve yerel kent/nehir meclislerine aktarılır. Önceden var olan yerli province payları korunur; state ölçeği çizgisi sonraki sınır ayrıntısına açıktır. Bajío, kart20 aktarımına kadar MEX doğrulama ankrajıdır.','countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['MEX']}}
 TARGET.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n');print(f'wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)')
if __name__=='__main__':main()
