#!/usr/bin/env python3
"""Actual Z80/RVM proof that negative REAL SQRT traps (not conformance)."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv):
    try:
        p = subprocess.run(argv, text=True, capture_output=True, timeout=120)
        return {'argv': [str(x) for x in argv], 'exit_code': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as exc:
        return {'argv': [str(x) for x in argv], 'exit_code': None,
                'timeout': True, 'stdout': str(exc.stdout), 'stderr': str(exc.stderr)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', required=True)
    parser.add_argument('--rvm', required=True)
    parser.add_argument('--sdk-archive')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    original = ROOT/'tests/fortran/f77s_burkl2.f'
    source = original.read_text()
    old = '      R=SQRT(9.0)\n'
    assert source.count(old) == 1, 'negative-SQRT source mutation anchor changed'
    report = {'schema': 1, 'scope': 'REAL SQRT negative-domain ZX-UX runtime trap',
              'not_f77s_conformance': True, 'expected_exit_code': 2,
              'translator_sha256': hash_file(ROOT/'rfortranc/translator.py'),
              'rvm_sha256': hash_file(args.rvm),
              'sdk_archive_sha256': hash_file(args.sdk_archive) if args.sdk_archive else None}
    with tempfile.TemporaryDirectory(prefix='f77s-sqrt-neg-') as tmp:
        src = Path(tmp)/'negative_sqrt.f'
        dst = Path(tmp)/'negative_sqrt.ssx'
        src.write_text(source.replace(old, '      R=SQRT(-1.0)\n'))
        compile = run([sys.executable, str(ROOT/'bin/rfortranc'), '--std', 'f77s',
                       '--sdk', args.sdk, '--native', '-o', str(dst), str(src)])
        emulator = (run([sys.executable, args.rvm, '--headless', '--text', '--frames',
                         '1000', str(dst)]) if compile['exit_code'] == 0 and dst.exists() else None)
        passed = bool(emulator and emulator['exit_code'] == 2
                      and '(exit)' in emulator['stderr'] and dst.read_bytes().startswith(b'SSX1'))
        report['case'] = {'source_sha256': hash_file(src),
                          'ssx_sha256': hash_file(dst) if dst.exists() else None,
                          'compile': compile, 'emulator': emulator, 'passed': passed}
    report['result'] = {'passed': int(passed), 'total': 1}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('PASS' if passed else 'FAIL', 'negative-real-sqrt', flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
