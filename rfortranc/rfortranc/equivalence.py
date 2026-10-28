"""Restricted F77S EQUIVALENCE storage association.

Supported: local INTEGER/LOGICAL/REAL scalar and fixed size numeric arrays,
constant array subscripts, overlapping groups, and transitive association.
The implementation checks type equality (a stricter safe subset of ANSI F77S)
and rejects association with COMMON, dummy arguments, or mixed-type storage.
"""
from __future__ import annotations
import re
from .translator import FortranError, NAME, split_items
from .arrays import size as array_size

_TERM = re.compile(r'^(' + NAME + r')(?:\s*\(\s*([\d, ]+)\s*\))?$')


def layout(unit, common_aliases):
    """Return (C local declarations, F_name -> local C storage expression)."""
    edges: dict[str, list[tuple[str, int]]] = {}
    for st in unit.statements:
        if not re.match(r'^EQUIVALENCE\b', st.text):
            continue
        tail = st.text[len('EQUIVALENCE'):].strip()
        try:
            groups = split_items(tail)
        except ValueError as exc:
            raise FortranError(st.line, 'malformed EQUIVALENCE groups') from exc
        for group in groups:
            if not (group.startswith('(') and group.endswith(')')):
                raise FortranError(st.line, 'EQUIVALENCE needs parenthesized groups')
            try:
                terms = split_items(group[1:-1])
            except ValueError as exc:
                raise FortranError(st.line, 'malformed EQUIVALENCE group') from exc
            if len(terms) < 2:
                raise FortranError(st.line, 'EQUIVALENCE group needs two or more objects')
            objects = []
            for raw in terms:
                m = _TERM.fullmatch(raw)
                if not m:
                    raise FortranError(st.line, 'unsupported EQUIVALENCE object: ' + raw)
                name, subs = m.groups()
                if name not in unit.vars:
                    raise FortranError(st.line, 'undeclared EQUIVALENCE object: ' + name)
                if name in unit.args or name == unit.name or ('F_' + name) in common_aliases:
                    raise FortranError(st.line, 'EQUIVALENCE cannot alias dummy, function or COMMON: ' + name)
                ty, dims = unit.vars[name]
                if ty not in ('INTEGER', 'REAL', 'LOGICAL'):
                    raise FortranError(st.line, 'unsupported EQUIVALENCE type: ' + ty)
                if dims is None:
                    if subs is not None:
                        raise FortranError(st.line, 'scalar has no EQUIVALENCE subscripts: ' + name)
                    offset = 0
                else:
                    shape = (dims,) if isinstance(dims, int) else dims
                    if subs is None:
                        offset = 0
                    else:
                        values = [int(x.strip()) for x in subs.split(',')]
                        if len(values) != len(shape) or any(v < 1 or v > d for v, d in zip(values, shape)):
                            raise FortranError(st.line, 'EQUIVALENCE constant subscript out of bounds: ' + name)
                        offset, stride = 0, 1
                        for v, d in zip(values, shape):
                            offset += (v - 1) * stride
                            stride *= d
                objects.append((name, ty, offset))
            if len({o[0] for o in objects}) != len(objects):
                raise FortranError(st.line, 'same object occurs twice in EQUIVALENCE group')
            if len({o[1] for o in objects}) != 1:
                raise FortranError(st.line, 'mixed-type EQUIVALENCE not yet supported')
            anchor_name, _, anchor_offset = objects[0]
            edges.setdefault(anchor_name, [])
            for name, _, index in objects[1:]:
                # base(name) + index = base(anchor) + anchor_offset
                shift = anchor_offset - index
                edges.setdefault(name, [])
                edges[anchor_name].append((name, shift))
                edges[name].append((anchor_name, -shift))
    declarations, aliases, seen = [], {}, set()
    for initial in edges:
        if initial in seen:
            continue
        base = {initial: 0}
        stack = [initial]
        while stack:
            name = stack.pop()
            seen.add(name)
            for other, shift in edges[name]:
                value = base[name] + shift
                if other in base:
                    if base[other] != value:
                        raise FortranError(unit.line, 'inconsistent EQUIVALENCE offsets')
                else:
                    base[other] = value
                    stack.append(other)
        types = {unit.vars[name][0] for name in base}
        if len(types) != 1:
            raise FortranError(unit.line, 'mixed-type transitive EQUIVALENCE not supported')
        lowest = min(base.values())
        highest = max(base[name] + (array_size(unit.vars[name][1]) if unit.vars[name][1] else 1)
                      for name in base)
        total = highest - lowest
        if total > 32767:
            raise FortranError(unit.line, 'EQUIVALENCE storage exceeds memory limits')
        ident = 'f_eq_' + str(len(declarations))
        declarations.append(('float' if 'REAL' in types else 'int') + ' ' + ident + '[' + str(total) + '];')
        for name in base:
            offset = base[name] - lowest
            if unit.vars[name][1] is None:
                aliases['F_' + name] = ident + '[' + str(offset) + ']'
            else:
                aliases['F_' + name] = ident if offset == 0 else '(&' + ident + '[' + str(offset) + '])'
    return declarations, aliases