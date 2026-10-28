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
CASES = {'f77s_fmt': ['  42'], 'f77s_data': ['  9', '  2'], 'f77s_implicit': ['  3', '  7'], 'f77s_real': ['  2'], 'f77s_2d': ['  43'], 'f77s_3d': [' 11'], 'f77s_read': ['  49'], 'f77s_repeat': ['  3   5  10   18'], 'f77s_dim': ['  42'], 'f77s_common': ['  42'], 'f77s_comarr': ['  43'], 'f77s_blank': ['  42'], 'f77s_fc3': ['  42'], 'f77s_fc4': ['  42'], 'f77s_fc5': ['7','  42','***'], 'f77s_equiv': ['  42  42  11  42'], 'f77s_save': ['  42'], 'f77s_char': ['>  HI   <', '>ABC<'], 'f77s_charread': ['>XYZ  <'], 'f77s_burkprime': ['   4', '  25'], 'f77s_dmarr': ['  40'], 'f77s_dmchain': ['  30'], 'f77s_dmreal': ['  42'], 'f77s_burkvec': ['  15  13  11', '  65'], 'f77s_burksort': ['   1   5   9', '   7', '  -1'], 'f77s_dmseq': ['  42'], 'f77s_dmidx': ['  42'], 'f77s_dmadj': ['  42'], 'f77s_dmstar': ['  38'], 'f77s_dmalt': ['   9'], 'f77s_burkadj': ['   5   1  15', '  28'], 'f77s_dm2ad': ['  42'], 'f77s_dm3ad': ['  42'], 'f77s_dm2st': ['  42'], 'f77s_dm3st': ['  42'], 'f77s_burkmm': ['    7   22   23', '    7'], 'f77s_burkflip': ['   6   5   2   1', '   1   6'], 'f77s_dm2el': ['  42   5']}


INPUTS = {'f77s_read': '0042 007\n', 'f77s_repeat': '003 005 010\n', 'f77s_charread': 'XYZ\n'}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(cmd, timeout=60, input_text=None):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, input=input_text)
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
            zx_cmd = [sys.executable, a.rvm,'--headless','--text','--frames','1000']
            if name in INPUTS:
                zx_cmd += ['--keys', INPUTS[name]]
            zx_cmd.append(str(target))
            zx = execute(zx_cmd, 60) if compile_zx['exit_code'] == 0 and target.exists() else None
            reference = execute([str(host)], input_text=INPUTS.get(name)) if compile_host['exit_code'] == 0 else None
            case = {'name': name, 'source_sha256': digest(src),
                    'ssx_sha256': digest(target) if target.exists() else None,
                    'ssx_bytes': target.stat().st_size if target.exists() else None,
                    'expected_lines': expectation, 'stdin': INPUTS.get(name), 'compile_zx': compile_zx,
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
