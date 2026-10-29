#!/usr/bin/env python3
"""Measure ZX-UX SSX static memory reservations, not dynamic peak RAM.

Uses the target SDK's checksum-verifying SSX parser. The image/BSS/stack/
heap sum describes linked reservation and is NOT measured runtime high water.
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
DEFAULT_CASES = ['f77s_burkl2', 'f77s_burkcopy', 'f77s_burkrsrt',
                 'f77s_trig', 'f77s_rpow', 'f77s_afmt', 'f77s_ewdee',
                 'f77s_bnbz', 'f77s_eread']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def measure(ssx, rld):
    data = Path(ssx).read_bytes()
    hdr = rld.parse_ssx(data)  # Includes checksum, relocation and header checks
    image = len(hdr['image'])
    reserved = image + hdr['bss'] + hdr['stack'] + hdr['heap']
    return {'ssx_bytes': len(data), 'image_bytes': image, 'bss_bytes': hdr['bss'],
            'reserved_stack_bytes': hdr['stack'], 'reserved_heap_bytes': hdr['heap'],
            'total_static_reservation_bytes': reserved,
            'relocation_count': len(hdr['relocs']), 'ssx_sha256': hashlib.sha256(data).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=12288)
    parser.add_argument('--cases', nargs='+', default=DEFAULT_CASES)
    args = parser.parse_args(argv)
    if not (1 <= args.limit <= 65535):
        parser.error('--limit must be in 1..65535')
    sdk = args.sdk.resolve()
    if not (sdk/'rld.py').is_file():
        parser.error('SDK source root with rld.py required')
    sys.path.insert(0, str(sdk))
    import rld  # target SDK's SSX1 structure and checksum parser

    record = {'schema': 1, 'scope': 'linker-declared SSX static memory reservations',
              'not_runtime_peak_measurement': True, 'not_physical_spectrum_test': True,
              'target_limit_bytes': args.limit, 'target_sdk_linker_sha256': sha(sdk/'rld.py'),
              'compiler_sha256': sha(ROOT/'rfortranc/translator.py'), 'cases': []}
    failures = []
    with tempfile.TemporaryDirectory(prefix='f77s-ssx-memory-') as tmp:
        for name in args.cases:
            source = ROOT/'tests/fortran'/(name+'.f')
            if not source.is_file():
                parser.error('missing strict F77S fixture: '+name)
            dest = Path(tmp)/(name+'.ssx')
            command = [sys.executable, str(ROOT/'bin/rfortranc'), '--std', 'f77s',
                       '--sdk', str(sdk), '--native', '-o', str(dest), str(source)]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
            item = {'name': name, 'source_sha256': sha(source),
                    'compiler_exit': completed.returncode,
                    'compiler_stderr': completed.stderr.strip()}
            if completed.returncode == 0 and dest.exists():
                try:
                    item.update(measure(dest, rld))
                    item['within_limit'] = item['total_static_reservation_bytes'] <= args.limit
                except (ValueError, rld.LinkError, IndexError, KeyError) as exc:
                    item['parse_error'] = str(exc)
            if not item.get('within_limit', False):
                failures.append(name)
            record['cases'].append(item)
            print(('PASS' if item.get('within_limit', False) else 'FAIL'), name,
                  item.get('total_static_reservation_bytes'), 'bytes reserved', flush=True)
    record['result'] = {'within_limit': len(record['cases'])-len(failures),
                        'total': len(record['cases']), 'failures': failures}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print('RESULT', record['result'], flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
