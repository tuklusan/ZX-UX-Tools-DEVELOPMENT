#!/usr/bin/env python3
"""Build three strict F77S LGPL numerics as SSX1 + native TZX; execute each SSX in ZX-UX RVM."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'f77s_burkl2': ['    5.00', '    4.00', '    3.00', '    1.41', '    0.50', '  100.00', '    0.01'],
    'f77s_burkcopy': ['   -2.00    3.25    4.00    0.00    0.00', '    1.00   -2.00    3.25    4.00   -5.00'],
    'f77s_burkrsrt': ['    3.00   -1.00    2.00    4.00    0.00', '   -1.00    0.00    2.00    3.00    4.00'],
    'f77s_burkreal': ['   27.50', '   27.00'],
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return {'argv': list(map(str, cmd)), 'exit_code': r.returncode,
                'stdout': r.stdout, 'stderr': r.stderr}
    except subprocess.TimeoutExpired as err:
        return {'argv': list(map(str, cmd)), 'exit_code': None, 'timeout': True,
                'stdout': str(err.stdout), 'stderr': str(err.stderr)}


def lines(s):
    return [line.rstrip() for line in s.splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', required=True)
    parser.add_argument('--rvm', required=True)
    parser.add_argument('--sdk-archive')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = {'schema': 1, 'purpose': 'numeric F77S native release SSX/TZX manifest and ZX-UX execution',
              'not_hardware_validation': True, 'release_script_sha256': sha(ROOT/'tools/release.py'),
              'translator_sha256': sha(ROOT/'rfortranc/translator.py'), 'rvm_sha256': sha(args.rvm),
              'sdk_archive_sha256': sha(args.sdk_archive) if args.sdk_archive else None,
              'cases': []}
    with tempfile.TemporaryDirectory(prefix='f77s-release-check-') as tmp:
        out = Path(tmp)/'artifacts'
        names = list(EXPECTED)
        build = command([sys.executable, str(ROOT/'tools/release.py'), '--sdk', args.sdk,
                         '--native', '--out', str(out), '--only', *names])
        report['release_build'] = build
        records = json.loads((out/'manifest.json').read_text()) if build['exit_code'] == 0 else []
        report['manifest'] = records
        tape_names = [r['tape_name'].upper() for r in records]
        for name in names:
            meta = next((r for r in records if r['program'] == name), None)
            ssx, tzx = out/(name+'.ssx'), out/(name+'.tzx')
            ssx_good = ssx.is_file() and ssx.read_bytes().startswith(b'SSX1')
            tzx_good = tzx.is_file() and tzx.read_bytes().startswith(b'ZXTape!\x1a')
            emulator = command([sys.executable, args.rvm, '--headless', '--text', '--frames',
                                '1000', str(ssx)]) if ssx_good else None
            actual = lines(emulator['stdout']) if emulator else []
            passed = bool(meta and ssx_good and tzx_good and emulator
                          and emulator['exit_code'] == 0 and '(exit)' in emulator['stderr']
                          and actual == EXPECTED[name] and meta['standard_mode'] == 'f77s'
                          and meta['native'] is True
                          and meta['ssx_sha256'] == sha(ssx)
                          and meta['tzx_sha256'] == sha(tzx)
                          and meta['source_sha256'] == sha(ROOT/'tests/fortran'/(name+'.f'))
                          and len(set(tape_names)) == len(tape_names))
            report['cases'].append({'name': name, 'source_sha256': sha(ROOT/'tests/fortran'/(name+'.f')),
                                    'expected_lines': EXPECTED[name], 'observed_lines': actual,
                                    'ssx_sha256': sha(ssx) if ssx_good else None,
                                    'tzx_sha256': sha(tzx) if tzx_good else None,
                                    'emulator': emulator, 'passed': passed})
            print('PASS' if passed else 'FAIL', name, flush=True)
    report['result'] = {'passed': sum(c['passed'] for c in report['cases']),
                        'total': len(EXPECTED)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
    print('RESULT', report['result'], flush=True)
    return 0 if report['result']['passed'] == report['result']['total'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
