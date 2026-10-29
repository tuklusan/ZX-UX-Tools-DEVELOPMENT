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
    'f77s_blankvary': '   5  42   7',
    'f77s_chcommon': 'HI',
    'f77s_chcomarr': 'AB  CD',
    'f77s_fc3': '  42',
    'f77s_fc4': '  42',
    'f77s_fc5': '***',
    'f77s_equiv': '  42  42  11  42',
    'f77s_chequiv': 'BB  CC  CC  AA',
    'f77s_eqdata': '   41   42',
    'f77s_eqchdat': 'BB  CC',
    'f77s_save': '  42',
    'f77s_char': '>  HI   <',
    'f77s_charread': '>XYZ  <',
    'f77s_burkprime': '  25',
    'f77s_dmarr': '  40',
    'f77s_dmchain': '  30',
    'f77s_dmreal': '  42',
    'f77s_burkvec': '  65',
    'f77s_burksort': '  -1',
    'f77s_dmseq': '  42',
    'f77s_dmidx': '  42',
    'f77s_dmadj': '  42',
    'f77s_dmstar': '  38',
    'f77s_dmalt': '   9',
    'f77s_burkadj': '  28',
    'f77s_dm2ad': '  42',
    'f77s_leaddim': '    6   42',
    'f77s_cbound': '    6   42',
    'f77s_ldstar': '    6   99',
    'f77s_ld3star': '    8   77',
    'f77s_dm3ad': '  42',
    'f77s_dm2st': '  42',
    'f77s_dm3st': '  42',
    'f77s_burkmm': '    7   22   23',
    'f77s_burkflip': '   6   5   2   1',
    'f77s_dm2el': '  42   5',
    'f77s_dm3el': '  42  10   8',
    'f77s_subdata': '  42',
    'f77s_subarr': '   6',
    'f77s_burkcum': '   3   6   9  -2   5',
    'f77s_burkdot': '  35',
    'f77s_burkgcd': '  14',
    'f77s_chdata': 'XY',
    'f77s_imchar': 'A/B',
    'f77s_charg': 'HI',
    'f77s_charray': 'XY OK',
    'f77s_chdummy': 'XY CC HI',
    'f77s_arrread': 'NO XYZ',
    'f77s_chr3d': '42GG',
    'f77s_realio': '   -3.25',
    'f77s_burkmean': '    2.50',
    'f77s_burkmin': '   -3.25    4.00',
    'f77s_burkreal': '   27.50',
    'f77s_burkl1': '   12.00',
    'f77s_logio': '   F   T',
    'f77s_burkvar': '    2.50',
    'f77s_burkscale': '    2.00   -4.00    6.00    8.00  -10.00',
    'f77s_burkl2': '    5.00',
    'f77s_burkcopy': '   -2.00    3.25',
    'f77s_burkrsrt': '    3.00   -1.00',
    'f77s_expout': '  0.123400E+02',
    'f77s_datado': '  42',
    'f77s_dotype': '   12',
    'f77s_int': '     3    -3     0     0    -2',
    'f77s_datcom': '  42  41',
    'f77s_invtrig': '   0.5236   1.0472   0.4636   0.5463   2.0000',
    'f77s_hyper': '   0.5211   1.1276   0.4621   0.6931',
    'f77s_rmath': '   2.3562  -2.3562   1.5000  -1.5000   1.5708',
    'f77s_sigdim': '     7    -7     7     0',
    'f77s_maxmin': '    7   -4    3   -2',
    'f77s_modint': '      2     -2      2     -1',
    'f77s_ipow': '   16384  -32768       1       1     -27',
    'f77s_imul': '  -32768    -240',
    'f77s_idiv': '  -16384      -3      -2',
    'f77s_iaddsub': '  -32767   32766  -32768',
    'f77s_trig': '     0.48     0.88     1.65     0.50    -0.48',
    'f77s_stfn': '    12.00    99.00',
    'f77s_rpow': '     8.00     3.00     4.00     0.25    -8.00   512.00',
    'f77s_assgn': '  42',
    'f77s_ewdee': '   0.123400E+003    0.125000E-001   -0.123000E-004',
    'f77s_eread': '   123.40     5.00',
    'f77s_bnbz': '  420   12',
    'f77s_chlit': 'HELLO',
    'f77s_fmtch': '   42',
    'f77s_barefn': '    9.00',
    'f77s_iodo': '   2   4   6',
    'f77s_vario': '   1   2',
    'f77s_varreal': '     4.00    -3.75',
    'f77s_varlc': '   T   F',
    'f77s_varexp': '   0.123400E+003',
    'f77s_iord': '   1   2   3   4',
    'f77s_numcv': '   321    -3    -2',
    'f77s_idxexpr': '  20',
    'f77s_pscale': '   12.30    1.23',
    'f77s_f6': '    1.234567   -0.000125    9.999999',
    'f77s_pause': '  42',
    'f77s_exintr': '     1.48',
    'f77s_procdum': '    9.00    6.00',
    'f77s_iprocdum': '     9     6',
    'f77s_frevert': '   1   2',
    'f77s_unitvar': '   42',
    'f77s_seqend2': '  -42   17   -1',
    'f77s_seqtri': '     -42       0   32767       0',
    'f77s_seqquad': '      42       0   32767     -17',
    'f77s_seqreal': '   -3.50',
    'f77s_seqlog': '  T',
    'f77s_seqchar': 'WXYZ',
    'f77s_seqmix': '    -42     1.25',
    'f77s_seqmixend': '    -42     1.25    0',
    'f77s_backend': '  -42',
    'f77s_seqpair': '  -42   17',
    'f77s_iostat': '   23   -1',
    'f77s_endgoto': '    7    7',
    'f77s_endfile': '   23',
    'f77s_sequnio': '  -17',
    'f77s_direct2': '  -42   17',
    'f77s_directio': '    9',
    'f77s_fmtchr': '   12   34',
    'f77s_afread': '   12   34',
    'f77s_vuniio': '   1   2',
    'f77s_nestrevert': '  1   2    3   4    5',
    'f77s_afmt': '    42',
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
    'data-int-overflow': 'PROGRAM A\nINTEGER N\nDATA N/32768/\nEND\n',
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
    p.add_argument('--only', nargs='+', choices=sorted(PROGRAMS),
                   help='run only listed positive programs, omitting negatives and TZX')
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
            if args.only and name not in args.only:
                continue
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
                if name in ('f77s_read', 'f77s_repeat', 'f77s_charread', 'f77s_arrread', 'f77s_realio', 'f77s_logio', 'f77s_eread', 'f77s_bnbz', 'f77s_iord', 'f77s_pscale', 'f77s_pause', 'f77s_frevert', 'f77s_nestrevert', 'f77s_f6', 'f77s_vario', 'f77s_varreal', 'f77s_varlc', 'f77s_varexp', 'f77s_unitvar', 'f77s_vuniio', 'f77s_fmtchr', 'f77s_afread'):
                    keys = {'f77s_read': '0042 007\n', 'f77s_repeat': '003 005 010\n',
                            'f77s_charread': 'XYZ\n', 'f77s_arrread': 'XYZ\n', 'f77s_realio': '   -3.25\n  001234\n', 'f77s_logio': '   F   T\n', 'f77s_eread': '   0.123400E+003   0.500000E+001\n', 'f77s_bnbz': '  42  12  \n', 'f77s_iord': '001002003\n', 'f77s_pscale': '   12.30    1.23\n', 'f77s_pause': 'go\n', 'f77s_unitvar': '  42\n', 'f77s_fmtchr': '  12  34\n', 'f77s_afread': '  12  34\n', 'f77s_vuniio': '001002\n003004\n005\n', 'f77s_frevert': '001002\n003004\n005\n', 'f77s_nestrevert': '  1   2    3   4    5\n   6    7   8    9\n  10\n', 'f77s_f6':'    1.234567   -0.000125    9.999999\n', 'f77s_vario':'001002\n003004\n005\n', 'f77s_varreal':'   1.25   2.50\n  -3.75   4.00\n', 'f77s_varlc':'  T  F\n  T\nABCDEF\nGHI\n', 'f77s_varexp':'   0.123400E+003\n   0.500000E+001\n'}
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
        for name, source in (NEGATIVE.items() if not args.only else []):
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
        if not args.frontend_only and not args.only:
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
