from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).with_name('card31.json')
def main():
 p=R/'build/political-clm-catalog.json';subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','CLM','--out',str(p)],cwd=R,check=True);s=next(x for x in json.loads(p.read_text())['states'] if x['id']=='STATE_CUNDINAMARCA');parts=[{'owner':'VMU' if e['tag']=='CLM' else e['tag'],'provinces':['x'+q[1:].upper() for q in dict.fromkeys(e['provinces'])]} for e in s['owners']]
 d={'version':1,'title':'Kart 5T — Muisca Kent Birliği','description':'Bogotá yüksek havzasının doğrulanmış Cundinamarca payı Muisca Kent Birliğine aktarılır. Dar Yeni İşbiliye kıyı çekirdeği ayrı province kartında kurulacaktır.','countries':{'VMU':{'name':'Muisca City League','name_tr':'Muisca Kent Birliği','color':[131,117,82],'country_type':'recognized','tier':'principality','cultures':['muisca'],'religion':'animist','capital':'STATE_CUNDINAMARCA'},'CLM':{'name':'Residual Colombian Interior','name_tr':'Geçici Kolombiya İç Bölgesi','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['colombian'],'religion':'catholic','capital':'STATE_ANTIOQUIA','companies':{'mode':'replace','add':[],'remove':[]}}},'states':{'STATE_CUNDINAMARCA':{'split':parts,'pops':'drop','buildings':'drop'}}};O.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
