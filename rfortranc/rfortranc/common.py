"""Early ANSI F77S named COMMON support: scalar numeric sequence association.

Fixed scalar and constant-bound INTEGER/REAL/LOGICAL arrays are handled here.
Layout uses storage sequence position; array extents can differ in rank if the
flat storage extent and numeric element type agree. Named and blank COMMON
are supported with restricted equal-size views. F77S SAVE /name/ is validated.
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
            if m:
                block, item_text = m.groups()
            else:
                m = re.fullmatch(r'COMMON\s*//\s*(.+)', st.text)
                if not m:
                    m = re.fullmatch(r'COMMON\s+([^/].*)', st.text)
                if not m:
                    raise FortranError(st.line, 'unsupported COMMON syntax (expected /name/, // or variable list)')
                block, item_text = '0', m.group(1)  # internal blank-block key
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
                if spec[0] not in ('INTEGER', 'REAL', 'LOGICAL'):
                    raise FortranError(st.line, 'COMMON requires INTEGER, REAL or LOGICAL: ' + name)
                if spec[1] is None:
                    length, is_array = 1, False
                else:
                    from .arrays import size as total_extent
                    length, is_array = total_extent(spec[1]), True
                signature = (spec[0], length, is_array)
                slot = len(members)
                # C48 identifiers have a 15-char maximum.
                if slot > 99:
                    raise FortranError(st.line, 'COMMON block exceeds 100 scalar slots')
                entry = signature
                if block in blocks and slot < len(blocks[block]) and blocks[block][slot] != signature:
                    raise FortranError(st.line, 'COMMON block type mismatch at position ' + str(slot + 1))
                members.append(entry)
                per_name[name] = 'f_com_' + block + '_' + str(slot)
        # ANSI F77S Appendix D3.8: SAVE permits *only* named COMMON blocks.
        # COMMON objects are emitted as static storage, so this is a checked
        # source-level lifetime declaration, not an extra allocation.
        saved = set()
        for st in unit.statements:
            if not re.match(r'^SAVE\b', st.text):
                continue
            tail = st.text[4:].strip()
            if not tail:
                raise FortranError(st.line, 'F77S SAVE must list named COMMON blocks')
            try:
                entries = split_items(tail)
            except ValueError as exc:
                raise FortranError(st.line, 'malformed SAVE common block list') from exc
            for entry in entries:
                m = re.fullmatch(r'/([A-Z][A-Z0-9]{0,5})/', entry.strip())
                if not m:
                    raise FortranError(st.line, 'F77S SAVE accepts only /named COMMON/ blocks')
                name = m.group(1)
                if name not in per_block:
                    raise FortranError(st.line, 'SAVE names COMMON block absent from unit: /' + name + '/')
                if name in saved:
                    raise FortranError(st.line, 'duplicate SAVE common block: /' + name + '/')
                saved.add(name)
        for block, members in per_block.items():
            types = list(members)
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
        for slot, (ty, count, is_array) in enumerate(blocks[block]):
            result.append('static ' + ('float' if ty == 'REAL' else 'int') + ' f_com_' + block + '_' + str(slot)
                          + ('[' + str(count) + ']' if is_array else '') + ';')
    return result, uses


def bind(text, aliases):
    """Replace exact generated C variable names, never literal contents."""
    if not aliases:
        return text
    tokens = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\bF_[A-Z][A-Z0-9_]*\b')
    return tokens.sub(lambda m: aliases.get(m.group(), m.group()), text)
