"""FORTRAN 77 subset -> C48. Z80 code, SSO and SSX are produced by ZX-UX rcc.

Design constraint: never silently reinterpret unsupported Fortran as valid C.
Syntax and scope are deliberately narrower than the full FORTRAN 77 standard.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


class FortranError(Exception):
    def __init__(self, line, message):
        super().__init__(f'line {line}: {message}')
        self.line = line


@dataclass
class Statement:
    line: int
    label: str | None
    text: str


@dataclass
class Unit:
    name: str
    kind: str
    line: int
    args: list[str] = field(default_factory=list)
    type: str = 'INTEGER'
    statements: list[Statement] = field(default_factory=list)
    vars: dict[str, tuple[str, int | tuple[int | str, ...] | None]] = field(default_factory=dict)
    temps: list[tuple[str, str]] = field(default_factory=list)
    statement_functions: dict[str, tuple[list[str], str]] = field(default_factory=dict)
    unprefixed: bool = False
    result_explicit: bool = False
    std: str = 'zxux'
    externals: set[str] = field(default_factory=set)
    intrinsics: set[str] = field(default_factory=set)


NAME = r'[A-Z][A-Z0-9_]*'
NAME_RE = re.compile(r'^' + NAME + r'$')
UNSUPPORTED = ('DATA', 'BLOCK DATA', 'EXTERNAL',
               'INTRINSIC', 'OPEN', 'CLOSE', 'REWIND', 'BACKSPACE',
               'ENDFILE', 'ENTRY', 'PAUSE', 'WRITE', 'INQUIRE', 'NAMELIST',
               'COMPLEX', 'DOUBLE PRECISION', 'ASSIGN ', 'ASSIGNED ',
               'BLOCK ', 'PARAMETER')


def strip_comment(text):
    """Remove ! comments without eating ! inside quoted Fortran strings."""
    quote = None
    i = 0
    while i < len(text):
        c = text[i]
        if quote and c == quote and text[i:i + 2] == quote * 2:
            i += 2
            continue
        if c == quote:
            quote = None
        elif not quote and c in "'\"":
            quote = c
        elif not quote and c == '!':
            return text[:i]
        i += 1
    return text


def lines(source):
    """Accept traditional 72-column fixed format and the upstream's free layout.

    Fixed labels require columns 1-5 and blank or continuation column 6.
    Free-layout labels at the start of a statement also work. Newline is a
    separator, except for fixed-format continuation lines.
    """
    out = []
    raw_lines = [raw.expandtabs(8) for raw in source.splitlines()]
    # Fixed-form C/c comments occupy column one, with no required blank after
    # the C.  Detect fixed form from code lines so free-form CALL/CONTINUE at
    # column one are still parsed as statements.
    fixed_count = sum(bool(re.match(r'^ {5}[ 0-9]', raw))
                      for raw in raw_lines if raw.strip())
    free_count = sum(bool(raw.strip() and not raw.startswith(('C ', 'c ', '*', '!'))
                          and not re.match(r'^ {5}[ 0-9]', raw))
                     for raw in raw_lines)
    fixed_form = fixed_count > 0 and fixed_count >= free_count
    for no, raw in enumerate(raw_lines, 1):
        if not raw.strip():
            continue
        if raw[0] in '*!' or (raw[0] in 'cC' and
            (fixed_form or len(raw) == 1 or raw[1].isspace())):
            continue
        fixed = (bool(re.match(r'^ {5}[ \d]', raw))
                 or bool(len(raw) >= 6 and re.fullmatch(r'[ 0-9]{5}', raw[:5])
                         and raw[:5].strip() and raw[5] in ' 0')
                 or bool(fixed_form and len(raw) >= 6 and raw[:5].strip() == ''
                         and raw[5] not in ' 0'))
        if fixed:
            lab = raw[:5].replace(' ', '') or None
            continuation = raw[5] not in ' 0'
            body = strip_comment(raw[6:72]).strip()
            if continuation:
                if not out or lab:
                    raise FortranError(no, 'orphaned continuation line')
                out[-1].text += ' ' + body
                continue
        else:
            body = strip_comment(raw).strip()
            lab = None
            m = re.match(r'^(\d{1,5})\s+(.+)$', body)
            if m:
                lab, body = m.groups()
        if body:
            if lab and (not lab.isdecimal() or int(lab) > 99999):
                raise FortranError(no, 'invalid statement label')
            if lab:
                lab = str(int(lab))  # 00010 and 10 name the same statement
            out.append(Statement(no, lab, body.upper() if not re.search(r"['\"]", body) else _keywords_upper(body)))
    return out


def _keywords_upper(line):
    # Fortran is case insensitive except for character literals.
    p, q, quote, i = [], [], None, 0
    while i < len(line):
        c = line[i]
        if quote:
            q.append(c)
            if c == quote:
                if i + 1 < len(line) and line[i + 1] == quote:
                    q.append(line[i + 1]); i += 1
                else:
                    quote = None
            i += 1
            continue
        if c in "'\"":
            quote = c
            p.append(''.join(q).upper()); q = [c]
        else:
            if q and q[0] in "'\"":
                p.append(''.join(q)); q = []
            q.append(c)
        i += 1
    p.append(''.join(q) if quote or (q and q[0] in "'\"") else ''.join(q).upper())
    return ''.join(p)


def split_items(s):
    """Comma-separated arguments respecting parentheses and string literals."""
    parts, buf, level, quote, i = [], [], 0, None, 0
    while i < len(s):
        c = s[i]
        if quote:
            buf.append(c)
            if c == quote:
                if i + 1 < len(s) and s[i + 1] == quote:
                    buf.append(s[i + 1]); i += 1
                else:
                    quote = None
        elif c in "'\"":
            quote = c; buf.append(c)
        elif c == '(':
            level += 1; buf.append(c)
        elif c == ')':
            level -= 1; buf.append(c)
        elif c == ',' and level == 0:
            parts.append(''.join(buf).strip()); buf = []
        else:
            buf.append(c)
        i += 1
    if quote or level != 0:
        raise ValueError('unbalanced expression or string')
    parts.append(''.join(buf).strip())
    return parts


def expand_static_io_items(values, unit, line):
    """Expand fixed whole arrays and literal-control I/O implied-DO.

    General variable control bounds require runtime FORMAT reversion; reject
    unsupported bounds rather than silently producing the wrong record.
    """
    from .arrays import size as total_extent
    out = []
    final_indices = []
    def emit(item, depth):
        if depth > 3 or len(out) > 255:
            raise FortranError(line, 'I/O implied-DO nesting/list exceeds target limits')
        item = item.strip()
        if item.startswith('(') and item.endswith(')'):
            parts = split_items(item[1:-1])
            control_at = next((i for i in range(len(parts))
                               if re.fullmatch(NAME + r'\s*=\s*[+-]?\d+', parts[i])), None)
            if control_at is not None and control_at > 0:
                control = parts[control_at]
                var, start = [x.strip() for x in control.split('=', 1)]
                if unit.vars.get(var) != ('INTEGER', None):
                    raise FortranError(line, 'implied-DO index must be INTEGER scalar')
                bounds = parts[control_at+1:]
                if len(bounds) not in (1, 2) or any(not re.fullmatch(r'[+-]?\d+', x) for x in bounds):
                    raise FortranError(line, 'runtime implied-DO bounds are not yet implemented')
                first, last = int(start), int(bounds[0])
                stride = int(bounds[1]) if len(bounds) == 2 else 1
                if stride == 0:
                    raise FortranError(line, 'implied-DO step must be nonzero')
                iters = list(range(first, last + (1 if stride > 0 else -1), stride))
                if len(iters) * control_at + len(out) > 255:
                    raise FortranError(line, 'I/O implied-DO expansion exceeds 255 items')
                for n in iters:
                    for obj in parts[:control_at]:
                        emit(re.sub(r'\b' + re.escape(var) + r'\b', str(n), obj), depth+1)
                final_indices.append((var, iters[-1] + stride if iters else first))
                return
        if re.fullmatch(NAME, item) and item in unit.vars and unit.vars[item][1] is not None:
            _ty, dims = unit.vars[item]
            if dynamic_extent(dims):
                raise FortranError(line, 'runtime whole-array I/O extent not yet implemented')
            total = total_extent(dims)
            if total + len(out) > 255:
                raise FortranError(line, 'whole-array I/O exceeds 255 elements')
            for linear in range(total):
                offset = linear
                subs = []
                for bound in ((dims,) if isinstance(dims, int) else dims):
                    subs.append(str(offset % bound + 1))
                    offset //= bound
                out.append(item + '(' + ','.join(subs) + ')')
            return
        if not re.fullmatch(NAME + r'(?:\s*\(\s*[+-]?\d+(?:\s*,\s*[+-]?\d+){0,2}\s*\))?', item):
            raise FortranError(line, 'F77S I/O item must be scalar or simple array element: ' + item)
        if len(out) >= 255:
            raise FortranError(line, 'I/O list exceeds 255 items')
        out.append(item)
    for val in values:
        emit(val, 0)
    return out, final_indices


def parse(source, std='zxux'):
    units = []
    unit = None
    for st in lines(source):
        s = st.text.strip()
        fm = re.fullmatch(r'(INTEGER|REAL|LOGICAL)\s+FUNCTION\s+(' + NAME + r')\s*\(([^)]*)\)', s)
        bare = re.fullmatch(r'FUNCTION\s+(' + NAME + r')\s*\(([^)]*)\)', s)
        sm = re.fullmatch(r'SUBROUTINE\s+(' + NAME + r')\s*\(([^)]*)\)', s)
        pm = re.fullmatch(r'PROGRAM\s+(' + NAME + r')', s)
        if fm or bare or sm or pm:
            if unit:
                raise FortranError(st.line, 'missing END before next program unit')
            if fm:
                ty, name, arg = fm.groups(); kind = 'function'
            elif bare:
                name, arg = bare.groups(); kind = 'function'
                ty = 'INTEGER' if 'I' <= name[0] <= 'N' else 'REAL'
            elif sm:
                name, arg = sm.groups(); ty, kind = 'INTEGER', 'subroutine'
            else:
                name = pm.group(1); arg, ty, kind = '', 'INTEGER', 'program'
            args = [] if not arg.strip() else [a.strip() for a in split_items(arg)]
            if any(not NAME_RE.fullmatch(a) for a in args) or len(args) != len(set(args)):
                raise FortranError(st.line, 'invalid or duplicate dummy arguments')
            unit = Unit(name, kind, st.line, args, ty, unprefixed=bool(bare), std=std)
            continue
        if s == 'END':
            if unit is None:
                raise FortranError(st.line, 'END without program unit')
            units.append(unit); unit = None
            continue
        if unit is None:
            if not units and not s.startswith(('FUNCTION', 'SUBROUTINE')):
                # FORTRAN permits an unnamed main program.
                unit = Unit('MAIN', 'program', st.line, std=std)
            else:
                raise FortranError(st.line, 'statement outside program unit')
        unit.statements.append(st)
    if unit:
        raise FortranError(unit.line, 'missing END')
    if not units or sum(u.kind == 'program' for u in units) != 1:
        raise FortranError(1, 'exactly one main program is required')
    names = [u.name for u in units]
    if len(names) != len(set(names)):
        raise FortranError(1, 'duplicate program unit')
    for u in units:
        for a in u.args:
            u.vars[a] = ('INTEGER', None)
        if u.kind == 'function':
            u.vars[u.name] = (u.type, None)
        for st in u.statements:
            m = re.fullmatch(r'(INTEGER|REAL|LOGICAL|CHARACTER(?:\s*\*\s*(?:\d+|\(\s*\d+\s*\)))?)\s+(.+)', st.text)
            if not m:
                continue
            ty, rest = m.groups()
            if ty.startswith('CHARACTER'):
                mlen = re.fullmatch(r'CHARACTER(?:\s*\*\s*(?:([0-9]+)|\(\s*([0-9]+)\s*\)))?', ty)
                width = int(mlen.group(1) or mlen.group(2)) if (mlen.group(1) or mlen.group(2)) else 1
                if not 1 <= width <= 255:
                    raise FortranError(st.line, 'F77S CHARACTER length must be 1..255')
                ty = 'CHARACTER*' + str(width)
            for spec in split_items(rest):
                var = re.fullmatch(r'(' + NAME + r')(?:\s*\(\s*([^()]*)\s*\))?', spec)
                if not var:
                    raise FortranError(st.line, 'unsupported declaration: ' + spec)
                name, count = var.groups()
                size = parse_dims(count, name, u, st.line) if count is not None else None
                if name in u.vars and name not in u.args and name != u.name:
                    raise FortranError(st.line, 'duplicate declaration: ' + name)
                u.vars[name] = (ty, size)
                if name == u.name and u.kind == 'function':
                    u.result_explicit = True
    # ANSI F77S DIMENSION may appear independently of INTEGER/REAL/LOGICAL.
    # Fixed-size arrays are implemented; adjustable/assumed-size dummy arrays
    # are deliberately diagnosed rather than silently miscompiled.
    for u in units:
        implicit_types = None
        for st in u.statements:
            dim_statement = re.fullmatch(r'DIMENSION\s+(.+)', st.text)
            if not dim_statement:
                continue
            for spec in split_items(dim_statement.group(1)):
                var = re.fullmatch(r'(' + NAME + r')\s*\(\s*([^()]*)\s*\)', spec)
                if not var:
                    raise FortranError(st.line, 'unsupported DIMENSION specification: ' + spec)
                name, counts = var.groups()
                dims = parse_dims(counts, name, u, st.line)
                if name == u.name:
                    raise FortranError(st.line, 'DIMENSION cannot apply to function result')
                present = u.vars.get(name)
                if present and present[1] is not None:
                    raise FortranError(st.line, 'duplicate array dimensions: ' + name)
                if present:
                    ty = present[0]
                elif std == 'f77s':
                    if implicit_types is None:
                        from .implicit import mapping
                        implicit_types = mapping(u.statements)
                    ty = implicit_types[name[0]]
                else:
                    raise FortranError(st.line, 'DIMENSION needs an explicitly typed name: ' + name)
                u.vars[name] = (ty, dims)
    if std == 'f77s':
        from .implicit import infer, mapping
        known = set(names)
        for u in units:
            infer(u, known)
            if u.unprefixed:
                resolved = (u.vars[u.name][0] if u.result_explicit
                            else mapping(u.statements)[u.name[0]])
                if resolved not in ('INTEGER', 'REAL', 'LOGICAL'):
                    raise FortranError(u.line, 'non-numeric unprefixed FUNCTION return unsupported')
                u.type = resolved
                u.vars[u.name] = (resolved, None)
    for u in units:
        for st in u.statements:
            decl = re.fullmatch(r'(EXTERNAL|INTRINSIC)\s+(.+)', st.text)
            if not decl:
                continue
            kind, listing = decl.groups()
            for name in split_items(listing):
                if not re.fullmatch(r'[A-Z][A-Z0-9]{0,5}', name):
                    raise FortranError(st.line, 'F77S procedure declaration name must be 1..6 chars')
                if name in u.externals or name in u.intrinsics:
                    raise FortranError(st.line, 'duplicate EXTERNAL/INTRINSIC procedure name: ' + name)
                if name in u.args or u.vars.get(name, (None, None))[1] is not None:
                    raise FortranError(st.line, 'EXTERNAL/INTRINSIC name conflicts with dummy/array')
                if kind == 'INTRINSIC':
                    if name not in ('ABS','IABS','INT','IFIX','FLOAT','AINT','NINT',
                                    'SQRT','SIN','COS','EXP','LOG','ALOG','SINH','COSH','TANH','ANINT','REAL','TAN','ASIN','ACOS','ATAN','ATAN2','ALOG10','AMOD','ISIGN','SIGN','IDIM','DIM','MAX0','MIN0','AMAX1','AMIN1','AMAX0','AMIN0','MAX1','MIN1','MOD'):
                        raise FortranError(st.line, 'INTRINSIC specific not yet supported: ' + name)
                    u.intrinsics.add(name)
                else:
                    if name in ('SIN','COS','EXP','LOG','TAN','ASIN','ACOS','ATAN','ATAN2','ALOG10','AMOD','ABS','IABS','INT','MOD'):
                        raise FortranError(st.line, 'external intrinsic-name shadowing not yet supported')
                    u.externals.add(name)
    # Statement functions have specification scope, before DATA/executables.
    # An explicit array declaration distinguishes F(I)=... array assignment
    # from a statement-function definition F(X)=....
    for u in units:
        saw_sf = False
        saw_exec = False
        saw_data = False
        for st in u.statements:
            text = st.text.strip()
            spec = (re.match(r'^(INTEGER|REAL|LOGICAL|DIMENSION|IMPLICIT|COMMON|SAVE|EQUIVALENCE|EXTERNAL|INTRINSIC)\b', text)
                    or re.match(r'^CHARACTER(?:\*|\s)', text))
            if spec:
                if saw_sf or saw_data or saw_exec:
                    raise FortranError(st.line, 'specification after statement function/DATA/executable')
                continue
            if re.match(r'^DATA\s+', text):
                if saw_exec:
                    raise FortranError(st.line, 'DATA after executable statement')
                saw_data = True
                continue
            if re.match(r'^FORMAT\s*\(', text):
                continue
            sf = re.fullmatch(r'(' + NAME + r')\s*\(([^()]*)\)\s*=\s*(.+)', text)
            if sf and u.vars.get(sf.group(1), ('', None))[1] is None:
                name, names, expression_text = sf.groups()
                args = [arg.strip() for arg in split_items(names)]
                if (not args or any(not NAME_RE.fullmatch(arg) or len(arg) > 6 for arg in args)
                        or len(args) != len(set(args)) or name in u.args
                        or len(name) > 6 or name == u.name):
                    raise FortranError(st.line, 'invalid statement function/dummy names')
                if saw_data or saw_exec:
                    raise FortranError(st.line, 'statement function after DATA/executable')
                if name in u.statement_functions:
                    raise FortranError(st.line, 'duplicate statement function: ' + name)
                if u.vars.get(name, ('REAL', None))[0].startswith('CHARACTER*'):
                    raise FortranError(st.line, 'CHARACTER statement functions excluded in F77S')
                u.statement_functions[name] = (args, expression_text)
                saw_sf = True
            else:
                saw_exec = True
    for u in units:
        shared_names = common_scalar_names(u)
        for name, (ty, dims) in u.vars.items():
            if dims is not None and ty.startswith('CHARACTER*') and not dynamic_extent(dims):
                from .arrays import size as total_extent
                width = int(ty.split('*')[1])
                if total_extent(dims) * (width + 1) > 32767:
                    raise FortranError(u.line, 'CHARACTER array byte extent exceeds ZX-UX 16-bit range')
            if dynamic_extent(dims):
                for bound in dims:
                    if isinstance(bound, str) and bound != '*':
                        if u.vars.get(bound) != ('INTEGER', None) or (bound not in u.args and bound not in shared_names):
                            raise FortranError(u.line, 'adjustable array bound must be INTEGER scalar dummy or COMMON: ' + bound)
                if ty.startswith('CHARACTER*'):
                    raise FortranError(u.line, 'adjustable CHARACTER dummy arrays not yet implemented')
                if u.kind == 'function':
                    raise FortranError(u.line, 'adjustable FUNCTION dummy arrays not yet implemented')
    return units




def common_scalar_names(unit):
    """COMMON scalar names usable as adjustable dummy-array bounds."""
    names = set()
    for st in unit.statements:
        m = re.fullmatch(r'COMMON\s+(?:/[A-Z][A-Z0-9]{0,5}/|//)?\s*(.+)', st.text)
        if m:
            names.update(item.strip() for item in split_items(m.group(1))
                         if NAME_RE.fullmatch(item.strip()))
    return names


def parse_dims(spec, name, unit, line):
    """Fixed bounds or INTEGER dummy-controlled rank-1..3 numeric arrays.

    Each adjustable bound names an INTEGER scalar dummy. An assumed-size '*'
    is permitted only at the last dimension. The caller passes the remaining
    actual sequence length for runtime capacity checks.
    """
    pieces = [p.strip() for p in spec.split(',')]
    if len(pieces) > 3 or not pieces or any(not p for p in pieces):
        raise FortranError(line, 'bad array rank or dimensions: ' + spec)
    if all(re.fullmatch(r'\d+', p) for p in pieces):
        dims = tuple(int(p) for p in pieces)
        from .arrays import size as total_extent
        if any(d < 1 or d > 32767 for d in dims) or total_extent(dims) > 32767:
            raise FortranError(line, 'array extent or total size out of bounds')
        return dims[0] if len(dims) == 1 else dims
    if name not in unit.args:
        raise FortranError(line, 'adjustable array must be a dummy argument')
    dims = []
    for i, token in enumerate(pieces):
        if re.fullmatch(r'\d+', token):
            value = int(token)
            if value < 1 or value > 32767:
                raise FortranError(line, 'array extent or total size out of bounds')
            dims.append(value)
        elif token == '*' and i == len(pieces)-1:
            dims.append(token)
        elif NAME_RE.fullmatch(token) and (token in unit.args or token in common_scalar_names(unit)) and token != name:
            dims.append(token)
        else:
            raise FortranError(line, 'adjustable bound must be a scalar dummy argument: ' + token)
    from .arrays import size as total_extent
    if total_extent(tuple(x for x in dims if isinstance(x, int))) > 32767:
        raise FortranError(line, 'array extent or total size out of bounds')
    return tuple(dims)


def dynamic_extent(dims):
    return isinstance(dims, tuple) and any(isinstance(x, str) for x in dims)


def array_subscript(indices, name, unit, line):
    """Checked column-major offset, honoring the caller's actual capacity."""
    dims = unit.vars[name][1]
    if dynamic_extent(dims):
        if len(indices) != len(dims):
            raise FortranError(line, 'dummy array subscript count must match rank')
        capacity = 'F__LEN_' + name
        stride = '1'
        terms = []
        for i, (sub, bound) in enumerate(zip(indices, dims)):
            if bound == '*':
                limit = '(' + capacity + ' / (' + stride + '))'
            elif isinstance(bound, str):
                scalar = '(*F_' + bound + ')' if bound in unit.args else 'F_' + bound
                limit = 'f_extent(' + scalar + ', (' + capacity + ' / (' + stride + ')))'
            else:
                limit = str(bound)
            term = 'f_index(' + sub + ', ' + limit + ')'
            terms.append(term if stride == '1' else '(' + term + ' * (' + stride + '))')
            if i < len(dims)-1:
                stride = '(' + stride + ' * (' + limit + '))'
        return 'f_seqcheck((' + ' + '.join(terms) + '), ' + capacity + ', 1)'
    from .arrays import offset
    return offset(indices, dims, line)


TOKENS = re.compile(r"\s*(?:((?:\d+(?:\.\d*)?|\.\d+)(?:[ED][+-]?\d+)?)|(\.[A-Z]+\.)|([A-Z][A-Z0-9_]*)|(\*\*|[+\-*/(),]))", re.I)
PRECEDENCE = {'.OR.': 1, '.AND.': 2, '.EQ.': 3, '.NE.': 3, '.LT.': 3,
              '.LE.': 3, '.GT.': 3, '.GE.': 3, '+': 4, '-': 4, '*': 5, '/': 5,
              '**': 7}
BIN = {'.OR.': '||', '.AND.': '&&', '.EQ.': '==', '.NE.': '!=', '.LT.': '<',
       '.LE.': '<=', '.GT.': '>', '.GE.': '>='}


class Expr:
    def __init__(self, text, unit, known_units, line,
                 substitutions=None, active_functions=frozenset()):
        self.unit, self.known, self.line = unit, known_units, line
        self.substitutions = substitutions or {}
        self.active_functions = active_functions
        self.expr_types = {}
        self.toks = []
        pos = 0
        while pos < len(text):
            if text[pos:].isspace():
                break
            m = TOKENS.match(text, pos)
            if not m:
                raise FortranError(line, 'unsupported expression near: ' + text[pos:pos+20])
            self.toks.append(next(g for g in m.groups() if g is not None).upper())
            pos = m.end()
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def pop(self):
        t = self.peek()
        if t is None:
            raise FortranError(self.line, 'incomplete expression')
        self.i += 1
        return t

    def read(self):
        expr = self.pratt(0)
        if self.peek():
            raise FortranError(self.line, 'unexpected token: ' + self.peek())
        return expr

    def pratt(self, min_prec):
        t = self.pop()
        if t in ('+', '-', '.NOT.'):
            op = '!' if t == '.NOT.' else t
            operand = self.pratt(6)
            lhs = '(' + op + operand + ')'
            result_type = 'LOGICAL' if t == '.NOT.' else self.expr_types[operand]
        elif t == '(':
            operand = self.pratt(0)
            lhs = '(' + operand + ')'
            result_type = self.expr_types[operand]
            if self.pop() != ')':
                raise FortranError(self.line, 'missing closing parenthesis')
        elif t in ('.TRUE.', '.FALSE.'):
            lhs = '1' if t == '.TRUE.' else '0'
            result_type = 'LOGICAL'
        elif re.fullmatch(r'\d+(?:\.\d*)?(?:[ED][+-]?\d+)?|\.\d+(?:[ED][+-]?\d+)?', t):
            lhs = t.replace('D', 'E')
            result_type = 'REAL' if '.' in t or 'E' in t or 'D' in t else 'INTEGER'
        elif NAME_RE.fullmatch(t):
            if self.peek() == '(':
                self.pop()
                params = []
                if self.peek() != ')':
                    while True:
                        params.append(self.pratt(0))
                        if self.peek() != ',':
                            break
                        self.pop()
                if self.pop() != ')':
                    raise FortranError(self.line, 'bad function or array argument list')
                if t in self.unit.vars and self.unit.vars[t][1] is not None:
                    if self.unit.vars[t][0].startswith('CHARACTER*'):
                        raise FortranError(self.line, 'CHARACTER array element requires character assignment/comparison or A FORMAT')
                    if any(self.expr_types[p] != 'INTEGER' for p in params):
                        raise FortranError(self.line, 'array subscript expression must have INTEGER type')
                    if self.unit.std == 'f77s' and any(
                            re.search(r'\bf_[a-z][a-z0-9_]*\s*\(|\bF_[A-Z][A-Z0-9_]*\s*\[', p)
                            for p in params):
                        raise FortranError(self.line, 'F77S subscript cannot contain function/array-element references')
                    lhs = 'F_' + t + '[' + array_subscript(params, t, self.unit, self.line) + ']'
                    result_type = self.unit.vars[t][0]
                elif t == 'INT' and len(params) == 1:
                    # ANSI subset numeric INT: discard the fractional part
                    # (truncation toward zero, not floor or rounding).
                    lhs = 'f_int_real(' + params[0] + ')'
                    result_type = 'INTEGER'
                elif t in ('ABS', 'IABS') and len(params) == 1:
                    arg_type = self.expr_types[params[0]]
                    if arg_type == 'INTEGER':
                        lhs = 'f_abs_int(' + params[0] + ')'
                        result_type = 'INTEGER'
                    elif t == 'ABS' and arg_type == 'REAL':
                        lhs = 'f_abs_real(' + params[0] + ')'
                        result_type = 'REAL'
                    else:
                        raise FortranError(self.line, t + ' intrinsic argument type mismatch')
                elif t in ('SQRT', 'SIN', 'COS', 'EXP', 'LOG', 'ALOG', 'TAN', 'ASIN', 'ACOS', 'ATAN', 'ALOG10', 'SINH', 'COSH', 'TANH') and len(params) == 1:
                    if self.expr_types[params[0]] != 'REAL':
                        raise FortranError(self.line, t + ' needs REAL argument')
                    lhs = 'f_' + ('sqrt' if t == 'SQRT' else 'log' if t == 'ALOG' else t.lower()) + '_real(' + params[0] + ')'
                    result_type = 'REAL'
                elif t in ('FLOAT', 'REAL', 'IFIX', 'AINT', 'NINT', 'ANINT') and len(params) == 1:
                    arg_type = self.expr_types[params[0]]
                    if (t == 'FLOAT' and arg_type != 'INTEGER' or
                        t == 'REAL' and arg_type not in ('INTEGER', 'REAL') or
                        t not in ('FLOAT', 'REAL') and arg_type != 'REAL'):
                        raise FortranError(self.line, t + ' intrinsic argument type mismatch')
                    lhs = ('((float)(' + params[0] + '))' if t in ('FLOAT', 'REAL') else
                           'f_int_real(' + params[0] + ')' if t == 'IFIX' else
                           '((float)f_int_real(' + params[0] + '))' if t == 'AINT' else
                           '((float)f_nint_real(' + params[0] + '))' if t == 'ANINT' else
                           'f_nint_real(' + params[0] + ')')
                    result_type = 'INTEGER' if t in ('IFIX', 'NINT') else 'REAL'
                elif t in self.unit.statement_functions:
                    if t in self.active_functions:
                        raise FortranError(self.line, 'recursive statement function: ' + t)
                    formals, body = self.unit.statement_functions[t]
                    if len(params) != len(formals):
                        raise FortranError(self.line, 'statement function argument count mismatch: ' + t)
                    local = dict(self.substitutions)
                    local.update(zip(formals, params))
                    lhs = '(' + Expr(body, self.unit, self.known, self.line,
                                     local, self.active_functions | {t}).read() + ')'
                    result_type = self.unit.vars[t][0]
                elif t in ('ISIGN', 'SIGN', 'IDIM', 'DIM') and len(params) == 2:
                    expected = 'INTEGER' if t in ('ISIGN', 'IDIM') else 'REAL'
                    if any(self.expr_types[p] != expected for p in params):
                        raise FortranError(self.line, t + ' needs two ' + expected + ' arguments')
                    lhs = 'f_' + t.lower() + '(' + ', '.join(params) + ')'
                    result_type = expected
                elif t in ('MAX0', 'MIN0', 'AMAX1', 'AMIN1', 'AMAX0', 'AMIN0', 'MAX1', 'MIN1') and len(params) >= 2:
                    expected = 'REAL' if t in ('AMAX1', 'AMIN1', 'MAX1', 'MIN1') else 'INTEGER'
                    if any(self.expr_types[p] != expected for p in params):
                        raise FortranError(self.line, t + ' requires at least two ' + expected + ' arguments')
                    chosen = ('f_max0' if t in ('MAX0', 'AMAX0') else
                              'f_min0' if t in ('MIN0', 'AMIN0') else
                              'f_amax1' if t in ('AMAX1', 'MAX1') else 'f_amin1')
                    lhs = params[0]
                    for param in params[1:]:
                        lhs = chosen + '(' + lhs + ', ' + param + ')'
                    if t in ('AMAX0', 'AMIN0'):
                        lhs = '((float)(' + lhs + '))'
                    elif t in ('MAX1', 'MIN1'):
                        lhs = 'f_int_real(' + lhs + ')'
                    result_type = 'REAL' if t in ('AMAX0', 'AMIN0', 'AMAX1', 'AMIN1') else 'INTEGER'
                elif t in ('ATAN2', 'AMOD') and len(params) == 2:
                    if any(self.expr_types[p] != 'REAL' for p in params):
                        raise FortranError(self.line, t + ' intrinsic needs two REAL arguments')
                    lhs = 'f_' + t.lower() + '_real(' + ', '.join(params) + ')'
                    result_type = 'REAL'
                elif t == 'MOD' and len(params) == 2:
                    lhs = '((' + params[0] + ') % (' + params[1] + '))'
                    result_type = 'INTEGER'
                elif t in self.known and self.known[t].kind == 'function':
                    target = self.known[t]
                    caller = self.unit.vars.get(t)
                    if caller and caller[0] != target.type:
                        raise FortranError(self.line, 'external function result type mismatch: ' + t)
                    if len(params) != len(self.known[t].args):
                        raise FortranError(self.line, 'wrong number of function arguments: ' + t)
                    target = self.known[t]
                    refs = [reference_actual(arg, self.unit, target.vars[dummy][0])
                            for arg, dummy in zip(params, target.args)]
                    lhs = 'f_' + t + '(' + ', '.join(refs) + ')'
                    result_type = target.type
                else:
                    raise FortranError(self.line, 'unknown function: ' + t)
            elif t in self.unit.externals or t in self.unit.intrinsics:
                raise FortranError(self.line, 'procedure name cannot be used as scalar: ' + t)
            elif t in self.substitutions:
                lhs = '(' + self.substitutions[t] + ')'
                result_type = self.unit.vars.get(t, ('REAL', None))[0]
            elif t in self.unit.vars and self.unit.vars[t][1] is None:
                if self.unit.vars[t][0].startswith('CHARACTER*'):
                    raise FortranError(self.line, 'CHARACTER must use character assignment/comparison or A FORMAT')
                lhs = '(*F_' + t + ')' if t in self.unit.args else 'F_' + t
                result_type = self.unit.vars[t][0]
            else:
                raise FortranError(self.line, 'undeclared variable: ' + t)
        else:
            raise FortranError(self.line, 'invalid expression token: ' + t)
        self.expr_types[lhs] = result_type
        while True:
            op = self.peek()
            prec = PRECEDENCE.get(op, -1)
            if prec < min_prec:
                break
            self.pop()
            rhs = self.pratt(prec if op == '**' else prec + 1)
            lt, rt = self.expr_types[lhs], self.expr_types[rhs]
            if op == '**':
                if lt == 'INTEGER' and rt == 'INTEGER':
                    lhs = 'f_ipow(' + lhs + ', ' + rhs + ')'
                    result_type = 'INTEGER'
                elif rt == 'INTEGER':
                    lhs = 'f_ripow_real(' + lhs + ', ' + rhs + ')'
                    result_type = 'REAL'
                else:
                    lhs = 'f_rpow_real(' + lhs + ', ' + rhs + ')'
                    result_type = 'REAL'
            else:
                lhs = '((' + lhs + ') ' + BIN.get(op, op) + ' (' + rhs + '))'
                result_type = ('LOGICAL' if op.startswith('.') else
                               'REAL' if lt == 'REAL' or rt == 'REAL' else 'INTEGER')
            self.expr_types[lhs] = result_type
        return lhs


def reference_actual(value, unit, ty):
    """Pass a FORTRAN actual argument by address, materializing rvalues.

    Each expression actual gets its own local temporary.  A routine may change
    dummy arguments only when its actual is an assignable variable or element.
    """
    if re.fullmatch(r'\(\*F_[A-Z][A-Z0-9_]*\)', value):
        return value[2:-1]  # existing dummy: its value is already an address
    if re.fullmatch(r'F_[A-Z][A-Z0-9_]*(?:\[.*\])?', value):
        return '&(' + value + ')'
    key = 'f_argtmp_' + str(len(unit.temps))
    unit.temps.append((key, ty))
    if ty == 'REAL':
        return 'f_ref_real(&' + key + ', ' + value + ')'
    return 'f_ref_int(&' + key + ', ' + value + ')'


RUNTIME = '''#include <c48.h>
/* FORTRAN words are 16-bit on this ZX Spectrum target. */
static int *f_ref_int(int *p, int value) { *p = value; return p; }
static float *f_ref_real(float *p, float value) { *p = value; return p; }
/* F77S REAL -> 16-bit INTEGER INT, truncating toward zero.
   Trap values outside the representable result range instead of wrapping. */
static int f_int_real(float x) {
    if (x >= 32768.0 || x <= -32769.0) exit(2);
    return (int)x;
}
/* F77S real absolute value (numeric generic typing remains partial). */
static float f_abs_real(float x) { if (x < 0.0) return -x; return x; }
static int f_abs_int(int x) {
    if (x == -32768) exit(2);
    if (x < 0) return -x;
    return x;
}
/* Specific integer and real SIGN/DIM: avoid undefined 16-bit overflow. */
static int f_isign(int x, int y) {
    if (x == -32768) {
        if (y < 0) return -32768;
        exit(2);
    }
    if (x < 0) x = -x;
    if (y < 0) return -x;
    return x;
}
static float f_sign(float x, float y) {
    if (x < 0.0) x = -x;
    if (y < 0.0) return -x;
    return x;
}
static int f_idim(int x, int y) {
    if (x <= y) return 0;
    if (y < 0 && x > 32767 + y) exit(2);
    return x - y;
}
static float f_dim(float x, float y) {
    if (x <= y) return 0.0;
    return x - y;
}
static int f_max0(int a,int b) { if(a>b)return a; return b; }
static int f_min0(int a,int b) { if(a<b)return a; return b; }
static float f_amax1(float a,float b) { if(a>b)return a; return b; }
static float f_amin1(float a,float b) { if(a<b)return a; return b; }
static int f_nint_real(float x) {
    if (x < 0.0) return f_int_real(x - 0.5);
    return f_int_real(x + 0.5);
}
static float f_scale_real(float value, int factor) {
    while (factor > 0) { value = value * 10.0; factor--; }
    while (factor < 0) { value = value / 10.0; factor++; }
    return value;
}
/* ANSI subset REAL SQRT, Newton iteration with domain check. */
static float f_sqrt_real(float x) {
    if (x < 0.0) exit(2);
    return sqrt(x);
}
static int f_add_checked(int a, int b) {
    if (b > 0 && a > 32767 - b) exit(2);
    if (b < 0 && a < ((-32767 - b) - 1)) exit(2);
    return a + b;
}
static int f_index(int n, int size) {
    if (n < 1 || n > size) exit(2);
    return n - 1;
}
/* Check an array-element actual covers the complete dummy sequence. */
static int f_seqcheck(int start, int total, int needed) {
    if (start < 0 || needed < 1 || start > total - needed) exit(2);
    return start;
}
/* Dynamic dummy bounds may be smaller than the caller's actual storage. */
static int f_extent(int declared, int available) {
    if (declared < 1 || declared > available) exit(2);
    return declared;
}
static int f_ipow(int base, int e) {
    int n;
    int result;
    result = 1;
    if (e < 0) exit(2);
    for (n = 0; n < e; n++) result = result * base;
    return result;
}
/* F77S unnamed direct-access scratch units; one file per unit 1..9.
   A direct unformatted INTEGER record is stored as a sign-extended
   four-byte little-endian value, compatible with a 32-bit host reference.
   C48 INTEGER remains 16-bit and record indices must fit 16-bit seek. */
static int f_dh[10];
static int f_dl[10];
static void f_dopen(int unit, int recl) {
    char path[9];
    int fd;
    if (unit < 1 || unit > 9 || (recl != 4 && recl != 8)) exit(2);
    strcpy(path, "/tmp/fu0");
    path[7] = '0' + unit;
    fd = creat(path, 438);
    if (fd < 0) exit(2);
    if (close(fd) < 0) exit(2);
    fd = open(path, 2);
    if (fd < 0) exit(2);
    f_dh[unit] = fd;
    f_dl[unit] = recl;
}
static void f_dseek(int unit, int rec) {
    int offset;
    if (unit < 1 || unit > 9 || (f_dl[unit] != 4 && f_dl[unit] != 8)) exit(2);
    if (rec < 1 || rec > (32768 / f_dl[unit])) exit(2);
    offset = (rec - 1) * f_dl[unit];
    if (seek(f_dh[unit], offset) < 0) exit(2);
}
static void f_dwritei(int unit, int rec, int value) {
    int high;
    if (f_dl[unit] != 4) exit(2);
    f_dseek(unit, rec);
    high = 0;
    if (value < 0) high = -1;
    if (write(f_dh[unit], &value, 2) != 2) exit(2);
    if (write(f_dh[unit], &high, 2) != 2) exit(2);
}
static int f_dreadi(int unit, int rec) {
    int value;
    int high;
    if (f_dl[unit] != 4) exit(2);
    f_dseek(unit, rec);
    if (read(f_dh[unit], &value, 2) != 2) exit(2);
    if (read(f_dh[unit], &high, 2) != 2) exit(2);
    if (value < 0) { if (high != -1) exit(2); }
    else if (high != 0) exit(2);
    return value;
}
/* Two INTEGER values in one direct unformatted RECL=8 scratch record. */
static void f_dputi(int unit, int value) {
    int high;
    high = 0;
    if (value < 0) high = -1;
    if (write(f_dh[unit], &value, 2) != 2) exit(2);
    if (write(f_dh[unit], &high, 2) != 2) exit(2);
}
static int f_dgeti(int unit) {
    int value;
    int high;
    if (read(f_dh[unit], &value, 2) != 2) exit(2);
    if (read(f_dh[unit], &high, 2) != 2) exit(2);
    if (value < 0) { if (high != -1) exit(2); }
    else if (high != 0) exit(2);
    return value;
}
static void f_dwrite2(int unit, int rec, int a, int b) {
    if (f_dl[unit] != 8) exit(2);
    f_dseek(unit, rec);
    f_dputi(unit, a);
    f_dputi(unit, b);
}
static void f_dread2(int unit, int rec, int *a, int *b) {
    if (f_dl[unit] != 8) exit(2);
    f_dseek(unit, rec);
    *a = f_dgeti(unit);
    *b = f_dgeti(unit);
}
/* Unnamed sequential unformatted INTEGER scratch I/O, one data item.
   Records have 32-bit gfortran-compatible length markers and 32-bit sign-
   extended integer data. ZX-UX seek/tell are 16-bit bounded. */
static int f_sh[10];
static int f_sused[10];
static void f_sopen(int unit, int reading) {
    char path[9];
    int fd;
    if (unit < 1 || unit > 9) exit(2);
    if (f_sused[unit]) return;
    strcpy(path, "/tmp/fs0");
    path[7] = '0' + unit;
    if (!reading) {
        fd = creat(path, 438);
        if (fd < 0) exit(2);
        if (close(fd) < 0) exit(2);
    }
    fd = open(path, 2);
    if (fd < 0) exit(2);
    f_sh[unit] = fd;
    f_sused[unit] = 1;
}
static void f_swrite(int unit, int value) {
    int length;
    int high;
    f_sopen(unit, 0);
    length = 4;
    high = 0;
    if (value < 0) high = -1;
    if (tell(f_sh[unit]) > 32755) exit(2);
    if (write(f_sh[unit], &length, 2) != 2) exit(2);
    length = 0;
    if (write(f_sh[unit], &length, 2) != 2) exit(2);
    if (write(f_sh[unit], &value, 2) != 2) exit(2);
    if (write(f_sh[unit], &high, 2) != 2) exit(2);
    length = 4;
    if (write(f_sh[unit], &length, 2) != 2) exit(2);
    length = 0;
    if (write(f_sh[unit], &length, 2) != 2) exit(2);
}
static int f_sreadstat(int unit, int *dest) {
    int length, upper, value, high, tail, upper2, got;
    f_sopen(unit, 1);
    got = read(f_sh[unit], &length, 2);
    if (got == 0) return 0;
    if (got != 2) exit(2);
    if (read(f_sh[unit], &upper, 2) != 2) exit(2);
    if (length == 0 && upper == 0) return 0;
    if (length != 4 || upper != 0) exit(2);
    if (read(f_sh[unit], &value, 2) != 2) exit(2);
    if (read(f_sh[unit], &high, 2) != 2) exit(2);
    if (read(f_sh[unit], &tail, 2) != 2) exit(2);
    if (read(f_sh[unit], &upper2, 2) != 2) exit(2);
    if (tail != 4 || upper2 != 0) exit(2);
    if (value < 0) { if (high != -1) exit(2); }
    else if (high != 0) exit(2);
    *dest = value;
    return 1;
}
static int f_sread(int unit) {
    int value;
    if (!f_sreadstat(unit, &value)) exit(2);
    return value;
}
static void f_srewind(int unit) {
    f_sopen(unit, 1);
    if (seek(f_sh[unit], 0) < 0) exit(2);
}
static void f_send(int unit) {
    int zero;
    f_sopen(unit, 0);
    if (tell(f_sh[unit]) > 32763) exit(2);
    zero = 0;
    if (write(f_sh[unit], &zero, 2) != 2) exit(2);
    if (write(f_sh[unit], &zero, 2) != 2) exit(2);
}
static void f_sback(int unit) {
    int pos;
    int tail, upper;
    f_sopen(unit, 1);
    pos = tell(f_sh[unit]);
    if (pos < 0) exit(2);
    if (pos == 0) return;
    if (pos < 12) exit(2);
    if (seek(f_sh[unit], pos - 4) < 0) exit(2);
    if (read(f_sh[unit], &tail, 2) != 2) exit(2);
    if (read(f_sh[unit], &upper, 2) != 2) exit(2);
    if (tail != 4 || upper != 0) exit(2);
    if (seek(f_sh[unit], pos - 12) < 0) exit(2);
}
static void f_outstr(char *s) {
    while (*s) { putchar(*s); s++; }
}
static void f_outint(int n) {
    unsigned int u;
    unsigned int digit;
    unsigned int div;
    int begun;
    if (n < 0) {
        putchar('-');
        u = (unsigned int)0 - (unsigned int)n;
    } else u = (unsigned int)n;
    div = 10000;
    begun = 0;
    while (div > 1) {
        digit = u / div;
        if (digit || begun) { putchar('0' + digit); begun = 1; }
        u = u % div;
        div = div / 10;
    }
    putchar('0' + u);
}
/* Restricted standard F77S FORMAT Lw for LOGICAL values. */
static void f_outlogw(int value, int width) {
    int i;
    for (i = 1; i < width; i++) putchar(' ');
    if (value) putchar('T'); else putchar('F');
}
/* FORMAT Iw: leading blanks, asterisks if the value overflows. */
static void f_outintw(int value, int width) {
    int chars;
    int n;
    int k;
    n = value;
    if (n < 0) chars = 2;
    else chars = 1;
    while (n <= -10 || n >= 10) { n = n / 10; chars++; }
    if (chars > width) {
        for (k = 0; k < width; k++) putchar('*');
    } else {
        for (k = chars; k < width; k++) putchar(' ');
        f_outint(value);
    }
}
/* Restricted ANSI F77S Fw.d decimal output for 16-bit-scale REAL values.
   Values outside this target's represented decimal range show stars. */
static void f_outrealw(float value, int width, int places) {
    int i;
    int negative;
    int integer_part;
    int fraction;
    int scale;
    int divisor;
    int digs[7];
    int carry;
    float fpart;
    int digits;
    int chars;
    float x;
    x = value;
    negative = x < 0.0;
    if (negative) x = -x;
    if (x > 32766.0) {
        for (i = 0; i < width; i++) putchar('*');
        return;
    }
    integer_part = (int)x;
    scale = 1;
    fraction = 0;
    if (places <= 4) {
        for (i = 0; i < places; i++) scale = scale * 10;
        fraction = (int)((x - (float)integer_part) * (float)scale + 0.5);
        if (fraction >= scale) { integer_part++; fraction = 0; }
    } else {
        fpart = x - (float)integer_part;
        for (i = 0; i <= places; i++) {
            fpart = fpart * 10.0;
            digs[i] = (int)fpart;
            if (digs[i] < 0) digs[i] = 0;
            if (digs[i] > 9) digs[i] = 9;
            fpart = fpart - (float)digs[i];
        }
        carry = digs[places] >= 5;
        for (i = places - 1; i >= 0; i--) {
            if (carry) {
                digs[i]++;
                if (digs[i] == 10) digs[i] = 0;
                else carry = 0;
            }
        }
        if (carry) { integer_part++; }
    }
    if (integer_part > 32767) {
        for (i = 0; i < width; i++) putchar('*');
        return;
    }
    digits = 1;
    divisor = integer_part;
    while (divisor >= 10) { digits++; divisor = divisor / 10; }
    chars = digits + negative + 1 + places;
    if (chars > width) {
        for (i = 0; i < width; i++) putchar('*');
        return;
    }
    for (i = chars; i < width; i++) putchar(' ');
    if (negative) putchar('-');
    f_outint(integer_part);
    putchar('.');
    if (places > 4) {
        for (i = 0; i < places; i++) putchar('0' + digs[i]);
    } else {
        divisor = scale / 10;
        while (divisor > 0) {
            putchar('0' + fraction / divisor);
            fraction = fraction % divisor;
            divisor = divisor / 10;
        }
    }
}
/* Restricted ANSI F77S Ew.d output (two-digit exponent, 1..6 digits).
   Compute digits separately to avoid 16-bit integer overflow on Z80. */
static void f_outexpw(float value, int width, int places, int exponent_width) {
    int negative;
    int exponent;
    int digs[7];
    int i;
    int digit;
    int carry;
    int chars;
    float v;
    negative = value < 0.0;
    v = value;
    if (negative) v = -v;
    exponent = 0;
    if (v != 0.0) {
        while (v >= 1.0 && exponent < 100) { v = v / 10.0; exponent++; }
        while (v < 0.1 && exponent > -100) { v = v * 10.0; exponent--; }
    }
    if (exponent >= 100 || exponent <= -100) {
        for (i = 0; i < width; i++) putchar('*');
        return;
    }
    for (i = 0; i <= places; i++) {
        v = v * 10.0;
        digit = (int)v;
        if (digit < 0) digit = 0;
        if (digit > 9) digit = 9;
        digs[i] = digit;
        v = v - (float)digit;
    }
    carry = digs[places] >= 5;
    for (i = places - 1; i >= 0; i--) {
        if (carry) {
            digs[i]++;
            if (digs[i] == 10) digs[i] = 0;
            else carry = 0;
        }
    }
    if (carry) {
        digs[0] = 1;
        for (i = 1; i < places; i++) digs[i] = 0;
        exponent++;
        if (exponent >= 100) {
            for (i = 0; i < width; i++) putchar('*');
            return;
        }
    }
    chars = places + 4 + exponent_width + negative;
    if (exponent_width == 1 && (exponent >= 10 || exponent <= -10)) {
        for (i = 0; i < width; i++) putchar('*');
        return;
    }
    if (chars > width) {
        for (i = 0; i < width; i++) putchar('*');
        return;
    }
    for (i = chars; i < width; i++) putchar(' ');
    if (negative) putchar('-');
    putchar('0');
    putchar('.');
    for (i = 0; i < places; i++) putchar('0' + digs[i]);
    putchar('E');
    if (exponent < 0) { putchar('-'); exponent = -exponent; }
    else putchar('+');
    if (exponent_width >= 3) putchar('0');
    if (exponent_width >= 4) putchar('0');
    if (exponent_width >= 2) putchar('0' + exponent / 10);
    putchar('0' + exponent % 10);
}
static void f_outexp(float value, int width, int places) {
    f_outexpw(value, width, places, 2);
}
/* ANSI F77S formatted INTEGER input (limited Iw/X/slash subset).
   Fields are blank-padded to the end of each input record. */
static int f_fmt_eor;
static int f_fmt_bzero;
static int f_fmt_get(void) {
    int ch;
    if (f_fmt_eor) return ' ';
    ch = getchar();
    if (ch == 10 || ch == 13 || ch < 0) {
        f_fmt_eor = 1;
        return ' ';
    }
    return ch;
}
static void f_fmt_skip(int width) {
    int i;
    for (i = 0; i < width; i++) f_fmt_get();
}
static int f_fmt_int(int width) {
    int i;
    int ch;
    int sign;
    int digits;
    int signed_seen;
    int value;
    int digit;
    sign = 1;
    digits = 0;
    signed_seen = 0;
    value = 0;
    for (i = 0; i < width; i++) {
        ch = f_fmt_get();
        if (ch == ' ') {
            if (!f_fmt_bzero) continue;
            ch = '0';
        }
        if ((ch == '-' || ch == '+') && !digits && !signed_seen) {
            if (ch == '-') sign = -1;
            else sign = 1;
            signed_seen = 1;
            continue;
        }
        if (ch < '0' || ch > '9') exit(2);
        digit = ch - '0';
        if (value > 3276 || (value == 3276 && ((sign < 0 && digit > 8) || (sign >= 0 && digit > 7)))) exit(2);
        value = value * 10 + digit;
        digits = 1;
    }
    return value * sign;
}
/* Restricted F77S Lw READ: T/F, optional dots, blank padding. */
static int f_fmt_logical(int width) {
    int i;
    int ch;
    int found;
    int result;
    found = 0;
    result = 0;
    for (i = 0; i < width; i++) {
        ch = f_fmt_get();
        if (ch == ' ' || ch == '.') continue;
        if (ch == 't') ch = 'T';
        if (ch == 'f') ch = 'F';
        if (ch != 'T' && ch != 'F') exit(2);
        if (found) exit(2);
        found = 1;
        result = ch == 'T';
    }
    if (!found) exit(2);
    return result;
}
/* Restricted Fw.d READ: decimal fields, optional sign/point; no exponent. */
static float f_fmt_real(int width, int places) {
    int i;
    int ch;
    int sign;
    int after;
    int point;
    int started;
    float v;
    v = 0.0;
    sign = 1;
    after = 0;
    point = 0;
    started = 0;
    for (i = 0; i < width; i++) {
        ch = f_fmt_get();
        if (ch == ' ') {
            if (!f_fmt_bzero) continue;
            ch = '0';
        }
        if ((ch == '-' || ch == '+') && !started) {
            if (ch == '-') sign = -1;
            started = 1;
            continue;
        }
        if (ch == '.' && !point) { point = 1; started = 1; continue; }
        if (ch < '0' || ch > '9') exit(2);
        v = v * 10.0 + (float)(ch - '0');
        started = 1;
        if (point) after++;
    }
    if (!point) after = places;
    for (i = 0; i < after; i++) v = v / 10.0;
    if (sign < 0) v = -v;
    return v;
}
/* F77S E input: explicit or implicit decimal point, signed E/D exponent.
   Current source conversion uses BN (blank-ignore) behavior. */
static float f_fmt_ereal(int width, int places) {
    float value;
    int i, ch, sign, exponent, exp_sign, after, point;
    int digits, exp_digits, in_exp, exp_sign_seen;
    value = 0.0;
    sign = 1;
    exponent = 0;
    exp_sign = 1;
    after = 0;
    point = 0;
    digits = 0;
    exp_digits = 0;
    in_exp = 0;
    exp_sign_seen = 0;
    for (i = 0; i < width; i++) {
        ch = f_fmt_get();
        if (ch == ' ') {
            if (!f_fmt_bzero) continue;
            ch = '0';
        }
        if (!in_exp && (ch == '+' || ch == '-') && !digits && !point) {
            if (ch == '-') sign = -1;
            continue;
        }
        if (!in_exp && ch == '.' && !point) { point = 1; continue; }
        if ((ch == 'E' || ch == 'e' || ch == 'D' || ch == 'd') && !in_exp && digits) {
            in_exp = 1;
            continue;
        }
        if (in_exp && (ch == '+' || ch == '-') && !exp_digits && !exp_sign_seen) {
            if (ch == '-') exp_sign = -1;
            exp_sign_seen = 1;
            continue;
        }
        if (ch < '0' || ch > '9') exit(2);
        if (in_exp) {
            if (exponent > 20) exit(2);
            exponent = exponent * 10 + ch - '0';
            exp_digits++;
        } else {
            value = value * 10.0 + (float)(ch - '0');
            digits++;
            if (point) after++;
        }
    }
    if (!digits || (in_exp && !exp_digits)) exit(2);
    if (!point) after = places;
    exponent = exponent * exp_sign - after;
    if (exponent > 20 || exponent < -20) exit(2);
    for (i = 0; i < exponent; i++) value = value * 10.0;
    for (i = exponent; i < 0; i++) value = value / 10.0;
    if (sign < 0) value = -value;
    return value;
}
static void f_fmt_end(void) {
    int ch;
    if (!f_fmt_eor) {
        ch = getchar();
        while (ch >= 0 && ch != 10 && ch != 13) ch = getchar();
    }
    f_fmt_eor = 0;
}
/* F77S CHARACTER is fixed length, padded with spaces (not C zeroes). */
static void f_char_copy(char *dst, int length, char *src) {
    int i;
    for (i = 0; i < length; i++) {
        if (*src) { dst[i] = *src; src++; }
        else dst[i] = ' ';
    }
    dst[length] = 0;
}
static int f_char_cmp(char *a, int na, char *b, int nb) {
    int i;
    int n;
    int ca;
    int cb;
    n = na;
    if (nb > n) n = nb;
    for (i = 0; i < n; i++) {
        if (i < na) ca = a[i]; else ca = ' ';
        if (i < nb) cb = b[i]; else cb = ' ';
        if (ca < cb) return -1;
        if (ca > cb) return 1;
    }
    return 0;
}
static void f_outcharw(char *src, int length, int width) {
    int i;
    for (i = length; i < width; i++) putchar(' ');
    for (i = 0; i < width && i < length; i++) putchar(src[i]);
}
static void f_fmt_inchar(char *dst, int length, int width) {
    int i;
    int ch;
    for (i = 0; i < length; i++) dst[i] = ' ';
    for (i = 0; i < width; i++) {
        ch = f_fmt_get();
        if (width <= length) dst[i] = ch;
        else if (i >= width - length) dst[i - (width - length)] = ch;
    }
    dst[length] = 0;
}
static int f_inint(void) {
    int ch;
    int sign;
    int v;
    v = 0; sign = 1;
    ch = getchar();
    while (ch == ' ' || ch == 10 || ch == 13) ch = getchar();
    if (ch == '-') { sign = -1; ch = getchar(); }
    while (ch >= '0' && ch <= '9') {
        v = v * 10 + ch - '0';
        ch = getchar();
    }
    return v * sign;
}
'''


def character_item(token, unit, units, line):
    """Resolve a scalar/element to a fixed-length NUL-terminated storage slot."""
    m = re.fullmatch(r'(' + NAME + r')(?:\s*\(([^()]*)\))?', token.strip())
    if not m:
        return None
    name, indices = m.groups()
    info = unit.vars.get(name)
    if not info or not info[0].startswith('CHARACTER*'):
        return None
    width = int(info[0].split('*')[1])
    if info[1] is None:
        if indices is not None:
            raise FortranError(line, 'CHARACTER subscript on scalar: ' + name)
        return ('F_' + name, width)
    if indices is None:
        raise FortranError(line, 'CHARACTER array requires element subscripts: ' + name)
    params = [expression(t, unit, units, line) for t in split_items(indices)]
    index = array_subscript(params, name, unit, line)
    return ('(F_' + name + ' + (' + index + ') * ' + str(width + 1) + ')', width)


def expression(src, unit, units, line):
    # F77S CHARACTER operands are blank-padded to equal length for comparison.
    # Restrict lowering to scalar CHARACTER names and string literals.
    m = re.fullmatch(r'\s*(.*?)\s*(\.(?:EQ|NE|LT|LE|GT|GE)\.)\s*(.*?)\s*', src)
    if m:
        def char_operand(token):
            token = token.strip()
            if re.fullmatch(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"", token):
                q = token[0]
                return c_string(token), len(token[1:-1].replace(q * 2, q))
            return character_item(token, unit, units, line)
        lhs, rhs = char_operand(m.group(1)), char_operand(m.group(3))
        if lhs or rhs:
            if not lhs or not rhs:
                raise FortranError(line, 'CHARACTER comparison requires CHARACTER operands')
            operators = {'.EQ.': '==', '.NE.': '!=', '.LT.': '<',
                         '.LE.': '<=', '.GT.': '>', '.GE.': '>='}
            return '(f_char_cmp(' + lhs[0] + ', ' + str(lhs[1]) + ', ' + rhs[0] + ', ' + str(rhs[1]) + ') ' + operators[m.group(2)] + ' 0)'
    return Expr(src, unit, units, line).read()


def c_string(s):
    assert s[0] in "'\"" and s[-1] == s[0]
    chars = s[1:-1].replace(s[0] * 2, s[0])
    return '"' + ''.join(('\\\\' if c == '\\' else '\\"' if c == '"' else
                          '\\n' if c == '\n' else '\\x%02x' % ord(c) if ord(c) < 32
                          else c) for c in chars) + '"'


def subset_format(source, line):
    """Parse the implemented F77S Iw/X/slash/literal FORMAT operations.

    Nested parenthesized groups and repeat counts are expanded at compile
    time.  Reject the not-yet-implemented descriptors instead of ignoring
    them; bound expansion for a 48K microcomputer target.
    """
    operations = []

    def append(op, count=1):
        if count < 1 or count > 255 or len(operations) + count > 255:
            raise FortranError(line, 'FORMAT repetition exceeds 255 operations')
        operations.extend([op] * count)

    def descend(items, depth):
        if depth > 3:
            raise FortranError(line, 'F77S FORMAT permits at most three parenthesis levels')
        for token in split_items(items):
            token = token.strip()
            group = re.fullmatch(r'([1-9][0-9]*)?\((.*)\)', token)
            if group:
                repeat = int(group.group(1) or 1)
                if repeat > 255:
                    raise FortranError(line, 'FORMAT group repetition exceeds 255')
                before = len(operations)
                descend(group.group(2), depth + 1)
                pattern = operations[before:]
                if len(operations) + (repeat - 1) * len(pattern) > 255:
                    raise FortranError(line, 'FORMAT expands beyond 255 operations')
                operations.extend(pattern * (repeat - 1))
                continue
            scale = re.fullmatch(r'([+-]?[0-9]+)P', token)
            if scale:
                multiplier = int(scale.group(1))
                if not -4 <= multiplier <= 4:
                    raise FortranError(line, 'P scale factor exceeds target supported range -4..4')
                append(('scale', multiplier))
                continue
            if token in ('BN', 'BZ'):
                append(('blank', 0 if token == 'BN' else 1))
                continue
            if re.fullmatch(r"'(?:[^']|'')*'", token):
                append(('literal', token))
                continue
            integer = re.fullmatch(r'([1-9][0-9]*)?I([1-9][0-9]*)', token)
            if integer:
                repeat, width = int(integer.group(1) or 1), int(integer.group(2))
                if width > 255:
                    raise FortranError(line, 'I field width exceeds 255')
                append(('integer', width), repeat)
                continue
            real = re.fullmatch(r'([1-9][0-9]*)?F([1-9][0-9]*)\.([0-9]+)', token)
            if real:
                repeat = int(real.group(1) or 1)
                width, places = int(real.group(2)), int(real.group(3))
                if width > 255 or places > 6 or width < places + 2:
                    raise FortranError(line, 'F field size/decimal places exceed supported limits')
                append(('real', (width, places)), repeat)
                continue
            exponent_digits = re.fullmatch(r'([1-9][0-9]*)?E([1-9][0-9]*)\.([0-9]+)E([1-9][0-9]*)', token)
            if exponent_digits:
                repeat = int(exponent_digits.group(1) or 1)
                width, places, expwidth = map(int, exponent_digits.groups()[1:])
                if width > 255 or not (1 <= places <= 6) or not (1 <= expwidth <= 4) or width < places + 4 + expwidth:
                    raise FortranError(line, 'E field width/precision/exponent exceeds supported limits')
                append(('realexpdigits', (width, places, expwidth)), repeat)
                continue
            exponential = re.fullmatch(r'([1-9][0-9]*)?E([1-9][0-9]*)\.([0-9]+)', token)
            if exponential:
                repeat = int(exponential.group(1) or 1)
                width, places = int(exponential.group(2)), int(exponential.group(3))
                if width > 255 or not (1 <= places <= 6) or width < places + 6:
                    raise FortranError(line, 'E field width/precision exceeds supported limits')
                append(('realexp', (width, places)), repeat)
                continue
            logical = re.fullmatch(r'([1-9][0-9]*)?L([1-9][0-9]*)', token)
            if logical:
                repeat, width = int(logical.group(1) or 1), int(logical.group(2))
                if width > 255:
                    raise FortranError(line, 'L field width exceeds 255')
                append(('logical', width), repeat)
                continue
            character = re.fullmatch(r'([1-9][0-9]*)?A([1-9][0-9]*)?', token)
            if character:
                repeat = int(character.group(1) or 1)
                width = int(character.group(2)) if character.group(2) else None
                if width is not None and width > 255:
                    raise FortranError(line, 'A field width exceeds 255')
                append(('character', width), repeat)
                continue
            spacing = re.fullmatch(r'([1-9][0-9]*)?X', token)
            if spacing:
                append(('space', 1), int(spacing.group(1) or 1))
                continue
            slash = re.fullmatch(r'([1-9][0-9]*)?/', token)
            if slash:
                append(('newline', None), int(slash.group(1) or 1))
                continue
            raise FortranError(line, 'unsupported FORMAT descriptor: ' + token)

    descend(source, 1)
    return operations


# Optional REAL specific-intrinsic helpers. Only referenced helpers are
# included in generated C48, so integer-only programs do not pay for them.
REAL_MATH_RUNTIME = {
    'SIN': """
static float f_sin_real(float x) { return sin(x); }
""",
    'COS': """
static float f_cos_real(float x) { return cos(x); }
""",
    'EXP': """
static float f_exp_real(float x) {
    if (x > 80.0) exit(2);
    if (x < -80.0) return 0.0;
    return exp(x);
}
""",
    'LOG': """
static float f_log_real(float x) { if (x <= 0.0) exit(2); return log(x); }
""",
    'TAN': """
static float f_tan_real(float x) { return tan(x); }
""",
    'SINH': """
static float f_sinh_real(float x) {
    float positive;
    float negative;
    if (x > 10.0 || x < -10.0) exit(2);
    positive = f_exp_real(x);
    negative = f_exp_real(-x);
    return (positive - negative) / 2.0;
}
""",
    'COSH': """
static float f_cosh_real(float x) {
    float positive;
    float negative;
    if (x > 10.0 || x < -10.0) exit(2);
    positive = f_exp_real(x);
    negative = f_exp_real(-x);
    return (positive + negative) / 2.0;
}
""",
    'TANH': """
static float f_tanh_real(float x) {
    float e;
    if (x > 8.0) return 1.0;
    if (x < -8.0) return -1.0;
    e = f_exp_real(x);
    return (e * e - 1.0) / (e * e + 1.0);
}
""",
    'ASIN': """
static float f_asin_real(float x) { if (x < -1.0 || x > 1.0) exit(2); return asin(x); }
""",
    'ACOS': """
static float f_acos_real(float x) { if (x < -1.0 || x > 1.0) exit(2); return acos(x); }
""",
    'ATAN': """
static float f_atan_real(float x) { return atan(x); }
""",
    'ALOG10': """
static float f_alog10_real(float x) { if (x <= 0.0) exit(2); return log(x) * 0.4342944819; }
""",
    'ATAN2': """
static float f_atan2_real(float y, float x) {
    if (x == 0.0) {
        if (y > 0.0) return 1.57079633;
        if (y < 0.0) return -1.57079633;
        exit(2);
    }
    if (x > 0.0) return atan(y / x);
    if (y >= 0.0) return atan(y / x) + 3.14159265;
    return atan(y / x) - 3.14159265;
}
""",
    'AMOD': """
static float f_amod_real(float x, float y) {
    float quotient;
    if (y == 0.0) exit(2);
    quotient = x / y;
    if (quotient >= 32768.0 || quotient <= -32769.0) exit(2);
    return x - (float)((int)quotient) * y;
}
""",
    'RIPOW': """
static float f_ripow_real(float base, int power) {
    float result;
    int inverse;
    inverse = 0;
    if (power == -32768) exit(2);
    if (power < 0) { if (base == 0.0) exit(2); power = -power; inverse = 1; }
    result = 1.0;
    while (power > 0) {
        if (power % 2 != 0) result = result * base;
        power = power / 2;
        if (power > 0) base = base * base;
    }
    if (inverse) return 1.0 / result;
    return result;
}
""",
    'RPOW': """
static float f_rpow_real(float base, float power) {
    if (base == 0.0 && power > 0.0) return 0.0;
    if (base <= 0.0) exit(2);
    return f_exp_real(power * f_log_real(base));
}
"""
}


def sparse_runtime(runtime, used_in):
    """Keep only C48 runtime functions reachable from one linked SSO unit.

    The legacy monolithic translator emitted every runtime helper into every
    SSO. Separate compilation had an O(units * runtime) footprint. Scan the
    static function bodies and recursively retain only reachable helpers.
    Do not change the ABI or remove range checks from the retained helpers.
    """
    head = re.compile(r'^static\s+(?:void|int|float|char)\s*\*?\s*(f_[a-z0-9_]+)\s*\(', re.M)
    functions = {}
    for match in head.finditer(runtime):
        opening = runtime.find('{', match.end())
        if opening == -1:
            raise ValueError('malformed C48 runtime helper definition')
        depth = 0
        closing = -1
        for position in range(opening, len(runtime)):
            if runtime[position] == '{':
                depth += 1
            elif runtime[position] == '}':
                depth -= 1
                if depth == 0:
                    closing = position + 1
                    break
        if closing == -1:
            raise ValueError('unbalanced C48 runtime helper definition')
        functions[match.group(1)] = runtime[match.start():closing]
    if len(functions) < 25:
        raise ValueError('runtime helper scanning lost functions')
    required = {name for name in functions
                if re.search(r'\b' + name + r'\s*\(', used_in)}
    pending = list(required)
    while pending:
        source = functions[pending.pop()]
        for name in functions:
            if name not in required and re.search(r'\b' + name + r'\s*\(', source):
                required.add(name)
                pending.append(name)
    functions_src = '\n'.join(body for name, body in functions.items() if name in required)
    globals_src = ''
    for name in ('f_fmt_eor', 'f_fmt_bzero'):
        if re.search(r'\b' + name + r'\b', used_in + functions_src):
            globals_src += 'static int ' + name + ';\n'
    if re.search(r'\bf_d(?:open|seek|writei|readi|write2|read2)\s*\(', used_in + functions_src):
        globals_src += 'static int f_dh[10];\nstatic int f_dl[10];\n'
    if re.search(r'\bf_s(?:open|write|read|readstat|rewind|back|end)\s*\(', used_in + functions_src):
        globals_src += 'static int f_sh[10];\nstatic int f_sused[10];\n'
    return '#include <c48.h>\n' + globals_src + functions_src + '\n'


def convert(units, emit_units=None):
    """Build explicit control-flow blocks, then lower them to portable C48.

    The PC dispatcher avoids non-C48 goto/switch and also handles branches
    into and out of nested FORTRAN constructs, including numbered DO loops.
    """
    known = {u.name: u for u in units}
    from .common import layout, bind
    from .equivalence import layout as equivalence_layout
    common_decls, common_uses = layout(units)
    if emit_units is not None:
        # Every independently translated unit sees the same COMMON ABI.
        # The main translation owns one externally visible definition; the
        # remaining objects import it through the target linker.
        is_owner = any(u.kind == 'program' and u.name in emit_units for u in units)
        common_decls = [(d[7:] if is_owner else 'extern ' + d[7:])
                        if d.startswith('static ') else d for d in common_decls]
    chunks = [RUNTIME] + common_decls
    ctype = lambda ty: 'float' if ty == 'REAL' else 'int'
    def signature(u):
        args = [('char' if u.vars[a][0].startswith('CHARACTER*') else ctype(u.vars[a][0])) + ' *F_' + a for a in u.args]
        args.extend('int F__LEN_' + a for a in u.args if dynamic_extent(u.vars[a][1]))
        return ', '.join(args) or 'void'
    for u in units:
        if u.kind != 'program':
            ty = 'void' if u.kind == 'subroutine' else ctype(u.type)
            sig = signature(u)
            chunks.append(ty + ' f_' + u.name + '(' + sig + ');')
    for unit_ordinal, u in enumerate(units):
        if emit_units is not None and u.name not in emit_units:
            continue
        is_main = u.kind == 'program'
        ret = 'int' if is_main else 'void' if u.kind == 'subroutine' else ctype(u.type)
        sig = 'void' if is_main else signature(u)
        name = 'main' if is_main else 'f_' + u.name
        u.temps = []
        output = [ret + ' ' + name + '(' + sig + ') {']
        eq_decls, eq_uses = equivalence_layout(u, common_uses.get(u.name, {}))
        aliases = {**common_uses.get(u.name, {}), **eq_uses}
        from .data_init import initializers
        data_entries = initializers(u)
        data_guard = None
        if data_entries and not is_main:
            # A DATA-initialized EQUIVALENCE storage sequence must survive
            # repeated calls just like an ordinary subprogram DATA object.
            # Use a unit-specific external identifier for each static group.
            data_names_for_eq = {re.match(r'F_([A-Z0-9_]+)', target).group(1)
                                 for target, _ in data_entries}
            if any('F_' + name in eq_uses for name in data_names_for_eq):
                renames = {}
                for n, declaration in enumerate(eq_decls):
                    original = 'f_eq_' + str(n)
                    replacement = 'f_e' + str(unit_ordinal) + '_' + str(n)
                    renames[original] = replacement
                    chunks.append('static ' + declaration.replace(original, replacement))
                eq_decls = []
                for alias, expr_text in eq_uses.items():
                    for original, replacement in renames.items():
                        expr_text = re.sub(r'\b' + original + r'\b', replacement, expr_text)
                    aliases[alias] = expr_text
            # A DATA object must outlive the subprogram's stack frame.
            # C48 identifiers are limited to 15 characters.
            from .arrays import size as total_extent
            data_names = set()
            for target, _ in data_entries:
                m = re.fullmatch(r'F_([A-Z0-9_]+)(?:\[\d+\])?', target)
                if not m:
                    raise FortranError(u.line, 'internal DATA storage target')
                data_names.add(m.group(1))
            for var in sorted(data_names):
                if 'F_' + var in aliases:
                    if 'F_' + var in common_uses.get(u.name, {}):
                        raise FortranError(u.line, 'DATA cannot initialize COMMON storage: ' + var)
                    if 'F_' + var in eq_uses:
                        continue  # storage allocated statically as entire EQUIVALENCE group
                    raise FortranError(u.line, 'DATA with unsupported storage association: ' + var)
                typ, extent = u.vars[var]
                if typ not in ('INTEGER', 'REAL', 'LOGICAL') and not typ.startswith('CHARACTER*'):
                    raise FortranError(u.line, 'unsupported subprogram DATA type: ' + typ)
                global_name = 'f_sd' + str(unit_ordinal) + '_' + var
                if len(global_name) > 15:
                    raise FortranError(u.line, 'DATA storage name exceeds C48 limit')
                if typ.startswith('CHARACTER*'):
                    count = total_extent(extent) if extent else 1
                    chunks.append('static char ' + global_name + '[' +
                                  str(count * (int(typ.split('*')[1]) + 1)) + '];')
                else:
                    chunks.append('static ' + ctype(typ) + ' ' + global_name +
                                  ('[' + str(total_extent(extent)) + ']' if extent else '') + ';')
                aliases['F_' + var] = global_name
            data_guard = 'f_sdi' + str(unit_ordinal)
            chunks.append('static int ' + data_guard + ';')
        output.extend('    ' + declaration for declaration in eq_decls)
        def decl(text):
            output.append('    ' + text)
        for var, (ty, n) in u.vars.items():
            if var not in u.args and var not in u.statement_functions and var not in u.externals and var not in u.intrinsics and ('F_' + var) not in aliases:
                from .arrays import size as total_extent
                if ty.startswith('CHARACTER*'):
                    count = total_extent(n) if n is not None else 1
                    decl('char F_' + var + '[' + str(count * (int(ty.split('*')[1]) + 1)) + '];')
                else:
                    decl(ctype(ty) + ' F_' + var + (('[' + str(total_extent(n)) + ']') if n else '') + ';')
        extra_decls = []
        local_decl_index = len(output)
        decl('int f_pc;')
        for arg in u.args:
            dims = u.vars[arg][1]
            if not dynamic_extent(dims) or not any(isinstance(b, str) and b != '*' and b not in u.args for b in dims):
                continue
            cap = 'F__LEN_' + arg
            prefix = '1'
            for bound in dims:
                if bound == '*':
                    break
                value = ('(*F_' + bound + ')' if isinstance(bound, str) and bound in u.args
                         else 'F_' + bound if isinstance(bound, str) else str(bound))
                checked = 'f_extent(' + value + ', (' + cap + ' / (' + prefix + ')))'
                prefix = '(' + prefix + ' * ' + checked + ')'
            decl('f_seqcheck(0, ' + cap + ', ' + prefix + ');')
        if u.kind == 'function':
            decl('F_' + u.name + ' = 0;')
        def data_init_statement(target, value):
            if isinstance(value, tuple) and value[0] == 'character':
                pointer = target
                slot = re.fullmatch(r'F_([A-Z][A-Z0-9_]*)\[(\d+)\]', target)
                if slot:
                    pointer = 'F_' + slot.group(1) + ' + ' + slot.group(2) + ' * ' + str(value[1] + 1)
                return 'f_char_copy(' + pointer + ', ' + str(value[1]) + ', ' + value[2] + ');'
            return target + ' = ' + value + ';'
        if data_guard is not None:
            decl('if (!' + data_guard + ') {')
            for target, value in data_entries:
                decl('    ' + data_init_statement(target, value))
            decl('    ' + data_guard + ' = 1;')
            decl('}')
        else:
            for target, value in data_entries:
                decl(data_init_statement(target, value))
        # Each ASSIGN is a label-valued INTEGER definition, distinct from
        # assignment of an arithmetic expression to that integer.
        assigned_by_var = {}
        for st in u.statements:
            assigned = re.fullmatch(r'ASSIGN\s+(\d{1,5})\s+TO\s+(' + NAME + r')', st.text)
            if assigned:
                label, var = assigned.groups()
                assigned_by_var.setdefault(var, set()).add(str(int(label)))
        code = []
        labels = {}
        gotos = []
        conditional_gotos = []  # (pc, condition, true_label, false_pc, source_line)
        blocks = []
        formats = {}
        format_sources = {}
        for st in u.statements:
            fm = re.fullmatch(r'FORMAT\s*\((.*)\)', st.text)
            if fm:
                if not st.label:
                    raise FortranError(st.line, 'FORMAT requires a statement label')
                if st.label in formats:
                    raise FortranError(st.line, 'duplicate FORMAT label: ' + st.label)
                formats[st.label] = subset_format(fm.group(1), st.line)
                format_sources[st.label] = fm.group(1)
        def add(lines, tail=None):
            code.append((list(lines), tail))
            return len(code) - 1
        def update(n, tail):
            code[n] = (code[n][0], tail)
        def E(text, line):
            return expression(text, u, known, line)
        def ret_stmt():
            return 'return ' + ('0' if is_main else 'F_' + u.name if u.kind == 'function' else '') + ';'
        def resolve_format(identifier, line):
            if identifier.isdecimal():
                label = str(int(identifier))
                if label not in formats:
                    raise FortranError(line, 'undefined FORMAT label: ' + label)
                return formats[label]
            quote = identifier[0]
            if (quote not in ("'", '"') or identifier[-1] != quote):
                raise FortranError(line, 'invalid CHARACTER FORMAT identifier')
            body = identifier[1:-1].replace(quote + quote, quote)
            if len(body) < 2 or not (body[0] == '(' and body[-1] == ')'):
                raise FortranError(line, 'CHARACTER FORMAT needs parenthesized format')
            return subset_format(body[1:-1], line)
        def revert_simple_format(items, count, identifier, line):
            """Expand record reversion from the rightmost repeated FORMAT group.

            F77S allows up to three nested groups. On reversion the next
            record begins at the repeat count preceding the last opening
            parenthesis (including edits following that group); without a
            nested group the entire FORMAT is restarted.
            """
            data_kinds = ('integer', 'real', 'realexp', 'realexpdigits',
                          'logical', 'character')
            descriptors = sum(kind in data_kinds for kind, _ in items)
            if count <= descriptors:
                return items
            if descriptors == 0:
                raise FortranError(line, 'FORMAT reversion needs a data descriptor')
            if identifier.isdecimal():
                source = format_sources[str(int(identifier))]
            else:
                q = identifier[0]
                source = identifier[2:-2].replace(q + q, q)
            stack = []
            groups = []
            quote = None
            i = 0
            while i < len(source):
                ch = source[i]
                if quote:
                    if ch == quote:
                        if i + 1 < len(source) and source[i + 1] == quote:
                            i += 2
                            continue
                        quote = None
                elif ch in ("'", '"'):
                    quote = ch
                elif ch == '(':
                    stack.append(i)
                elif ch == ')':
                    if not stack:
                        raise FortranError(line, 'unmatched closing FORMAT parenthesis')
                    start = stack.pop()
                    groups.append((start, i))
                i += 1
            if stack:
                raise FortranError(line, 'unmatched opening FORMAT parenthesis')
            reversion = items
            if groups:
                op, close = max(groups, key=lambda pair: pair[0])
                start = op
                while start > 0 and source[start - 1].isdigit():
                    start -= 1
                # Ancestor group closing parentheses are structural only;
                # do not repeat their enclosing initial descriptors.
                suffix = source[start:]
                depth = 0
                quote = None
                text = []
                j = 0
                while j < len(suffix):
                    ch = suffix[j]
                    if quote:
                        text.append(ch)
                        if ch == quote:
                            if j + 1 < len(suffix) and suffix[j + 1] == quote:
                                text.append(suffix[j + 1]); j += 1
                            else:
                                quote = None
                    elif ch in ("'", '"'):
                        quote = ch
                        text.append(ch)
                    elif ch == '(':
                        depth += 1
                        text.append(ch)
                    elif ch == ')':
                        if depth:
                            depth -= 1
                            text.append(ch)
                    else:
                        text.append(ch)
                    j += 1
                reversion = subset_format(''.join(text).strip().strip(','), line)
            reversion_descriptors = sum(kind in data_kinds for kind, _ in reversion)
            if reversion_descriptors == 0:
                raise FortranError(line, 'rightmost FORMAT group reversion lacks a data descriptor')
            result = list(items)
            remaining = count - descriptors
            while remaining > 0:
                if len(result) + len(reversion) + 1 > 255:
                    raise FortranError(line, 'FORMAT reversion exceeds 255 operations')
                result.append(('newrecord', None))
                result.extend(reversion)
                remaining -= reversion_descriptors
            return result
        def assigned_format(kind, channel, selector, arguments, line):
            if u.vars.get(selector) != ('INTEGER', None):
                raise FortranError(line, 'assigned FORMAT selector must be INTEGER scalar')
            candidates = [lab for lab in sorted(assigned_by_var.get(selector, ()), key=int)
                          if lab in formats]
            if not candidates:
                raise FortranError(line, 'assigned FORMAT has no assigned FORMAT label')
            flag = 'f_fmtok_' + str(len(code))
            extra_decls.append('int ' + flag + ';')
            result = [flag + ' = 0;']
            for lab in candidates:
                before = len(code)
                stmt(kind + '(' + channel + ',' + lab + ') ' + arguments, line)
                if len(code) != before + 1 or code[-1][1] is not None:
                    raise FortranError(line, 'internal assigned FORMAT expansion')
                lowered, _ = code.pop()
                result.append('if (F_' + selector + ' == ' + lab + ') {')
                result.append('    ' + flag + ' = 1;')
                result.extend('    ' + op for op in lowered)
                result.append('}')
            result.append('if (!' + flag + ') exit(2);')
            add(result)
        def runtime_io_implied_do(values, format_ops, mode, line, guard=None):
            """One runtime-count INTEGER array-list implied DO and I edit.

            FORMAT I edits must be identical; wrap at the descriptor repeat
            count. Nonstandard device mapping and general lists remain errors.
            """
            if len(values) != 1 or not values[0].startswith('(') or not values[0].endswith(')'):
                return False
            parts = split_items(values[0][1:-1])
            if len(parts) not in (3, 4):
                return False
            target = re.fullmatch(r'(' + NAME + r')\s*\(\s*(' + NAME + r')\s*\)', parts[0].strip())
            control = re.fullmatch(r'(' + NAME + r')\s*=\s*([+-]?[0-9]+|' + NAME + r')', parts[1].strip())
            if not target or not control or target.group(2) != control.group(1):
                return False
            var, first = control.groups()
            if u.vars.get(var) != ('INTEGER', None):
                raise FortranError(line, 'runtime implied-DO needs INTEGER scalar control')
            array = target.group(1)
            ty, extent = u.vars.get(array, (None, None))
            if extent is None or (isinstance(extent, tuple) and len(extent) != 1):
                raise FortranError(line, 'runtime I/O implied-DO needs a rank-1 array')
            values_expr = [first] + parts[2:]
            for token in values_expr:
                if not re.fullmatch(r'[+-]?[0-9]+|' + NAME, token):
                    raise FortranError(line, 'implied-DO runtime bound must be INTEGER variable or constant')
                if NAME_RE.fullmatch(token) and u.vars.get(token) != ('INTEGER', None):
                    raise FortranError(line, 'implied-DO bound must be INTEGER scalar: ' + token)
            if not any(NAME_RE.fullmatch(token) for token in values_expr):
                return False  # fixed-count I/O expansion retains its original behavior
            step = values_expr[2] if len(values_expr) == 3 else '1'
            if step == '0':
                raise FortranError(line, 'implied-DO step must be nonzero')
            if not format_ops or any(entry != format_ops[0] for entry in format_ops):
                raise FortranError(line, 'runtime implied-DO needs identical data edit descriptors')
            kind, edit = format_ops[0]
            compatible = ((kind == 'integer' and ty == 'INTEGER') or
                          (kind in ('real', 'realexp', 'realexpdigits') and ty == 'REAL') or
                          (kind == 'logical' and ty == 'LOGICAL') or
                          (kind == 'character' and ty.startswith('CHARACTER*')))
            if not compatible:
                raise FortranError(line, 'runtime implied-DO FORMAT/array type mismatch')
            n = len(format_ops)
            if n > 255:
                raise FortranError(line, 'FORMAT field count exceeds target 255 cap')
            unique = str(len(code))
            end = 'f_iend_' + unique
            inc = 'f_istep_' + unique
            count = 'f_icount_' + unique
            for name in (end, inc, count):
                extra_decls.append('int ' + name + ';')
            bound_expr = lambda token: E(token, line)
            body = [end + ' = ' + bound_expr(values_expr[1]) + ';',
                    inc + ' = ' + bound_expr(step) + ';',
                    count + ' = 0;',
                    'F_' + var + ' = ' + bound_expr(first) + ';',
                    'if (' + inc + ' == 0) exit(2);']
            if mode == 'READ':
                body.append('f_fmt_bzero = 0;')
            body += ['while ((' + inc + ' > 0 && F_' + var + ' <= ' + end +
                     ') || (' + inc + ' < 0 && F_' + var + ' >= ' + end + ')) {',
                     '    if (' + count + ' >= 255) exit(2);']
            if mode == 'READ':
                body.append('    if (' + count + ' && (' + count + ' % ' + str(n) + ') == 0) f_fmt_end();')
            else:
                body.append('    if (' + count + ' && (' + count + ' % ' + str(n) + ') == 0) putchar(10);')
            if kind == 'character':
                pointer, length = character_item(parts[0], u, known, line)
                width = edit or length
                operation = ('f_fmt_inchar(' if mode == 'READ' else 'f_outcharw(') + pointer + ', ' + str(length) + ', ' + str(width) + ');'
            else:
                value = E(parts[0], line)
                if mode == 'READ':
                    reader = {'integer':'f_fmt_int', 'logical':'f_fmt_logical',
                              'real':'f_fmt_real', 'realexp':'f_fmt_ereal',
                              'realexpdigits':'f_fmt_ereal'}[kind]
                    params = str(edit) if kind in ('integer','logical') else str(edit[0]) + ', ' + str(edit[1])
                    operation = value + ' = ' + reader + '(' + params + ');'
                else:
                    writer = {'integer':'f_outintw', 'logical':'f_outlogw',
                              'real':'f_outrealw', 'realexp':'f_outexp',
                              'realexpdigits':'f_outexpw'}[kind]
                    params = (str(edit) if kind in ('integer','logical') else
                              ', '.join(str(x) for x in edit))
                    operation = writer + '(' + value + ', ' + params + ');'
            body.append('    ' + operation)
            body += ['    ' + count + ' = ' + count + ' + 1;',
                     '    F_' + var + ' = f_add_checked(F_' + var + ', ' + inc + ');',
                     '}', 'f_fmt_end();' if mode == 'READ' else 'putchar(10);']
            if guard:
                body.insert(0, guard)
            add(body)
            return True

        def stmt(s, line):
            sf = re.match(r'^(' + NAME + r')\s*\(', s)
            if sf and sf.group(1) in u.statement_functions:
                return  # statement function is expanded on each reference
            if re.fullmatch(r'FORMAT\s*\((.*)\)', s):
                return  # FORMAT is a non-executable specification statement
            if re.match(r'^COMMON\s+', s):
                return  # COMMON names use global positional storage
            if re.match(r'^EQUIVALENCE\s*\(', s):
                return  # EQUIVALENCE objects share local storage
            if re.match(r'^DATA\s+', s):
                return  # initialized once for subprogram DATA
            if re.match(r'^SAVE\b', s):
                return  # checked by common.layout; storage is already global/static
            if re.match(r'^(EXTERNAL|INTRINSIC)\b', s):
                return  # declaration checked in parse()
            assigned = re.fullmatch(r'ASSIGN\s+(\d{1,5})\s+TO\s+(' + NAME + r')', s)
            if assigned:
                label, var = assigned.groups()
                if u.vars.get(var) != ('INTEGER', None):
                    raise FortranError(line, 'ASSIGN needs INTEGER scalar variable')
                label = str(int(label))
                n = add([E(var, line) + ' = ' + label + ';'])
                gotos.append((None, label, line))  # validate target exists, including FORMAT
                return
            # F77S unnamed sequential unformatted scratch unit 1..9.
            seqpos = re.fullmatch(r'(REWIND|BACKSPACE|ENDFILE)\s*(?:\(\s*([1-9])\s*\)|([1-9]))', s)
            if seqpos:
                op, paren, plain = seqpos.groups()
                add([('f_srewind' if op == 'REWIND' else 'f_send' if op == 'ENDFILE' else 'f_sback') + '(' + (paren or plain) + ');'])
                return
            seqend = re.fullmatch(
                r'READ\s*\(\s*([1-9])\s*,\s*END\s*=\s*([0-9]{1,5})\s*\)\s*([A-Z][A-Z0-9_]*)', s)
            if seqend:
                unit_no, target, name = seqend.groups()
                if u.vars.get(name) != ('INTEGER', None):
                    raise FortranError(line, 'END= sequential READ needs one INTEGER scalar')
                temp = 'f_sok_' + str(len(code))
                extra_decls.append('int ' + temp + ';')
                pc = add([temp + ' = f_sreadstat(' + unit_no + ', &F_' + name + ');'])
                conditional_gotos.append((pc, '!' + temp, str(int(target)), pc + 1, line))
                return
            seqio = re.fullmatch(r'(READ|WRITE)\s*\(\s*([1-9])\s*\)\s*([A-Z][A-Z0-9_]*)', s)
            if seqio:
                kind, unit_no, name = seqio.groups()
                if u.vars.get(name) != ('INTEGER', None):
                    raise FortranError(line, 'sequential unformatted scratch record needs one INTEGER scalar')
                if kind == 'WRITE':
                    add(['f_swrite(' + unit_no + ', F_' + name + ');'])
                else:
                    add(['F_' + name + ' = f_sread(' + unit_no + ');'])
                return
            # F77S narrow unnamed direct-access unformatted scratch files.
            # Each unit 1..9 owns /tmp/fuN; no named FILE= specifier.
            direct_open = re.fullmatch(
                r"OPEN\s*\(\s*([1-9])\s*,\s*ACCESS\s*=\s*'DIRECT'\s*,\s*RECL\s*=\s*(4|8)\s*\)",
                s)
            if direct_open:
                unit_no, rec_len = direct_open.groups()
                add(['f_dopen(' + unit_no + ', ' + rec_len + ');'])
                return
            if re.match(r'^OPEN\b', s):
                raise FortranError(line, 'only unnamed direct INTEGER RECL=4 OPEN is currently implemented')
            direct_pair = re.fullmatch(
                r'(READ|WRITE)\s*\(\s*([1-9])\s*,\s*REC\s*=\s*([0-9]+|[A-Z][A-Z0-9_]*)\s*\)\s*([A-Z][A-Z0-9_]*)\s*,\s*([A-Z][A-Z0-9_]*)',
                s)
            if direct_pair:
                kind, unit_no, rec, first, second = direct_pair.groups()
                if u.vars.get(first) != ('INTEGER', None) or u.vars.get(second) != ('INTEGER', None):
                    raise FortranError(line, 'RECL=8 direct I/O needs two INTEGER scalars')
                if NAME_RE.fullmatch(rec) and u.vars.get(rec) != ('INTEGER', None):
                    raise FortranError(line, 'REC identifier must be INTEGER scalar')
                if rec.isdecimal() and not (1 <= int(rec) <= 4096):
                    raise FortranError(line, 'direct record number out of supported range')
                rec_expr = ('F_' + rec) if NAME_RE.fullmatch(rec) else rec
                if kind == 'WRITE':
                    add(['f_dwrite2(' + unit_no + ', ' + rec_expr + ', F_' + first + ', F_' + second + ');'])
                else:
                    add(['f_dread2(' + unit_no + ', ' + rec_expr + ', &F_' + first + ', &F_' + second + ');'])
                return
            direct_io = re.fullmatch(
                r'(READ|WRITE)\s*\(\s*([1-9])\s*,\s*REC\s*=\s*([0-9]+|[A-Z][A-Z0-9_]*)\s*\)\s*([A-Z][A-Z0-9_]*)',
                s)
            if direct_io:
                kind, unit_no, rec, name = direct_io.groups()
                if u.vars.get(name) != ('INTEGER', None):
                    raise FortranError(line, 'direct unformatted I/O requires a single INTEGER scalar')
                if NAME_RE.fullmatch(rec) and u.vars.get(rec) != ('INTEGER', None):
                    raise FortranError(line, 'REC identifier must be INTEGER scalar')
                if rec.isdecimal() and not (1 <= int(rec) <= 8192):
                    raise FortranError(line, 'direct record number out of supported range')
                rec_expr = ('F_' + rec) if NAME_RE.fullmatch(rec) else rec
                if kind == 'WRITE':
                    add(['f_dwritei(' + unit_no + ', ' + rec_expr + ', F_' + name + ');'])
                else:
                    add(['F_' + name + ' = f_dreadi(' + unit_no + ', ' + rec_expr + ');'])
                return
            if re.match(r'^(READ|WRITE)\s*\(\s*[0-9]+\s*,\s*REC\s*=', s):
                raise FortranError(line, 'direct unformatted I/O supports one INTEGER scalar and REC')
            def console_unit_guard(identifier, required):
                if identifier in (str(required), '*'):
                    return None
                if u.std == 'f77s' and NAME_RE.fullmatch(identifier):
                    if u.vars.get(identifier) != ('INTEGER', None):
                        raise FortranError(line, 'formatted I/O unit must be INTEGER scalar')
                    return 'if (F_' + identifier + ' != ' + str(required) + ') exit(2);'
                raise FortranError(line, 'ZX-UX formatted I/O supports only console unit ' + str(required))
            unit_ident = r'(\d{1,5}|\*|[A-Z][A-Z0-9_]*)'
            fmt_ident = r'(\d{1,5}|[A-Z][A-Z0-9_]*|\'(?:[^\']|\'\')*\'|"(?:[^"]|"")*")'
            fm = re.fullmatch(r'WRITE\s*\(\s*' + unit_ident + r'\s*,\s*' + fmt_ident + r'\s*\)\s*(.*)', s)
            if fm:
                channel, format_label, arguments = fm.groups()
                guard = console_unit_guard(channel, 6)
                if NAME_RE.fullmatch(format_label):
                    assigned_format('WRITE', channel, format_label, arguments, line)
                    return
                format_ops = resolve_format(format_label, line)
                values = split_items(arguments) if arguments.strip() else []
                if u.std == 'f77s' and runtime_io_implied_do(values, format_ops, 'WRITE', line, guard):
                    return
                if u.std == 'f77s':
                    values, index_updates = expand_static_io_items(values, u, line)
                else:
                    index_updates = []
                format_ops = revert_simple_format(format_ops, len(values), format_label, line)
                operations = [guard] if guard else []
                pos = 0
                scale_factor = 0
                for mode, item in format_ops:
                    if mode == 'newrecord':
                        operations.append('putchar(10);')
                        continue
                    if mode == 'scale':
                        scale_factor = item
                        continue
                    if mode == 'blank':
                        continue  # BN/BZ affect numeric input conversion, not output
                    if mode == 'literal':
                        operations.append('f_outstr(' + c_string(item) + ');')
                    elif mode == 'space':
                        operations.extend(["putchar(' ');"] * item)
                    elif mode == 'newline':
                        operations.append('putchar(10);')
                    elif mode == 'character':
                        if pos == len(values):
                            break
                        name = values[pos].strip()
                        char_value = character_item(name, u, known, line)
                        if not char_value:
                            raise FortranError(line, 'FORMAT A requires CHARACTER scalar/array element')
                        pointer, length = char_value
                        operations.append('f_outcharw(' + pointer + ', ' + str(length) + ', ' + str(item or length) + ');')
                        pos += 1
                    elif mode == 'logical':
                        if pos == len(values):
                            break
                        name = values[pos].strip()
                        m = re.fullmatch(r'(' + NAME + r')(?:\s*\(([^()]*)\))?', name)
                        info = u.vars.get(m.group(1)) if m else None
                        if not info or info[0] != 'LOGICAL' or (info[1] is None) != (m.group(2) is None):
                            raise FortranError(line, 'FORMAT L needs LOGICAL scalar/array element')
                        operations.append('f_outlogw(' + E(name, line) + ', ' + str(item) + ');')
                        pos += 1
                    elif mode in ('real', 'realexp', 'realexpdigits'):
                        if pos == len(values):
                            break
                        name = values[pos].strip()
                        m = re.fullmatch(r'(' + NAME + r')(?:\s*\(([^()]*)\))?', name)
                        info = u.vars.get(m.group(1)) if m else None
                        if not info or info[0] != 'REAL' or (info[1] is None) != (m.group(2) is None):
                            raise FortranError(line, 'FORMAT F/E needs REAL variable/element')
                        if mode != 'real' and scale_factor:
                            raise FortranError(line, 'P scale for E output not yet supported')
                        value = E(name, line)
                        if mode == 'real' and scale_factor:
                            value = 'f_scale_real(' + value + ', ' + str(scale_factor) + ')'
                        if mode == 'realexpdigits':
                            operations.append('f_outexpw(' + value + ', ' + str(item[0]) + ', ' + str(item[1]) + ', ' + str(item[2]) + ');')
                        else:
                            operations.append(('f_outrealw(' if mode == 'real' else 'f_outexp(') + value + ', ' + str(item[0]) + ', ' + str(item[1]) + ');')
                        pos += 1
                    elif mode == 'integer':
                        if pos == len(values):
                            break
                        arg = values[pos]
                        if re.search(r'\d+\.\d*', arg) or any(re.search(r'\b' + re.escape(k) + r'\b', arg) for k, v in u.vars.items() if v[0] == 'REAL'):
                            raise FortranError(line, 'FORMAT I requires INTEGER item')
                        operations.append('f_outintw(' + E(arg, line) + ', ' + str(item) + ');')
                        pos += 1
                if pos != len(values):
                    raise FortranError(line, 'WRITE has more items than FORMAT')
                operations.append('putchar(10);')
                operations.extend('F_' + var + ' = ' + str(value) + ';' for var, value in index_updates)
                add(operations)
                return
            fm = re.fullmatch(r'READ\s*\(\s*' + unit_ident + r'\s*,\s*' + fmt_ident + r'\s*\)\s*(.*)', s)
            if fm:
                channel, format_label, arguments = fm.groups()
                guard = console_unit_guard(channel, 5)
                if NAME_RE.fullmatch(format_label):
                    assigned_format('READ', channel, format_label, arguments, line)
                    return
                format_ops = resolve_format(format_label, line)
                values = split_items(arguments) if arguments.strip() else []
                if u.std == 'f77s' and runtime_io_implied_do(values, format_ops, 'READ', line, guard):
                    return
                if u.std == 'f77s':
                    values, index_updates = expand_static_io_items(values, u, line)
                else:
                    index_updates = []
                format_ops = revert_simple_format(format_ops, len(values), format_label, line)
                operations = ([guard] if guard else []) + ['f_fmt_bzero = 0;']
                pos = 0
                scale_factor = 0
                for mode, item in format_ops:
                    if mode == 'newrecord':
                        operations.append('f_fmt_end();')
                        continue
                    if mode == 'scale':
                        scale_factor = item
                        continue
                    if mode == 'blank':
                        operations.append('f_fmt_bzero = ' + str(item) + ';')
                    elif mode == 'space':
                        operations.append('f_fmt_skip(' + str(item) + ');')
                    elif mode == 'newline':
                        operations.append('f_fmt_end();')
                    elif mode == 'character':
                        if pos == len(values):
                            break
                        name = values[pos].strip()
                        char_value = character_item(name, u, known, line)
                        if not char_value:
                            raise FortranError(line, 'FORMAT A requires CHARACTER scalar/array element')
                        pointer, length = char_value
                        operations.append('f_fmt_inchar(' + pointer + ', ' + str(length) + ', ' + str(item or length) + ');')
                        pos += 1
                    elif mode == 'logical':
                        if pos == len(values):
                            break
                        name = values[pos].strip()
                        m = re.fullmatch(r'(' + NAME + r')(?:\s*\(([^()]*)\))?', name)
                        info = u.vars.get(m.group(1)) if m else None
                        if not info or info[0] != 'LOGICAL' or (info[1] is None) != (m.group(2) is None):
                            raise FortranError(line, 'FORMAT L needs LOGICAL scalar/array element')
                        operations.append(E(name, line) + ' = f_fmt_logical(' + str(item) + ');')
                        pos += 1
                    elif mode in ('real', 'realexp', 'realexpdigits'):
                        if pos == len(values):
                            break
                        name = values[pos].strip()
                        m = re.fullmatch(r'(' + NAME + r')(?:\s*\(([^()]*)\))?', name)
                        info = u.vars.get(m.group(1)) if m else None
                        if not info or info[0] != 'REAL' or (info[1] is None) != (m.group(2) is None):
                            raise FortranError(line, 'FORMAT F needs REAL variable/element')
                        reader = 'f_fmt_real' if mode == 'real' else 'f_fmt_ereal'
                        value = reader + '(' + str(item[0]) + ', ' + str(item[1]) + ')'
                        if scale_factor:
                            if mode != 'real':
                                raise FortranError(line, 'P scale for E input not yet supported')
                            value = 'f_scale_real(' + value + ', ' + str(-scale_factor) + ')'
                        operations.append(E(name, line) + ' = ' + value + ';')
                        pos += 1
                    elif mode == 'integer':
                        if pos == len(values):
                            break
                        arg = values[pos]
                        target = re.fullmatch(r'(' + NAME + r')(?:\s*\(([^()]*)\))?', arg)
                        if not target:
                            raise FortranError(line, 'formatted READ item must be a variable/array element')
                        ty = u.vars.get(target.group(1))
                        if not ty or ty[0] != 'INTEGER' or (ty[1] is not None) != (target.group(2) is not None):
                            raise FortranError(line, 'FORMAT I requires INTEGER scalar/array element')
                        dest = E(arg, line)
                        operations.append(dest + ' = f_fmt_int(' + str(item) + ');')
                        pos += 1
                    else:
                        raise FortranError(line, 'unsupported FORMAT descriptor for READ: ' + mode)
                if pos != len(values):
                    raise FortranError(line, 'READ has more items than FORMAT')
                operations.append('f_fmt_end();')
                operations.extend('F_' + var + ' = ' + str(value) + ';' for var, value in index_updates)
                add(operations)
                return
            pause = re.fullmatch(r'PAUSE(?:\s+([0-9]{1,5}|\'(?:[^\']|\'\')*\'|"(?:[^"]|"")*"))?', s)
            if pause:
                code_text = pause.group(1)
                message = 'PAUSE' if code_text is None else 'PAUSE ' + (code_text[1:-1].replace(code_text[0]*2, code_text[0]) if code_text[0] in ("'", '"') else code_text)
                add(['f_outstr(' + c_string("'" + message + "'") + ');',
                     'putchar(10);', 'getchar();'])
                return
            if s.startswith(UNSUPPORTED):
                raise FortranError(line, 'unsupported FORTRAN statement: ' + s.split()[0])
            if (re.match(r'^(INTEGER|REAL|LOGICAL|IMPLICIT|DIMENSION)\s+', s)
                    or re.match(r'^CHARACTER(?:\*|\s)', s) or s == 'IMPLICIT NONE'):
                return
            if s == 'CONTINUE':
                return
            if s == 'STOP':
                add(['exit(0);'], 'return'); return
            if s == 'RETURN':
                add([ret_stmt()], 'return'); return
            m = re.fullmatch(r'GO\s*TO\s+(\d+)', s)
            if m:
                n = add([]); gotos.append((n, str(int(m.group(1))), line)); return
            # F77S computed GO TO accepts an INTEGER name or constant as
            # its selector; an out-of-range selector falls through.
            m = re.fullmatch(r'GO\s*TO\s*\(([^()]*)\)\s*,?\s*(.+)', s)
            if m:
                targets = [item.strip() for item in split_items(m.group(1))]
                selector = m.group(2).strip()
                if (not targets or any(not re.fullmatch(r'\d{1,5}', x) for x in targets)
                        or not re.fullmatch(r'(?:\d+|' + NAME + r')', selector)):
                    raise FortranError(line, 'computed GO TO needs labels and an INTEGER selector')
                if NAME_RE.fullmatch(selector) and u.vars.get(selector) != ('INTEGER', None):
                    raise FortranError(line, 'computed GO TO selector must be INTEGER')
                key = 'f_select_' + str(len(code))
                extra_decls.append('int ' + key + ';')
                add([key + ' = ' + E(selector, line) + ';'])
                for index, label in enumerate(targets, 1):
                    pc = add([])
                    conditional_gotos.append((pc, key + ' == ' + str(index),
                                              str(int(label)), pc + 1, line))
                return
            # Assigned GO TO: allowed label lists are checked against active
            # executable labels; missing labels are trapped, not ignored.
            ag = re.fullmatch(r'GO\s*TO\s+(' + NAME + r')(?:\s*,?\s*\(([^()]*)\))?', s)
            if ag:
                var, listed = ag.groups()
                if u.vars.get(var) != ('INTEGER', None):
                    raise FortranError(line, 'assigned GO TO needs INTEGER scalar variable')
                if listed is None:
                    targets = sorted(assigned_by_var.get(var, ()), key=int)
                else:
                    targets = [item.strip() for item in split_items(listed)]
                if not targets or any(not re.fullmatch(r'\d{1,5}', x) for x in targets):
                    raise FortranError(line, 'assigned GO TO needs valid label list or ASSIGN values')
                for lab in targets:
                    pc = add([])
                    conditional_gotos.append((pc, E(var, line) + ' == ' + str(int(lab)),
                                              str(int(lab)), pc + 1, line))
                add(['exit(2);'], 'return')  # undefined transfer is never a silent fallthrough
                return
            if s.startswith('CALL '):
                m = re.fullmatch(r'CALL\s+(' + NAME + r')\s*\((.*)\)', s)
                if not m or m.group(1) not in known or known[m.group(1)].kind != 'subroutine':
                    raise FortranError(line, 'invalid or unknown SUBROUTINE call')
                f, a = m.groups()
                args = [] if not a.strip() else split_items(a)
                if len(args) != len(known[f].args):
                    raise FortranError(line, 'SUBROUTINE argument count mismatch')
                refs = []
                prelude = []
                extra_capacity = []
                for actual, dummy in zip(args, known[f].args):
                    ty, dims = known[f].vars[dummy]
                    actual = actual.strip()
                    if dims is not None and ty.startswith('CHARACTER*'):
                        # A fixed-length CHARACTER dummy array aliases complete
                        # fixed-size elements, not individual C bytes.
                        from .arrays import size as total_extent, literal_offset
                        element = re.fullmatch(r'(' + NAME + r')\s*\((.*)\)', actual)
                        actual_name = element.group(1) if element else actual
                        info = u.vars.get(actual_name)
                        if not info or info[1] is None or info[0] != ty:
                            raise FortranError(line, 'CHARACTER dummy needs same-length array/element actual')
                        if dynamic_extent(info[1]):
                            raise FortranError(line, 'adjustable CHARACTER actual is not implemented')
                        width = int(ty.split('*')[1])
                        avail = total_extent(info[1])
                        needed = total_extent(dims)
                        if element:
                            parts = [part.strip() for part in split_items(element.group(2))]
                            if all(re.fullmatch(r'\d+', part) for part in parts):
                                off = literal_offset([int(part) for part in parts], info[1], line)
                                if avail - off < needed:
                                    raise FortranError(line, 'CHARACTER actual shorter than dummy')
                                start = str(off)
                            else:
                                start = array_subscript([E(part, line) for part in parts], actual_name, u, line)
                                start = 'f_seqcheck(' + start + ', ' + str(avail) + ', ' + str(needed) + ')'
                            refs.append('(F_' + actual_name + ' + (' + start + ') * ' + str(width + 1) + ')')
                        else:
                            if avail < needed:
                                raise FortranError(line, 'CHARACTER actual shorter than dummy')
                            refs.append('F_' + actual_name)
                    elif dims is not None:
                        # FORTRAN array arguments are references to the first
                        # sequence element, not copies of the array contents.
                        # At this stage only named fixed-size whole arrays
                        # are supported; adjustable bound expressions and
                        # element designators need separate checks.
                        # A whole array or an array element can designate a
                        # sequence of storage elements. For element actuals,
                        # constant subscripts let us prove the remaining
                        # extent before emitting a by-reference pointer.
                        # Dynamic starting subscripts additionally check
                        # that the remaining sequence covers the dummy.
                        element = re.fullmatch(r'(' + NAME + r')\s*\((.*)\)', actual)
                        actual_name = element.group(1) if element else actual
                        info = u.vars.get(actual_name)
                        if not info or info[1] is None:
                            raise FortranError(line, 'dummy array needs an array variable or element actual: ' + dummy)
                        if info[0] != ty:
                            raise FortranError(line, 'array argument type mismatch: ' + actual)
                        from .arrays import size as total_extent, literal_offset
                        variable_actual = dynamic_extent(info[1])
                        actual_total = 'F__LEN_' + actual_name if variable_actual else str(total_extent(info[1]))
                        required = total_extent(dims) if not dynamic_extent(dims) else None
                        last_bound = dims[-1] if dynamic_extent(dims) else None
                        def caller_bound(bound):
                            if isinstance(bound, int):
                                return str(bound)
                            if bound == '*':
                                return '*'
                            if bound not in known[f].args:
                                # COMMON bound resolved from the callee's own
                                # shared sequence; validate whole shape at entry.
                                return '1'
                            bound_pos = known[f].args.index(bound)
                            return E(args[bound_pos], line)
                        required = str(required) if required is not None else None
                        ptr_offset = '0'
                        if element:
                            subscripts = split_items(element.group(2))
                            if not variable_actual and all(re.fullmatch(r'\d+', sub.strip()) for sub in subscripts):
                                start = literal_offset([int(sub.strip()) for sub in subscripts], info[1], line)
                                if not dynamic_extent(dims) and total_extent(info[1]) - start < total_extent(dims):
                                    raise FortranError(line, 'array actual shorter than dummy: ' + actual)
                                ptr_offset = str(start)
                            else:
                                ptr_offset = array_subscript([E(sub, line) for sub in subscripts], actual_name, u, line)
                            capacity = '(' + actual_total + ' - (' + ptr_offset + '))'
                        else:
                            capacity = actual_total
                        if not dynamic_extent(dims) and not variable_actual and not element and total_extent(info[1]) < total_extent(dims):
                            raise FortranError(line, 'array actual shorter than dummy: ' + actual)
                        if dynamic_extent(dims):
                            # Callee receives remaining physical capacity separately.
                            # Capture once to prevent duplicate side effects.
                            key = 'f_cap_' + str(len(code)) + '_' + str(len(refs))
                            extra_decls.append('int ' + key + ';')
                            def guard_against(cap):
                                prefix = '1'
                                for bound in dims[:-1]:
                                    value = caller_bound(bound)
                                    # Validate each factor before multiplying: avoids
                                    # 16-bit overflow of malformed adjustable bounds.
                                    checked = 'f_extent(' + value + ', (' + cap + ' / (' + prefix + ')))'
                                    prefix = '(' + prefix + ' * ' + checked + ')'
                                if last_bound == '*':
                                    return 'f_seqcheck(0, ' + cap + ', ' + prefix + ');'
                                limit = 'f_extent(' + caller_bound(last_bound) + ', (' + cap + ' / (' + prefix + ')))'
                                return 'f_seqcheck(0, ' + cap + ', (' + prefix + ' * ' + limit + '));'
                            if element:
                                # Compute index once; the caller's passed pointer and
                                # hidden capacity must start at the same element.
                                idxkey = 'f_idx_' + str(len(code)) + '_' + str(len(refs))
                                extra_decls.append('int ' + idxkey + ';')
                                refs.append('&F_' + actual_name + '[' + idxkey + ']')
                                extra_capacity.append(key)
                                prelude.extend([idxkey + ' = ' + ptr_offset + ';', key + ' = (' + actual_total + ' - ' + idxkey + ');',
                                                guard_against(key)])
                            else:
                                refs.append('F_' + actual_name)
                                extra_capacity.append(key)
                                prelude.extend([key + ' = ' + capacity + ';', guard_against(key)])
                        else:
                            if element and not variable_actual and not re.fullmatch(r'\d+', ptr_offset):
                                ptr_offset = 'f_seqcheck(' + ptr_offset + ', ' + actual_total + ', ' + required + ')'
                            refs.append('&F_' + actual_name + '[' + ptr_offset + ']' if element else 'F_' + actual_name)
                            if variable_actual:
                                prelude.append('f_seqcheck(0, ' + capacity + ', ' + required + ');')
                    elif ty.startswith('CHARACTER*'):
                        length = int(ty.split('*')[1])
                        lit = re.fullmatch(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"", actual)
                        if lit:
                            quote = actual[0]
                            chars = actual[1:-1].replace(quote + quote, quote)
                            if len(chars) != length:
                                raise FortranError(line, 'CHARACTER constant actual needs same length as dummy')
                            # A constant actual must not be defined by the
                            # callee; don't pass literals to writable dummies.
                            callee = known[f]
                            writing = any(
                                re.match(r'^' + re.escape(dummy) + r'\s*(?:\([^)]*\))?\s*=', st.text)
                                or (re.match(r'^READ\b', st.text) and
                                    re.search(r'\b' + re.escape(dummy) + r'\b', st.text))
                                or (re.match(r'^CALL\b', st.text) and
                                    re.search(r'\b' + re.escape(dummy) + r'\b', st.text))
                                for st in callee.statements)
                            if writing:
                                raise FortranError(line, 'CHARACTER constant actual cannot bind writable dummy')
                            refs.append(c_string(actual))
                        else:
                            item = character_item(actual, u, known, line)
                            if item is None or item[1] != length:
                                raise FortranError(line, 'CHARACTER dummy requires same-length CHARACTER scalar actual: ' + actual)
                            refs.append(item[0])
                    else:
                        # A by-reference scalar actual has to match its
                        # dummy type. C48's pointer conversion is not a
                        # valid FORTRAN storage association conversion.
                        actual_ty = None
                        scalar = re.fullmatch(r'(' + NAME + r')(?:\s*\((.*)\))?', actual)
                        if scalar:
                            declared = u.vars.get(scalar.group(1))
                            if declared:
                                actual_ty = declared[0]
                            elif scalar.group(1) in known:
                                actual_ty = known[scalar.group(1)].type
                        elif re.fullmatch(r'[+-]?[0-9]+', actual):
                            actual_ty = 'INTEGER'
                        elif re.fullmatch(r'[+-]?(?:(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[ED][+-]?[0-9]+)?|[0-9]+[ED][+-]?[0-9]+)', actual):
                            actual_ty = 'REAL'
                        elif actual in ('.TRUE.', '.FALSE.'):
                            actual_ty = 'LOGICAL'
                        if actual_ty is not None and actual_ty != ty:
                            raise FortranError(line, 'scalar argument type mismatch: ' + actual)
                        refs.append(reference_actual(E(actual, line), u, ty))
                add(prelude + ['f_' + f + '(' + ', '.join(refs + extra_capacity) + ');'])
                return
            m = re.fullmatch(r'PRINT\s*\*\s*,\s*(.*)', s)
            if m:
                operations = []
                for i, p in enumerate(split_items(m.group(1))):
                    if i:
                        operations.append("putchar(' ');")
                    if p.startswith(("'", '"')) and p.endswith(p[0]):
                        operations.append('f_outstr(' + c_string(p) + ');')
                    else:
                        if re.search(r'\d+\.\d*', p) or any(re.search(r'\b' + re.escape(k) + r'\b', p) for k, v in u.vars.items() if v[0] == 'REAL'):
                            raise FortranError(line, 'REAL list-directed PRINT is not implemented')
                        operations.append('f_outint(' + E(p, line) + ');')
                operations.append('putchar(10);')
                add(operations); return
            m = re.fullmatch(r'READ\s*\*\s*,\s*(.*)', s)
            if m:
                operations = []
                for p in split_items(m.group(1)):
                    dest = E(p, line)
                    if not (dest.startswith('F_') or dest.startswith('(*F_')):
                        raise FortranError(line, 'READ requires an INTEGER variable')
                    nm = re.match(r'\s*([A-Z][A-Z0-9_]*)\s*(?:\(.*\))?$', p)
                    if not nm or u.vars.get(nm.group(1), ('', None))[0] != 'INTEGER':
                        raise FortranError(line, 'READ requires an INTEGER variable')
                    operations.append(dest + ' = f_inint();')
                add(operations); return
            m = re.fullmatch(r'(' + NAME + r'(?:\s*\([^)]*\))?)\s*=\s*(.*)', s)
            if m:
                lhs, rhs = m.group(1).strip(), m.group(2).strip()
                target = character_item(lhs, u, known, line)
                if target:
                    pointer, length = target
                    if re.fullmatch(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"", rhs):
                        value = c_string(rhs)
                    else:
                        source = character_item(rhs, u, known, line)
                        if not source:
                            raise FortranError(line, 'CHARACTER assignment must use a literal or CHARACTER item')
                        value = source[0]
                    add(['f_char_copy(' + pointer + ', ' + str(length) + ', ' + value + ');'])
                    return
                dest, value = E(m.group(1), line), E(m.group(2), line)
                if not (dest.startswith('F_') or dest.startswith('(*F_')):
                    raise FortranError(line, 'assignment requires a scalar or array element')
                add([dest + ' = ' + value + ';']); return
            raise FortranError(line, 'unsupported FORTRAN statement: ' + s)
        for st in u.statements:
            s = st.text.strip()
            if st.label:
                if st.label in labels:
                    raise FortranError(st.line, 'duplicate statement label: ' + st.label)
                labels[st.label] = len(code)
            if s == 'ELSE':
                if not blocks or blocks[-1]['kind'] != 'if' or blocks[-1].get('else'):
                    raise FortranError(st.line, 'ELSE without IF')
                b = blocks[-1]
                j = add([])
                update(b['check'], ('cond', b['cond'], b['start'], len(code)))
                b['endjump'] = j; b['else'] = True
                continue
            if s in ('ENDIF', 'END IF'):
                if not blocks or blocks[-1]['kind'] != 'if':
                    raise FortranError(st.line, 'ENDIF without IF')
                b = blocks.pop()
                if b.get('else'):
                    update(b['endjump'], ('jump', len(code)))
                else:
                    update(b['check'], ('cond', b['cond'], b['start'], len(code)))
                continue
            m = re.fullmatch(r'DO\s+(\d{1,5})\s+(' + NAME + r')\s*=\s*(.+)', s)
            if m:
                lab, var, values = m.groups()
                parts = split_items(values)
                if len(parts) not in (2, 3) or u.vars.get(var) != ('INTEGER', None):
                    raise FortranError(st.line, 'DO needs INTEGER scalar and 2 or 3 limits')
                beg, finish = parts[:2]
                step = parts[2] if len(parts) == 3 else '1'
                k = len(code)
                endvar, stepvar = 'f_end_' + str(k), 'f_step_' + str(k)
                extra_decls.append('int ' + endvar + ';')
                extra_decls.append('int ' + stepvar + ';')
                add(['F_' + var + ' = ' + E(beg, st.line) + ';',
                     endvar + ' = ' + E(finish, st.line) + ';',
                     stepvar + ' = ' + E(step, st.line) + ';',
                     'if (' + stepvar + ' == 0) exit(2);'])
                check = len(code)
                cond = '((' + stepvar + ' > 0 && F_' + var + ' <= ' + endvar + ') || (' + stepvar + ' < 0 && F_' + var + ' >= ' + endvar + '))'
                add([])
                blocks.append({'kind': 'do', 'label': lab, 'var': var, 'step': stepvar,
                               'check': check, 'start': len(code), 'cond': cond})
                continue
            m = re.match(r'IF\s*\(', s)
            if m:
                i, depth = m.end(), 1
                while i < len(s) and depth:
                    if s[i] == '(':
                        depth += 1
                    if s[i] == ')':
                        depth -= 1
                    i += 1
                if depth:
                    raise FortranError(st.line, 'IF condition not closed')
                raw_condition = s[m.end():i - 1]
                tail = s[i:].strip()
                # Arithmetic IF is an F77S control statement, distinct from
                # logical IF. Evaluate the expression exactly once before
                # choosing its negative/zero/positive label.
                arithmetic_labels = re.fullmatch(r'(\d{1,5})\s*,\s*(\d{1,5})\s*,\s*(\d{1,5})', tail)
                if arithmetic_labels:
                    value = 'f_arth_' + str(len(code))
                    extra_decls.append('float ' + value + ';')
                    add([value + ' = ' + E(raw_condition, st.line) + ';'])
                    neg_pc = add([])
                    zero_pc = add([])
                    minus, zero, plus = (str(int(n)) for n in arithmetic_labels.groups())
                    conditional_gotos.append((neg_pc, value + ' < 0', minus, zero_pc, st.line))
                    conditional_gotos.append((zero_pc, value + ' == 0', zero, ('label', plus), st.line))
                else:
                    cond = E(raw_condition, st.line)
                    check = add([])
                    if tail == 'THEN':
                        blocks.append({'kind': 'if', 'check': check, 'cond': cond, 'start': len(code)})
                    elif tail:
                        start = len(code)
                        stmt(tail, st.line)
                        update(check, ('cond', cond, start, len(code)))
                    else:
                        raise FortranError(st.line, 'IF must have THEN or following statement')
            else:
                stmt(s, st.line)
            # The DO terminal statement executes before increment. Repeat for
            # nested DO statements with a shared termination label.
            while blocks and blocks[-1]['kind'] == 'do' and blocks[-1]['label'] == st.label:
                b = blocks.pop()
                add(['F_' + b['var'] + ' = F_' + b['var'] + ' + ' + b['step'] + ';'], ('jump', b['check']))
                update(b['check'], ('cond', b['cond'], b['start'], len(code)))
        if blocks:
            raise FortranError(u.line, 'unterminated DO or IF construct')
        for n, lab, ln in gotos:
            if lab not in labels:
                raise FortranError(ln, 'undefined statement label: ' + lab)
            if n is None:
                continue  # ASSIGN only defines a label; FORMAT targets are legal
            if lab in formats:
                raise FortranError(ln, 'control transfer to FORMAT label: ' + lab)
            update(n, ('jump', labels[lab]))
        for n, condition, lab, alternative, ln in conditional_gotos:
            if lab not in labels:
                raise FortranError(ln, 'undefined statement label: ' + lab)
            if lab in formats:
                raise FortranError(ln, 'control transfer to FORMAT label: ' + lab)
            if lab in formats:
                raise FortranError(ln, 'control transfer to FORMAT label: ' + lab)
            if isinstance(alternative, tuple):
                other = alternative[1]
                if other not in labels:
                    raise FortranError(ln, 'undefined statement label: ' + other)
                if other in formats:
                    raise FortranError(ln, 'control transfer to FORMAT label: ' + other)
                alternative = labels[other]
            update(n, ('cond', condition, labels[lab], alternative))
        for temp, ty in u.temps:
            extra_decls.append(ctype(ty) + ' ' + temp + ';')
        decl('f_pc = 0;')
        decl('while (1) {')
        for n, (operations, tail) in enumerate(code):
            decl('    if (f_pc == ' + str(n) + ') {')
            for op in operations:
                decl('        ' + op)
            if tail != 'return':
                if tail is None:
                    decl('        f_pc = ' + str(n + 1) + ';')
                elif tail[0] == 'jump':
                    decl('        f_pc = ' + str(tail[1]) + ';')
                else:
                    _, cond, yes, no = tail
                    decl('        if (' + cond + ') f_pc = ' + str(yes) + ';')
                    decl('        else f_pc = ' + str(no) + ';')
                decl('        continue;')
            decl('    }')
        decl('    ' + ret_stmt())
        decl('}')
        output[local_decl_index:local_decl_index] = ['    ' + d for d in extra_decls]
        output.append('}')
        chunks.append(bind('\n'.join(output), aliases))
    # Supply only the REAL math code called by this translation unit.
    emitted = '\n'.join(chunks)
    needed = {name for name in ('SIN', 'COS', 'EXP', 'LOG', 'TAN', 'SINH', 'COSH', 'TANH', 'ASIN', 'ACOS', 'ATAN', 'ATAN2', 'ALOG10', 'AMOD', 'RIPOW', 'RPOW')
              if 'f_' + name.lower() + '_real(' in emitted}
    if 'RPOW' in needed:
        needed.update(('EXP', 'LOG'))
    if needed.intersection(('SINH', 'COSH', 'TANH')):
        needed.add('EXP')
    chunks[1:1] = [REAL_MATH_RUNTIME[name] for name in
                    ('SIN', 'COS', 'EXP', 'LOG', 'TAN', 'SINH', 'COSH', 'TANH', 'ASIN', 'ACOS', 'ATAN', 'ATAN2', 'ALOG10', 'AMOD', 'RIPOW', 'RPOW') if name in needed]
    if emit_units is not None:
        chunks[0] = sparse_runtime(RUNTIME, '\n'.join(chunks[1:]))
    return '\n\n'.join(chunks) + '\n'
