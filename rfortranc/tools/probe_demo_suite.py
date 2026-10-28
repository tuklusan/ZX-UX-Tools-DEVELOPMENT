#!/usr/bin/env python3
"""Strict F77S syntax-only probe of the user-provided 20-demo ZX-UX ZIP.

This intentionally reports *every* source without pretending accepted C48 is
an executable. No external source content is checked into this repository.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip', type=Path, required=True, help='original user 20-program archive')
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=20)
    args = p.parse_args(argv)
    if args.timeout < 1:
        p.error('timeout must be positive')
    archive = args.zip.read_bytes()
    cases = []
    with zipfile.ZipFile(args.zip) as z, tempfile.TemporaryDirectory(prefix='f77s-demo-') as temp:
        members = sorted(n for n in z.namelist() if n.startswith('F77S_Z80_SUITE/') and
                         n.count('/') == 1 and n.upper().endswith('.FOR'))
        if len(members) != 20:
            p.error('expected 20 root demo programs; archive has ' + str(len(members)))
        for n in members:
            contents = z.read(n)
            src = Path(temp) / Path(n).name
            src.write_bytes(contents)
            cmd = [sys.executable, str(ROOT/'bin/rfortranc'), '--std', 'f77s',
                   '--emit-c', '-o', str(Path(temp)/'output.c'), str(src)]
            try:
                proc = subprocess.run(cmd, text=True, capture_output=True,
                                      timeout=args.timeout, check=False)
                accepted = proc.returncode == 0
                result = {'exit_code': proc.returncode, 'stderr': proc.stderr, 'stdout': proc.stdout}
            except subprocess.TimeoutExpired:
                accepted = False
                result = {'exit_code': None, 'timeout': True}
            cases.append({'source': Path(n).name, 'sha256': sha(contents), 'bytes': len(contents),
                          'accepted_frontend_only': accepted, 'compile': result})
            print(('ACCEPT' if accepted else 'REJECT'), Path(n).name, flush=True)
    accepted = sum(c['accepted_frontend_only'] for c in cases)
    report = {'schema': 1, 'purpose': 'source compatibility census only; not Z80 runtime or ANSI certification',
              'archive_sha256': sha(archive), 'archive_bytes': len(archive),
              'translator_sha256': sha((ROOT/'rfortranc/translator.py').read_bytes()),
              'command': [str(x) for x in sys.argv],
              'result': {'accepted': accepted, 'rejected': len(cases)-accepted, 'total': len(cases)},
              'cases': cases}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('RESULT', report['result'], flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
