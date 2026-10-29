#!/usr/bin/env python3
"""Independent host and native separate-SSO F77S linkage proof.

Compile each unit to its own relocatable SSO, link through the actual ZX-UX
SDK, execute in RVM and compare stdout with gfortran. Not physical hardware.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'tests/fortran/separate'
FILES = [SRC/'main.f', SRC/'step.f']
EXPECT = ['  42']


def run(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=180)
    return {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', required=True)
    p.add_argument('--rvm', required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    record = {'schema': 1, 'scope': 'independent compiled Z80 SSO units linked with ZX-UX rld',
              'not_hardware_test': True, 'compiler_sha256': sha(ROOT/'rfortranc/translator.py'),
              'driver_sha256': sha(ROOT/'rfortranc/driver.py'),
              'sdk_linker_sha256': sha(Path(a.sdk)/'rld.py'),
              'source_sha256': {f.name: sha(f) for f in FILES}}
    with tempfile.TemporaryDirectory(prefix='f77s-separate-') as d:
        out = Path(d)
        ssx = out/'sepm.ssx'
        tzx = out/'sepm.tzx'
        objects = out/'objects'
        command = [sys.executable, str(ROOT/'bin/rfortranc'), '--std', 'f77s',
                   '--sdk', a.sdk, '--native', '--separate']
        built = run(command+['--object-dir', str(objects), '-o', str(ssx)]+list(map(str, FILES)))
        record['native_compile'] = built
        if built['exit_code'] == 0 and ssx.is_file():
            record['ssx_sha256'] = sha(ssx)
            record['ssx_bytes'] = ssx.stat().st_size
            record['objects'] = {f.name: {'sha256': sha(f), 'bytes': f.stat().st_size}
                                 for f in objects.glob('*.sso')}
            record['target_run'] = run([sys.executable, a.rvm, '--headless', '--text', '--frames', '1000', str(ssx)])
            record['tape_compile'] = run(command+['--tzx', '-o', str(tzx)]+list(map(str, FILES)))
            record['tzx_sha256'] = sha(tzx) if tzx.is_file() else None
            record['valid_tzx_header'] = tzx.is_file() and tzx.read_bytes().startswith(b'ZXTape!\x1a')
            record['low_max'] = run(command+['--max', '1000', '-o', str(out/'small.ssx')]+list(map(str, FILES)))
            record['low_max_did_not_leave_binary'] = not (out/'small.ssx').exists()
        record['host_compile'] = run(['gfortran', '-std=legacy', '-ffixed-form', '-o', str(out/'ref')]+list(map(str, FILES)))
        if record['host_compile']['exit_code'] == 0:
            record['host_run'] = run([str(out/'ref')])
    def lines(output):
        return [s.rstrip() for s in output.splitlines() if s.strip()]
    native = record.get('target_run', {})
    host = record.get('host_run', {})
    ok = (len(record.get('objects', {})) == 2 and
          record.get('valid_tzx_header', False) and
          record.get('low_max_did_not_leave_binary', False) and
          record.get('low_max', {}).get('exit_code') != 0 and
          record.get('tape_compile', {}).get('exit_code') == 0 and
          native.get('exit_code') == 0 and '(exit)' in native.get('stderr', '') and
          host.get('exit_code') == 0 and
          lines(native.get('stdout', '')) == lines(host.get('stdout', '')) == EXPECT)
    record['result'] = {'passed': bool(ok), 'expected_lines': EXPECT}
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print(('PASS' if ok else 'FAIL')+' independent SSO linking / Z80 / TZX / host differential')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
