"""Host command: FORTRAN -> C48 -> rcc -> ras/rld -> SSX/TZX."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import re
import struct
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

def link_existing_objects(sdk, packaged, objects, target, args, rtap, tape_name):
    """Link retained native Z80 SSO objects without FORTRAN source parsing.

    Every retained F77S SSO has a versioned SHA-256 tag describing its
    procedure ABI; legacy raw SSO requires explicit unverified opt-in.
    """
    linker = sdk / ('rld' if packaged else 'bin/rld')
    library = sdk / 'lib/libc48.ssa'
    if not linker.is_file() or not library.is_file():
        raise ValueError('ZX-UX SDK linker/library missing for object linkage')
    for obj in objects:
        if obj.suffix.lower() != '.sso' or not obj.is_file():
            raise ValueError('link input must be an existing SSO object: ' + str(obj))
    if not objects:
        raise ValueError('at least one SSO object required')
    from .abi import validate as validate_abi
    validate_abi(objects, getattr(args, 'allow_untagged_objects', False))
    with tempfile.TemporaryDirectory(prefix='rfortranc-link-') as scratch:
        binary = Path(scratch) / 'linked.ssx' if args.tzx else target
        linkcmd = [sys.executable, str(linker), '-o', str(binary)]
        if args.stack is not None:
            linkcmd += ['--stack', str(args.stack)]
        linkcmd += [str(obj) for obj in objects] + [str(library)]
        rc = subprocess.run(linkcmd, check=False)
        if rc.returncode:
            if not args.tzx:
                binary.unlink(missing_ok=True)
            return rc.returncode
        # Header describes reserved RAM, NOT observed runtime high-water.
        blob = binary.read_bytes()
        if len(blob) < 22 or blob[:4] != b'SSX1':
            binary.unlink(missing_ok=True)
            raise ValueError('linker generated an invalid SSX image')
        _, _, image, bss, stack, heap, _, _, _ = struct.unpack_from('<BBHHHHHHH', blob, 4)
        need = max(len(blob), image + bss + stack + heap)
        if need > (args.max if args.max is not None else 14000):
            binary.unlink(missing_ok=True)
            raise ValueError('linked SSX exceeds memory limit: ' + str(need))
        if not args.tzx:
            return 0
        if not (1 <= len(tape_name) <= 10 and
                all(32 < ord(c) < 127 and c != '/' for c in tape_name)):
            raise ValueError('TZX program name must have 1..10 printable ASCII chars without /')
        return subprocess.run([sys.executable, str(rtap), '-o', str(target),
                               str(binary) + '=' + tape_name], check=False).returncode


def main(argv=None):
    p = argparse.ArgumentParser(prog='rfortranc', description='FORTRAN 77 subset to ZX-UX SSX/TZX')
    p.add_argument('source', nargs='+', help='FORTRAN source .f or .for')
    p.add_argument('--separate', action='store_true', help='compile each F77S program unit to SSO and link them')
    p.add_argument('--link-only', action='store_true', help='link retained Z80 SSO objects without FORTRAN source')
    p.add_argument('--object-dir', help='preserve per-unit SSO objects (requires --separate)')
    p.add_argument('--allow-untagged-objects', action='store_true',
                   help='link legacy C48 SSO without F77S ABI checking (--link-only only)')
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
    target = Path(args.output or str(Path(args.source[0]).with_suffix(suffix))).resolve()
    sources = [Path(item).resolve() for item in args.source]
    try:
        if args.tape_name is not None and not args.tzx:
            raise ValueError('--tape-name requires --tzx')
        if target in sources:
            raise ValueError('output would overwrite FORTRAN source')
        if len(sources) > 1 and not (args.separate or args.link_only):
            raise ValueError('multiple sources require --separate')
        if args.object_dir and not args.separate:
            raise ValueError('--object-dir requires --separate')
        if args.allow_untagged_objects and not args.link_only:
            raise ValueError('--allow-untagged-objects requires --link-only')
        if args.separate and (args.std != 'f77s' or args.emit_c or args.S or args.c or args.bytecode or args.no_fit):
            raise ValueError('--separate needs --std f77s with linked native SSX/TZX output')
        if args.link_only:
            if (args.separate or args.std != 'f77s' or args.emit_c or args.S or args.c or
                    args.bytecode or args.no_fit or args.object_dir):
                raise ValueError('--link-only requires --std f77s with native SSX/TZX objects')
            sdk = sdk_path(args.sdk)
            if not sdk:
                raise ValueError('ZX-UX SDK not found; pass --sdk or set ZXUX_SDK')
            packaged = (sdk / 'py/rcc').is_dir()
            rtap = sdk / ('rtap' if packaged else 'bin/rtap')
            name = args.tape_name if args.tape_name is not None else sources[0].stem[:10]
            return link_existing_objects(sdk, packaged, sources, target, args, rtap, name)
        program = ''.join(source.read_text(encoding='utf-8').rstrip('\n') + '\n' for source in sources)
        units = parse(program, std=args.std)
        if args.std == 'f77s':
            from .f77s import validate_source
            validate_source(program, units)
        c48 = convert(units) if not args.separate else None
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
            if args.separate:
                linker = sdk / ('rld' if packaged else 'bin/rld')
                library = sdk / 'lib/libc48.ssa'
                if not linker.is_file() or not library.is_file():
                    raise ValueError('ZX-UX SDK linker/library missing for --separate')
                objects = []
                from .abi import write as write_abi
                known = {unit.name: unit for unit in units}
                preserved = Path(args.object_dir).resolve() if args.object_dir else None
                if preserved:
                    preserved.mkdir(parents=True, exist_ok=True)
                for i, u in enumerate(units):
                    unit_name = '%02d_%s' % (i, u.name)
                    generated = tmp / (unit_name + '.c')
                    obj = (preserved if preserved else tmp)/(unit_name + '.sso')
                    generated.write_text(convert(units, emit_units={u.name}), encoding='utf-8')
                    rc = subprocess.run([sys.executable, str(rcc), '-c', '--native',
                                         '-o', str(obj), str(generated)], check=False)
                    if rc.returncode:
                        return rc.returncode
                    write_abi(u, known, obj)
                    objects.append(obj)
                name = args.tape_name if args.tape_name is not None else sources[0].stem[:10]
                return link_existing_objects(sdk, packaged, objects, target, args, rtap, name)
            generated = tmp / (sources[0].stem + '.c')
            generated.write_text(c48, encoding='utf-8')
            binary = tmp / (sources[0].stem + '.ssx') if args.tzx else target
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
                name = args.tape_name if args.tape_name is not None else sources[0].stem[:10]
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
