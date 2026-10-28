#!/usr/bin/env python3
"""Build and run user-supplied fixed-form F77S numerical demos as ZX-UX SSX1.

Every one of the 20 originals is accounted for. Not a conformance test; a
compile or run success is kept separate from numerical agreement with host.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
NUMBER=re.compile(r'(?<![A-Za-z0-9_])[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?')

def sha(src):
    return hashlib.sha256(Path(src).read_bytes()).hexdigest()

def call(argv, timeout):
    try:
        v=subprocess.run(list(map(str,argv)),text=True,capture_output=True,timeout=timeout)
        return {'argv':list(map(str,argv)),'exit_code':v.returncode,'stdout':v.stdout,'stderr':v.stderr}
    except subprocess.TimeoutExpired as e:
        return {'argv':list(map(str,argv)),'exit_code':None,'timeout':True,
                'stdout':(e.stdout or b'').decode('utf-8','replace'),
                'stderr':(e.stderr or b'').decode('utf-8','replace')}

def numerical_comparison(host, zx, abs_tol=0.015, rel_tol=0.02):
    # A Spectrum screen may wrap a wide FORMAT record; do not silently treat
    # differing token counts or labels as matching numerical results.
    hlines=[s for s in host.splitlines() if s.strip()]
    zlines=[s for s in zx.splitlines() if s.strip()]
    h=' '.join(hlines)
    z=' '.join(zlines)
    hn=NUMBER.findall(h)
    zn=NUMBER.findall(z)
    hlabels=NUMBER.sub('',h).split()
    zlabels=NUMBER.sub('',z).split()
    if hlabels!=zlabels or len(hn)!=len(zn):
        return {'matched':False,'reason':'label or numeric field count differs',
                'host_values':len(hn),'zxux_values':len(zn),'host_labels':hlabels,'zxux_labels':zlabels}
    differences=[]
    for i,(a,b) in enumerate(zip(hn,zn)):
        try:
            av=float(a);bv=float(b)
        except ValueError:
            differences.append({'index':i,'host':a,'zxux':b,'reason':'not numeric'})
            continue
        if not (math.isfinite(av) and math.isfinite(bv) and math.isclose(av,bv,rel_tol=rel_tol,abs_tol=abs_tol)):
            differences.append({'index':i,'host':av,'zxux':bv})
    return {'matched':not differences,'outlier_count':len(differences),
            'outliers':differences[:25],'numeric_field_count':len(hn),
            'tolerance_abs':abs_tol,'tolerance_rel':rel_tol}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip',required=True,type=Path)
    p.add_argument('--sdk',required=True,type=Path)
    p.add_argument('--rvm',required=True,type=Path)
    p.add_argument('--report',required=True,type=Path)
    p.add_argument('--timeout',type=int,default=60)
    p.add_argument('--frames',type=int,default=5000)
    a=p.parse_args()
    result={'schema':1,'not_f77s_certification':True,'source_archive_sha256':sha(a.zip),
            'translator_sha256':sha(ROOT/'rfortranc/translator.py'),
            'rvm_sha256':sha(a.rvm),'mode':'real native SSX1 and matched ZX-UX RVM',
            'args':sys.argv[1:],'cases':[]}
    with zipfile.ZipFile(a.zip) as z, tempfile.TemporaryDirectory(prefix='f77s-20native-') as tmp:
        names=sorted(n for n in z.namelist() if n.startswith('F77S_Z80_SUITE/') and n.count('/')==1 and n.upper().endswith('.FOR'))
        if len(names)!=20: p.error('archive is not original 20-root demo suite')
        for n in names:
            src=Path(tmp)/Path(n).name;src.write_bytes(z.read(n))
            ssx=src.with_suffix('.ssx'); host=src.with_suffix('.host')
            c=call([sys.executable,ROOT/'bin/rfortranc','--std','f77s','--sdk',a.sdk,
                    '--native','-o',ssx,src],a.timeout)
            h=call(['gfortran','-std=legacy','-ffixed-form','-o',host,src],a.timeout)
            zrun=call([sys.executable,a.rvm,'--headless','--text','--frames',str(a.frames),ssx],a.timeout) if c['exit_code']==0 and ssx.is_file() else None
            hrun=call([host],a.timeout) if h['exit_code']==0 and host.is_file() else None
            comp=numerical_comparison(hrun['stdout'],zrun['stdout']) if hrun and zrun and hrun['exit_code']==zrun['exit_code']==0 else None
            case={'source':Path(n).name,'source_sha256':sha(src),'compile_zxux':c,'compile_host':h,
                  'ssx_sha256':sha(ssx) if ssx.is_file() else None,'ssx_bytes':ssx.stat().st_size if ssx.is_file() else None,
                  'memory_fit_estimate_only': bool(ssx.is_file() and ssx.stat().st_size<=12288),
                  'run_zxux':zrun,'run_host':hrun,'numeric_comparison':comp,
                  'native_built':bool(c['exit_code']==0 and ssx.is_file() and ssx.read_bytes().startswith(b'SSX1')),
                  'native_exited_zero':bool(zrun and zrun['exit_code']==0 and '(exit)' in zrun['stderr']),
                  'numerically_close':bool(comp and comp['matched'])}
            result['cases'].append(case)
            print(Path(n).name,'build',case['native_built'],'run',case['native_exited_zero'],'numeric',case['numerically_close'],flush=True)
    cases=result['cases']
    result['result']={'total':len(cases),'compiled_ssx1':sum(c['native_built'] for c in cases),
                      'ran_zxux_exit0':sum(c['native_exited_zero'] for c in cases),
                      'numeric_close_to_host':sum(c['numerically_close'] for c in cases),
                      'reported_failures':len(cases)-sum(c['numerically_close'] for c in cases)}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('RESULT',result['result'],flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
