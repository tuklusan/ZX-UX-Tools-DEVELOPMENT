"""Minimal ANSI F77S DATA initializer lowering.

Supports single numeric/logical main-program scalar and 1D array objects.
Deliberately rejects implied DO, repeated initialization, type conversion,
subprogram DATA, and other forms not yet correctly modeled.
"""
from __future__ import annotations
import re
from .translator import FortranError, NAME, split_items


def initializers(unit):
    result = []
    used = set()
    saw_exec = False
    saw_data = False
    for st in unit.statements:
        s = st.text.strip()
        m = re.fullmatch(r'DATA\s+(.+)', s)
        if not m:
            if re.match(r'^(INTEGER|REAL|LOGICAL|CHARACTER|DIMENSION|IMPLICIT|COMMON|SAVE|EQUIVALENCE|INTRINSIC|EXTERNAL)\b', s):
                if saw_exec or saw_data:
                    raise FortranError(st.line, 'specification statement after DATA or executable statement')
            elif not re.match(r'^FORMAT\s*\(', s):
                saw_exec = True
            continue
        saw_data = True
        if unit.kind != 'program':
            raise FortranError(st.line, 'DATA in subprogram not yet supported; persistent storage required')
        if saw_exec:
            raise FortranError(st.line, 'F77S DATA must precede executable statements')
        parts = m.group(1)
        pos = 0
        while pos < len(parts):
            fst = parts.find('/', pos)
            if fst == -1:
                raise FortranError(st.line, 'bad DATA statement; expected /values/')
            snd = parts.find('/', fst + 1)
            if snd == -1:
                raise FortranError(st.line, 'missing closing DATA slash')
            name_src = parts[pos:fst].strip()
            val_src = parts[fst+1:snd].strip()
            if not name_src or not val_src:
                raise FortranError(st.line, 'empty DATA name or value list')
            targets = []
            for spec in split_items(name_src):
                item = re.fullmatch(r'(' + NAME + r')(?:\(\s*(\d+)\s*\))?', spec)
                if not item:
                    raise FortranError(st.line, 'unsupported DATA object: ' + spec)
                name, idx = item.groups()
                if name not in unit.vars:
                    raise FortranError(st.line, 'DATA object not declared: ' + name)
                typ, size = unit.vars[name]
                if name in unit.args or name == unit.name:
                    raise FortranError(st.line, 'DATA cannot initialize dummy/result object')
                if idx is not None:
                    n = int(idx)
                    if size is None or not 1 <= n <= size:
                        raise FortranError(st.line, 'invalid DATA array index')
                    targets.append((f'F_{name}[{n-1}]', typ))
                elif size is not None:
                    targets.extend((f'F_{name}[{i}]', typ) for i in range(size))
                else:
                    targets.append((f'F_{name}', typ))
            values = []
            for token in split_items(val_src):
                rep = re.fullmatch(r'(\d+)\s*\*\s*(.+)', token)
                count, literal = (int(rep.group(1)), rep.group(2).strip()) if rep else (1, token.strip())
                if count < 1 or count > 32767:
                    raise FortranError(st.line, 'invalid DATA repeat count')
                values.extend([literal] * count)
                if len(values) > 32767:
                    raise FortranError(st.line, 'DATA list too large')
            if len(values) != len(targets):
                raise FortranError(st.line, 'DATA object/value count mismatch')
            for (target, typ), val in zip(targets, values):
                if target in used:
                    raise FortranError(st.line, 'DATA object initialized twice: ' + target)
                used.add(target)
                if typ == 'INTEGER' and re.fullmatch(r'[+-]?\d+', val):
                    value = val
                elif typ == 'LOGICAL' and val in ('.TRUE.', '.FALSE.'):
                    value = '1' if val == '.TRUE.' else '0'
                elif typ == 'REAL' and re.fullmatch(r'[+-]?(?:\d+\.\d*|\.\d+)(?:E[+-]?\d+)?', val):
                    value = val
                else:
                    raise FortranError(st.line, 'DATA values must match type exactly: ' + val)
                result.append((target, value))
            pos = snd + 1
            if pos < len(parts):
                if parts[pos] != ',':
                    raise FortranError(st.line, 'DATA groups must be comma separated')
                pos += 1
                if pos == len(parts):
                    raise FortranError(st.line, 'trailing comma after DATA group')
    return result
