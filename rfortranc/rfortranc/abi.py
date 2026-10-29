"""Versioned F77S procedure ABI tags for retained ZX-UX Z80 SSO objects.

SSO is a linker format, not a FORTRAN object format. Keep the declarations in
checked SHA-256 sidecars so mixed separately-compiled sources cannot quietly
pass the wrong by-reference scalar or dynamic-array ABI to the same symbol.
This validates tagged objects; older, untagged SSO requires explicit opt-in.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

VERSION = 1
NAME = re.compile(r'^[A-Z][A-Z0-9]{0,5}$')
TYPES = {'INTEGER', 'REAL', 'LOGICAL'}


def path_for(obj):
    return Path(obj).with_suffix('.f77s-abi.json')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _parameter(unit, name):
    ty, dims = unit.vars[name]
    return {'type': ty, 'form': ('procedure' if name in unit.externals else
                                'array' if dims is not None else 'scalar'),
            'capacity_argument': bool(isinstance(dims, tuple) and
                                      any(not isinstance(x, int) for x in dims))}


def _signature(unit):
    return {'kind': unit.kind, 'result': unit.type if unit.kind == 'function' else None,
            'args': [_parameter(unit, name) for name in unit.args]}


def manifest(unit, known, object_file):
    """Keep only referenced procedures, not unrelated units in a compilation."""
    external = {}
    for name, called in known.items():
        if name == unit.name or called.kind == 'program':
            continue
        # A known external procedure may appear in CALL, an expression,
        # or as a procedure actual argument, including nested calls.
        pattern = re.compile(r'\b' + re.escape(name) + r'\b')
        if any(pattern.search(st.text) for st in unit.statements):
            external[name] = _signature(called)
    return {'version': VERSION, 'unit': unit.name, 'object_sha256': sha256(object_file),
            'exports': _signature(unit), 'requires': external}


def write(unit, known, object_file):
    dest = path_for(object_file)
    # Atomic sidecar publication, so a failed build doesn't leave a new tag
    # over a stale object. Repeated builds replace only their own sidecars.
    tmp = dest.with_name(dest.name + '.tmp')
    tmp.write_text(json.dumps(manifest(unit, known, object_file), indent=2,
                              sort_keys=True) + '\n', encoding='utf-8')
    tmp.replace(dest)


def validate(objects, allow_untagged=False):
    """Reject invalid/tampered or mutually inconsistent retained F77S objects.

    Legacy C48 SSO without metadata is only allowed with an explicit switch;
    no FORTRAN ABI verification is claimed for that mode.
    """
    if not objects:
        raise ValueError('no objects to ABI-check')
    tagged = [path_for(obj).is_file() for obj in objects]
    if not all(tagged):
        if any(tagged):
            raise ValueError('F77S ABI: mixed tagged and untagged SSO objects')
        if not allow_untagged:
            raise ValueError('F77S ABI tags missing; use --allow-untagged-objects for unverified C48 SSO')
        return False
    exports = {}
    required = {}
    for obj in objects:
        tag = path_for(obj)
        try:
            data = json.loads(tag.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise ValueError('F77S ABI: malformed tag ' + str(tag)) from exc
        if not isinstance(data, dict) or data.get('version') != VERSION:
            raise ValueError('F77S ABI: unsupported tag version ' + str(tag))
        name = data.get('unit')
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise ValueError('F77S ABI: invalid export name ' + str(tag))
        if data.get('object_sha256') != sha256(obj):
            raise ValueError('F77S ABI: object SHA-256 mismatch ' + str(obj))
        sig = data.get('exports')
        if not _valid_signature(sig) or name in exports:
            raise ValueError('F77S ABI: invalid or duplicate export ' + name)
        exports[name] = sig
        reqs = data.get('requires')
        if not isinstance(reqs, dict):
            raise ValueError('F77S ABI: invalid requirements for ' + name)
        for callee, expected in reqs.items():
            if not isinstance(callee, str) or not NAME.fullmatch(callee) or not _valid_signature(expected):
                raise ValueError('F77S ABI: invalid import in ' + name)
            required.setdefault(callee, []).append((name, expected))
    if sum(sig['kind'] == 'program' for sig in exports.values()) != 1:
        raise ValueError('F77S ABI: exactly one main PROGRAM required')
    for callee, callers in required.items():
        if callee not in exports:
            raise ValueError('F77S ABI: missing procedure ' + callee)
        for caller, expected in callers:
            if exports[callee] != expected:
                raise ValueError('F77S ABI mismatch for ' + callee + ' imported by ' + caller)
    return True


def _valid_signature(sig):
    if not isinstance(sig, dict) or set(sig) != {'kind', 'result', 'args'}:
        return False
    if sig['kind'] not in ('program', 'subroutine', 'function'):
        return False
    if (sig['kind'] == 'function') != (isinstance(sig['result'], str) and
                                    sig['result'] in TYPES):
        return False
    if not isinstance(sig['args'], list):
        return False
    for arg in sig['args']:
        if not isinstance(arg, dict) or set(arg) != {'type', 'form', 'capacity_argument'}:
            return False
        ty = arg['type']
        if (not isinstance(ty, str) or
                (ty not in TYPES and
                 not re.fullmatch(r'CHARACTER\*[1-9][0-9]*', ty))):
            return False
        if arg['form'] not in ('scalar', 'array', 'procedure') or type(arg['capacity_argument']) is not bool:
            return False
        if arg['form'] != 'array' and arg['capacity_argument']:
            return False
        if arg['form'] == 'procedure' and ty not in ('INTEGER', 'REAL'):
            return False
    return True
