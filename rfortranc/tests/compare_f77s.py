#!/usr/bin/env python3
"""Compare actual ZX-UX output with gfortran for pinned ANSI subset sources.

This is an integration comparison for the covered programs, not F77S certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = {'f77s_fmt': ['  42'], 'f77s_data': ['  9', '  2'], 'f77s_implicit': ['  3', '  7'], 'f77s_real': ['  2'], 'f77s_2d': ['  43'], 'f77s_3d': [' 11'], 'f77s_read': ['  49'], 'f77s_repeat': ['  3   5  10   18'], 'f77s_dim': ['  42'], 'f77s_common': ['  42'], 'f77s_comarr': ['  43'], 'f77s_blank': ['  42'], 'f77s_blankvary': ['   5  42   7'], 'f77s_chcommon': ['HI'], 'f77s_chcomarr': ['AB  CD'], 'f77s_fc3': ['  42'], 'f77s_fc4': ['  42'], 'f77s_fc5': ['7','  42','***'], 'f77s_equiv': ['  42  42  11  42'], 'f77s_save': ['  42'], 'f77s_char': ['>  HI   <', '>ABC<'], 'f77s_charread': ['>XYZ  <'], 'f77s_burkprime': ['   4', '  25'], 'f77s_dmarr': ['  40'], 'f77s_dmchain': ['  30'], 'f77s_dmreal': ['  42'], 'f77s_burkvec': ['  15  13  11', '  65'], 'f77s_burksort': ['   1   5   9', '   7', '  -1'], 'f77s_dmseq': ['  42'], 'f77s_dmidx': ['  42'], 'f77s_dmadj': ['  42'], 'f77s_dmstar': ['  38'], 'f77s_dmalt': ['   9'], 'f77s_burkadj': ['   5   1  15', '  28'], 'f77s_dm2ad': ['  42'], 'f77s_dm3ad': ['  42'], 'f77s_dm2st': ['  42'], 'f77s_dm3st': ['  42'], 'f77s_burkmm': ['    7   22   23', '    7'], 'f77s_burkflip': ['   6   5   2   1', '   1   6'], 'f77s_dm2el': ['  42   5'], 'f77s_dm3el': ['  42  10   8'], 'f77s_subdata': ['  42', '  42'], 'f77s_subarr': ['   6', '   6'], 'f77s_burkcum': ['   3   6   9  -2   5', '   6  -1   4'], 'f77s_burkdot': ['  35', '  30'], 'f77s_burkgcd': ['   2', '   6', '  14'], 'f77s_chdata': ['A/B', 'AB', 'XY'], 'f77s_imchar': ['A/B'], 'f77s_charg': ['HI'], 'f77s_charray': ['AB C', 'XY OK', 'ABCD', 'ABEF'], 'f77s_chdummy': ['XY CC HI', 'EE'], 'f77s_arrread': ['NO XYZ'], 'f77s_chr3d': ['42GG'], 'f77s_realio': ['   12.50', '   -3.25', '    0.25   -1.75', '   12.34'], 'f77s_burkmean': ['    2.50', '    0.00'], 'f77s_burkmin': ['   -3.25    4.00', '   -2.50    3.75'], 'f77s_burkreal': ['   27.50', '   27.00'], 'f77s_burkl1': ['   12.00', '    7.50'], 'f77s_logio': ['   T   F', '   F   T'], 'f77s_burkvar': ['    2.50', '    1.00', '    0.00'], 'f77s_burkscale': ['    2.00   -4.00    6.00    8.00  -10.00', '    2.00    2.00   -3.00   -4.00  -10.00'], 'f77s_burkl2': ['    5.00', '    4.00', '    3.00', '    1.41', '    0.50', '  100.00', '    0.01'], 'f77s_burkcopy': ['   -2.00    3.25    4.00    0.00    0.00', '    1.00   -2.00    3.25    4.00   -5.00'], 'f77s_burkrsrt': ['    3.00   -1.00    2.00    4.00    0.00', '   -1.00    0.00    2.00    3.00    4.00']}

CASES['f77s_expout'] = ['  0.123400E+02 -0.125000E-01', '  0.000000E+00', '  0.100000E+01', '  0.100000E+03', ' -0.123000E-04']
CASES['f77s_datado'] = ['  42']
CASES['f77s_int'] = ['     3    -3     0     0    -2']
CASES['f77s_datcom'] = ['  42  41']
CASES['f77s_leaddim'] = ['    6   42']
CASES['f77s_cbound'] = ['    6   42']
CASES['f77s_ldstar'] = ['    6   99']
CASES['f77s_ld3star'] = ['    8   77']
CASES['f77s_chequiv'] = ['BB  CC  CC  AA']
CASES['f77s_eqdata'] = ['   41   42']
CASES['f77s_eqchdat'] = ['BB  CC']
CASES['f77s_invtrig'] = ['   0.5236   1.0472   0.4636   0.5463   2.0000']
CASES['f77s_hyper'] = ['   0.5211   1.1276   0.4621   0.6931', '  -3.0000   3.0000   3.0000  -0.4621']
CASES['f77s_rmath'] = ['   2.3562  -2.3562   1.5000  -1.5000   1.5708']
CASES['f77s_sigdim'] = ['     7    -7     7     0', '     2.50    -2.50     5.00     0.00']
CASES['f77s_maxmin'] = ['    7   -4    3   -2', '     3.25    -1.50     7.00    -4.00']
CASES['f77s_trig'] = ['     0.48     0.88     1.65     0.50    -0.48']
CASES['f77s_stfn'] = ['    12.00    99.00']
CASES['f77s_rpow'] = ['     8.00     3.00     4.00     0.25    -8.00   512.00']
CASES['f77s_assgn'] = ['  42']
CASES['f77s_ewdee'] = ['   0.123400E+003    0.125000E-001   -0.123000E-004']
CASES['f77s_eread'] = ['   123.40     5.00']
CASES['f77s_bnbz'] = ['  420   12']
CASES['f77s_chlit'] = ['HELLO']
CASES['f77s_fmtch'] = ['   42']
CASES['f77s_barefn'] = ['    9.00']
CASES['f77s_iodo'] = ['   2   4   6', '   2   4   6', '   4']
CASES['f77s_vario'] = ['   1   2', '   3   4', '   5', '   5   4', '   3   2', '   1', '   6']
CASES['f77s_varreal'] = ['     4.00    -3.75', '     2.50     1.25', '   0']
CASES['f77s_varlc'] = ['   T   F', '   T', 'ABCDEF', 'GHI']
CASES['f77s_varexp'] = ['   0.123400E+003', '   0.500000E+001']
CASES['f77s_iord'] = ['   1   2   3   4']
CASES['f77s_numcv'] = ['   321    -3    -2', '   321.00    -3.00     3.25']
CASES['f77s_idxexpr'] = ['  20']
CASES['f77s_pscale'] = ['   12.30    1.23', '    1.23    1.23']
CASES['f77s_f6'] = ['    1.234567   -0.000125    9.999999', '    1.234567   -0.000125    9.999999']
CASES['f77s_exintr'] = ['     1.48']
CASES['f77s_frevert'] = ['   1   2', '   3   4', '   5']
CASES['f77s_unitvar'] = ['   42']
CASES['f77s_endgoto'] = ['    7    7']
CASES['f77s_endfile'] = ['   23']
CASES['f77s_sequnio'] = ['  -17', '   41']
CASES['f77s_direct2'] = ['  -42   17', '    9   -8']
CASES['f77s_directio'] = ['  -42','    9']
CASES['f77s_fmtchr'] = ['   12   34']
CASES['f77s_afread'] = ['   12   34']
CASES['f77s_vuniio'] = ['   1   2','   3   4','   5','   5   4','   3   2','   1','   6']
CASES['f77s_nestrevert'] = ['  1   2    3   4    5', '   6    7   8    9', '  10']
CASES['f77s_afmt'] = ['  42', '    42']


INPUTS = {'f77s_unitvar':'  42\n', 'f77s_fmtchr':'  12  34\n', 'f77s_afread':'  12  34\n', 'f77s_vuniio':'001002\n003004\n005\n', 'f77s_varreal':'   1.25   2.50\n  -3.75   4.00\n', 'f77s_varlc':'  T  F\n  T\nABCDEF\nGHI\n', 'f77s_varexp':'   0.123400E+003\n   0.500000E+001\n', 'f77s_vario':'001002\n003004\n005\n', 'f77s_f6': '    1.234567   -0.000125    9.999999\n', 'f77s_nestrevert':'  1   2    3   4    5\n   6    7   8    9\n  10\n', 'f77s_frevert': '001002\n003004\n005\n', 'f77s_pscale': '   12.30    1.23\n', 'f77s_iord': '001002003\n', 'f77s_bnbz': '  42  12  \n', 'f77s_eread': '   0.123400E+003   0.500000E+001\n', 'f77s_read': '0042 007\n', 'f77s_repeat': '003 005 010\n', 'f77s_charread': 'XYZ\n', 'f77s_arrread': 'XYZ\n', 'f77s_realio': '   -3.25\n  001234\n', 'f77s_logio': '   F   T\n'}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(cmd, timeout=180, input_text=None):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, input=input_text)
        return {'argv': [str(x) for x in cmd], 'exit_code': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as e:
        return {'argv': [str(x) for x in cmd], 'exit_code': None, 'timeout': True,
                'stdout': (e.stdout or b'').decode('utf-8', 'replace'),
                'stderr': (e.stderr or b'').decode('utf-8', 'replace')}


def lines(s):
    # The RVM screen text includes blank rows after exit; do not lose leading spaces.
    return [line.rstrip() for line in s.splitlines() if line.strip()]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', required=True)
    p.add_argument('--rvm', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sdk-archive', type=Path)
    p.add_argument('--timeout', type=int, default=180, help='seconds per compiler/emulator process')
    p.add_argument('--only', nargs='+', choices=sorted(CASES),
                   help='run only listed strict F77S host-vs-Z80 programs')
    a = p.parse_args()
    if a.timeout < 1:
        p.error('--timeout must be positive')
    if not shutil.which('gfortran'):
        p.error('gfortran required for independent comparison')
    report = {'schema': 1, 'purpose': 'F77S example differential execution',
              'not_full_conformance': True,
              'tools': {'gfortran': execute(['gfortran', '--version'])['stdout'].splitlines()[0],
                        'rvm_sha256': digest(a.rvm),
                        'rfortranc_sha256': digest(ROOT/'rfortranc/translator.py'),
                        'sdk_archive_sha256': digest(a.sdk_archive) if a.sdk_archive else None,
                        'differential_harness_sha256': digest(__file__),
                        'timeout_seconds': a.timeout},
              'cases': []}
    with tempfile.TemporaryDirectory() as d:
        for name, expectation in CASES.items():
            if a.only and name not in a.only:
                continue
            src = ROOT/'tests/fortran'/(name+'.f')
            target = Path(d)/(name+'.ssx')
            host = Path(d)/(name+'.host')
            compile_zx = execute([sys.executable, str(ROOT/'bin/rfortranc'),
                                  '--std','f77s','--sdk',a.sdk,'--native',
                                  '-o',str(target),str(src)], a.timeout)
            compile_host = execute(['gfortran','-std=legacy','-ffixed-form',
                                    '-o',str(host),str(src)], a.timeout)
            zx_cmd = [sys.executable, a.rvm,'--headless','--text','--frames','1000']
            if name in INPUTS:
                zx_cmd += ['--keys', INPUTS[name]]
            zx_cmd.append(str(target))
            zx = execute(zx_cmd, a.timeout) if compile_zx['exit_code'] == 0 and target.exists() else None
            reference = execute([str(host)], timeout=a.timeout, input_text=INPUTS.get(name)) if compile_host['exit_code'] == 0 else None
            case = {'name': name, 'source_sha256': digest(src),
                    'ssx_sha256': digest(target) if target.exists() else None,
                    'ssx_bytes': target.stat().st_size if target.exists() else None,
                    'expected_lines': expectation, 'stdin': INPUTS.get(name), 'compile_zx': compile_zx,
                    'compile_gfortran': compile_host,'zxux_run': zx, 'gfortran_run': reference}
            case['passed'] = bool(zx and reference and compile_zx['exit_code'] == 0
                                  and compile_host['exit_code'] == 0
                                  and zx['exit_code'] == 0 and reference['exit_code'] == 0
                                  and '(exit)' in zx['stderr']
                                  and lines(zx['stdout']) == lines(reference['stdout']) == expectation)
            report['cases'].append(case)
            print(('PASS' if case['passed'] else 'FAIL'), name, flush=True)
    report['result'] = {'passed': sum(c['passed'] for c in report['cases']),
                        'total': len(report['cases'])}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('RESULT', report['result'], flush=True)
    return 0 if report['result']['passed'] == report['result']['total'] else 1

if __name__=='__main__':
    raise SystemExit(main())
