#!/usr/bin/env python3
"""Fail-closed checker gate for the exact Git index or a Git commit tree.

The owner's private checker archive must stay outside this repository.
"""
import argparse
import base64
import io
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile


def run_git(*args):
    proc = subprocess.run(['git', *args], check=True, stdout=subprocess.PIPE)
    return proc.stdout


def tracked_entries(ref):
    if ref is None:
        data = run_git('ls-files', '--stage', '-z')
    else:
        data = run_git('ls-tree', '-rz', '--full-tree', ref)
    entries = []
    seen = set()
    for record in data.split(b'\0'):
        if not record:
            continue
        meta, sep, raw_name = record.partition(b'\t')
        if not sep:
            raise ValueError('Invalid Git listing')
        parts = meta.split()
        if ref is None:
            if len(parts) != 3 or parts[2] != b'0':
                raise ValueError('Unresolved index entry')
            mode, oid = parts[:2]
        else:
            if len(parts) != 3 or parts[1] != b'blob':
                raise ValueError('Unscannable Git tree entry')
            mode, oid = parts[0], parts[2]
        if mode not in (b'100644', b'100755'):
            raise ValueError('Links, submodules, and other non-file entries are not supported')
        name = raw_name.decode('utf-8', 'strict')
        path = PurePosixPath(name)
        if (not name or name.startswith('/') or '\\' in name or
                any(part in ('', '.', '..') for part in name.split('/')) or
                path.as_posix() != name or name in seen):
            raise ValueError('Unsafe or duplicate tracked path')
        if not re.fullmatch(b'[a-f0-9]{40}|[a-f0-9]{64}', oid):
            raise ValueError('Invalid Git object identifier')
        seen.add(name)
        entries.append((oid, name))
    if not entries:
        raise ValueError('No tracked files found')
    return entries


def make_snapshot(entries, destination):
    # Git blobs, not the possibly dirty working tree, are scanned.
    with tempfile.TemporaryFile() as requests:
        for oid, _ in entries:
            requests.write(oid + b'\n')
        requests.seek(0)
        with subprocess.Popen(['git', 'cat-file', '--batch'], stdin=requests,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            for oid, name in entries:
                header = proc.stdout.readline().split()
                if len(header) != 3 or header[0] != oid or header[1] != b'blob':
                    raise ValueError('Missing or invalid Git blob')
                remaining = int(header[2])
                target = destination.joinpath(*PurePosixPath(name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('wb') as output:
                    while remaining:
                        block = proc.stdout.read(min(1024 * 1024, remaining))
                        if not block:
                            raise ValueError('Truncated Git blob')
                        output.write(block)
                        remaining -= len(block)
                if proc.stdout.read(1) != b'\n':
                    raise ValueError('Invalid Git blob framing')
            if proc.wait() != 0:
                raise ValueError('Git object reader failed')


def install_private_checker(destination):
    zip_path = os.environ.get('ZXUX_CHECKER_ZIP')
    zip_b64 = os.environ.get('ZXUX_CHECKER_ZIP_B64')
    if bool(zip_path) == bool(zip_b64):
        raise ValueError('Set exactly one private checker source: ZXUX_CHECKER_ZIP or ZXUX_CHECKER_ZIP_B64')
    if zip_path:
        checkout = Path(run_git('rev-parse', '--show-toplevel').decode().strip()).resolve()
        source = Path(zip_path).resolve()
        if source.is_relative_to(checkout):
            raise ValueError('Private checker must stay outside the Git checkout')
        archive = source.read_bytes()
    else:
        archive = base64.b64decode(zip_b64, validate=True)
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        if zf.testzip() is not None:
            raise ValueError('Private checker archive is damaged')
        names = set()
        for item in zf.infolist():
            name = item.filename
            mode = (item.external_attr >> 16) & 0o170000
            if (name in names or not name or name in ('.', '..') or
                    '/' in name or '\\' in name or item.is_dir() or
                    mode == 0o120000):
                raise ValueError('Unsafe private checker archive entry')
            names.add(name)
            file = destination / name
            file.write_bytes(zf.read(item))
            file.chmod(0o600)
        if not {'checker.py', 'rules.txt', 'external_tools.py'}.issubset(names):
            raise ValueError('Private checker archive missing required components')
    return destination / 'checker.py'


def checked_call(checker, *arguments):
    subprocess.run([sys.executable, '-B', str(checker), *map(str, arguments)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--staged', action='store_true', help='Scan the complete staged index')
    mode.add_argument('--ref', help='Scan the complete tree at a Git commit')
    mode.add_argument('--message-file', type=Path, help='Scan an exact commit message file')
    parser.add_argument('--check-ref-message', action='store_true',
                        help='Also scan the commit message for --ref')
    args = parser.parse_args()
    if not (args.staged or args.ref or args.message_file):
        parser.error('Choose --staged, --ref, or --message-file')
    if args.check_ref_message and not args.ref:
        parser.error('--check-ref-message requires --ref')

    with tempfile.TemporaryDirectory(prefix='zxux-gate-') as temp:
        root = Path(temp)
        checker = install_private_checker(root)
        checked_call(checker, 'self-test')
        if args.message_file:
            checked_call(checker, 'check', '--message-file', args.message_file)
        else:
            entries = tracked_entries(args.ref)
            snapshot = root / 'snapshot'
            snapshot.mkdir()
            make_snapshot(entries, snapshot)
            checked_call(checker, 'check', '--tree', snapshot)
            print(f'PASS: checked the complete Git snapshot ({len(entries)} tracked files; checker policy applies)')
            if args.check_ref_message:
                message = run_git('show', '-s', '--format=%B', args.ref)
                msg_file = root / 'message.txt'
                msg_file.write_bytes(message)
                checked_call(checker, 'check', '--message-file', msg_file)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.CalledProcessError,
            UnicodeError, OverflowError, EOFError) as error:
        print(f'FAIL: private checker gate blocked this operation ({type(error).__name__})', file=sys.stderr)
        sys.exit(1)
