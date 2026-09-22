"""Declare the written Mughal contractual relationships without conflating them."""
from __future__ import annotations
import json
from pathlib import Path
OUT=Path(__file__).with_name('card39.json')
def main():
 card={
  'version':2,
  'title':'Kart 2B — Gurkanî sözleşme ağı',
  'description':'Keşmir, vanilla Pencap vasallığından çıkarılır ve Gurkanî’ye sözleşmeli bağlı devlet olur. Jaipur ve Mewar, iç egemenliklerini koruyarak yalnız sınırlı koruma/katkı düzenine girer. Harita sahibi değiştirilmez.',
  'countries':{}, 'states':{},
  'subject_types':{
   've_contractual_vassal':{'base':'vassal','name':'Contractual Vassal','name_tr':'Sözleşmeli Bağlı','overlord_types':['recognized','unrecognized'],'subject_types':['recognized','unrecognized'],'can_have_subjects':False,'join_overlord_wars':True,'income_transfer':0.1},
   've_limited_protection':{'base':'protectorate','name':'Limited Protection Compact','name_tr':'Sınırlı Koruma Antlaşması','overlord_types':['recognized','unrecognized'],'subject_types':['recognized','unrecognized'],'can_have_subjects':False,'join_overlord_wars':False,'income_transfer':0.03},
  },
  'diplomacy':{'mode':'inherit','reset_countries':['KAS','JAI','MEW'],'subjects':[
   {'overlord':'MUG','subject':'KAS','type':'ve_contractual_vassal','liberty_desire':35},
   {'overlord':'MUG','subject':'JAI','type':'ve_limited_protection','liberty_desire':45},
   {'overlord':'MUG','subject':'MEW','type':'ve_limited_protection','liberty_desire':45},
  ]},
 }
 OUT.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
