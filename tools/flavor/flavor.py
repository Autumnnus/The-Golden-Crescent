#!/usr/bin/env python3
"""Flavor Studio CLI. Atlas is optional; game output always needs a review receipt."""
import argparse
import json
from pathlib import Path
import sys
import webbrowser

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studio.model import Plan, load, ident
from studio.source import Sources, TABLES, FlavorError, MOD
from studio.preview import write_preview
from studio.compiler import write_bundle, install, check_installed, record_approval


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('validate','preview','build','install','approve'):
        p=sub.add_parser(name);p.add_argument('plan',type=Path)
        p.add_argument('--context',type=Path,help='Optional full v2 Atlas scenario-report.json')
        if name in ('build','install'):p.add_argument('--approval',required=True,type=Path)
        if name in ('preview','build'):p.add_argument('--out',type=Path)
        if name=='preview':p.add_argument('--open',action='store_true')
        if name=='approve':
            p.add_argument('--review',type=Path,required=True)
            p.add_argument('--user-confirmation',required=True,help='Record an explicit user approval of this review; never self-approve')
            p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('catalog');p.add_argument('kind',choices=[*TABLES,'icons']);p.add_argument('--query',default='')
    p.add_argument('--limit',type=int,default=20);p.add_argument('--offset',type=int,default=0)
    p=sub.add_parser('check');p.add_argument('namespace');p.add_argument('--plan',type=Path);p.add_argument('--context',type=Path)
    args=parser.parse_args(argv)
    if args.command=='catalog':
        if not 1<=args.limit<=100 or args.offset<0:raise FlavorError('limit 1..100, offset >= 0 olmalı.')
        print(json.dumps(Sources().query(args.kind,args.query,args.limit,args.offset),ensure_ascii=False,indent=2));return 0
    if args.command=='check':
        result=check_installed(ident(args.namespace))
        if args.plan:
            plan=Plan(load(args.plan),args.plan,Sources(args.context))
            if result['fingerprint']!=plan.fingerprint():raise FlavorError('Kurulu paket mevcut plan/kaynak/bağlam sürümünden farklı; yeniden önizleyin.')
        print(f'PASS: {len(result["files"])} kurulu dosya manifest ile aynı.');return 0
    plan=Plan(load(args.plan),args.plan,Sources(args.context))
    if args.command=='validate':print(json.dumps(plan.report(),ensure_ascii=False,indent=2))
    elif args.command=='approve':print(record_approval(plan,args.review,args.user_confirmation,args.out))
    elif args.command=='preview':
        path=write_preview(plan,args.out);print(f'Önizleme: {path}\nOyun dosyası üretilmedi. Diyagramdaki onay düğmesi derleme belgesini indirir.')
        if args.open:webbrowser.open(path.as_uri())
    elif args.command=='build':
        path=write_bundle(plan,args.approval,args.out or MOD/'build/flavor'/plan.namespace/'bundle')
        print(f'Derlendi: {path}\nEtkin moda kurulmadı.')
    else:
        files=install(plan,args.approval);print(f'Kuruldu: {len(files)} dosya. Atlas history/metadata dosyaları değiştirilmedi.')
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (FlavorError,OSError,ValueError) as exc:
        print(f'Hata: {exc}',file=sys.stderr);raise SystemExit(1)
