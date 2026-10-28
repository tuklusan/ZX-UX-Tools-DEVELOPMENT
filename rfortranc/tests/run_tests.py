#!/usr/bin/env python3
"""Compile and optionally execute FORTRAN tests; emit reproducible evidence.

Frontend-only checks are *not* Z80, SDK, or runtime conformance tests.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
PROGRAMS = {
    'hello': 'Hello FORTRAN on ZX-UX',
    'factorial': '720',
    'arrays': '55',
    'branch': 'NEG',
    'function': '14',
    'prime': 'PRIME',
    'backstep': '9',
    'bases': '1101',
    'nested': '18',
    'strings': "John's ZX-UX OK",
    'realcmp': 'REAL OK',
    'subcall': '8',
    'byref': '8',
    'realbyref': 'REF REAL OK',
    'fixedcomment': '3',
    'arithmetic_if': '  99',
    'computed_goto': '  44',
    'format_write': 'N=****',
    'fixed_continue': '  15',
    'f77s_fmt': '  42',
    'f77s_data': '  9',
    'f77s_implicit': '  3',
    'f77s_real': '  2',
    'f77s_2d': '  43',
    'f77s_3d': ' 11',
    'f77s_read': '  49',
    'f77s_repeat': '  18',
    'f77s_dim': '  42',
    'f77s_common': '  42',
    'f77s_comarr': '  43',
    'f77s_blank': '  42',
    'f77s_fc3': '  42',
    'f77s_fc4': '  42',
    'f77s_fc5': '***',
    'f77s_equiv': '  42  42  11  42',
    'f77s_save': '  42',
    'f77s_char': '>  HI   <',
    'f77s_charread': '>XYZ  <',
    'f77s_burkprime': '  25',
}
NEGATIVE = {
    'undefined-label': 'PROGRAM A\nINTEGER N\nGOTO 70\nEND\n',
    'undefined-variable': 'PROGRAM A\nN = 123\nEND\n',
    'unsupported-format': 'PROGRAM A\nFORMAT (I6)\nEND\n',
    'real-read': 'PROGRAM A\nREAL X\nREAD *, X\nEND\n',
    'arithmetic-undefined-target': 'PROGRAM A\nINTEGER N\nN=1\nIF (N) 10,20,30\n10 CONTINUE\n20 CONTINUE\nEND\n',
    'computed-undefined-target': 'PROGRAM A\nINTEGER N\nN=1\nGO TO (10,20),N\n10 CONTINUE\nEND\n',
    'computed-real-selector': 'PROGRAM A\nREAL R\nR=1.0\nGO TO (10,20),R\n10 CONTINUE\n20 CONTINUE\nEND\n',
    'write-undefined-format': 'PROGRAM A\nINTEGER N\nN=1\nWRITE (6,10) N\nEND\n',
    'write-bad-descriptor': 'PROGRAM A\nINTEGER N\nN=1\nWRITE (6,10) N\n10 FORMAT(F8.2)\nEND\n',
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def hash_path(path):
    path = Path(path)
    return {'file': str(path), 'sha256': sha256(path.read_bytes()), 'bytes': path.stat().st_size} if path.is_file() else None


def command(argv, timeout):
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, check=False)
        return {'exit_code': proc.returncode, 'stdout': proc.stdout[:8192],
                'stderr': proc.stderr[:8192],
                'seconds': round(time.monotonic() - started, 3)}
    except subprocess.TimeoutExpired as e:
        return {'exit_code': None, 'timeout': True,
                'stdout': (e.stdout or b'').decode('utf-8', 'replace')[:8192],
                'stderr': (e.stderr or b'').decode('utf-8', 'replace')[:8192],
                'seconds': round(time.monotonic() - started, 3)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', help='ZX-UX SDK source root or dist/sdk/bin')
    p.add_argument('--frontend-only', action='store_true', help='parser/lowering only: no ZX-UX execution')
    p.add_argument('--rvm', help='path to the matching built ZX-UX rvm')
    p.add_argument('--rvm-frames', type=int, default=2000)
    p.add_argument('--timeout', type=int, default=90, help='seconds per tool invocation')
    p.add_argument('--report', type=Path, help='write detailed JSON to this path, pass or fail')
    p.add_argument('--sdk-archive', type=Path, help='optional original SDK zip for hash pinning')
    args = p.parse_args(argv)
    if not args.frontend_only and not args.sdk:
        p.error('--sdk is required unless --frontend-only is specified')
    if args.rvm and args.frontend_only:
        p.error('cannot run emulator with --frontend-only')
    if args.timeout < 1 or args.rvm_frames < 1:
        p.error('timeout and rvm-frames must be positive')
    mode = ('frontend-only' if args.frontend_only else
            'sdk+emulator' if args.rvm else 'sdk-compile-only')
    report = {
        'schema': 1,
        'mode': mode,
        'tool': 'rfortranc',
        'python': sys.version.split()[0],
        'platform': platform.platform(),
        'frontend_sha256': hash_path(ROOT / 'rfortranc/translator.py'),
        'driver_sha256': hash_path(ROOT / 'rfortranc/driver.py'),
        'options': {'rvm_frames': args.rvm_frames if args.rvm else None,
                    'timeout_seconds': args.timeout},
        'inputs': {'sdk_archive': hash_path(args.sdk_archive) if args.sdk_archive else None,
                   'rvm': hash_path(args.rvm) if args.rvm else None},
        'cases': [],
    }
    if args.sdk:
        sdk = Path(args.sdk).resolve()
        src = sdk if (sdk / 'ras.py').is_file() else sdk.parent.parent
        report['inputs']['sdk_path'] = str(sdk)
        report['inputs']['compiler'] = hash_path(src / 'rcc/driver.py')
        report['inputs']['assembler'] = hash_path(src / 'ras.py')
        report['inputs']['linker'] = hash_path(src / 'rld.py')
        report['inputs']['tape'] = hash_path(src / 'rtap.py')
        report['inputs']['libc48'] = hash_path(src / 'lib/libc48.ssa')
    failures = []
    with tempfile.TemporaryDirectory(prefix='rfortranc-tests-') as td:
        tmp = Path(td)
        for name, expected in PROGRAMS.items():
            src = ROOT / 'tests/fortran' / (name + '.f')
            ext = '.c' if args.frontend_only else '.ssx'
            binary = tmp / (name + ext)
            cmd = [sys.executable, str(ROOT / 'bin/rfortranc')]
            if name.startswith('f77s_'):
                cmd += ['--std', 'f77s']
            if args.frontend_only:
                cmd += ['--emit-c']
            else:
                cmd += ['--sdk', args.sdk, '--native']
            cmd += ['-o', str(binary), str(src)]
            result = command(cmd, args.timeout)
            artifact = hash_path(binary)
            valid = (result['exit_code'] == 0 and artifact is not None and
                     (binary.read_bytes().startswith(b'int main(void)') or
                      b'int main(void)' in binary.read_bytes()) if args.frontend_only else
                     result['exit_code'] == 0 and artifact is not None and
                     binary.read_bytes().startswith(b'SSX1'))
            case = {'name': name, 'kind': 'positive', 'source': src.name,
                    'source_sha256': sha256(src.read_bytes()),
                    'expected_output_contains': expected,
                    'compile': result, 'artifact': artifact}
            if valid and args.rvm and not args.frontend_only:
                emu_argv = [sys.executable, args.rvm, '--headless', '--text',
                            '--frames', str(args.rvm_frames)]
                if name in ('f77s_read', 'f77s_repeat', 'f77s_charread'):
                    keys = {'f77s_read': '0042 007\n', 'f77s_repeat': '003 005 010\n',
                            'f77s_charread': 'XYZ\n'}
                    emu_argv += ['--keys', keys[name]]
                emu_argv += [str(binary)]
                emu = command(emu_argv, args.timeout)
                valid = (emu['exit_code'] == 0 and '(exit)' in emu['stderr']
                         and expected in emu['stdout'])
                case['emulator'] = emu
            case['passed'] = bool(valid)
            report['cases'].append(case)
            if not valid:
                failures.append(name)
            print('PASS' if valid else 'FAIL', name, flush=True)
        for name, source in NEGATIVE.items():
            src = tmp / (name + '.f')
            src.write_text(source, encoding='utf-8')
            out = tmp / (name + ('.c' if args.frontend_only else '.ssx'))
            cmd = [sys.executable, str(ROOT / 'bin/rfortranc')]
            cmd += ['--emit-c'] if args.frontend_only else ['--sdk', args.sdk]
            result = command(cmd + ['-o', str(out), str(src)], args.timeout)
            valid = result['exit_code'] not in (0, None) and not out.exists()
            report['cases'].append({'name': name, 'kind': 'negative', 'passed': valid,
                                    'source_sha256': sha256(src.read_bytes()), 'compile': result})
            if not valid:
                failures.append(name)
            print('PASS' if valid else 'FAIL', name, flush=True)
        if not args.frontend_only:
            source = ROOT / 'tests/fortran/hello.f'
            tape = tmp / 'hello.tzx'
            cmd = [sys.executable, str(ROOT / 'bin/rfortranc'), '--sdk', args.sdk,
                   '--native', '--tzx', '-o', str(tape), str(source)]
            result = command(cmd, args.timeout)
            valid = (result['exit_code'] == 0 and tape.is_file() and
                     tape.read_bytes().startswith(b'ZXTape!\x1a'))
            report['cases'].append({'name': 'tzx', 'kind': 'packaging', 'passed': bool(valid),
                                    'compile': result, 'artifact': hash_path(tape)})
            if not valid:
                failures.append('tzx')
            print('PASS' if valid else 'FAIL', 'tzx', flush=True)
    report['result'] = {'passed': len(report['cases']) - len(failures),
                        'failed': len(failures), 'total': len(report['cases']),
                        'failed_cases': failures}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print('REPORT', args.report, flush=True)
    print('%d/%d checks passed' % (report['result']['passed'], report['result']['total']), flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
