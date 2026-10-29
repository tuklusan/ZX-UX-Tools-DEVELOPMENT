#!/usr/bin/env python3
"""Check F77S PAUSE: host gfortran operator protocol and ZX-UX keyboard."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'tests/fortran/f77s_pause.f'
def run(argv, input_text=None):
    p = subprocess.run(argv, input=input_text, capture_output=True, text=True, timeout=120)
    return {'exit':p.returncode, 'stdout':p.stdout, 'stderr':p.stderr}
def main():
    a=argparse.ArgumentParser()
    a.add_argument('--sdk',required=True)
    a.add_argument('--rvm',required=True)
    a.add_argument('--report',type=Path,required=True)
    args=a.parse_args()
    with tempfile.TemporaryDirectory() as d:
        target=Path(d)/'pause.ssx'
        host=Path(d)/'pause.host'
        native_compile=run([sys.executable,str(ROOT/'bin/rfortranc'),'--std','f77s',
                            '--sdk',args.sdk,'--native','-o',str(target),str(SRC)])
        host_compile=run(['gfortran','-std=legacy','-ffixed-form','-o',str(host),str(SRC)])
        native=(run([sys.executable,args.rvm,'--headless','--text','--frames','1000',
                     '--keys','go\n',str(target)]) if native_compile['exit']==0 else None)
        gfortran=run([str(host)], 'go\n') if host_compile['exit']==0 else None
        passed=bool(native and gfortran and native['exit']==gfortran['exit']==0 and
                    native['stdout'].splitlines()[:2]==['PAUSE 99','  42'] and
                    gfortran['stdout'].splitlines()==['  42'] and
                    'PAUSE 99' in gfortran['stderr'] and '(exit)' in native['stderr'])
        result={'schema':1,'passed':passed,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
                'native_compile':native_compile,'gfortran_compile':host_compile,
                'native_run':native,'host_run':gfortran,'not_physical_hardware':True,
                'host_requires_go_native_accepts_single_key':True}
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2)+'\n')
        print('PASS' if passed else 'FAIL','PAUSE host vs ZX-UX semantics')
        return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
