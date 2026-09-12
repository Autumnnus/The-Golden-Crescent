"""Machine-readable authoring contract. Semantic checks use installed game sources."""
import json
from .world import _COUNTRY_KEYS, _STATE_KEYS


def obj(properties, required=()):
    return {'type':'object','properties':properties,'additionalProperties':False,
            **({'required':list(required)} if required else {})}


def array(items):return {'type':'array','items':items}
def mapping(items):return {'type':'object','additionalProperties':items}
def enum(*values):return {'enum':list(values)}
def ref(name):return {'$ref':'#/$defs/'+name}
TEXT={'type':'string'}
RATIO={'type':'number','minimum':0,'maximum':1}
COUNT={'type':'integer','minimum':0}


def document():
    population=obj({
        'total':COUNT,'scale':{'type':'number','minimum':0,'maximum':100},
        'literacy':RATIO,'wealth':{'type':'number','minimum':1,'maximum':100},
        'cultures':mapping(RATIO),'religions':mapping(RATIO),
        'composition':array(obj({'culture':TEXT,'religion':TEXT,'share':RATIO,'pop_type':TEXT},('culture','religion','share'))),
    })
    building={'oneOf':[COUNT,obj({'level':{'type':'integer','minimum':0,'maximum':10000},
        'production_methods':array(TEXT),'ownership':enum('self','government'),'reserves':RATIO},('level',))]}
    industry=obj({'mode':enum('merge','replace'),'scale':{'type':'number','minimum':0,'maximum':100},'buildings':mapping(building)})
    state_pop=obj({**population['properties'],'by_owner':mapping(ref('population'))})
    state_ind=obj({**industry['properties'],'by_owner':mapping(ref('industry'))})
    country={k:{} for k in _COUNTRY_KEYS}
    country.update({
        'population':ref('population'),'industry':ref('industry'),'history_mode':enum('inherit','replace'),
        'technology':obj({'mode':enum('merge','replace'),'tier':{'type':'integer','minimum':1,'maximum':7},
                          'add':array(TEXT),'remove':array(TEXT),'prerequisites':enum('add','error')}),
        'laws':obj({'mode':enum('merge','replace'),'values':array(TEXT)}),
        'institutions':mapping({'type':'integer','minimum':0,'maximum':5}),
        'interest_groups':obj({'mode':enum('merge','replace'),'ruling':array(TEXT),'strength':mapping({'type':'number','minimum':-1,'maximum':10})}),
        'companies':obj({'mode':enum('merge','replace'),'add':array(obj({'type':TEXT,'headquarters':TEXT},('type','headquarters'))),'remove':array(TEXT)}),
        'military':obj({'mode':enum('merge','replace'),'formations':array(obj({
            'name':TEXT,'type':enum('army','fleet'),'hq_region':TEXT,
            'units':array(ref('unit')),'ships':array(ref('unit'))},('type','hq_region')))}),
    })
    for k in ('name','name_tr','adjective','adjective_tr','capital','market_capital','religion','notes'):country[k]=TEXT
    country.update({'cultures':array(TEXT),'country_type':enum('recognized','unrecognized','decentralized','colonial'),
                    'color':{'type':'array','items':{'type':'number','minimum':0,'maximum':255},'minItems':3,'maxItems':3}})
    state={k:{} for k in _STATE_KEYS}
    state.update({'owner':TEXT,'split':array(obj({'owner':TEXT,'provinces':array(TEXT),'rest':{'type':'boolean'},'state_type':TEXT},('owner',))),
                  'population':state_pop,'industry':state_ind,'homelands':array(TEXT),'claims':array(TEXT),
                  'pops':enum('inherit','drop'),'buildings':enum('inherit','drop')})
    party=obj({'actor':TEXT,'target':TEXT,'type':TEXT},('actor','target','type'))
    schema=obj({'version':{'const':2},'title':TEXT,'description':TEXT,'countries':mapping(obj(country)),
        'states':mapping({'oneOf':[TEXT,obj(state)]}),
        'subject_types':mapping(obj({'base':TEXT,'name':TEXT,'name_tr':TEXT,'overlord_types':array(TEXT),'subject_types':array(TEXT),
                                    'can_have_subjects':{'type':'boolean'},'join_overlord_wars':{'type':'boolean'},'income_transfer':RATIO})),
        'diplomacy':obj({'mode':enum('inherit','replace'),'reset_countries':array(TEXT),
            'subjects':array(obj({'overlord':TEXT,'subject':TEXT,'type':TEXT,'liberty_desire':{'type':'number','minimum':0,'maximum':100}},('overlord','subject','type'))),
            'relations':array(obj({'actor':TEXT,'target':TEXT,'value':{'type':'number','minimum':-100,'maximum':100}},('actor','target','value'))),
            'pacts':array(party),'remove':array(obj(party['properties'],('actor','target')))})},('version',))
    schema.update({'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Victoria 3 Scenario v2',
                   'description':'Run scenario validate for installed IDs, totals, ownership, technology, resource and diplomacy checks. Fractions sum to 1. Narrower state/by_owner plans override country defaults.',
                   '$defs':{'population':population,'industry':industry,'unit':obj({'type':TEXT,'state':TEXT,'count':{'type':'integer','minimum':1,'maximum':10000}},('type','count'))}})
    return schema


def export(out=None):
    text=json.dumps(document(),ensure_ascii=False,indent=2)
    if out:
        from .atlas import write_output
        write_output(out,text)
    else:print(text)
    return 0
