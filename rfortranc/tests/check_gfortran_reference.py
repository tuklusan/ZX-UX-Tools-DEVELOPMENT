#!/usr/bin/env python3
"""Independent host-gfortran baseline for all strict F77S executable fixtures.

This verifies the test oracle, not ZX-UX binaries or ANSI subset conformance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from compare_f77s import CASES, INPUTS, ROOT, lines


def run(cmd, *, stdin=None, timeout=30):
    try:
        p = subprocess.run(cmd, text=True, input=stdin, capture_output=True,
                           timeout=timeout, check=False)
        return {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as exc:
        return {'exit_code': None, 'timeout': True,
                'stdout': str(exc.stdout), 'stderr': str(exc.stderr)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='write JSON evidence')
    args = parser.parse_args()
    compiler = shutil.which('gfortran')
    if not compiler:
        parser.error('gfortran is required')
    report = {'schema': 1, 'scope': 'host-only fixed-form reference outputs',
              'not_zxux_execution': True, 'not_ansi_certification': True,
              'gfortran_version': run([compiler, '--version'])['stdout'].splitlines()[0],
              'cases': []}
    with tempfile.TemporaryDirectory(prefix='f77s-host-') as directory:
        for name, expected in CASES.items():
            src = ROOT/'tests'/'fortran'/(name+'.f')
            target = Path(directory)/(name+'.host')
            built = run([compiler, '-std=legacy', '-ffixed-form',
                         '-o', str(target), str(src)])
            executed = run([str(target)], stdin=INPUTS.get(name)) if built['exit_code'] == 0 else None
            passed = (executed is not None and executed['exit_code'] == 0
                      and lines(executed['stdout']) == expected)
            report['cases'].append({
                'name': name, 'sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
                'expected_lines': expected, 'compile': built, 'execute': executed,
                'passed': passed})
            print(('PASS' if passed else 'FAIL'), name, flush=True)
    report['result'] = {'passed': sum(c['passed'] for c in report['cases']),
                        'total': len(report['cases'])}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('RESULT', report['result'], flush=True)
    return 0 if report['result']['passed'] == report['result']['total'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
