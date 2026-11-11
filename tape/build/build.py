#!/usr/bin/env python3
"""Build the ZX-UX system cassette, build/out/ZX-UX.tzx, from tape/src/zx-ux.

This is only the tape part of the upstream project's build/build.py (the lines
that copy src/zx-ux to build/src, run osbuild.py and call
turbo_boot_build.create_tzx); the SDK, compilers, assets and docs it also
builds are not needed for the cassette.

    python3 -B build/build.py [--sjasm] [PATH-TO-SJASMPLUS]

SJASMPlus 1.24.0 is looked up as the optional argument, then `sjasmplus` on the
PATH, then the Linux binary in build/dependencies/sjasmplus/ (build it from the
source tarball next to it on other systems). The paths all resolve from this
file, not from the current directory.
"""
import pathlib
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
R = pathlib.Path(__file__).resolve().parents[1]      # the tape/ folder
B, S = R / 'build', R / 'src'
sys.path.insert(0, str(S / 'zx-ux-sdk/tools'))
import osbuild, turbo_boot_build


def main():
    argv = sys.argv[1:]
    argv = argv[1:] if argv[:1] == ['--sjasm'] else argv
    bundled = B / 'dependencies/sjasmplus/sjasmplus-1.24.0-linux-amd64'
    sjasm = (str(pathlib.Path(argv[0]).resolve()) if len(argv) == 1
             else shutil.which('sjasmplus') or str(bundled))
    no_cache = shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo')
    for name in ('src', 'out'):                      # a fresh, disposable workspace
        path = B / name
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise RuntimeError('Unsafe build workspace: ' + str(path))
        if path.exists():
            shutil.rmtree(path)
    shutil.copytree(S / 'zx-ux', B / 'src', ignore=no_cache)
    (B / 'out').mkdir()
    # Assemble the kernel and the programs, make the root file system and the
    # merged boot image: build/out/{unix.bin,lowk.bin,fs.img,merged-image.bin}.
    subprocess.run([sys.executable, '-B', str(S / 'zx-ux-sdk/tools/osbuild.py'), sjasm],
                   check=True)
    syms = dict((m.group(1), int(m.group(2), 16))
                for line in (B / 'src/unix.sym').read_text().splitlines()
                if (m := re.match(r'(\S+): EQU 0x([0-9A-Fa-f]+)', line)))
    _, _, free, _ = osbuild.mkfs(syms, osbuild.program_list())
    # Wrap the image as the turbo-loading cassette and verify it independently.
    turbo_boot_build.create_tzx(sjasm, syms, syms['kend'] - 0x6000, free,
                                output_name='ZX-UX.tzx')
    print('cassette:', B / 'out/ZX-UX.tzx')


if __name__ == '__main__':
    main()
