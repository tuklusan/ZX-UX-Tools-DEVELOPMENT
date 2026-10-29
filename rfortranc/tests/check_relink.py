#!/usr/bin/env python3
"""Check independent SSO relinking, exact image and Z80 execution.

No claim of prebuilt FORTRAN ABI type checking or physical Spectrum boot.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [ROOT/'tests/fortran/separate'/name for name in ('main.f', 'step.f')]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(command):
    try:
        p = subprocess.run(command, text=True, capture_output=True, timeout=90)
        return {'code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired:
        return {'code': None, 'error': 'timeout'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sdk', required=True)
    ap.add_argument('--rvm', required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()
    cli = [sys.executable, str(ROOT/'bin/rfortranc'), '--std','f77s',
           '--sdk',a.sdk,'--native']
    r = {'schema':1, 'scope':'prebuilt ZX-UX SSO object relinking and execution',
         'not_hardware_proof':True,'not_abi_type_proof':True,
         'driver_sha256':digest(ROOT/'rfortranc/driver.py'),
         'sources':{src.name:digest(src) for src in SOURCES}}
    with tempfile.TemporaryDirectory(prefix='f77s-relink-') as d:
        tmp=Path(d)
        objects=tmp/'objects'
        original=tmp/'original.ssx'
        linked=tmp/'linked.ssx'
        first=run(cli+['--separate','--object-dir',str(objects),'-o',str(original)]
                  +list(map(str,SOURCES)))
        objs=sorted(objects.glob('*.sso'))
        second=run(cli+['--link-only','-o',str(linked)]+list(map(str,objs)))
        native=run([sys.executable,a.rvm,'--headless','--text','--frames','500',str(linked)]) if linked.exists() else {}
        host=tmp/'host'
        ref_compiled=run(['gfortran','-std=legacy','-ffixed-form','-o',str(host)]
                         +list(map(str,SOURCES)))
        reference=run([str(host)]) if ref_compiled['code']==0 else {}
        low_binary=tmp/'too-small.ssx'
        low=run(cli+['--link-only','--max','1000','-o',str(low_binary)]
                +list(map(str,objs)))
        missing=run(cli+['--link-only','-o',str(tmp/'missing.ssx'),str(tmp/'none.sso')])
        wrong=run(cli+['--link-only','-o',str(tmp/'wrong.ssx'),str(SOURCES[0])])
        r.update({'original_build':first,'object_link':second,'target_run':native,
                  'host_compile':ref_compiled,'host_reference':reference,
                  'low_max':low,'missing_object':missing,
                  'bad_extension':wrong,'object_sha256':{obj.name:digest(obj) for obj in objs},
                  'ssx_sha256':digest(linked) if linked.exists() else None,
                  'ssx_bytes':linked.stat().st_size if linked.exists() else None})
        def lines(s): return [x.rstrip() for x in s.splitlines() if x.strip()]
        conditions={
            'objects':len(objs)==2,
            'build_and_relink':first['code']==second['code']==0,
            'bit_identical':linked.exists() and original.exists() and digest(linked)==digest(original),
            'actual_z80':native.get('code')==0 and '(exit)' in native.get('stderr',''),
            'independent_host':reference.get('code')==0 and
                               lines(native.get('stdout',''))==lines(reference.get('stdout',''))==['  42'],
            'memory_limit':low['code']!=0 and not low_binary.exists(),
            'missing_object_rejected':missing['code']!=0,
            'bad_extension_rejected':wrong['code']!=0
        }
        r['checks']=conditions
        r['result']={'passed':sum(conditions.values()),'total':len(conditions)}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('PASS' if r['result']['passed']==r['result']['total'] else 'FAIL',r['result'],flush=True)
    return 0 if r['result']['passed']==r['result']['total'] else 1


if __name__=='__main__': raise SystemExit(main())
