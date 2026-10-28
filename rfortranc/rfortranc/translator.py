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
    vars: dict[str, tuple[str, int | None]] = field(default_factory=dict)


NAME = r'[A-Z][A-Z0-9_]*'
NAME_RE = re.compile(r'^' + NAME + r'$')
UNSUPPORTED = ('COMMON', 'EQUIVALENCE', 'SAVE', 'DATA', 'BLOCK DATA', 'EXTERNAL',
               'INTRINSIC', 'FORMAT', 'OPEN', 'CLOSE', 'REWIND', 'BACKSPACE',
               'ENDFILE', 'ENTRY', 'PAUSE', 'WRITE', 'INQUIRE', 'NAMELIST',
               'CHARACTER', 'COMPLEX', 'DOUBLE PRECISION', 'ASSIGN ', 'ASSIGNED ',
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
    for no, raw in enumerate(source.splitlines(), 1):
        raw = raw.expandtabs(8)
        if not raw.strip():
            continue
        if raw[0] in 'cC*!' and (len(raw) == 1 or raw[1].isspace() or raw[0] in '*!'):
            continue
        fixed = bool(re.match(r'^ {5}[ \d]', raw)) or bool(len(raw) >= 6 and raw[:5].strip().isdigit() and raw[5] == ' ')
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


def parse(source):
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
            m = re.fullmatch(r'(INTEGER|REAL|LOGICAL)\s+(.+)', st.text)
            if not m:
                continue
            ty, rest = m.groups()
            for spec in split_items(rest):
                var = re.fullmatch(r'(' + NAME + r')(?:\s*\(\s*(\d+)\s*\))?', spec)
                if not var:
                    raise FortranError(st.line, 'unsupported declaration: ' + spec)
                name, count = var.groups()
                size = int(count) if count else None
                if size is not None and not 1 <= size <= 32767:
                    raise FortranError(st.line, 'array extent out of bounds')
                if name in u.vars and name not in u.args and name != u.name:
                    raise FortranError(st.line, 'duplicate declaration: ' + name)
                u.vars[name] = (ty, size)
    return units


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
                    if len(params) != 1:
                        raise FortranError(self.line, 'only 1D arrays supported')
                    lhs = 'F_' + t + '[f_index(' + params[0] + ', ' + str(self.unit.vars[t][1]) + ')]'
                elif t == 'MOD' and len(params) == 2:
                    lhs = '((' + params[0] + ') % (' + params[1] + '))'
                elif t in self.known and self.known[t].kind == 'function':
                    if len(params) != len(self.known[t].args):
                        raise FortranError(self.line, 'wrong number of function arguments: ' + t)
                    lhs = 'f_' + t + '(' + ', '.join(params) + ')'
                else:
                    raise FortranError(self.line, 'unknown function: ' + t)
            elif t in self.unit.vars and self.unit.vars[t][1] is None:
                lhs = 'F_' + t
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


RUNTIME = '''#include <c48.h>
/* FORTRAN words are 16-bit on this ZX Spectrum target. */
static int f_index(int n, int size) {
    if (n < 1 || n > size) exit(2);
    return n - 1;
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


def expression(src, unit, units, line):
    return Expr(src, unit, units, line).read()


def c_string(s):
    assert s[0] in "'\"" and s[-1] == s[0]
    chars = s[1:-1].replace(s[0] * 2, s[0])
    return '"' + ''.join(('\\\\' if c == '\\' else '\\"' if c == '"' else
                          '\\n' if c == '\n' else '\\x%02x' % ord(c) if ord(c) < 32
                          else c) for c in chars) + '"'


def convert(units):
    """Build explicit control-flow blocks, then lower them to portable C48.

    The PC dispatcher avoids non-C48 goto/switch and also handles branches
    into and out of nested FORTRAN constructs, including numbered DO loops.
    """
    known = {u.name: u for u in units}
    chunks = [RUNTIME]
    ctype = lambda ty: 'float' if ty == 'REAL' else 'int'
    for u in units:
        if u.kind != 'program':
            ty = 'void' if u.kind == 'subroutine' else ctype(u.type)
            sig = ', '.join(ctype(u.vars[a][0]) + ' F_' + a for a in u.args) or 'void'
            chunks.append(ty + ' f_' + u.name + '(' + sig + ');')
    for u in units:
        is_main = u.kind == 'program'
        ret = 'int' if is_main else 'void' if u.kind == 'subroutine' else ctype(u.type)
        sig = 'void' if is_main or not u.args else ', '.join(ctype(u.vars[a][0]) + ' F_' + a for a in u.args)
        name = 'main' if is_main else 'f_' + u.name
        output = [ret + ' ' + name + '(' + sig + ') {']
        def decl(text):
            output.append('    ' + text)
        for var, (ty, n) in u.vars.items():
            if var not in u.args:
                decl(ctype(ty) + ' F_' + var + (('[' + str(n) + ']') if n else '') + ';')
        decl('int f_pc;')
        if u.kind == 'function':
            decl('F_' + u.name + ' = 0;')
        code = []
        labels = {}
        gotos = []
        blocks = []
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
            if s.startswith(UNSUPPORTED):
                raise FortranError(line, 'unsupported FORTRAN statement: ' + s.split()[0])
            if re.match(r'^(INTEGER|REAL|LOGICAL)\s+', s) or s == 'IMPLICIT NONE':
                return
            if s == 'CONTINUE':
                return
            if s == 'STOP':
                add(['exit(0);'], 'return'); return
            if s == 'RETURN':
                add([ret_stmt()], 'return'); return
            m = re.fullmatch(r'GO\s*TO\s+(\d+)', s)
            if m:
                n = add([]); gotos.append((n, m.group(1), line)); return
            if s.startswith('CALL '):
                m = re.fullmatch(r'CALL\s+(' + NAME + r')\s*\((.*)\)', s)
                if not m or m.group(1) not in known or known[m.group(1)].kind != 'subroutine':
                    raise FortranError(line, 'invalid or unknown SUBROUTINE call')
                f, a = m.groups()
                args = [] if not a.strip() else split_items(a)
                if len(args) != len(known[f].args):
                    raise FortranError(line, 'SUBROUTINE argument count mismatch')
                add(['f_' + f + '(' + ', '.join(E(p, line) for p in args) + ');'])
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
                    if not dest.startswith('F_'):
                        raise FortranError(line, 'READ requires an INTEGER variable')
                    operations.append(dest + ' = f_inint();')
                add(operations); return
            m = re.fullmatch(r'(' + NAME + r'(?:\s*\([^)]*\))?)\s*=\s*(.*)', s)
            if m:
                dest, value = E(m.group(1), line), E(m.group(2), line)
                if not dest.startswith('F_'):
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
                cond = E(s[m.end():i - 1], st.line)
                tail = s[i:].strip()
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
            update(n, ('jump', labels[lab]))
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
        output.append('}')
        chunks.append('\n'.join(output))
    return '\n\n'.join(chunks) + '\n'
