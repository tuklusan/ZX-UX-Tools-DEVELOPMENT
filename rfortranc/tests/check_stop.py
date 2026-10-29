#!/usr/bin/env python3
"""Verify standard STOP codes with real ZX-UX Z80 execution and gfortran."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def execute(command):
    run = subprocess.run(command, capture_output=True, text=True, timeout=120)
    return {'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', required=True)
    parser.add_argument('--rvm', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    cases = []
    with tempfile.TemporaryDirectory(prefix='f77s-stop-') as tmp:
        for kind, exit_code, label in [('msg', 0, 'DONE'), ('num', 42, '42')]:
            source = ROOT/'tests/fortran'/('f77s_stop'+kind+'.f')
            ssx = Path(tmp)/(kind+'.ssx')
            host = Path(tmp)/(kind+'.host')
            zx_compile = execute([sys.executable, str(ROOT/'bin/rfortranc'), '--std',
                                  'f77s', '--sdk', args.sdk, '--native', '-o', str(ssx), str(source)])
            host_compile = execute(['gfortran', '-std=legacy', '-ffixed-form', '-o', str(host), str(source)])
            zx = execute([sys.executable, args.rvm, '--headless', '--text', '--frames', '1000', str(ssx)]) if zx_compile['exit_code'] == 0 else None
            reference = execute([str(host)]) if host_compile['exit_code'] == 0 else None
            result = {'kind': kind, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                      'ssx_sha256': hashlib.sha256(ssx.read_bytes()).hexdigest() if ssx.exists() else None,
                      'ssx_bytes': ssx.stat().st_size if ssx.exists() else None,
                      'zx_compile': zx_compile, 'host_compile': host_compile,
                      'zx_run': zx, 'host_run': reference}
            result['passed'] = bool(zx and reference and
                zx['exit_code'] == reference['exit_code'] == exit_code and
                zx['stdout'].splitlines()[:2] == ['  42', 'STOP ' + label] and
                reference['stdout'].splitlines() == ['  42'] and
                'STOP ' + label in reference['stderr'] and '(exit)' in zx['stderr'])
            cases.append(result)
            print(('PASS' if result['passed'] else 'FAIL'), 'STOP', kind, flush=True)
    report = {'schema': 1, 'scope': 'F77S STOP code/message: ZX-UX console versus gfortran stderr',
              'cases': cases, 'result': {'passed': sum(x['passed'] for x in cases), 'total': len(cases)},
              'physical_hardware_tested': False}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    return 0 if report['result']['passed'] == report['result']['total'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
