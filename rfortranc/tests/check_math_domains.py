#!/usr/bin/env python3
"""Domain traps for subset REAL specific intrinsics, matched ZX-UX SDK/RVM.

Negative-domain inputs are outside valid mathematical domains. These checks
prove a target guard, not a FORTRAN subset numeric accuracy guarantee.
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
CASES = [('ASIN', '1.25'), ('ACOS','-1.25'), ('LOG','0.0'),
         ('ALOG10','-0.125'), ('EXP','90.0'), ('SQRT','-1.0'),
         ('ATAN2','0.0,0.0'), ('AMOD','1.0,0.0')]

def command(args):
    try:
        result=subprocess.run(args,text=True,capture_output=True,timeout=120)
        return {'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    except subprocess.TimeoutExpired:
        return {'exit_code':None,'timeout':True}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk',required=True)
    parser.add_argument('--rvm',required=True)
    parser.add_argument('--report',type=Path,required=True)
    a=parser.parse_args()
    report={'schema':1,'scope':'F77S REAL specific-domain traps on actual ZX-UX Z80 RVM',
            'not_f77s_accuracy_certification':True,'not_physical_hardware':True,
            'translator_sha256':digest(ROOT/'rfortranc/translator.py'),
            'rvm_sha256':digest(a.rvm),'cases':[]}
    with tempfile.TemporaryDirectory(prefix='f77s-math-domains-') as d:
        for i,(func,val) in enumerate(CASES):
            src=Path(d)/('math_%02d.f'%i)
            exe=src.with_suffix('.ssx')
            fixture = ROOT/'tests/negative/math_log_zero.f'
            src.write_text(fixture.read_text() if (func, val) == ('LOG', '0.0') else
                           '      PROGRAM BAD\n      REAL X\n      X='+func+'('+val+')\n      END\n')
            built=command([sys.executable,str(ROOT/'bin/rfortranc'),'--std','f77s',
                           '--sdk',a.sdk,'--native','-o',str(exe),str(src)])
            ran=command([sys.executable,a.rvm,'--headless','--text','--frames','1000',str(exe)]) if built['exit_code']==0 else None
            passed=bool(ran and ran['exit_code']==2 and '(exit)' in ran.get('stderr','')
                        and exe.read_bytes().startswith(b'SSX1'))
            report['cases'].append({'function':func,'value':val,'source_sha256':digest(src),
                                    'ssx_sha256':digest(exe) if exe.exists() else None,
                                    'build':built,'run':ran,'passed':passed})
            print('PASS' if passed else 'FAIL',func,val,flush=True)
    passed=sum(case['passed'] for case in report['cases'])
    report['result']={'passed':passed,'total':len(report['cases'])}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('RESULT',report['result'],flush=True)
    return 0 if passed==len(report['cases']) else 1

if __name__=='__main__': raise SystemExit(main())
