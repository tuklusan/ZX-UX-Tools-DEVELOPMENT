#!/usr/bin/env python3
"""Build a reproducible FORTRAN sample release with SSX + TZX outputs.

Use a clean output directory. Compiler and tape utility are sourced from
an existing ZX-UX SDK; no native binaries are redistributed in this repo.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sdk', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--native', action='store_true')
    opts = p.parse_args()
    dest = Path(opts.out).resolve()
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit('release destination must be empty: ' + str(dest))
    dest.mkdir(parents=True, exist_ok=True)
    sample = ROOT / 'tests/fortran'
    names = set()
    records = []
    for source in sorted(sample.glob('*.f')):
        name = source.stem
        if not 1 <= len(name) <= 10 or name in names:
            raise SystemExit('invalid or repeated tape name: ' + name)
        names.add(name)
        ssx = dest / (name + '.ssx')
        tzx = dest / (name + '.tzx')
        compile_args = [sys.executable, str(ROOT / 'bin/rfortranc'), '--sdk', opts.sdk]
        if opts.native:
            compile_args.append('--native')
        subprocess.run(compile_args + ['-o', str(ssx), str(source)], check=True)
        subprocess.run(compile_args + ['--tzx', '-o', str(tzx), str(source)], check=True)
        records.append({'program': name, 'source': str(source.relative_to(ROOT)),
                        'ssx_sha256': hashlib.sha256(ssx.read_bytes()).hexdigest(),
                        'tzx_sha256': hashlib.sha256(tzx.read_bytes()).hexdigest(),
                        'ssx_bytes': ssx.stat().st_size, 'tzx_bytes': tzx.stat().st_size})
    (dest / 'manifest.json').write_text(json.dumps(records, indent=2) + '\n')
    print('Released', len(records), 'FORTRAN programs')


if __name__ == '__main__':
    main()
