#!/usr/bin/env python3
"""Execute real Z80 SSO separate/link-only and reject cross-build F77S ABI mismatches."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'tests/fortran/separate'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd):
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=150)
        return {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    except subprocess.TimeoutExpired:
        return {'exit_code': None, 'timeout': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', required=True)
    parser.add_argument('--rvm', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    checks = {}
    with tempfile.TemporaryDirectory(prefix='f77s-abi-') as temp:
        temp = Path(temp)
        cli = [sys.executable, str(ROOT/'bin/rfortranc'), '--std', 'f77s',
               '--sdk', args.sdk, '--native']
        original = temp/'first.ssx'
        home = temp/'integer-objs'
        primary = run(cli + ['--separate', '--object-dir', str(home), '-o', str(original),
                             str(SRC/'main.f'), str(SRC/'step.f')])
        objects = sorted(home.glob('*.sso'))
        checks['built_two_tagged_sso'] = primary['exit_code'] == 0 and len(objects) == 2 and all(
            o.with_suffix('.f77s-abi.json').is_file() for o in objects)
        linked = temp/'relinked.ssx'
        link = run(cli + ['--link-only', '-o', str(linked)] + list(map(str, objects)))
        checks['strict_relink_bit_exact'] = link['exit_code'] == 0 and linked.is_file() and digest(original) == digest(linked)
        emulator = run([sys.executable, args.rvm, '--headless', '--text', '--frames', '700', str(linked)]) if linked.is_file() else {}
        ref_compile = run(['gfortran', '-std=legacy', '-ffixed-form', '-o', str(temp/'host'),
                           str(SRC/'main.f'), str(SRC/'step.f')])
        host = run([str(temp/'host')]) if ref_compile['exit_code'] == 0 else {}
        checks['real_z80_matches_gfortran'] = (emulator.get('exit_code') == host.get('exit_code') == 0 and
              emulator.get('stdout','').strip() == host.get('stdout','').strip() == '42' and
              '(exit)' in emulator.get('stderr',''))
        # Build a second, individually valid program with a REAL dummy of
        # the *same external symbol name*, then link the original INTEGER
        # caller against its incompatible REAL callee.
        real_main = temp/'rmain.f'
        real_main.write_text('      PROGRAM SEPM\n      REAL N\n      N=40.0\n      CALL STEPER(N)\n      END\n')
        real_step = temp/'rstep.f'
        real_step.write_text('      SUBROUTINE STEPER(N)\n      REAL N\n      N=N+2.0\n      END\n')
        real_home = temp/'real-objs'
        real_compile = run(cli+['--separate', '--object-dir', str(real_home),
                                '-o', str(temp/'real.ssx'),str(real_main),str(real_step)])
        mismatched = temp/'mismatch.ssx'
        bad = run(cli+['--link-only','-o',str(mismatched),str(objects[0]),
                       str(real_home/'01_STEPER.sso')])
        checks['reject_differently_compiled_dummy_type'] = (real_compile['exit_code'] == 0 and
            bad['exit_code'] != 0 and 'F77S ABI mismatch for STEPER' in bad['stderr'] and not mismatched.exists())
        # Swapping or editing SSO bytes must not quietly reuse a stale ABI
        # tag. Modifying one byte preserves a plausible object filename.
        modified = bytearray(objects[1].read_bytes())
        modified[-1] ^= 1
        objects[1].write_bytes(modified)
        tampered = temp/'tampered.ssx'
        changed = run(cli+['--link-only','-o',str(tampered)]+list(map(str,objects)))
        checks['reject_stale_object_hash'] = (changed['exit_code'] != 0 and
            'object SHA-256 mismatch' in changed['stderr'] and not tampered.exists())
        objects[1].write_bytes(bytes(x ^ 1 if i == len(modified)-1 else x
                                      for i,x in enumerate(modified)))
        # Missing one of several tags must be an error, not a silent fallback.
        tag = objects[1].with_suffix('.f77s-abi.json')
        tag.rename(tag.with_suffix('.json.disabled'))
        mix = temp/'mixed.ssx'
        partial = run(cli+['--link-only','-o',str(mix)]+list(map(str,objects)))
        checks['reject_mixed_untagged_objects'] = (partial['exit_code'] != 0 and
            'mixed tagged and untagged' in partial['stderr'] and not mix.exists())
        objects[0].with_suffix('.f77s-abi.json').unlink()
        unverified = temp/'untagged.ssx'
        reject = run(cli+['--link-only','-o',str(unverified)]+list(map(str,objects)))
        checks['reject_untagged_by_default'] = (reject['exit_code'] != 0 and
            'ABI tags missing' in reject['stderr'] and not unverified.exists())
        allow = run(cli+['--link-only','--allow-untagged-objects','-o',str(unverified)]+list(map(str,objects)))
        checks['legacy_explicit_opt_in'] = (allow['exit_code'] == 0 and
            unverified.is_file() and digest(unverified) == digest(original))
        record = {'schema': 1, 'source_commit_required': 'tagged F77S object compilation',
                  'sdk_source': str(args.sdk), 'compiler_sha256': digest(ROOT/'rfortranc/translator.py'),
                  'driver_sha256': digest(ROOT/'rfortranc/driver.py'),
                  'abi_sha256': digest(ROOT/'rfortranc/abi.py'),
                  'check': checks, 'primary': primary, 'link': link,
                  'real_build': real_compile, 'mismatch': bad, 'tampered': changed,
                  'partial': partial, 'unverified': reject, 'legacy_opt_in': allow,
                  'native': emulator, 'host': host,
                  'source_sha256': {p.name: digest(p) for p in (SRC/'main.f', SRC/'step.f')},
                  'physical_spectrum_tested': False,
                  'result': {'passed': sum(checks.values()), 'total': len(checks)}}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(record, sort_keys=True, indent=2)+'\n')
    for label, good in checks.items():
        print('PASS' if good else 'FAIL', label, flush=True)
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
