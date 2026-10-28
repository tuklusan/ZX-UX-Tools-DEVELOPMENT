#!/usr/bin/env python3
"""Install rfortranc as a sibling of rcc in a ZX-UX SDK source tree.

SDK's sdkpack.py automatically includes both the new bin shim and Python
package in the usual dist/sdk/bin/ + dist/sdk/bin/py layout.
"""
from pathlib import Path
import argparse
import shutil


def install(sdk):
    source = Path(__file__).resolve().parents[1]
    sdk = Path(sdk).resolve()
    if not (sdk / 'rcc').is_dir() or not (sdk / 'bin/rcc').is_file():
        raise SystemExit('Expected ZX-UX source SDK containing rcc/ and bin/rcc')
    dest = sdk / 'rfortranc'
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source / 'rfortranc', dest,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copy2(source / 'bin/rfortranc', sdk / 'bin/rfortranc')
    (sdk / 'bin/rfortranc').chmod(0o755)
    print('Installed', dest)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('sdk', help='path to src/zx-ux-sdk')
    install(p.parse_args().sdk)
