#!/usr/bin/env python3
"""Run the private checker on added Git diff lines, not existing files."""
import argparse
import base64
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
DIFF_FLAGS = ('--no-ext-diff', '--no-textconv', '--no-color',
              '--find-renames', '--diff-filter=ACMRT', '--unified=0')


def git(*args):
    return subprocess.run(['git', *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True).stdout


def changed_lines(ref):
    if ref is None:
        endpoints = ('--cached', 'HEAD')
    else:
        parents = git('rev-list', '--parents', '-n', '1', ref).split()
        if not parents:
            raise ValueError('Missing commit')
        base = parents[1].decode('ascii') if len(parents) > 1 else EMPTY_TREE
        endpoints = (base, ref)
    raw_names = git('diff', *DIFF_FLAGS, '--name-only', '-z', *endpoints)
    names = raw_names.rstrip(b'\0').split(b'\0') if raw_names else []
    patch = git('diff', *DIFF_FLAGS, *endpoints)
    sections = []
    selected = None
    in_hunk = False
    for line in patch.splitlines(keepends=True):
        if line.startswith(b'diff --git '):
            if selected is not None:
                sections.append(bytes(selected))
            selected = bytearray()
            in_hunk = False
        elif line.startswith(b'@@ '):
            if selected is None:
                raise ValueError('Invalid Git diff')
            in_hunk = True
        elif in_hunk and line.startswith(b'+'):
            selected.extend(line[1:])
        elif in_hunk and line.startswith((b'-', b' ', b'\\')):
            pass
        else:
            in_hunk = False
    if selected is not None:
        sections.append(bytes(selected))
    if len(names) != len(sections):
        raise ValueError('Git diff path and content mismatch')
    result = []
    for raw_name, payload in zip(names, sections):
        name = raw_name.decode('utf-8', 'strict')
        if (not name or name.startswith('/') or '\\' in name or
                any(part in ('', '.', '..') for part in name.split('/'))):
            raise ValueError('Unsafe changed path')
        if name.rsplit('/', 1)[-1].casefold() in ('checker.zip', 'checker.zip.base64'):
            raise ValueError('Keep the private checker outside Git')
        result.append((name, payload))
    return result


def private_checker(destination):
    path = os.environ.get('ZXUX_CHECKER_ZIP')
    encoded = os.environ.get('ZXUX_CHECKER_ZIP_B64')
    if bool(path) == bool(encoded):
        raise ValueError('Set exactly one private checker source')
    if path:
        checkout = Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve()
        source = Path(path).resolve()
        if source.is_relative_to(checkout):
            raise ValueError('Private checker must stay outside the repository')
        data = source.read_bytes()
    else:
        data = base64.b64decode(encoded, validate=True)
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('Invalid private checker archive')
        seen = set()
        for entry in bundle.infolist():
            name = entry.filename
            mode = (entry.external_attr >> 16) & 0o170000
            if (name in seen or not name or '/' in name or '\\' in name or
                    entry.is_dir() or mode == 0o120000):
                raise ValueError('Unsafe private checker archive entry')
            seen.add(name)
            file = destination / name
            file.write_bytes(bundle.read(entry))
            file.chmod(0o600)
        if not {'checker.py', 'rules.txt', 'external_tools.py'}.issubset(seen):
            raise ValueError('Private checker archive is incomplete')
    return destination / 'checker.py'


def check(checker, *args, data=None):
    subprocess.run([sys.executable, '-B', str(checker), *map(str, args)],
                   input=data, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    scope = p.add_mutually_exclusive_group(required=True)
    scope.add_argument('--staged', action='store_true')
    scope.add_argument('--ref')
    scope.add_argument('--message-file', type=Path)
    p.add_argument('--check-ref-message', action='store_true')
    args = p.parse_args()
    if args.check_ref_message and not args.ref:
        p.error('--check-ref-message requires --ref')
    with tempfile.TemporaryDirectory(prefix='zxux-check-') as tmp:
        checker = private_checker(Path(tmp))
        check(checker, 'self-test')
        if args.message_file:
            check(checker, 'check', '--message-file', args.message_file)
            return 0
        delta = changed_lines(args.ref)
        total = 0
        for name, lines in delta:
            if lines:
                check(checker, 'check', '--path', name, '--stdin', data=lines)
                total += len(lines.splitlines())
            else:
                check(checker, 'check', '--path', name)
        print(f'PASS: checked {total} added lines in {len(delta)} changed paths')
        if args.check_ref_message:
            message = git('show', '-s', '--format=%B', args.ref)
            file = Path(tmp) / 'commit-message.txt'
            file.write_bytes(message)
            check(checker, 'check', '--message-file', file)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.CalledProcessError,
            UnicodeError, OverflowError, EOFError) as error:
        print(f'FAIL: private checker stopped the change ({type(error).__name__})',
              file=sys.stderr)
        sys.exit(1)
