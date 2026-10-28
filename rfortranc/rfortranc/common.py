"""Early ANSI F77S named COMMON support: scalar numeric sequence association.

Only fixed scalar INTEGER/REAL/LOGICAL blocks are handled here. This remains
partial; layout mismatches, arrays and blank COMMON fail closed.
"""
import re
from .translator import FortranError, NAME, split_items


def layout(units):
    blocks = {}
    uses = {}
    for unit in units:
        per_block = {}
        per_name = {}
        for st in unit.statements:
            if not re.match(r'^COMMON\b', st.text):
                continue
            m = re.fullmatch(r'COMMON\s+/([A-Z][A-Z0-9]{0,5})/\s*(.+)', st.text)
            if not m:
                raise FortranError(st.line, 'only named scalar COMMON /name/ lists implemented')
            block, item_text = m.groups()
            members = per_block.setdefault(block, [])
            for token in split_items(item_text):
                name = token.strip()
                if not re.fullmatch(NAME, name) or len(name) > 6:
                    raise FortranError(st.line, 'COMMON requires scalar F77S names of 1..6 chars')
                if name in per_name:
                    raise FortranError(st.line, 'duplicate COMMON member: ' + name)
                if name in unit.args or name == unit.name:
                    raise FortranError(st.line, 'COMMON member cannot be dummy/function result')
                spec = unit.vars.get(name)
                if spec is None:
                    from .implicit import mapping
                    unit.vars[name] = (mapping(unit.statements)[name[0]], None)
                    spec = unit.vars[name]
                if spec[1] is not None or spec[0] not in ('INTEGER', 'REAL', 'LOGICAL'):
                    raise FortranError(st.line, 'COMMON arrays/character storage not yet supported: ' + name)
                slot = len(members)
                # C48 identifiers have a 15-char maximum.
                if slot > 99:
                    raise FortranError(st.line, 'COMMON block exceeds 100 scalar slots')
                entry = (spec[0], slot)
                if block in blocks and slot < len(blocks[block]) and blocks[block][slot] != spec[0]:
                    raise FortranError(st.line, 'COMMON block type mismatch at position ' + str(slot + 1))
                members.append(entry)
                per_name[name] = 'f_com_' + block + '_' + str(slot)
        for block, members in per_block.items():
            types = [t for t, _ in members]
            if block not in blocks:
                blocks[block] = types
            elif blocks[block] != types:
                raise FortranError(unit.line, 'COMMON block layout mismatch: /' + block + '/')
        if per_name:
            if any(re.match(r'^DATA\s+', st.text) for st in unit.statements):
                raise FortranError(unit.line, 'DATA with COMMON needs BLOCK DATA semantics (not supported)')
            uses[unit.name] = {'F_' + key: value for key, value in per_name.items()}
    result=[]
    for block in sorted(blocks):
        for slot, ty in enumerate(blocks[block]):
            result.append('static ' + ('float' if ty == 'REAL' else 'int') + ' f_com_' + block + '_' + str(slot) + ';')
    return result, uses


def bind(text, aliases):
    """Replace exact generated C variable names, never literal contents."""
    if not aliases:
        return text
    tokens = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\bF_[A-Z][A-Z0-9_]*\b')
    return tokens.sub(lambda m: aliases.get(m.group(), m.group()), text)
