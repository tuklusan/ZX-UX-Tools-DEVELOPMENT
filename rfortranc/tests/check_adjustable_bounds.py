#!/usr/bin/env python3
"""Prove malformed adjustable dummy access terminates ZX-UX, not memory corruption.

All tests compile actual Z80/SSX and execute against matching ZX-UX kernel in rvm.
This is a narrow safety regression, not complete ANSI F77S certification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = {
    'declared_extent_exceeds_tail': (
        'f77s_dmadj.f', '      N=3\n', '      N=4\n'),
    'assumed_size_access_exceeds_tail': (
        'f77s_dmstar.f', '      B(2)=B(2)+30\n', '      B(3)=B(3)+30\n'),
    'callee_changes_extent': (
        'f77s_dmadj.f', '      B(2)=B(2)+38\n',
        '      N=4\n      B(2)=B(2)+38\n'),
    'rank2_declared_last_extent_exceeds_storage': (
        'f77s_dm2ad.f', '      N=3\n', '      N=4\n'),
    'rank3_assumed_size_out_of_storage': (
        'f77s_dm3st.f', '      B(2,2,2)=B(2,2,2)+34\n',
        '      B(2,2,3)=B(2,2,3)+34\n'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    try:
        proc = subprocess.run(args, text=True, capture_output=True, timeout=75)
        return {'args': [str(x) for x in args], 'exit_code': proc.returncode,
                'stdout': proc.stdout, 'stderr': proc.stderr}
    except subprocess.TimeoutExpired as exc:
        return {'args': [str(x) for x in args], 'exit_code': None,
                'timeout': True, 'stdout': str(exc.stdout), 'stderr': str(exc.stderr)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', required=True)
    p.add_argument('--rvm', type=Path, required=True)
    p.add_argument('--sdk-archive', type=Path)
    p.add_argument('--report', type=Path, required=True)
    opts = p.parse_args()
    report = {'schema': 1, 'purpose': 'adjustable F77S dummy bounds negative execution',
              'expected_rvm_exit_code': 2, 'not_f77s_conformance': True,
              'source_translator_sha256': sha(ROOT/'rfortranc/translator.py'),
              'rvm_sha256': sha(opts.rvm),
              'sdk_archive_sha256': sha(opts.sdk_archive) if opts.sdk_archive else None,
              'cases': []}
    with tempfile.TemporaryDirectory(prefix='f77s-adjust-bounds-') as temp:
        for name, (filename, needle, replacement) in FIXTURES.items():
            original = ROOT/'tests/fortran'/filename
            original_text = original.read_text(encoding='utf-8')
            if original_text.count(needle) != 1:
                raise RuntimeError('fixture has changed; expected exactly one occurrence: '+name)
            source = Path(temp)/(name+'.f')
            source.write_text(original_text.replace(needle, replacement), encoding='utf-8')
            ssx = source.with_suffix('.ssx')
            compile_cmd = [sys.executable, str(ROOT/'bin/rfortranc'), '--std', 'f77s',
                           '--native', '--sdk', opts.sdk, '-o', str(ssx), str(source)]
            compiled = run(compile_cmd)
            emu = run([sys.executable, str(opts.rvm), '--headless', '--text',
                       '--frames', '1000', str(ssx)]) if compiled['exit_code'] == 0 and ssx.exists() else None
            passed = bool(emu and emu['exit_code'] == 2 and '(exit)' in emu['stderr']
                          and ssx.read_bytes().startswith(b'SSX1'))
            report['cases'].append({'name': name, 'source_sha256': sha(source),
                                    'ssx_sha256': sha(ssx) if ssx.exists() else None,
                                    'compile': compiled, 'emulator': emu, 'passed': passed})
            print(('PASS' if passed else 'FAIL'), name, flush=True)
    report['result'] = {'passed': sum(x['passed'] for x in report['cases']),
                        'total': len(report['cases'])}
    opts.report.parent.mkdir(parents=True, exist_ok=True)
    opts.report.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('RESULT', report['result'], flush=True)
    return 0 if report['result']['passed'] == report['result']['total'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
