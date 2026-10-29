#!/usr/bin/env python3
"""Prove F77S INT truncation, range traps and original MACHAR on ZX-UX.

MACHAR reports the target's floating properties; host and ROM results are
intentionally *not* required to match. This is not physical hardware proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def execute(argv, timeout=120):
    try:
        p = subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=timeout)
        return {'argv': list(map(str, argv)), 'exit_code': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as e:
        return {'argv': list(map(str, argv)), 'timeout': True, 'exit_code': None,
                'stdout': str(e.stdout), 'stderr': str(e.stderr)}

def fingerprint(output):
    parts = output.strip().split()
    if len(parts) != 5 or parts[0] != 'MACHAR':
        return None
    try:
        return {'radix': int(parts[1]), 'digits': int(parts[2]),
                'epsilon': float(parts[3]), 'negative_epsilon': float(parts[4])}
    except ValueError:
        return None

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sdk', type=Path, required=True)
    ap.add_argument('--rvm', type=Path, required=True)
    ap.add_argument('--demo-archive', type=Path)
    ap.add_argument('--sdk-archive', type=Path)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()
    src = ROOT / 'tests/fortran/f77s_machar.f'
    if args.demo_archive:
        with zipfile.ZipFile(args.demo_archive) as z:
            original = z.read('F77S_Z80_SUITE/MACHAR.FOR')
        if original != src.read_bytes():
            ap.error('committed MACHAR differs from user-supplied original')
    report = {'schema': 1, 'scope': 'F77S INT original MACHAR actual ZX-UX SSX1',
              'not_physical_hardware': True, 'not_full_conformance': True,
              'tools': {'translator_sha256': sha(ROOT/'rfortranc/translator.py'),
                        'rvm_sha256': sha(args.rvm),
                        'sdk_archive_sha256': sha(args.sdk_archive) if args.sdk_archive else None,
                        'original_demo_archive_sha256': sha(args.demo_archive) if args.demo_archive else None,
                        'gfortran_version': execute(['gfortran', '--version'])['stdout'].splitlines()[0]},
              'cases': []}
    with tempfile.TemporaryDirectory(prefix='f77s-int-machar-') as d:
        for name in ('f77s_int', 'f77s_machar', 'int_overflow_positive', 'int_overflow_negative'):
            path = Path(d)/f'{name}.f' if name.startswith('int_overflow') else ROOT/'tests/fortran'/f'{name}.f'
            if name.startswith('int_overflow'):
                value = '32768.0' if name.endswith('positive') else '-32769.0'
                path.write_text('      PROGRAM RANGE\n      INTEGER I\n      REAL X\n'
                                f'      X={value}\n      I=INT(X)\n'
                                '      WRITE(6,10) I\n   10 FORMAT(I6)\n      END\n')
            ssx, host = Path(d)/f'{name}.ssx', Path(d)/f'{name}.host'
            cc = execute([sys.executable, ROOT/'bin/rfortranc', '--std', 'f77s',
                          '--sdk', args.sdk, '--native', '-o', ssx, path])
            hc = execute(['gfortran', '-std=legacy', '-ffixed-form', '-o', host, path])
            zr = execute([sys.executable, args.rvm, '--headless', '--text', '--frames',
                          '20000', ssx]) if cc['exit_code'] == 0 and ssx.exists() else None
            hr = execute([host]) if hc['exit_code'] == 0 and host.exists() else None
            zfp = fingerprint(zr['stdout']) if zr and name == 'f77s_machar' else None
            hfp = fingerprint(hr['stdout']) if hr and name == 'f77s_machar' else None
            if name == 'f77s_machar':
                passed = bool(zfp and hfp and zr['exit_code'] == hr['exit_code'] == 0 and
                              '(exit)' in zr['stderr'] and zfp['radix'] == hfp['radix'] == 2 and
                              zfp['digits'] == 33 and hfp['digits'] == 24 and
                              math.isclose(zfp['epsilon'], 2**-32, rel_tol=0.01) and
                              math.isclose(zfp['negative_epsilon'], 2**-31, rel_tol=0.01))
            elif name == 'f77s_int':
                passed = bool(zr and hr and zr['exit_code'] == hr['exit_code'] == 0 and
                              '(exit)' in zr['stderr'] and zr['stdout'].splitlines()[0] ==
                              hr['stdout'].strip('\n') == '     3    -3     0     0    -2')
            else:
                passed = bool(zr and zr['exit_code'] == 2 and '(exit)' in zr['stderr'])
            report['cases'].append({'name': name, 'source_sha256': sha(path),
                'native_sha256': sha(ssx) if ssx.exists() else None,
                'native_size_bytes': ssx.stat().st_size if ssx.exists() else None,
                'native_ssx1': ssx.exists() and ssx.read_bytes().startswith(b'SSX1'),
                'compile_native': cc, 'compile_host': hc,
                'run_native': zr, 'run_host': hr, 'native_machine_characteristics': zfp,
                'host_machine_characteristics': hfp, 'passed': passed})
            print(('PASS' if passed else 'FAIL'), name, flush=True)
    report['result'] = {'total': len(report['cases']),
                        'passed': sum(x['passed'] for x in report['cases'])}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('RESULT', report['result'], flush=True)
    return 0 if report['result']['total'] == report['result']['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
