#!/usr/bin/env python3
"""Extract one Spectrum BASIC .bas file per program in the six OTS TZX sides.

Uses the preserved ZX-UX ROM LLIST converter alongside this script. The original
recorded TZX bytes are never modified. Zero-duration TZX stop/pause markers are
ignored *only inside the in-memory conversion parser*, allowing subsequent
standalone BASIC recordings on the same physical cassette to be read.

Out-of-order line numbers, notably Alien Blitz's stored line 185 following 330,
are preserved in their recorded order rather than repaired or reordered.

Run: python3 tools/extract_ots_basic.py [folder-with-six-tzx-files]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import types


def load_converter():
    path = Path(__file__).with_name('rom_tzx2bas.py')
    source = path.read_text(encoding='utf-8')
    original = "if kind == 0x20 and _u16(info, 0) == 0:"
    if source.count(original) != 1:
        raise RuntimeError('Unsupported converter revision: expected pause handling was not found')
    source = source.replace(original, "if False and kind == 0x20 and _u16(info, 0) == 0:", 1)
    module = types.ModuleType('ots_rom_converter')
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


def original_order_listing(mod, program: bytes) -> str:
    """Fallback for malformed original recordings: retain stored line order."""
    out = []
    p = 0
    while p < len(program):
        header, p = mod._take(program, p, 4, 'BASIC line header')
        number = int.from_bytes(header[:2], 'big')
        size = mod._u16(header, 2)
        if not (0 <= number <= 9999) or size < 1:
            raise mod.TapeError(f'Invalid BASIC line number or length at offset {p - 4}')
        body, p = mod._take(program, p, size, f'Line {number}')
        if body[-1] != 13:
            raise mod.TapeError(f'Line {number}: missing terminator')
        out.append(mod.list_line(number, body[:-1]))
    return '\n'.join(out) + '\n'


def extract(root: Path) -> None:
    mod = load_converter()
    for cassette in (1, 2, 3):
        for side in 'AB':
            tape = root / f'OverTheSpectrumCassette{cassette}_Side{side}.tzx'
            data = tape.read_bytes()
            entries = list(mod.basic_programs(data))
            for i, (header_name, program) in enumerate(entries):
                name = header_name.decode('ascii', 'replace').strip().lower()
                slug = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
                if not slug:
                    raise ValueError(f'{tape.name}: unnamed BASIC program {i}')
                directory = root / f'OTS_tape_{cassette}_side_{side}_{slug}'
                output = directory / f'{slug}.bas'
                try:
                    listing = mod.listing(data, program_index=i)
                except mod.TapeError as e:
                    if 'BASIC line numbers out of order' not in str(e):
                        raise
                    listing = original_order_listing(mod, program)
                encoded = listing.encode('ascii')
                if output.exists():
                    if output.read_bytes() != encoded:
                        raise RuntimeError(f'Existing BASIC file differs; refusing overwrite: {output}')
                else:
                    directory.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(encoded)
                print(f'{tape.name}: {name} -> {output.relative_to(root)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path,
                        default=Path(__file__).resolve().parent.parent)
    extract(parser.parse_args().root.resolve())
