from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).with_name('card34.json')
def main():
 p=R/'build/political-dei-west-java-catalog.json';subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region','DEI','--out',str(p)],cwd=R,check=True);s=next(x for x in json.loads(p.read_text())['states'] if x['id']=='STATE_WEST_JAVA');parts=[{'owner':'YOG' if e['tag']=='DEI' else e['tag'],'provinces':['x'+q[1:].upper() for q in dict.fromkeys(e['provinces'])]} for e in s['owners']]
 d={'version':2,'title':'Kart 3D — Batı Java Yerel Yönetimi','description':'Batı Javadaki son DEI doğrudan payı Java yerel yönetimine aktarılır; DEI birleşik önizlemede topraksız kalır.','countries':{'DEI':{'name':'Residual Dutch East Indies Jurisdiction','name_tr':'Geçici Hollanda Doğu Hint Yetki Alanı','color':[125,125,125],'country_type':'recognized','tier':'principality','cultures':['dutch'],'religion':'protestant','capital':'STATE_EAST_JAVA','companies':{'mode':'replace','add':[],'remove':[]}}},'states':{'STATE_WEST_JAVA':{'split':parts,'pops':'drop','buildings':'drop'}},'diplomacy':{'mode':'inherit','reset_countries':['DEI']}};O.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
