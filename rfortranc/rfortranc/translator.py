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
                 or bool(len(raw) >= 6 and raw[:5].strip().isdigit() and raw[5] == ' ')
                 or bool(fixed_form and len(raw) >= 6 and raw[:5].strip() == ''
                         and raw[5] not in ' 0'))
        if fixed:
            lab = raw[:5].strip() or None
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


def parse(source, std='zxux'):
    units = []
    unit = None
    for st in lines(source):
        s = st.text.strip()
        fm = re.fullmatch(r'(INTEGER|REAL|LOGICAL)\s+FUNCTION\s+(' + NAME + r')\s*\(([^)]*)\)', s)
        sm = re.fullmatch(r'SUBROUTINE\s+(' + NAME + r')\s*\(([^)]*)\)', s)
        pm = re.fullmatch(r'PROGRAM\s+(' + NAME + r')', s)
        if fm or sm or pm:
            if unit:
                raise FortranError(st.line, 'missing END before next program unit')
            if fm:
                ty, name, arg = fm.groups(); kind = 'function'
            elif sm:
                name, arg = sm.groups(); ty, kind = 'INTEGER', 'subroutine'
            else:
                name = pm.group(1); arg, ty, kind = '', 'INTEGER', 'program'
            args = [] if not arg.strip() else [a.strip() for a in split_items(arg)]
            if any(not NAME_RE.fullmatch(a) for a in args) or len(args) != len(set(args)):
                raise FortranError(st.line, 'invalid or duplicate dummy arguments')
            unit = Unit(name, kind, st.line, args, ty)
            continue
        if s == 'END':
            if unit is None:
                raise FortranError(st.line, 'END without program unit')
            units.append(unit); unit = None
            continue
        if unit is None:
            if not units and not s.startswith(('FUNCTION', 'SUBROUTINE')):
                # FORTRAN permits an unnamed main program.
                unit = Unit('MAIN', 'program', st.line)
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
        from .implicit import infer
        known = set(names)
        for u in units:
            infer(u, known)
    for u in units:
        for name, (ty, dims) in u.vars.items():
            if dims is not None and ty.startswith('CHARACTER*') and not dynamic_extent(dims):
                from .arrays import size as total_extent
                width = int(ty.split('*')[1])
                if total_extent(dims) * (width + 1) > 32767:
                    raise FortranError(u.line, 'CHARACTER array byte extent exceeds ZX-UX 16-bit range')
            if dynamic_extent(dims):
                bound = dims[-1]
                if bound != '*' and u.vars.get(bound) != ('INTEGER', None):
                    raise FortranError(u.line, 'adjustable array bound must be INTEGER scalar dummy: ' + bound)
                if ty.startswith('CHARACTER*'):
                    raise FortranError(u.line, 'adjustable CHARACTER dummy arrays not yet implemented')
                if u.kind == 'function':
                    raise FortranError(u.line, 'adjustable FUNCTION dummy arrays not yet implemented')
    return units




def parse_dims(spec, name, unit, line):
    """Constant extents or a restricted ANSI F77S numeric dummy extent.

    The checked subset accepts A(N), A(*), A(2,N), A(2,*), and
    A(2,3,N), with fixed leading extents and dynamic final bound only.
    Unsupported dimension expressions fail rather than silently miscompile.
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
    if name not in unit.args or any(not re.fullmatch(r'\d+', v) for v in pieces[:-1]):
        raise FortranError(line, 'adjustable/assumed size only supported for dummy arrays with fixed leading dimensions')
    leading = tuple(int(v) for v in pieces[:-1])
    from .arrays import size as total_extent
    if any(v < 1 or v > 32767 for v in leading) or total_extent(leading) > 32767:
        raise FortranError(line, 'array extent or total size out of bounds')
    value = pieces[-1]
    if value != '*' and (not NAME_RE.fullmatch(value) or value not in unit.args or value == name):
        raise FortranError(line, 'adjustable bound must be a scalar dummy argument: ' + value)
    return leading + (value,)


def dynamic_extent(dims):
    return isinstance(dims, tuple) and len(dims) >= 1 and isinstance(dims[-1], str)


def array_subscript(indices, name, unit, line):
    """Checked column-major offset, honoring the actual caller's capacity."""
    dims = unit.vars[name][1]
    if dynamic_extent(dims):
        if len(indices) != len(dims):
            raise FortranError(line, 'dummy array subscript count must match rank')
        capacity = 'F__LEN_' + name
        stride, terms = 1, []
        for sub, bound in zip(indices[:-1], dims[:-1]):
            part = 'f_index(' + sub + ', ' + str(bound) + ')'
            terms.append('(' + part + ' * ' + str(stride) + ')' if stride != 1 else part)
            stride *= bound
        dynamic_bound = dims[-1]
        limit = capacity if dynamic_bound == '*' else 'f_extent((*F_' + dynamic_bound + '), (' + capacity + ' / ' + str(stride) + '))'
        last = 'f_index(' + indices[-1] + ', ' + limit + ')'
        terms.append('(' + last + ' * ' + str(stride) + ')' if stride != 1 else last)
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
    def __init__(self, text, unit, known_units, line):
        self.unit, self.known, self.line = unit, known_units, line
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
            lhs = '(' + op + self.pratt(6) + ')'
        elif t == '(':
            lhs = '(' + self.pratt(0) + ')'
            if self.pop() != ')':
                raise FortranError(self.line, 'missing closing parenthesis')
        elif t in ('.TRUE.', '.FALSE.'):
            lhs = '1' if t == '.TRUE.' else '0'
        elif re.fullmatch(r'\d+(?:\.\d*)?(?:[ED][+-]?\d+)?|\.\d+(?:[ED][+-]?\d+)?', t):
            lhs = t.replace('D', 'E')
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
                    lhs = 'F_' + t + '[' + array_subscript(params, t, self.unit, self.line) + ']'
                elif t == 'MOD' and len(params) == 2:
                    lhs = '((' + params[0] + ') % (' + params[1] + '))'
                elif t in self.known and self.known[t].kind == 'function':
                    if len(params) != len(self.known[t].args):
                        raise FortranError(self.line, 'wrong number of function arguments: ' + t)
                    target = self.known[t]
                    refs = [reference_actual(arg, self.unit, target.vars[dummy][0])
                            for arg, dummy in zip(params, target.args)]
                    lhs = 'f_' + t + '(' + ', '.join(refs) + ')'
                else:
                    raise FortranError(self.line, 'unknown function: ' + t)
            elif t in self.unit.vars and self.unit.vars[t][1] is None:
                if self.unit.vars[t][0].startswith('CHARACTER*'):
                    raise FortranError(self.line, 'CHARACTER must use character assignment/comparison or A FORMAT')
                lhs = '(*F_' + t + ')' if t in self.unit.args else 'F_' + t
            else:
                raise FortranError(self.line, 'undeclared variable: ' + t)
        else:
            raise FortranError(self.line, 'invalid expression token: ' + t)
        while True:
            op = self.peek()
            prec = PRECEDENCE.get(op, -1)
            if prec < min_prec:
                break
            self.pop()
            rhs = self.pratt(prec if op == '**' else prec + 1)
            if op == '**':
                lhs = 'f_ipow(' + lhs + ', ' + rhs + ')'
            else:
                lhs = '((' + lhs + ') ' + BIN.get(op, op) + ' (' + rhs + '))'
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
/* ANSI F77S formatted INTEGER input (limited Iw/X/slash subset).
   Fields are blank-padded to the end of each input record. */
static int f_fmt_eor;
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
        if (ch == ' ') continue;
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


def convert(units):
    """Build explicit control-flow blocks, then lower them to portable C48.

    The PC dispatcher avoids non-C48 goto/switch and also handles branches
    into and out of nested FORTRAN constructs, including numbered DO loops.
    """
    known = {u.name: u for u in units}
    from .common import layout, bind
    from .equivalence import layout as equivalence_layout
    common_decls, common_uses = layout(units)
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
                    raise FortranError(u.line, 'DATA with storage-associated object not yet supported: ' + var)
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
            if var not in u.args and ('F_' + var) not in aliases:
                from .arrays import size as total_extent
                if ty.startswith('CHARACTER*'):
                    count = total_extent(n) if n is not None else 1
                    decl('char F_' + var + '[' + str(count * (int(ty.split('*')[1]) + 1)) + '];')
                else:
                    decl(ctype(ty) + ' F_' + var + (('[' + str(total_extent(n)) + ']') if n else '') + ';')
        extra_decls = []
        local_decl_index = len(output)
        decl('int f_pc;')
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
        code = []
        labels = {}
        gotos = []
        conditional_gotos = []  # (pc, condition, true_label, false_pc, source_line)
        blocks = []
        formats = {}
        for st in u.statements:
            fm = re.fullmatch(r'FORMAT\s*\((.*)\)', st.text)
            if fm:
                if not st.label:
                    raise FortranError(st.line, 'FORMAT requires a statement label')
                if st.label in formats:
                    raise FortranError(st.line, 'duplicate FORMAT label: ' + st.label)
                formats[st.label] = subset_format(fm.group(1), st.line)
        def add(lines, tail=None):
            code.append((list(lines), tail))
            return len(code) - 1
        def update(n, tail):
            code[n] = (code[n][0], tail)
        def E(text, line):
            return expression(text, u, known, line)
        def ret_stmt():
            return 'return ' + ('0' if is_main else 'F_' + u.name if u.kind == 'function' else '') + ';'
        def stmt(s, line):
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
            fm = re.fullmatch(r'WRITE\s*\(\s*(6|\*)\s*,\s*(\d{1,5})\s*\)\s*(.*)', s)
            if fm:
                _, format_label, arguments = fm.groups()
                format_label = str(int(format_label))
                if format_label not in formats:
                    raise FortranError(line, 'undefined FORMAT label: ' + format_label)
                values = split_items(arguments) if arguments.strip() else []
                operations = []
                pos = 0
                for mode, item in formats[format_label]:
                    if mode == 'literal':
                        operations.append('f_outstr(' + c_string(item) + ');')
                    elif mode == 'space':
                        operations.extend(["putchar(' ');"] * item)
                    elif mode == 'newline':
                        operations.append('putchar(10);')
                    elif mode == 'character':
                        if pos == len(values):
                            raise FortranError(line, 'WRITE has fewer items than FORMAT')
                        name = values[pos].strip()
                        char_value = character_item(name, u, known, line)
                        if not char_value:
                            raise FortranError(line, 'FORMAT A requires CHARACTER scalar/array element')
                        pointer, length = char_value
                        operations.append('f_outcharw(' + pointer + ', ' + str(length) + ', ' + str(item or length) + ');')
                        pos += 1
                    elif mode == 'integer':
                        if pos == len(values):
                            raise FortranError(line, 'WRITE has fewer items than FORMAT')
                        arg = values[pos]
                        if re.search(r'\d+\.\d*', arg) or any(re.search(r'\b' + re.escape(k) + r'\b', arg) for k, v in u.vars.items() if v[0] == 'REAL'):
                            raise FortranError(line, 'FORMAT I requires INTEGER item')
                        operations.append('f_outintw(' + E(arg, line) + ', ' + str(item) + ');')
                        pos += 1
                if pos != len(values):
                    raise FortranError(line, 'WRITE has more items than FORMAT')
                operations.append('putchar(10);')
                add(operations)
                return
            fm = re.fullmatch(r'READ\s*\(\s*(5|\*)\s*,\s*(\d{1,5})\s*\)\s*(.*)', s)
            if fm:
                _, format_label, arguments = fm.groups()
                format_label = str(int(format_label))
                if format_label not in formats:
                    raise FortranError(line, 'undefined FORMAT label: ' + format_label)
                values = split_items(arguments) if arguments.strip() else []
                operations = []
                pos = 0
                for mode, item in formats[format_label]:
                    if mode == 'space':
                        operations.append('f_fmt_skip(' + str(item) + ');')
                    elif mode == 'newline':
                        operations.append('f_fmt_end();')
                    elif mode == 'character':
                        if pos == len(values):
                            raise FortranError(line, 'READ has fewer items than FORMAT')
                        name = values[pos].strip()
                        char_value = character_item(name, u, known, line)
                        if not char_value:
                            raise FortranError(line, 'FORMAT A requires CHARACTER scalar/array element')
                        pointer, length = char_value
                        operations.append('f_fmt_inchar(' + pointer + ', ' + str(length) + ', ' + str(item or length) + ');')
                        pos += 1
                    elif mode == 'integer':
                        if pos == len(values):
                            raise FortranError(line, 'READ has fewer items than FORMAT')
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
                add(operations)
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
                decl('int ' + key + ';')
                add([key + ' = ' + E(selector, line) + ';'])
                for index, label in enumerate(targets, 1):
                    pc = add([])
                    conditional_gotos.append((pc, key + ' == ' + str(index),
                                              str(int(label)), pc + 1, line))
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
                        last_value = None
                        if last_bound is not None and last_bound != '*':
                            bound_pos = known[f].args.index(last_bound)
                            last_value = E(args[bound_pos], line)
                        prefix = total_extent(dims[:-1]) if dynamic_extent(dims) else 1
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
                                if last_bound == '*':
                                    return 'f_seqcheck(0, ' + cap + ', ' + str(prefix) + ');'
                                return 'f_extent(' + last_value + ', (' + cap + ' / ' + str(prefix) + '));'
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
                        # Only writable same-width character variables/elements.
                        item = character_item(actual, u, known, line)
                        if item is None or item[1] != int(ty.split('*')[1]):
                            raise FortranError(line, 'CHARACTER dummy requires same-length CHARACTER scalar actual: ' + actual)
                        refs.append(item[0])
                    else:
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
                decl('int ' + endvar + ';')
                decl('int ' + stepvar + ';')
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
                    decl('float ' + value + ';')
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
            decl(ctype(ty) + ' ' + temp + ';')
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
    return '\n\n'.join(chunks) + '\n'
