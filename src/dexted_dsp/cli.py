"""File-only offline checks, human-oriented inspection, and deterministic demos."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from . import Biquad, certify, certify_cascade, verify_biquad, verify_cascade, __version__
from .model import positive_gamma


def load_json(path):
    data = Path(path).read_bytes()
    if len(data) > 1024*1024:
        raise ValueError('JSON input exceeds 1 MiB; use Python API for larger trusted objects')
    def bad_constant(x):
        raise ValueError(f'invalid JSON number: {x}')
    value = json.loads(data,parse_constant=bad_constant)
    if not isinstance(value,dict):
        raise ValueError('JSON root must be an object')
    return value


def load_filter(path):
    obj = load_json(path)
    kind = obj.get('type')
    precision = obj.get('precision','float64')
    gamma = positive_gamma(obj.get('max_gain',1.0))
    if kind=='biquad':
        rows = (Biquad.from_coefficients(obj['coefficients'],precision=precision),)
    elif kind=='cascade':
        rows = tuple(Biquad.from_coefficients(r,precision=precision) for r in obj['sections'])
        if not 1<=len(rows)<=32:raise ValueError('one to 32 sections are required')
    else:
        raise ValueError('type must be biquad or cascade; .dsp/ONNX/native plugins are not parsed')
    return kind,rows,gamma


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',action='version',version=__version__)
    subs=parser.add_subparsers(dest='command',required=True)
    check=subs.add_parser('check',help='check filter JSON; exit 0 only for CERTIFIED')
    check.add_argument('input',type=Path)
    check.add_argument('--output',type=Path)
    check.add_argument('--max-depth',type=int,default=48)
    check.add_argument('--max-nodes',type=int,default=20000)
    verify=subs.add_parser('verify',help='recheck a PASS certificate against original input')
    verify.add_argument('input',type=Path)
    verify.add_argument('certificate',type=Path)
    inspect=subs.add_parser('inspect',help='inspect deployed filters; produce gain bounds and proof JSON')
    inspect.add_argument('input',type=Path)
    inspect.add_argument('--output',type=Path,help='save JSON proof envelope')
    inspect.add_argument('--report',type=Path,help='save Markdown inspection report')
    inspect.add_argument('--peak-bits',type=int,default=8)
    inspect.add_argument('--max-depth',type=int,default=48)
    inspect.add_argument('--max-nodes',type=int,default=20000)
    demo=subs.add_parser('demo',help='run a deterministic proof-versus-grid demonstration')
    demo.add_argument('name',choices=['hidden-peak'])
    demo.add_argument('--grid',type=int,default=1024)
    args=parser.parse_args(argv)
    try:
        if args.command=='demo':
            from .demo import hidden_peak_demo
            result=hidden_peak_demo(grid_size=args.grid)
            print(json.dumps(result,indent=2,allow_nan=False))
            return 0 if result['contradiction'] else 1
        kind,rows,gamma=load_filter(args.input)
        precision=load_json(args.input).get('precision','float64') if args.command=='inspect' else 'float64'
        if args.command=='verify':
            certificate=load_json(args.certificate)
            if certificate.get('schema')=='dexted-dsp/inspection/v1':
                from .inspection import verify_inspection
                ok=verify_inspection(certificate,rows[0] if kind=='biquad' else rows,
                                     precision=load_json(args.input).get('precision','float64'),max_gain=gamma)
            else:
                ok=(verify_biquad(certificate,rows[0],gamma) if kind=='biquad'
                    else verify_cascade(certificate,rows,gamma))
            print(json.dumps({'verified':ok}))
            return 0 if ok else 1
        if args.output is not None and args.output.resolve()==args.input.resolve():
            raise ValueError('output must not overwrite input')
        if args.command=='inspect':
            from .inspection import inspect_biquad,inspect_cascade
            if args.report is not None and args.report.resolve()==args.input.resolve():
                raise ValueError('report must not overwrite input')
            if args.output is not None and args.report is not None and args.output.resolve()==args.report.resolve():
                raise ValueError('report and JSON output must be different paths')
            report=(inspect_biquad(rows[0],max_gain=gamma,precision=precision,peak_bits=args.peak_bits)
                if kind=='biquad' else inspect_cascade(rows,max_gain=gamma,precision=precision,
                    peak_bits=args.peak_bits,max_depth=args.max_depth,max_nodes=args.max_nodes))
            text=json.dumps(report.as_dict(),indent=2,ensure_ascii=False,allow_nan=False)+'\n'
            if args.output:args.output.write_text(text,encoding='utf-8')
            if args.report:args.report.write_text(report.markdown(),encoding='utf-8')
            print(text,end='')
            return 0 if report.certified else 3 if report.status=='unknown' else 1
        report=(certify(rows[0],gamma).as_dict() if kind=='biquad' else
                certify_cascade(rows,gamma,max_depth=args.max_depth,max_nodes=args.max_nodes))
        text=json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
        if args.output:args.output.write_text(text,encoding='utf-8')
        print(text,end='')
        return 0 if report['certified'] else 3 if report['status']=='unknown' else 1
    except (ValueError,TypeError,KeyError,OSError,OverflowError,MemoryError) as exc:
        print(json.dumps({'status':'invalid_input','error':str(exc)}),file=sys.stderr)
        return 2
