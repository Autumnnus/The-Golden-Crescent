"""Self-contained, offline review artifact. Does not render game scripts."""
import base64
from io import BytesIO
import json
from pathlib import Path
from PIL import Image
from .compiler import atomic, destination
from .source import MOD, FlavorError, writable


def thumbnail(path):
    with Image.open(path) as source:
        image=source.convert('RGBA');image.thumbnail((1000,600))
        output=BytesIO();image.save(output,format='PNG')
        return 'data:image/png;base64,'+base64.b64encode(output.getvalue()).decode()


def write_preview(plan,root=None):
    root=writable(root or MOD/'build/flavor'/plan.namespace/'review')
    if MOD/'build/flavor' not in root.parents:raise FlavorError('Önizleme build/flavor/ altında olmalı.')
    report=plan.report();images={}
    for key,node in plan.nodes.items():
        icon=node.get('icon','gfx/interface/icons/event_icons/event_newspaper.dds')
        iconpath=plan.local_asset(icon['file'],{'.dds'}) if isinstance(icon,dict) else plan.sources.asset(icon)
        images[key]={'icon':thumbnail(iconpath)}
        if 'poster' in node.get('media',{}):
            images[key]['poster']=thumbnail(plan.local_asset(node['media']['poster'],{'.png','.jpg','.jpeg','.webp'}))
    report=plan.report()  # Include all image dependencies in the approval fingerprint.
    payload={**report,'images':images}
    base=Path(__file__).parent.parent/'web'
    html=(base/'preview.html').read_text()
    html=html.replace('/*STYLE*/',(base/'preview.css').read_text())
    html=html.replace('/*SCRIPT*/',(base/'preview.js').read_text())
    # Insert untrusted prose last; template-looking text must remain literal data.
    html=html.replace('/*DATA*/',json.dumps(payload,ensure_ascii=False).replace('<',r'\u003c').replace('\u2028',r'\u2028').replace('\u2029',r'\u2029'))
    atomic(destination(root,'index.html'),html.encode())
    atomic(destination(root,'review.json'),json.dumps(report,ensure_ascii=False,indent=2).encode())
    mermaid=['flowchart LR']
    # Labels contain only validated IDs; prose remains in the review JSON/HTML.
    for key,node in plan.nodes.items():mermaid.append(f'  {key}["{key} / {node["country"]} / {node["kind"]}"]')
    for edge in plan.edges:mermaid.append(f'  {edge["from"]} -->|"{edge["delay_days"]} days"| {edge["to"]}')
    atomic(destination(root,'flow.mmd'),'\n'.join(mermaid).encode())
    return root/'index.html'
