#!/usr/bin/env python3
"""Actual ZX-UX Z80 SSX/TZX build and real-tape pulse execution in RVM.

This tests the emulator's ROM cassette path; it is not a physical Spectrum test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=240)
    return {'argv': [str(x) for x in args], 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', type=Path, required=True)
    p.add_argument('--rvm', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    source = ROOT/'tests/fortran/f77s_stopmsg.f'
    with tempfile.TemporaryDirectory(prefix='f77s-realtape-') as temp:
        ssx = Path(temp)/'stopmsg.ssx'
        tzx = Path(temp)/'stopmsg.tzx'
        cmd = [sys.executable, str(ROOT/'bin/rfortranc'), '--std', 'f77s',
               '--sdk', str(a.sdk), '--native']
        compile_ssx = run(cmd + ['-o', str(ssx), str(source)])
        compile_tzx = run(cmd + ['--tzx', '--tape-name', 'STOPMSG',
                                  '-o', str(tzx), str(source)])
        emulator = run([sys.executable, str(a.rvm), '--headless', '--text',
                        '--real-tape', '--no-cache', '--frames', '1500', str(ssx)]) if ssx.is_file() else None
        report = {
            'schema': 1, 'scope': 'emulated 48K Spectrum full ZX-UX boot and EAR-pulse cassette load',
            'physical_hardware_tested': False, 'not_live_peak_ram_measurement': True,
            'source_sha256': sha256(source),
            'compiler_sha256': sha256(ROOT/'rfortranc/translator.py'),
            'rvm_sha256': sha256(a.rvm),
            'ssx_bytes': ssx.stat().st_size if ssx.is_file() else None,
            'ssx_sha256': sha256(ssx) if ssx.is_file() else None,
            'tzx_bytes': tzx.stat().st_size if tzx.is_file() else None,
            'tzx_sha256': sha256(tzx) if tzx.is_file() else None,
            'compile_ssx': compile_ssx, 'compile_tzx': compile_tzx,
            'rvm_real_tape': emulator
        }
        report['passed'] = bool(compile_ssx['exit_code'] == compile_tzx['exit_code'] == 0
                                and ssx.is_file() and ssx.read_bytes().startswith(b'SSX1')
                                and tzx.is_file() and tzx.read_bytes().startswith(b'ZXTape!\x1a')
                                and emulator and emulator['exit_code'] == 0
                                and emulator['stdout'].splitlines()[:2] == ['  42', 'STOP DONE']
                                and 'booted from the tape' in emulator['stderr']
                                and '(exit)' in emulator['stderr'])
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('PASS' if report['passed'] else 'FAIL', 'real-tape/no-cache full boot and ROM load', flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
