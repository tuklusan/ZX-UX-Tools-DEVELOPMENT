# ZX-UX distribution cassette: how it is made

Everything needed to build `ZX-UX.tzx`, the ZX-UX system cassette, copied from
the upstream project `tuklusan/ZX-UX-The-ZX-Spectrum-48K-Unix-Project-DEVELOPMENT`
(files under its `src/zx-ux`, `src/zx-ux-sdk/tools` and `build/dependencies`).
The upstream is read-only for this repository; nothing here is written back.

This copy differs from the upstream in one way: the cassette is received by the
turbo loader of the game Brian Bloodaxe (The Edge, 1985) instead of the
upstream's own bootstrap receiver (see "The loader" below). So the cassette
built here is no longer the same as `zx-ux/tzx/ZX-UX.tzx`, which is unchanged.

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
   it writes `turbo_table.inc` (the 24 blocks: length and address) and
   `turbo_lines.inc` (the 24 progress lines from `turbo_lines.txt`), assembles
   `turbo_boot.asm` (the bootstrap; it includes `bloodaxe_loader.bin` and
   `font4x8.bin`), and `turbo_segments.py` lays the image out as 24 turbo-speed
   TZX blocks behind a standard BASIC header block and the `ZX-UX BOOT` code
   block. `turbo_verify.py` and an independent reconstruction then check the
   result, which must be under 30,000 bytes.

## The loader

The ROM loads the BASIC program and the `ZX-UX BOOT` code block (`turbo_boot.asm`,
at D000h) as usual. The bootstrap draws the first of the 24 progress rows, copies
the loader to FF00h and runs it. The loader is the 256-byte routine hidden in
the `REM` line of the second BASIC program of the Brian Bloodaxe tape, used byte
for byte (`src/zx-ux/bloodaxe_loader.bin`: the code, FF00-FFB3, and its `LD ERR`
message, FFB4-FFBA). It is the ROM's own loading method (the ROM's edge-timing
routines at 05E3h and 05E7h with its own thresholds). Three things in it are
patched after the copy: the end of its block table, its block count (it loaded
two blocks, ours are 24), and the code after each block, which now jumps to
`part_done` in the bootstrap to draw the next progress row (and, after the last
block, to hand over to the kernel at 6000h).

A block is the part of the image followed by one parity byte (the XOR of the
part), and the loader reads it straight to its final address and checks the
parity. There is no header, ordinal or CRC, and no retry: on an error it prints
`LD ERR` and stops, as it does in the game. The pulses are those of the second
turbo block of the Bloodaxe tape (pilot 2042, sync 875 and 613, zero 513, one
1025 T-states), with each part's pilot doubled to 494 pulses (the loader needs
about 62 pulse pairs; Bloodaxe's own blocks have 247 pulses) and no gap between
the 24 blocks. With no gap, the pilot is also the time the bootstrap has to draw
a progress row (about 15 ms, against a pilot of 284 ms of which the loader needs
70 ms to lock).

## The banner

While the tape loads, the left half of the screen shows the 24 progress lines
(32 characters each, from `turbo_lines.txt`) and the right half shows a banner of
the Unix v1 basics: the system name, how to log in (any name of 1 to 8
characters, no password), the keys (ENTER ends a line, DELETE erases, EDIT is
Ctrl-D, BREAK interrupts) and the commands and manuals (`/bin` names from
`programs.txt`, `/usr/doc`). The BASIC loader prints it, in one `PRINT` of one
string whose embedded control codes (AT, INK, PAPER, BRIGHT) place and colour
it, so it needs no numbers in the BASIC and appears at once, before the first
part loads. It is defined by `BANNER` in `turbo_boot_build.py`: text rows 0 to
20, 16 characters wide from column 16 (not rows 13 and 14 or the last row: the
bytes 0Dh and 0Eh cannot be in a BASIC string, and a character in the last
column of the last row scrolls). The bootstrap only ever draws the 16 left
screen bytes and 16 left attribute cells of a row, so the banner is never
touched; just before the handover it resets all attributes to white on black,
because the kernel clears the bitmap but not the attributes.

Tested in Fuse 1.10 with every loading helper off (no auto-load, phantom typist,
loader detection, fast loading, tape traps or accelerate loaders) at 100% speed:
attach the tape, type `LOAD ""`, press F8. It loads to the `login:` prompt.

## Contents

    build/build.py                       the driver (tape part of upstream build.py)
    build/dependencies/sjasmplus/        SJASMPlus 1.24.0: Linux binary and source
    src/zx-ux/                           the kernel, programs, manuals, ROM, font
    src/zx-ux-sdk/tools/                 osbuild, turbo_boot_build, turbo_segments,
                                         turbo_verify, zxpack
