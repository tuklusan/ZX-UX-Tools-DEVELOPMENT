#!/usr/bin/env python3
"""Compare actual ZX-UX output with gfortran for pinned ANSI subset sources.

This is an integration comparison for the covered programs, not F77S certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = {'f77s_fmt': ['  42'], 'f77s_data': ['  9', '  2']}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {'argv': [str(x) for x in cmd], 'exit_code': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as e:
        return {'argv': [str(x) for x in cmd], 'exit_code': None, 'timeout': True,
                'stdout': (e.stdout or b'').decode('utf-8', 'replace'),
                'stderr': (e.stderr or b'').decode('utf-8', 'replace')}


def lines(s):
    # The RVM screen text includes blank rows after exit; do not lose leading spaces.
    return [line.rstrip() for line in s.splitlines() if line.strip()]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', required=True)
    p.add_argument('--rvm', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sdk-archive', type=Path)
    a = p.parse_args()
    if not shutil.which('gfortran'):
        p.error('gfortran required for independent comparison')
    report = {'schema': 1, 'purpose': 'F77S example differential execution',
              'not_full_conformance': True,
              'tools': {'gfortran': execute(['gfortran', '--version'])['stdout'].splitlines()[0],
                        'rvm_sha256': digest(a.rvm),
                        'rfortranc_sha256': digest(ROOT/'rfortranc/translator.py'),
                        'sdk_archive_sha256': digest(a.sdk_archive) if a.sdk_archive else None},
              'cases': []}
    with tempfile.TemporaryDirectory() as d:
        for name, expectation in CASES.items():
            src = ROOT/'tests/fortran'/(name+'.f')
            target = Path(d)/(name+'.ssx')
            host = Path(d)/(name+'.host')
            compile_zx = execute([sys.executable, str(ROOT/'bin/rfortranc'),
                                  '--std','f77s','--sdk',a.sdk,'--native',
                                  '-o',str(target),str(src)])
            compile_host = execute(['gfortran','-std=legacy','-ffixed-form',
                                    '-o',str(host),str(src)])
            zx = execute([sys.executable, a.rvm,'--headless','--text','--frames','1000',str(target)],
                         60) if compile_zx['exit_code'] == 0 and target.exists() else None
            reference = execute([str(host)]) if compile_host['exit_code'] == 0 else None
            case = {'name': name, 'source_sha256': digest(src),
                    'ssx_sha256': digest(target) if target.exists() else None,
                    'ssx_bytes': target.stat().st_size if target.exists() else None,
                    'expected_lines': expectation, 'compile_zx': compile_zx,
                    'compile_gfortran': compile_host,'zxux_run': zx, 'gfortran_run': reference}
            case['passed'] = bool(zx and reference and compile_zx['exit_code'] == 0
                                  and compile_host['exit_code'] == 0
                                  and zx['exit_code'] == 0 and reference['exit_code'] == 0
                                  and '(exit)' in zx['stderr']
                                  and lines(zx['stdout']) == lines(reference['stdout']) == expectation)
            report['cases'].append(case)
            print(('PASS' if case['passed'] else 'FAIL'), name, flush=True)
    report['result'] = {'passed': sum(c['passed'] for c in report['cases']),
                        'total': len(report['cases'])}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('RESULT', report['result'], flush=True)
    return 0 if report['result']['passed'] == report['result']['total'] else 1

if __name__=='__main__':
    raise SystemExit(main())
