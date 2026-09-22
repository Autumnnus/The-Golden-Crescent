"""End direct British colonial ownership in Australia and Aotearoa's north."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card41.json')
TARGETS={
 ('NSW','STATE_NEW_SOUTH_WALES'):'KNC', ('NSW','STATE_QUEENSLAND'):'MRA', ('NSW','STATE_VICTORIA'):'KLN',
 ('NSW','STATE_NORTHERN_TERRITORY'):'YGU', ('NSW','STATE_NORTH_ISLAND'):'NTO',
 ('SAS','STATE_SOUTH_AUSTRALIA'):'KAU', ('WAS','STATE_WESTERN_AUSTRALIA'):'NNG', ('TAS','STATE_TASMANIA'):'VTL',
}
COUNTRIES={'VTL':{'name':'Palawa Council','name_tr':'Palawa Meclisi','color':[128,91,78],'country_type':'unrecognized','tier':'principality','cultures':['aborigine'],'religion':'animist','capital':'STATE_TASMANIA'}}
def load(tag):
 p=ROOT/f'build/political-{tag.lower()}-catalog.json'
 subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region',tag,'--out',str(p)],cwd=ROOT,check=True)
 return {s['id']:s for s in json.loads(p.read_text())['states']}
def main():
 catalogs={tag:load(tag) for tag in {'NSW','SAS','WAS','TAS'}}; states={};seen=set()
 for (old,sid),target in TARGETS.items():
  state=catalogs[old][sid]
  if not any(o['tag']==old for o in state['owners']):raise RuntimeError(f'{old} missing in {sid}')
  seen.add((old,sid))
  states[sid]={'split':[{'owner':target if o['tag']==old else o['tag'],'provinces':['x'+h[1:].upper() for h in dict.fromkeys(o['provinces'])]} for o in state['owners']],'pops':'drop','buildings':'drop'}
 if seen!=set(TARGETS):raise RuntimeError('colonial target mismatch')
 card={'version':2,'title':'Kart 5S — Avustralya ve Aotearoa yerel egemenliği','description':('Avustralya kıtası egemen Britanya kolonisi değildir. NSW/WAS/SAS/TAS province payları state içindeki yerel Kulin, Kaurna, Noongar, Yolngu, Arrernte/Mara kuşaklarına aktarılır; Tasmania Palawa Meclisi’ne gider. Yeni Güney Galler’in Kuzey Ada payı Māori NTO’ya döner. Mevsimlik dış ticaret iskelesi doğrudan owner sayılmaz.'),'countries':COUNTRIES,'states':states,'diplomacy':{'mode':'inherit','reset_countries':['NSW','WAS','SAS','TAS','KAU','UNT']}}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
