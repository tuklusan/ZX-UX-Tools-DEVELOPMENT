#!/usr/bin/env python3
"""Reproducible compile probe for independent licensed FORTRAN corpora.

Do not mistake compile acceptance for standards conformance. No test is
silently excluded; file hashes and compiler messages are kept in the report.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('corpora', nargs='+', type=pathlib.Path, help='corpus files/dirs')
    ap.add_argument('--timeout', type=int, default=60, help='seconds per case')
    ap.add_argument('--report', type=pathlib.Path, required=True, help='JSON report path')
    ns = ap.parse_args(argv)
    if ns.timeout < 1:
        ap.error('--timeout must be positive')
    source_files = []
    for src in ns.corpora:
        if src.is_file() and src.suffix.lower() in ('.f', '.for', '.f77'):
            source_files.append(src)
        elif src.is_dir():
            source_files.extend(p for p in src.rglob('*')
                                if p.is_file() and p.suffix.lower() in ('.f', '.for', '.f77'))
        else:
            ap.error('not a readable FORTRAN file/directory: ' + str(src))
    cases = []
    seen = set()
    with tempfile.TemporaryDirectory(prefix='rfortranc-probe-') as temp:
        return probe(source_files, pathlib.Path(temp), ns)


def probe(source_files, temp, ns):
    cases = []
    seen = set()
    for file in sorted(source_files):
        file = file.resolve()
        if file in seen:
            continue
        seen.add(file)
        src = file.read_bytes()
        cmd = [sys.executable, str(ROOT / 'bin/rfortranc'),
               '--emit-c', '-o', str(temp / 'probe.c'), str(file)]
        # Output only to the isolated temporary directory (portable hosts).
        start = time.monotonic()
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True,
                                  timeout=ns.timeout, check=False)
            status = 'accepted' if proc.returncode == 0 else 'rejected'
            detail = (proc.stderr + '\n' + proc.stdout).strip()[:2000]
        except subprocess.TimeoutExpired:
            status = 'timeout'; detail = 'deadline exceeded'
        cases.append({'path': str(file), 'sha256': hashlib.sha256(src).hexdigest(),
                      'bytes': len(src), 'status': status, 'detail': detail,
                      'duration_seconds': round(time.monotonic() - start, 3)})
        print(status.upper(), file)
    counts = {st: sum(c['status'] == st for c in cases)
              for st in ('accepted', 'rejected', 'timeout')}
    data = {'tool': 'rfortranc', 'mode': 'frontend-only (NOT executable validation)',
            'source_corpora': [str(p.resolve()) for p in ns.corpora],
            'counts': counts, 'cases': cases}
    ns.report.parent.mkdir(parents=True, exist_ok=True)
    ns.report.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('REPORT', ns.report, counts)
    return 1 if counts['rejected'] or counts['timeout'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
