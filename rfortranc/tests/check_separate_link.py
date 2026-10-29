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
        commons = [SRC/'common_main.f', SRC/'common_sub.f']
        common_out = out/'common.ssx'
        record['common_sources'] = {src.name: sha(src) for src in commons}
        record['common_compile'] = run(command+['--object-dir', str(out/'common-objects'),
                                                '-o', str(common_out)]+list(map(str, commons)))
        if record['common_compile']['exit_code'] == 0 and common_out.exists():
            record['common_ssx_sha256'] = sha(common_out)
            record['common_ssx_bytes'] = common_out.stat().st_size
            record['common_objects'] = {f.name: sha(f) for f in (out/'common-objects').glob('*.sso')}
            record['common_target_run'] = run([sys.executable,a.rvm,'--headless',
                                                '--text','--frames','1000',str(common_out)])
        record['common_host_compile'] = run(['gfortran','-std=legacy','-ffixed-form',
                                             '-o',str(out/'common.host')]+list(map(str, commons)))
        if record['common_host_compile']['exit_code'] == 0:
            record['common_host_run'] = run([str(out/'common.host')])
        blank = ROOT/'tests/fortran/f77s_blankvary.f'
        blank_dest = out/'blank.ssx'
        blank_objects = out/'blank-objects'
        record['blank_source_sha256'] = sha(blank)
        record['blank_compile'] = run(command+['--max','12000','--object-dir',str(blank_objects),
                                               '-o',str(blank_dest),str(blank)])
        if record['blank_compile']['exit_code'] == 0 and blank_dest.exists():
            record['blank_ssx_bytes'] = blank_dest.stat().st_size
            record['blank_ssx_sha256'] = sha(blank_dest)
            record['blank_objects'] = {f.name:{'sha256':sha(f),'bytes':f.stat().st_size}
                                        for f in blank_objects.glob('*.sso')}
            record['blank_target_run'] = run([sys.executable,a.rvm,'--headless','--text',
                                                '--frames','1000',str(blank_dest)])
        record['blank_host_compile'] = run(['gfortran','-std=legacy','-ffixed-form',
                                            '-o',str(out/'blank.host'),str(blank)])
        if record['blank_host_compile']['exit_code'] == 0:
            record['blank_host_run'] = run([str(out/'blank.host')])
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
    common_native = record.get('common_target_run', {})
    common_host = record.get('common_host_run', {})
    common_ok = (len(record.get('common_objects', {})) == 2 and
                 common_native.get('exit_code') == 0 and '(exit)' in common_native.get('stderr','') and
                 common_host.get('exit_code') == 0 and
                 lines(common_native.get('stdout','')) == lines(common_host.get('stdout','')) == EXPECT)
    record['common_result'] = {'passed': common_ok, 'expected_lines': EXPECT}
    blank_native = record.get('blank_target_run', {})
    blank_host = record.get('blank_host_run', {})
    blank_expected=['   5  42   7']
    blank_ok=(len(record.get('blank_objects',{}))==3 and
              record.get('blank_ssx_bytes',12001) <= 12000 and
              blank_native.get('exit_code')==0 and '(exit)' in blank_native.get('stderr','') and
              blank_host.get('exit_code')==0 and
              lines(blank_native.get('stdout',''))==lines(blank_host.get('stdout',''))==blank_expected)
    record['blank_result']={'passed':blank_ok,'expected_lines':blank_expected}
    ok = ok and common_ok and blank_ok
    record['result'] = {'passed': bool(ok), 'expected_lines': EXPECT}
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print(('PASS' if ok else 'FAIL')+' independent SSO linking / Z80 / TZX / host differential')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
