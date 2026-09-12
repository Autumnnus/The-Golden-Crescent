'use strict';
const data=JSON.parse(document.getElementById('flavor-data').textContent),plan=data.plan;
const $=id=>document.getElementById(id),keys=Object.keys(plan.nodes);
let selected=keys.find(k=>plan.nodes[k].entry)||keys[0],language='tr',trail=[],scale=1;
const el=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
const title=k=>plan.nodes[k].title[language],label=n=>n.kind==='event'?'Event':'Günlük';
function download(name,value){const a=el('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),5000);}
$('title').textContent=plan.title;$('summary').textContent=plan.summary;
for(const [name,value] of [['Event',keys.filter(k=>plan.nodes[k].kind==='event').length],['Günlük',keys.filter(k=>plan.nodes[k].kind==='journal').length],['Bağlantı',data.edges.length]]){const box=el('div');box.append(el('strong',value),el('span',name));$('counts').append(box);}
$('revision').textContent='Taslak '+data.fingerprint.slice(0,12);
const depths=Object.create(null);function depth(k){return depths[k]??(depths[k]=Math.max(0,...data.edges.filter(e=>e.to===k).map(e=>depth(e.from)+1)));}keys.forEach(depth);
const rows=Object.create(null),positions=Object.create(null);for(const k of keys){const d=depths[k],row=rows[d]||0;rows[d]=row+1;positions[k]={x:30+d*285,y:65+row*178};}
const width=Math.max(...Object.values(positions).map(p=>p.x))+245,height=Math.max(350,...Object.values(positions).map(p=>p.y+165));
$('graph-content').style.width=width+'px';$('graph-content').style.height=height+'px';
const ns='http://www.w3.org/2000/svg',svg=$('connections');svg.setAttribute('width',width);svg.setAttribute('height',height);
const defs=document.createElementNS(ns,'defs'),marker=document.createElementNS(ns,'marker');marker.id='arrow';marker.setAttribute('viewBox','0 0 10 10');marker.setAttribute('refX','8');marker.setAttribute('refY','5');marker.setAttribute('markerWidth','5');marker.setAttribute('markerHeight','5');marker.setAttribute('orient','auto');const arrow=document.createElementNS(ns,'path');arrow.setAttribute('d','M 0 0 L 10 5 L 0 10 z');arrow.setAttribute('fill','#7d8e7b');marker.append(arrow);defs.append(marker);svg.append(defs);
const drawn=[];for(const edge of data.edges){let group=drawn.find(e=>e.from===edge.from&&e.to===edge.to&&e.delay_days===edge.delay_days);if(group)group.labels.push(edge.label);else drawn.push({...edge,labels:[edge.label]});}
for(const edge of drawn){const a=positions[edge.from],b=positions[edge.to],x=a.x+210,y=a.y+61,endY=b.y+61;const path=document.createElementNS(ns,'path');path.setAttribute('d',`M ${x} ${y} C ${x+42} ${y},${b.x-42} ${endY},${b.x-7} ${endY}`);path.setAttribute('fill','none');path.setAttribute('stroke','#7d8e7b');path.setAttribute('stroke-width','1.6');path.setAttribute('marker-end','url(#arrow)');svg.append(path);const t=document.createElementNS(ns,'text');t.setAttribute('x',(x+b.x)/2);t.setAttribute('y',(y+endY)/2-10);t.setAttribute('text-anchor','middle');t.setAttribute('fill','#626b61');t.setAttribute('font-size','10');t.textContent=edge.labels.map(label=>({'on_complete':'başarı','on_fail':'kayıp','on_timeout':'süre'}[label]||label.replace('seçim: ',''))).join(' / ')+' · '+edge.delay_days+'g';svg.append(t);}
function zoom(n){scale=Math.max(.35,Math.min(1.7,n));$('graph-content').style.transform=`scale(${scale})`;$('graph-space').style.width=width*scale+'px';$('graph-space').style.height=height*scale+'px';}
function fit(){zoom(Math.min(1,($('graph').clientWidth-12)/width));}
$('fit').onclick=fit;$('zoom-in').onclick=()=>zoom(scale+.15);$('zoom-out').onclick=()=>zoom(scale-.15);
function select(k,walk=false){selected=k;if(walk)trail.push(k);render();}
function rules(name,value){const d=el('details',undefined,'rules');d.append(el('summary',name),el('pre',typeof value==='string'?value:JSON.stringify(value,null,2)));return d;}
function nextRoute(links,labelText){const detail=$('detail'),group=el('div');group.append(el('p',labelText,'outcome'));if(!links.length)group.append(el('p','Bu dal burada tamamlanır.','muted'));for(const link of links){const target=plan.nodes[link.to],b=el('button',`${title(link.to)} → ${target.country} · ${link.delay_days||1} gün`,'route');b.onclick=()=>select(link.to,true);group.append(b);}detail.append(group);group.scrollIntoView({block:'nearest'});}
function render(){
  $('cards').replaceChildren();$('node-list').replaceChildren();
  const query=$('search').value.toLocaleLowerCase('tr');
  for(const k of keys){const n=plan.nodes[k],pos=positions[k],b=el('button',undefined,'node '+n.kind+(trail.includes(k)?' visited':''));b.style.left=pos.x+'px';b.style.top=pos.y+'px';b.dataset.node=k;b.setAttribute('aria-pressed',String(k===selected));b.setAttribute('aria-label',`${title(k)}, ${label(n)}, ${n.country}`);b.append(el('span',label(n),'kind'),el('strong',title(k)),el('span',n.country+' · '+k,'tag'));if(n.entry)b.append(el('span',n.entry.pulse==='monthly'?'AYLIK GİRİŞ':'YILLIK GİRİŞ','entry-badge'));b.onclick=()=>select(k);$('cards').append(b);
    if((title(k)+' '+k+' '+n.country).toLocaleLowerCase('tr').includes(query)){const nav=el('button',title(k),'nav-node');nav.append(el('small',label(n)+' / '+n.country));nav.setAttribute('aria-current',String(k===selected));nav.onclick=()=>select(k);$('node-list').append(nav);}}
  const n=plan.nodes[selected],d=$('detail');d.replaceChildren();const media=el('div',undefined,'scene-art'),im=el('img');im.src=data.images[selected].poster||data.images[selected].icon;im.className=data.images[selected].poster?'':'icon';im.alt=data.images[selected].poster?'Bu sahne için seçilen önizleme posteri':'Oyunda kullanılacak simge';media.append(im);d.append(media);
  d.append(el('p',n.media?(data.images[selected].poster?'Poster önizlemesi · ':'Simge önizlemesi · Bink video tarayıcıda oynatılmaz · ')+(n.media.alias||n.media.video):'Günlük simgesi','media-label'));
  d.append(el('span',label(n)+' / '+n.country,'scene-tag'),el('h2',title(selected),'scene-title'),el('p',n.description[language],'scene-desc'));
  if(n.flavor)d.append(el('p',n.flavor[language],'scene-flavor'));
  d.append(el('p',n.context,'context-box'));
  const opts=el('div',undefined,'options');
  if(n.kind==='event'){for(const option of n.options){const b=el('button',option.text[language],'option');b.dataset.option=option.id;b.append(el('small',(option.default?'Varsayılan · ':'')+'AI ağırlığı: '+(option.ai_weight??1)+(option.when?' · Koşullu':'')));b.onclick=()=>{render();$('detail').append(rules('Bu seçimin koşulu ve etkileri',{when:option.when||{always:true},effects:option.effects||[]}));nextRoute(option.next||[],'Seçilen dal');};opts.append(b);}}
  else{for(const [field,name] of [['on_complete','Tamamlandı'],['on_fail','Başarısız'],['on_timeout','Süre doldu']]){if(field==='on_fail'&&!n.fail||field==='on_timeout'&&!n.timeout_days)continue;const b=el('button',name,'option');b.dataset.outcome=field;b.onclick=()=>{render();$('detail').append(rules('Sonuç etkileri',n[field]?.effects||[]));nextRoute(n[field]?.next||[],name);};opts.append(b);}}
  d.append(opts,rules('Tetiklenme koşulları',n.trigger||{always:true}));
  if(n.kind==='journal')d.append(rules('Tamamlama, başarısızlık ve süre',{complete:n.complete,fail:n.fail||null,timeout_days:n.timeout_days||null,progress:n.progress||null}));
  if(n.immediate?.length)d.append(rules('Açılış etkileri',n.immediate));
  d.append(rules('Bağlantılar',data.edges.filter(e=>e.from===selected||e.to===selected)));
  $('trail').replaceChildren();for(const k of trail){const li=el('li'),b=el('button',title(k));b.onclick=()=>select(k);li.append(b);$('trail').append(li);}
}
$('search').oninput=render;$('language').onchange=e=>{language=e.target.value;render();};$('reset-walk').onclick=()=>{trail=[];select(keys.find(k=>plan.nodes[k].entry)||keys[0]);};
const notes=$('diagnostics'),list=el('ul');for(const warning of [...(plan.assumptions||[]),...data.warnings])list.append(el('li',warning));notes.append(list,rules('Kaynak kanıtları ve isteğe bağlı Atlas bağlamı',{context:data.context,dependencies:data.source_dependencies}));
$('diagnostics-label').textContent=`Kontroller geçti · ${data.warnings.length} inceleme notu`;
$('download-plan').onclick=()=>download(plan.namespace+'.json',plan);$('download-context').onclick=()=>download(plan.namespace+'-review.json',data);
$('review-open').onclick=()=>{$('confirm').checked=false;$('approve').disabled=true;$('approval-status').textContent='';$('review').showModal();};
$('confirm').onchange=()=>{$('approve').disabled=!$('confirm').checked;};
$('approve').onclick=()=>{if(!$('confirm').checked)return;download(plan.namespace+'-approval.json',{kind:'flavor-approval-v1',approved:true,namespace:plan.namespace,fingerprint:data.fingerprint,reviewed_at:new Date().toISOString(),note:$('review-note').value});$('approval-status').textContent='Onay belgesi indirildi. Planı veya görselleri değiştirirsen bu belge geçersiz olur.';};
render();requestAnimationFrame(fit);
