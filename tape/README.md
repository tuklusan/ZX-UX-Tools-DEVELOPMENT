# ZX-UX distribution cassette: how it is made

Everything needed to build `ZX-UX.tzx`, the ZX-UX system cassette, copied from
the upstream project `tuklusan/ZX-UX-The-ZX-Spectrum-48K-Unix-Project-DEVELOPMENT`
(files under its `src/zx-ux`, `src/zx-ux-sdk/tools` and `build/dependencies`).
The upstream is read-only for this repository; nothing here is written back.

This copy differs from the upstream in one way: the cassette is received by a
different turbo loader instead of the upstream's own bootstrap receiver (see
"The loader" below). So the cassette built here is no longer the same as
`zx-ux/tzx/ZX-UX.tzx`, which is unchanged.

## Build

    python3 -B build/build.py [PATH-TO-SJASMPLUS]

Run it from this folder or any other; paths resolve from the script. It needs
Python 3.8+ and SJASMPlus 1.24.0, looked up as the argument, then `sjasmplus` on
the PATH, then the Linux binary in `build/dependencies/sjasmplus/` (it needs
glibc 2.38, as on Debian 13; on any other system build it from the
`sjasmplus-1.24.0-src.tar.xz` beside it, or use the official Windows release).
The cassette is written to `build/out/ZX-UX.tzx`, which is tracked in git; the
other files in `build/out` and all of `build/src` are disposable and ignored.

Keep the text files in LF (`.gitattributes` does): the manuals are packed into
the cassette's file system as they are, and CRLF ones make a different tape (20
bytes larger). With the upstream's own receiver restored, this build (SJASMPlus
1.24.0, the official Windows release, Python 3.12) reproduced
`zx-ux/tzx/ZX-UX.tzx` byte for byte.

## What it does

`build/build.py` is only the tape part of the upstream `build/build.py`:

1. Copy `src/zx-ux` to `build/src`.
2. `src/zx-ux-sdk/tools/osbuild.py`
   - checks that `rom/48.rom` is the exact 16K ROM (SHA-256), as the kernel
     calls an internal SA-BYTES entry of it;
   - writes `ptab.inc` from the program list in `osbuild.py` and
     `programs.txt` (one `path label [octal mode bits]` per line: `/bin/ls`,
     `/bin/sh`, ... assembled as `t_<label>`..`e_<label>` inside the kernel);
   - assembles `unix.asm` (it includes `kvars.inc`, `const.inc`, `arena.asm`,
     `cext.asm`, `dev.asm`, `fs.asm`, `ulib.asm`, `zx.asm`, the `t_*.asm`
     programs and the generated `build/out/bootinfo.inc`) with SJASMPlus into
     `unix.bin`, `lowk.bin` and the symbol file `unix.sym`;
   - builds the root file system (i-node table and arena: `/bin`, `/dev`,
     `/etc`, `/tmp`, `/usr/doc` with the `zxpack`, `tar` and `more` manuals
     from the `*.doc` files, `/etc/motd`), packs files with `zxpack.py`, and
     repeats until the boot figures (`bootinfo.inc`: kernel size, free bytes,
     process count) settle;
   - writes `merged-image.bin` (low kernel, kernel and file system as one
     continuous block) and `kernel.json`.
3. `src/zx-ux-sdk/tools/turbo_boot_build.py` wraps the image as the cassette:
   it writes `turbo_table.inc` (the 25 blocks: length and address) and
   `turbo_lines.inc` (the 24 progress lines from `turbo_lines.txt`), assembles
   `turbo_boot.asm` (the bootstrap; it includes `turbo_loader.bin` and
   `font4x8.bin`), and `turbo_segments.py` lays out the cassette: a standard BASIC
   program and the `ZX-UX BOOT` code block, then the loading screen
   (`loading.scr`) and the image as 25 turbo-speed TZX blocks.
   `turbo_verify.py` and an independent reconstruction then check the result,
   which must be under 38,000 bytes.

## The loader

The ROM loads the BASIC program and the `ZX-UX BOOT` code block (`turbo_boot.asm`,
at D000h) as usual: the BASIC only sets the colours, clears the screen, clears
RAMTOP to CEFFh, loads the code and runs it. The bootstrap copies the loader to
FF00h and runs it. The loader is a 256-byte routine kept
unmodified in `src/zx-ux/turbo_loader.bin` (the code, FF00-FFB3, and its `LD ERR`
message, FFB4-FFBA). It is the ROM's own loading method (the ROM's edge-timing
routines at 05E3h and 05E7h with its own thresholds). Five things in it are
patched after the copy: the end of its block table, its block count (25), the
code after each block, which jumps to `part_done` in the bootstrap to draw the
next progress row (and, after the last block, to hand over to the kernel at
6000h), and two for speed, described below.

**Twice the ROM's speed.** The ROM's own edge routine (LD-EDGE-1, 05E7h) waits
about 350 T-states before it starts to look for an edge, which is why a loader
built on it needs pulses about as long as the ROM's. The bit reader's call to
LD-EDGE-2 (05E3h) is patched to call `edge2` in the bootstrap, which uses the ROM's
sampling loop (05EDh) without that delay, and the threshold that tells a one
from a zero is patched to match. The data pulses are then 428 T-states for a zero
and 855 for a one (two pulses per bit): 1283 T-states per bit on average against
the ROM's 2565, exactly twice the ROM's rate (2728 bits a second). In an emulation
of the loader against synthetic tape it decodes every bit with the tape running
8% fast or slow and 25 T-states of random jitter on each edge. The sync and the
pilot detection still use the ROM's routines and the longer pulses.

A block is its bytes followed by one parity byte (the XOR of the bytes), and the
loader reads it straight to its final address and checks the parity. There is no
header, ordinal or CRC, and no retry: on an error it prints `LD ERR` and stops.
The pulses are pilot 2042, sync 875 and 613, zero 428 and one 855 T-states, with
a pilot of 494 pulses before each block and no gap between the blocks (nor after
the bootstrap's own block). The loader needs about 165 pilot pulses (it waits 23
ms after the first edge, then counts 60 good pairs), so with no gap the pilot is
also the time the bootstrap has to draw a progress row (about 15 ms, against a
pilot of 288 ms of which the loader needs about 95 ms to lock).

## The loading screen and the progress lines

The first turbo block is the loading screen, a 6912-byte SCREEN$ read straight into
display memory (`src/zx-ux/loading.scr`); its left half is black. It was made from
the supplied picture (a 256x192 screen): the artwork is kept, the small lettering
(the "Unix for 48K / ZX Spectrum" subtitle, "DEC", "PDP11" and the monitor's
"v1 unix / $ _") is redrawn in clean pixel letters because the picture's own letters
had come out ragged at this size, and the ZX Spectrum at the bottom is redrawn after
a photograph of the real machine: four rows of keys in the real stagger (ten keys,
ten, nine and ENTER, CAPS SHIFT and ten with SYMBOL SHIFT and a wide SPACE) and the
rainbow flash as the real machine has it, running up the right-hand corner at 2:1.
Each 8x8 cell has at most two colours (an ink and a paper, all bright). In 27 cells
of the upper picture there are two colours besides the black (yellow lightning
touching the white mountains, and so on), which a Spectrum cell cannot show; there
the pixels of the less common colour take the cell's main colour: 115 of the 49,152
pixels (0.23%) differ in colour from the drawing, none in shape. The keyboard area
has no such pixels: the four rainbow bands are 8 pixels wide across and the keys stop
short of the cells they cross, so every cell there is two clean colours (the stripe's
cells use the neighbouring bands as ink and paper).

After each block (the first one after the screen has arrived) the bootstrap draws
one of the 24 lines of `turbo_lines.txt` (32 characters of the 4x8 font) in the left
half of the screen, one row at a time; it only ever draws the 16 left screen bytes
and 16 left attribute cells of a row, so the picture on the right is never touched.
The last line is already visible while the last block loads. Just before the
handover the bootstrap resets all attributes to white on black, because the kernel
clears the bitmap but not the attributes.

## Tested

The cassette is 35,136 bytes (the limit is 38,000). In Fuse 1.10 with every
loading helper off (no auto-load, phantom typist, loader detection, fast loading,
tape traps or accelerate loaders) at 100% speed (attach the tape, type `LOAD ""`,
press F8) the picture loads, the progress lines fill the left half, and it ends at
the `login:` prompt. The bootstrap and the tape's own pulses were also run through
an emulator, with the tape at nominal speed and 5% fast and 5% slow with 15
T-states of random jitter on every edge: in all three every byte of the image and
the right half of the screen came out identical.

## Contents

    build/build.py                       the driver (tape part of upstream build.py)
    build/dependencies/sjasmplus/        SJASMPlus 1.24.0: Linux binary and source
    src/zx-ux/                           the kernel, programs, manuals, ROM, font,
                                         the loading screen (loading.scr) and the
                                         bootstrap (turbo_boot.asm, turbo_loader.bin)
    src/zx-ux-sdk/tools/                 osbuild, turbo_boot_build, turbo_segments,
                                         turbo_verify, zxpack
