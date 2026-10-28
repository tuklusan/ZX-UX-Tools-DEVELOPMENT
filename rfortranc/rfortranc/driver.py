"""Host command: FORTRAN -> C48 -> rcc -> ras/rld -> SSX/TZX."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from .translator import FortranError, convert, parse


def sdk_path(explicit=None):
    choices = [explicit, os.environ.get('ZXUX_SDK')]
    here = Path(__file__).resolve()
    choices.extend([str(here.parents[1]), str(here.parents[2] / 'zx-ux-sdk'),
                    str(here.parents[2] / 'src/zx-ux-sdk')])
    for candidate in choices:
        if not candidate:
            continue
        root = Path(candidate).expanduser().resolve()
        if (root / 'bin/rcc').is_file() and (root / 'bin/rtap').is_file():
            return root
        if (root / 'rcc').is_file() and (root / 'rtap').is_file() and (root / 'py/rcc').is_dir():
            return root
    return None


def main(argv=None):
    p = argparse.ArgumentParser(prog='rfortranc', description='FORTRAN 77 subset to ZX-UX SSX/TZX')
    p.add_argument('source', help='FORTRAN source .f or .for')
    p.add_argument('-o', '--output', help='output file (default SOURCE.ssx)')
    p.add_argument('--sdk', help='ZX-UX source SDK root or packaged SDK bin')
    p.add_argument('--std', choices=('zxux', 'f77s'), default='zxux',
                   help='zxux extensions (default) or partial ANSI subset validation')
    modes = p.add_mutually_exclusive_group()
    modes.add_argument('-S', action='store_true', help='output Z80 assembly')
    modes.add_argument('-c', action='store_true', help='output SSO relocatable object')
    modes.add_argument('--emit-c', action='store_true', help='output generated C48 source')
    modes.add_argument('--tzx', action='store_true', help='emit TZX cassette image')
    backend = p.add_mutually_exclusive_group()
    backend.add_argument('--native', action='store_true', help='native Z80 code; skip automatic fit')
    backend.add_argument('--bytecode', action='store_true', help='use C48 bytecode backend')
    backend.add_argument('--no-fit', action='store_true', help='disable automatic fitting')
    p.add_argument('--max', type=int, help='max bytes required in ZX-UX memory')
    p.add_argument('--stack', type=int, help='reserved stack bytes')
    p.add_argument('--tape-name', help='ZX-UX program name (1..10 ASCII chars; --tzx only)')
    args = p.parse_args(argv)
    suffix = '.c' if args.emit_c else '.s' if args.S else '.sso' if args.c else '.tzx' if args.tzx else '.ssx'
    target = Path(args.output or str(Path(args.source).with_suffix(suffix))).resolve()
    source = Path(args.source).resolve()
    try:
        if args.tape_name is not None and not args.tzx:
            raise ValueError('--tape-name requires --tzx')
        if target == source:
            raise ValueError('output would overwrite FORTRAN source')
        program = source.read_text(encoding='utf-8')
        units = parse(program, std=args.std)
        if args.std == 'f77s':
            from .f77s import validate_source
            validate_source(program, units)
        c48 = convert(units)
        if args.emit_c:
            target.write_text(c48, encoding='utf-8')
            return 0
        sdk = sdk_path(args.sdk)
        if not sdk:
            raise ValueError('ZX-UX SDK not found; pass --sdk or set ZXUX_SDK')
        packaged = (sdk / 'py/rcc').is_dir()
        rcc = sdk / ('rcc' if packaged else 'bin/rcc')
        rtap = sdk / ('rtap' if packaged else 'bin/rtap')
        with tempfile.TemporaryDirectory(prefix='rfortranc-') as scratch:
            tmp = Path(scratch)
            generated = tmp / (source.stem + '.c')
            generated.write_text(c48, encoding='utf-8')
            binary = tmp / (source.stem + '.ssx') if args.tzx else target
            cmd = [sys.executable, str(rcc), str(generated), '-o', str(binary)]
            if args.S:
                cmd.append('-S')
            if args.c:
                cmd.append('-c')
            if args.native:
                cmd.append('--native')
            if args.bytecode:
                cmd.append('--bytecode')
            if args.no_fit:
                cmd.append('--no-fit')
            if args.max is not None:
                cmd.extend(['--max', str(args.max)])
            if args.stack is not None:
                cmd.extend(['--stack', str(args.stack)])
            result = subprocess.run(cmd, check=False)
            if result.returncode:
                return result.returncode
            if args.tzx:
                # ZX-UX rtap stores a name of at most ten printable ASCII chars.
                name = args.tape_name if args.tape_name is not None else source.stem[:10]
                if not (1 <= len(name) <= 10 and all(32 < ord(c) < 127 and c != '/' for c in name)):
                    raise ValueError('TZX program name must have 1..10 printable ASCII chars without /')
                return subprocess.run([sys.executable, str(rtap), '-o', str(target),
                                       str(binary) + '=' + name], check=False).returncode
        return 0
    except (OSError, ValueError, FortranError) as e:
        print('rfortranc: ' + str(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
