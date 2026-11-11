"""Offline boot-only turbo transport compiler, staged under retained tmp/.

Produces a compact timing/data TZX: two ROM blocks of BASIC, two of the bootstrap
(turbo_boot.asm, which carries the Bloodaxe turbo loader unmodified in
bloodaxe_loader.bin) and 24 turbo blocks. Independent verification gates must
pass before the staged distribution can replace last-good release/dist.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import shutil
import subprocess
import struct
import sys

from turbo_segments import layout, pack_tzx, read_segments, make_segments, COUNT, LOAD_BASE, ENTRY, MAX_TZX_BYTES, PAUSE_MS, TurboFormatError
import osbuild

HERE = Path(__file__).resolve().parent
TMP = HERE.parents[2] / 'build'
SRC = TMP / 'src'
OUT = TMP / 'out'
ORIGINAL = HERE.parent.parent / 'zx-ux/turbo_boot.asm'


def progress_lines(size: int, syms: dict, kernel: int, free: int):
    """24 canonical 32-character messages, in the supplied v02 file order.

    The beta default time is 09:00:00, unlike the older reference's 00:00:00.
    Each 4-pixel-wide glyph occupies one true 64-column cell; the remaining
    columns are blanked at the end, not inserted between characters.
    """
    source = (HERE.parent.parent / 'zx-ux/turbo_lines.txt').read_text().splitlines()
    if len(source) != COUNT or any(not s.isascii() or not s.isprintable() or len(s) > 32 for s in source):
        raise TurboFormatError('invalid 24-line canonical loader message file')
    return tuple(s.ljust(32) for s in source)


def encode_basic():
    def val(n):
        return b'\xb0"' + str(n).encode() + b'"'
    # The BASIC loader prints the banner on the right half of the screen and keeps the four bottom-right
    # attribute cells (the ribbon) set. The bootstrap's progress rows only ever touch the left half.
    line = (b'\xe7' + val(0) + b':' + b'\xda' + val(0) + b':' +
            b'\xd9' + val(7) + b':' + b'\xfd' + val(0xCEFF) + b':' +
            b'\xef""\xaf:' + b'\xfb:' +
            b'\xf5"' + banner_text() + b'";:' +    # PRINT "banner"; the right half, then the ribbon
            osbuild.ribbon_print(val) + b':' +
            b'\xf9\xc0' + val(0xD000) + b'\r')
    return struct.pack('>H', 10) + struct.pack('<H', len(line)) + line


def packed_line(line: str):
    """The left half of a row: 32 adjacent 4-pixel character cells; pad only at the right."""
    if not line.isascii() or len(line) > 32:
        raise TurboFormatError('loader display line outside 32-character width')
    return line.ljust(32)


# The banner of the right half of the screen, printed by the BASIC loader in one PRINT of one string
# (so it needs no numbers in the BASIC, and takes a fraction of a second): ROM control codes inside the
# string set the position and the colours. Rows are text rows 0..20 of the upper screen, 16 characters
# wide from column 16; row 21 is left alone (its last column would scroll the screen) and so are rows 13 and
# 14 (the byte 0Dh ends a BASIC line, and 0Eh marks a number there).
# Each entry: (row, paper, ink, bright, text).
BANNER = (
    (0, 1, 7, 1, ' ZX-UX  UNIX v1 '),
    (1, 1, 5, 1, ' for the 48K ZX  '[:16]),
    (2, 1, 5, 1, ' Spectrum       '),
    (4, 0, 7, 0, 'login: any name'),
    (5, 0, 7, 0, '(1-8 chars)'),
    (6, 0, 7, 0, 'no password'),
    (8, 0, 6, 1, 'Keys'),
    (9, 0, 7, 0, 'ENTER  end line'),
    (10, 0, 7, 0, 'DELETE erase'),
    (11, 0, 7, 0, 'EDIT   Ctrl-D'),
    (12, 0, 7, 0, 'BREAK  interrupt'),
    (15, 0, 6, 1, 'Commands'),
    (16, 0, 7, 0, 'ls cat cp mv rm'),
    (17, 0, 7, 0, 'mkdir df ps top'),
    (18, 0, 7, 0, 'date wc od vi'),
    (19, 0, 7, 0, 'more tar zxpack'),
    (20, 0, 7, 0, 'man: /usr/doc'),
)
BANNER_COLUMN = 16
RAINBOW_ROW = 3                      # four blocks of four cells: red, yellow, green, cyan paper


def banner_text() -> bytes:
    """The string printed by the BASIC loader (control codes: 10h INK, 11h PAPER, 13h BRIGHT, 16h AT)."""
    out = bytearray()
    def at(row):
        out.extend((0x16, row, BANNER_COLUMN))
    def colours(paper, ink, bright):
        out.extend((0x13, bright, 0x11, paper, 0x10, ink))
    at(RAINBOW_ROW)
    out.extend((0x13, 1))
    for paper in (2, 6, 4, 5):
        out.extend((0x11, paper))
        out.extend(b'    ')
    for row, paper, ink, bright, text in BANNER:
        if len(text) > 32 - BANNER_COLUMN or not text.isascii() or '"' in text:
            raise TurboFormatError('banner line outside 16 ASCII characters')
        at(row)
        colours(paper, ink, bright)
        out.extend(text.encode())
    if any(c in out for c in (0x0D, 0x0E, 0x22)):
        raise TurboFormatError('banner contains a byte BASIC cannot hold in a string')
    return bytes(out)


def create_tzx(sjasm: str, syms: dict, kernel: int, free: int, *, pause_ms=PAUSE_MS, output_name="ZX-UX-turbo-experimental.tzx"):
    raw = (OUT/'merged-image.bin').read_bytes()
    if syms['LOWK'] != LOAD_BASE or len(raw) + LOAD_BASE > 0xCE00:
        raise TurboFormatError('merged image or protected loader stack address changed')
    plan = layout(len(raw), load_base=syms['LOWK'])
    lines = progress_lines(len(raw), syms, kernel, free)
    # The loader walks its table from the last entry back to the first: block 1 is the last entry.
    # Each entry: data length, address it is read to, two unused bytes.
    (SRC/'turbo_table.inc').write_text(
        ''.join(f'        dw {length},{syms["LOWK"] + off},0\n' for off, length in reversed(plan)))
    (SRC/'turbo_lines.inc').write_text(
        ''.join(f'        db "{packed_line(line)}"\n' for line in lines))
    shutil.copyfile(ORIGINAL, SRC/'turbo_boot.asm')
    shutil.copyfile(HERE.parent.parent / 'zx-ux/font4x8.bin', SRC/'font4x8.bin')
    loader = OUT/'turbo_boot.bin'
    result = subprocess.run([sjasm, '--nologo', f'--raw={loader}', 'turbo_boot.asm'],
                            cwd=SRC, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Turbo loader assembly failed:\n'+result.stdout+result.stderr)
    code = loader.read_bytes()
    if not 100 < len(code) < 0x1000:
        raise TurboFormatError('bootstrap outside inspected D000-DFFF range')
    if (SRC/'bloodaxe_loader.bin').read_bytes() not in code:
        raise TurboFormatError('the Bloodaxe loader is not in the bootstrap unmodified')
    standard = (osbuild.header(0,'ZX-UX UNIX',len(encode_basic()),10,len(encode_basic())),
                osbuild.tap_block(0xFF,encode_basic()))
    bootstrap = (osbuild.header(3,'ZX-UX BOOT',len(code),0xD000,0x8000),
                 osbuild.tap_block(0xFF,code))
    tzx = pack_tzx(standard, bootstrap, raw, pause_ms=pause_ms)
    if output_name not in ('ZX-UX-turbo-experimental.tzx', 'ZX-UX.tzx'):
        raise TurboFormatError('invalid boot output name')
    target = OUT/output_name
    if len(tzx) >= MAX_TZX_BYTES:
        raise TurboFormatError('boot TZX is at least 30,000 bytes')
    target.write_bytes(tzx)
    from turbo_verify import check_tzx
    check_tzx(target, raw, code, load_base=syms['LOWK'])
    if read_segments(make_segments(raw), image_length=len(raw)) != raw:
        raise TurboFormatError('generated tape image failed independent reconstruction')
    return target, len(code), lines


def main():
    import re
    if len(sys.argv) != 2:
        raise SystemExit('usage: turbo_boot_build.py SJASMPLUS-1.24.0')
    syms = {}
    for line in (SRC/'unix.sym').read_text().splitlines():
        m = re.match(r'(\S+): EQU 0x([0-9A-Fa-f]+)', line)
        if m:
            syms[m.group(1)] = int(m.group(2), 16)
    image = (OUT/'merged-image.bin').read_bytes()
    _, _, free, _ = osbuild.mkfs(syms, osbuild.program_list())
    tape, size, lines = create_tzx(sys.argv[1],syms, syms['kend']-0x6000,free)
    print('EXPERIMENTAL boot turbo:', tape, '| ROM bootstrap', size, 'bytes; image',len(image),'bytes')

if __name__ == '__main__':
    main()
