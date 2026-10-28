#!/usr/bin/env python3
"""Build a reproducible FORTRAN sample release with SSX + TZX outputs.

Use a clean output directory. Compiler and tape utility are sourced from
an existing ZX-UX SDK; no native binaries are redistributed in this repo.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sdk', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--native', action='store_true')
    p.add_argument('--only', nargs='*', metavar='NAME', help='test names to build, default all')
    opts = p.parse_args()
    dest = Path(opts.out).resolve()
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit('release destination must be empty: ' + str(dest))
    dest.mkdir(parents=True, exist_ok=True)
    sample = ROOT / 'tests/fortran'
    names = set()
    wanted = set(opts.only or [])
    available = {f.stem for f in sample.glob('*.f')}
    if wanted - available:
        raise SystemExit('unknown tests: ' + ', '.join(sorted(wanted - available)))
    records = []
    for source in sorted(sample.glob('*.f')):
        name = source.stem
        if wanted and name not in wanted:
            continue
        tape_name = name[:10]
        if tape_name.upper() in names:
            tape_name = name[:6] + hashlib.sha256(name.encode('utf-8')).hexdigest()[:4]
        if tape_name.upper() in names or not tape_name.isascii():
            raise SystemExit('invalid or duplicate cassette name: ' + tape_name)
        names.add(tape_name.upper())
        ssx = dest / (name + '.ssx')
        tzx = dest / (name + '.tzx')
        std = 'f77s' if name.startswith('f77s_') else 'zxux'
        compile_args = [sys.executable, str(ROOT / 'bin/rfortranc'),
                        '--sdk', opts.sdk, '--std', std]
        if opts.native:
            compile_args.append('--native')
        subprocess.run(compile_args + ['-o', str(ssx), str(source)], check=True)
        subprocess.run(compile_args + ['--tzx', '--tape-name', tape_name,
                                       '-o', str(tzx), str(source)], check=True)
        if not ssx.read_bytes().startswith(b'SSX1') or not tzx.read_bytes().startswith(b'ZXTape!'):
            raise SystemExit('invalid generated ZX-UX binary or cassette: ' + name)
        records.append({'program': name, 'tape_name': tape_name,
                        'source': str(source.relative_to(ROOT)),
                        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'standard_mode': std, 'native': opts.native,
                        'ssx_sha256': hashlib.sha256(ssx.read_bytes()).hexdigest(),
                        'tzx_sha256': hashlib.sha256(tzx.read_bytes()).hexdigest(),
                        'ssx_bytes': ssx.stat().st_size, 'tzx_bytes': tzx.stat().st_size})
    (dest / 'manifest.json').write_text(json.dumps(records, indent=2) + '\n')
    print('Released', len(records), 'FORTRAN programs')


if __name__ == '__main__':
    main()
