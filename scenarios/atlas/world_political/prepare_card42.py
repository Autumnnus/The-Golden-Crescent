"""Close the four Iberian borders that were deliberately held open in card 05."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).with_name('card42.json')
TARGETS={'STATE_BEIRA':('POR','VAN'),'STATE_MURCIA':('SPA','VAN'),'STATE_VALENCIA':('SPA','VAR'),'STATE_BALEARIC_ISLANDS':('SPA','VAR')}
def main():
 p=ROOT/'build/political-iberia-final-catalog.json'
 # SPA catalog sees the three Spanish states; POR catalog supplies Beira.
 states={}
 for old in ('SPA','POR'):
  tmp=ROOT/f'build/political-card42-{old.lower()}-catalog.json'
  subprocess.run([sys.executable,'scenarios/atlas/world_political/catalog_vanilla.py','atlas','catalog','--baseline','vanilla','--region',old,'--scenario','build/world-political/partial-political-preview.json','--out',str(tmp)],cwd=ROOT,check=True)
  for s in json.loads(tmp.read_text())['states']:
   if s['id'] in TARGETS and TARGETS[s['id']][0]==old: states[s['id']]=s
 if set(states)!=set(TARGETS):raise RuntimeError(f'missing Iberian states: {sorted(set(TARGETS)-set(states))}')
 out={}
 for sid,(old,target) in TARGETS.items():
  st=states[sid]
  if not any(o['tag']==old for o in st['owners']):raise RuntimeError(f'{sid}: missing {old}')
  out[sid]={'split':[{'owner':target if o['tag']==old else o['tag'],'provinces':['x'+h[1:].upper() for h in dict.fromkeys(o['provinces'])]} for o in st['owners']],'pops':'drop','buildings':'drop'}
 card={'version':2,'title':'Kart 1K — İberya sınır kararları','description':('Açık bırakılmış dört İber state’i kesinleştirilir: Beira ve Murcia Endülüs’e, Valencia ve Balear Adaları Aragon’a geçer. SPA/POR’un denizaşırı geçici payları bu kartta korunur; onların dünya çapındaki tasfiyesi ayrı, çakışma-bilinçli kartlarla yapılacaktır.'),'countries':{},'states':out}
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
