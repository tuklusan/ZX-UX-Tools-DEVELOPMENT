#!/usr/bin/env python3
"""Compile and boot FORTRAN programs on ZX-UX (no syscall mocks)."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

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
}
NEGATIVE = {
    'undefined-label': 'PROGRAM A\nINTEGER N\nGOTO 70\nEND\n',
    'undefined-variable': 'PROGRAM A\nN = 123\nEND\n',
    'unsupported-format': 'PROGRAM A\nFORMAT (I6)\nEND\n',
}


def run(args):
    return subprocess.run(args, text=True, capture_output=True, timeout=150)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--sdk', help='ZX-UX SDK source root or dist/sdk/bin')
    p.add_argument('--frontend-only', action='store_true', help='test parser/lowering without SDK')
    p.add_argument('--rvm', help='path to packaged ZX-UX rvm; omit to test compile only')
    args = p.parse_args(argv)
    if not args.frontend_only and not args.sdk:
        p.error('--sdk is required unless --frontend-only is specified')
    failures = []
    with tempfile.TemporaryDirectory(prefix='rfortranc-tests-') as td:
        tmp = Path(td)
        for name, expected in PROGRAMS.items():
            src = ROOT / 'tests/fortran' / (name + '.f')
            binary = tmp / (name + '.ssx')
            if args.frontend_only:
                binary = tmp / (name + '.c')
                cmd = [sys.executable, str(ROOT / 'bin/rfortranc'), '--emit-c',
                       '-o', str(binary), str(src)]
            else:
                cmd = [sys.executable, str(ROOT / 'bin/rfortranc'), '--sdk', args.sdk,
                       '--native', '-o', str(binary), str(src)]
            r = run(cmd)
            if r.returncode or not binary.is_file() or (not args.frontend_only and binary.read_bytes()[:4] != b'SSX1') or (args.frontend_only and b'int main(void)' not in binary.read_bytes()):
                failures.append(name + ': compilation failed: ' + r.stderr + r.stdout)
                continue
            if args.rvm and not args.frontend_only:
                emu = run([sys.executable, args.rvm, '--headless', '--text',
                           '--frames', '2000', str(binary)])
                if emu.returncode or '(exit)' not in emu.stderr or expected not in emu.stdout:
                    failures.append(name + ': emulation mismatch: ' + emu.stderr + emu.stdout)
                    continue
            print('PASS', name)
        for name, source in NEGATIVE.items():
            src = tmp / (name + '.f')
            src.write_text(source)
            out = tmp / (name + '.ssx')
            cmd = [sys.executable, str(ROOT / 'bin/rfortranc')]
            if args.frontend_only:
                cmd.extend(['--emit-c'])
                out = tmp / (name + '.c')
            else:
                cmd.extend(['--sdk', args.sdk])
            r = run(cmd + ['-o', str(out), str(src)])
            if not r.returncode or out.exists():
                failures.append(name + ': invalid input not rejected')
            else:
                print('PASS', name)
        if not args.frontend_only:
            src = ROOT / 'tests/fortran/hello.f'
            tape = tmp / 'hello.tzx'
            r = run([sys.executable, str(ROOT / 'bin/rfortranc'), '--sdk', args.sdk,
                     '--native', '--tzx', '-o', str(tape), str(src)])
            if r.returncode or not tape.exists() or tape.read_bytes()[:8] != b'ZXTape!\x1a':
                failures.append('tzx: packaging failed: ' + r.stderr)
            else:
                print('PASS tzx')
    if failures:
        for fail in failures:
            print('FAIL', fail, file=sys.stderr)
    total = len(PROGRAMS) + len(NEGATIVE) + (0 if args.frontend_only else 1)
    print('%d/%d checks passed' % (total - len(failures), total))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
