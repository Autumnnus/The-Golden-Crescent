from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).with_name('card32.json')
def c(n,tr,col,cap):return {'name':n,'name_tr':tr,'color':col,'country_type':'unrecognized','tier':'principality','cultures':['mayan'],'religion':'animist','capital':cap}
C={'VGA':c('Guatemala Highland Council','Guatemala Yüksekova Meclisi',[115,136,91],'STATE_GUATEMALA'),'VHN':c('Honduras Coastal Council','Honduras Kıyı Meclisi',[83,133,143],'STATE_HONDURAS'),'VNC':c('Nicaragua Lake Council','Nikaragua Göl Meclisi',[122,121,151],'STATE_NICARAGUA'),'VKR':c('Costa Rica Assembly','Kosta Rika Meclisi',[128,139,97],'STATE_COSTA_RICA'),'VSS':c('San Salvador Council','San Salvador Meclisi',[142,110,100],'STATE_SAN_SALVADOR'),'UCA':{'name':'Residual Central American Jurisdiction','name_tr':'Geçici Orta Amerika Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['mayan'],'religion':'catholic','capital':'STATE_CHIAPAS','companies':{'mode':'replace','add':[],'remove':[]}}}
T={'STATE_COSTA_RICA':'VKR','STATE_GUATEMALA':'VGA','STATE_HONDURAS':'VHN','STATE_NICARAGUA':'VNC','STATE_SAN_SALVADOR':'VSS'}
def main():
 p=R/'build/political-uca-catalog.json';subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','UCA','--out',str(p)],cwd=R,check=True);by={s['id']:s for s in json.loads(p.read_text())['states']};st={}
 for sid,t in T.items():
  s=by[sid];st[sid]={'split':[{'owner':t if e['tag'] in {'UCA','GBR'} and sid=='STATE_GUATEMALA' else t if e['tag']=='UCA' or (sid=='STATE_NICARAGUA' and e['tag']=='MKT') else e['tag'],'provinces':['x'+q[1:].upper() for q in dict.fromkeys(e['provinces'])]} for e in s['owners']],'pops':'drop','buildings':'drop'}
 d={'version':2,'title':'Kart 5U — Orta Amerika Yerel Meclisleri','description':'UCA doğrudan payları Guatemala, Honduras, Nikaragua, Kosta Rika ve San Salvador yerel meclislerine ayrılır. Nikaragua’daki Mosquito protektora payı da Nikaragua Göl Meclisi’ne döner; Chiapastaki UCA payı mevcut Maya kartıyla aynı state olduğundan nihai province birleşimine bırakılmıştır.','countries':C,'states':st,'diplomacy':{'mode':'inherit','reset_countries':['UCA','MKT']}};O.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
