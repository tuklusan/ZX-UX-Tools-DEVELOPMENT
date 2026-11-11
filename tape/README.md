# ZX-UX distribution cassette: how it is made

Everything needed to build `ZX-UX.tzx`, the ZX-UX system cassette, copied from
the upstream project `tuklusan/ZX-UX-The-ZX-Spectrum-48K-Unix-Project-DEVELOPMENT`
(files under its `src/zx-ux`, `src/zx-ux-sdk/tools` and `build/dependencies`).
The upstream is read-only for this repository; nothing here is written back.

## Build

    python3 -B build/build.py [PATH-TO-SJASMPLUS]

Run it from this folder or any other; paths resolve from the script. It needs
Python 3.8+ and SJASMPlus 1.24.0, looked up as the argument, then `sjasmplus` on
the PATH, then the Linux binary in `build/dependencies/sjasmplus/` (it needs
glibc 2.38, as on Debian 13; on any other system build it from the
`sjasmplus-1.24.0-src.tar.xz` beside it, or use the official Windows release).
The cassette is written to `build/out/ZX-UX.tzx`; `build/src` and `build/out`
are disposable and ignored by git.

Verified: with SJASMPlus 1.24.0 (the official Windows release, Python 3.12) the
build reproduces `zx-ux/tzx/ZX-UX.tzx` byte for byte, and so also the upstream's
`dist/zx-ux/tzx/ZX-UX.tzx`. Keep the text files in LF (`.gitattributes` does):
the manuals are packed into the cassette's file system as they are, and CRLF
ones make a different tape (20 bytes larger).

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
   it writes `turbo_plan.inc` and `turbo_lines.inc` (the 24 loader progress
   lines from `turbo_lines.txt`), assembles `turbo_boot.asm` (the
   machine-code loader; it includes `font4x8.bin`), and `turbo_segments.py`
   lays the image out as turbo-speed TZX segments behind a standard BASIC
   header block and the `ZX-UX BOOT` code block. `turbo_verify.py` and an
   independent reconstruction then check the result, which must be under
   30,000 bytes.

## Contents

    build/build.py                       the driver (tape part of upstream build.py)
    build/dependencies/sjasmplus/        SJASMPlus 1.24.0: Linux binary and source
    src/zx-ux/                           the kernel, programs, manuals, ROM, font
    src/zx-ux-sdk/tools/                 osbuild, turbo_boot_build, turbo_segments,
                                         turbo_verify, zxpack
