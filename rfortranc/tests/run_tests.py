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
    p.add_argument('--sdk', required=True, help='ZX-UX SDK source root or dist/sdk/bin')
    p.add_argument('--rvm', help='path to packaged ZX-UX rvm; omit to test compile only')
    args = p.parse_args(argv)
    failures = []
    with tempfile.TemporaryDirectory(prefix='rfortranc-tests-') as td:
        tmp = Path(td)
        for name, expected in PROGRAMS.items():
            src = ROOT / 'tests/fortran' / (name + '.f')
            binary = tmp / (name + '.ssx')
            cmd = [sys.executable, str(ROOT / 'bin/rfortranc'), '--sdk', args.sdk,
                   '--native', '-o', str(binary), str(src)]
            r = run(cmd)
            if r.returncode or not binary.is_file() or binary.read_bytes()[:4] != b'SSX1':
                failures.append(name + ': compilation failed: ' + r.stderr + r.stdout)
                continue
            if args.rvm:
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
            r = run([sys.executable, str(ROOT / 'bin/rfortranc'), '--sdk', args.sdk,
                     '-o', str(out), str(src)])
            if not r.returncode or out.exists():
                failures.append(name + ': invalid input not rejected')
            else:
                print('PASS', name)
        src = ROOT / 'tests/fortran/hello.f'
        tape = tmp / 'hello.tzx'
        r = run([sys.executable, str(ROOT / 'bin/rfortranc'), '--sdk', args.sdk,
                 '--native', '--tzx', '-o', str(tape), str(src)])
        if r.returncode or tape.read_bytes()[:8] != b'ZXTape!\x1a':
            failures.append('tzx: packaging failed: ' + r.stderr)
        else:
            print('PASS tzx')
    if failures:
        for fail in failures:
            print('FAIL', fail, file=sys.stderr)
    total = len(PROGRAMS) + len(NEGATIVE) + 1
    print('%d/%d checks passed' % (total - len(failures), total))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
