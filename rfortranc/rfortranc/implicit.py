"""ANSI FORTRAN SUBSET implicit numeric/logical typing (partial).

Implicit defaults: I-N INTEGER, other letters REAL. Supports explicit
IMPLICIT INTEGER/REAL/LOGICAL letter and letter-range groups. It does not
change the default ZX-UX mode which requires explicit declarations.
"""
from __future__ import annotations
import re
from .translator import FortranError, NAME

DEFAULT = {chr(n): 'INTEGER' if 'I' <= chr(n) <= 'N' else 'REAL'
           for n in range(ord('A'), ord('Z') + 1)}
KEYWORDS = set('PROGRAM END INTEGER REAL LOGICAL IMPLICIT FUNCTION SUBROUTINE DO IF THEN ELSE ENDIF GO TO GOTO CALL READ WRITE PRINT FORMAT CONTINUE STOP RETURN MOD AND OR NOT EQ NE LT LE GT GE TRUE FALSE'.split())
LITERALS = re.compile(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"")
NUMBERS = re.compile(r'(?<![A-Z0-9_])(?:\d+\.?\d*|\.\d+)(?:[ED][+-]?\d+)?')


def mapping(statements):
    result = dict(DEFAULT)
    changed = set()
    for st in statements:
        if not st.text.startswith('IMPLICIT '):
            continue
        rest = st.text[len('IMPLICIT '):].strip()
        if rest == 'NONE':
            raise FortranError(st.line, 'IMPLICIT NONE is outside ANSI F77S')
        while rest:
            part = re.match(r'^\s*(INTEGER|REAL|LOGICAL)\s*\(([^()]*)\)\s*(?:,\s*|$)', rest)
            if not part:
                raise FortranError(st.line, 'unsupported F77S IMPLICIT declaration')
            ty, ranges = part.group(1), part.group(2)
            for range_item in ranges.split(','):
                pair = re.fullmatch(r'\s*([A-Z])\s*(?:-\s*([A-Z]))?\s*', range_item)
                if not pair:
                    raise FortranError(st.line, 'bad IMPLICIT letter range: ' + range_item)
                first, last = pair.group(1), pair.group(2) or pair.group(1)
                if first > last:
                    raise FortranError(st.line, 'reversed IMPLICIT letter range')
                for ordinal in range(ord(first), ord(last)+1):
                    letter = chr(ordinal)
                    if letter in changed:
                        raise FortranError(st.line, 'duplicate IMPLICIT letter: ' + letter)
                    changed.add(letter)
                    result[letter] = ty
            rest = rest[part.end():]
    return result


def infer(u, known):
    types = mapping(u.statements)
    explicitly_typed = set()
    for st in u.statements:
        declaration = re.fullmatch(r'(INTEGER|REAL|LOGICAL)\s+(.+)', st.text)
        if declaration:
            # These names were already checked and entered by parse().
            explicitly_typed.update(re.findall(NAME, declaration.group(2)))
    for name in u.args:
        if name not in explicitly_typed:
            u.vars[name] = (types[name[0]], None)
    for st in u.statements:
        s = st.text.strip()
        if (re.match(r'^(INTEGER|REAL|LOGICAL|IMPLICIT)\s+', s)
                or re.match(r'^FORMAT\s*\(', s)):
            continue
        s = LITERALS.sub(' ', s)
        s = re.sub(r'\.[A-Z]+\.', ' ', s)
        s = NUMBERS.sub(' ', s)
        for name in re.findall(NAME, s):
            if name in KEYWORDS or name in known or name in u.vars:
                continue
            if name not in u.vars:
                u.vars[name] = (types[name[0]], None)
