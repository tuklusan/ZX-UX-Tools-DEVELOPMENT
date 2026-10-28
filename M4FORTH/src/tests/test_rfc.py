"""rfc test suite: compile Forth with rfc and run the .ssx on ZX-UX via rvm,
asserting the console output; plus negative (compile-error) and unit tests.

Run:  python -m pytest src/tests/test_rfc.py -q
Needs the built ZX-UX system tape at reference/ZX-UX/build/out/ZX-UX.tzx
(rebuild with: python reference/ZX-UX/build/build.py <sjasmplus>)."""
import os
import sys
import subprocess
import tempfile
import pathlib

import pytest

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent                      # .../M4FORTH/src
PROJ = SRC.parent                      # .../M4FORTH
SDK_LOCAL = SRC / 'zx-ux-sdk'
REF_ROOT = pathlib.Path(os.environ.get('ZXUX_REFERENCE_ROOT',
                                       str(PROJ / 'reference' / 'ZX-UX')))
REF_SDK = REF_ROOT / 'src' / 'zx-ux-sdk'
TAPE = REF_ROOT / 'build' / 'out' / 'ZX-UX.tzx'
TMP = pathlib.Path(os.environ.get('TEMP', tempfile.gettempdir()))
os.environ.setdefault('ZXUX_SDK', str(REF_SDK))

sys.path.insert(0, str(SDK_LOCAL))
from rfc import driver                 # noqa: E402

needs_tape = pytest.mark.skipif(not TAPE.exists(),
                                reason='ZX-UX system tape not built (run build/build.py)')


def _compile(src_text, out):
    f = TMP / 'rfc_test_src.fth'
    f.write_text(src_text, encoding='utf-8')
    rc = driver.main([str(f), '-o', str(out)])
    assert rc == 0, 'rfc failed to compile'
    return out


def run_forth(src_text, name='t'):
    """Compile and run on rvm; return the console text (final --text screen)."""
    out = TMP / ('rfc_%s.ssx' % name)
    _compile(src_text, out)
    r = subprocess.run(
        [sys.executable, str(REF_SDK / 'rvm.py'), '--headless', '--text',
         '--frames', '12000', '--system', str(TAPE), str(out)],
        capture_output=True, text=True, timeout=180)
    return r.stdout


# --------------------------------------------------------------------------
# positive: two compact programs whose output fits one screen
# --------------------------------------------------------------------------
PROG_A = """
." arith " 3 4 + . 10 3 - . 6 7 * . -7 2 / . -7 2 mod . cr
." u " 5 negate . -5 abs . 3 8 min . 3 8 max . cr
." stk " 1 2 nip . 1 2 3 rot . 2drop cr
." cmp " 3 4 < . 3 3 = . 5 0> . -1 0< . cr
." log " 12 10 and . 12 10 or . 12 10 xor . cr
." ctl " 5 0> if 111 else 222 then . -5 0> if 1 else 2 then . cr
." lp " 0 11 1 do i + loop . 0 10 0 do i + 2 +loop . cr
." lv " 0 100 0 do i + i 4 = if leave then loop . cr
." bu " 5 begin 1- dup 0= until . cr
bye
"""
EXPECT_A = [
    'arith 7 7 42 -4 1',
    'u -5 5 3 8',
    'stk 2 1',
    'cmp -1 -1 -1 -1',
    'log 8 14 6',
    'ctl 111 2',
    'lp 55 20',
    'lv 10',
    'bu 0',
]


@needs_tape
def test_exit_returns_from_colon_definition():
    out = run_forth(': early 11 exit 22 ; early . cr bye', 'exit')
    assert '11' in out


@needs_tape
def test_user_definition_shadows_builtin_name():
    out = run_forth(': sign dup 0< if ." NEG " else ." NONNEG " then . cr ; '
                    '-5 sign 7 sign bye', 'shadow')
    assert 'NEG -5' in out
    assert 'NONNEG 7' in out


@needs_tape
def test_recurse_compiles_a_real_recursive_definition():
    out = run_forth(': factorial dup 1 > if dup 1- recurse * else drop 1 then ; 6 factorial . cr bye',
                    'recurse')
    assert '720' in out


@needs_tape
def test_case_insensitive_named_static_allocation_and_qdo():
    out = run_forth('64 CONSTANT SIZE CREATE FLAGS SIZE ALLOT '
                    'FLAGS SIZE 65 FILL FLAGS 63 + C@ . CR '
                    '0 0 ?DO 99 . LOOP 42 . CR bye', 'caseqdo')
    assert '65' in out
    assert '42' in out
    assert '99' not in out


@needs_tape
def test_f83_style_static_array_helpers():
    out = run_forth('4 ARRAY A 3 2ARRAY B 42 2 A ! 2 A @ . CR '
                    '11 22 1 B 2! 1 B 2@ . . CR bye', 'arrays')
    assert '42' in out
    assert '22 11' in out


@needs_tape
def test_double_cell_arithmetic_and_comparisons():
    out = run_forth('65535 1 1 2 d+ . . CR 0 4 1 2 d- . . CR '
                    '0 0 d0= . 1 0 d0= . CR 1 2 1 2 d= . 1 2 2 1 d= . CR '
                    '65535 1 0 2 du< . 0 2 65535 1 du< . CR bye', 'double')
    assert '4 0' in out
    assert '1 -1' in out
    assert '-1 0' in out


@needs_tape
def test_portable_calendar_corpus_program():
    source = (SRC / 'assets' / 'forth-src' / 'portable' / 'calendar.fth').read_text(
        encoding='utf-8')
    out = run_forth(source, 'calendar')
    assert 'Thursday, 2024 February 29' in out
    assert 'Tuesday, 1983 April 19' in out
    assert 'Saturday, 2000 January 1' in out


@needs_tape
def test_pforth_benchmark_corpus_program():
    source = (SRC / 'assets' / 'forth-src' / 'portable' / 'pfbench.fth').read_text(
        encoding='utf-8')
    out = run_forth(source, 'pfbench')
    assert 'pForth sum.cells: 1334' in out
    assert 'pForth factorial: 720' in out


@needs_tape
def test_pforth_sieve_corpus_program():
    source = (SRC / 'assets' / 'forth-src' / 'portable' / 'pfsieve.fth').read_text(
        encoding='utf-8')
    out = run_forth(source, 'pfsieve')
    assert 'pForth sieve primes: 308' in out


@needs_tape
def test_f83_huffman_memory_codec_corpus_program():
    source = (SRC / 'assets' / 'forth-src' / 'ported' / 'hufdemo.fth').read_text(
        encoding='utf-8')
    out = run_forth(source, 'hufdemo')
    assert 'F83 Huffman memory codec: BANANA_BANDANA' in out
    assert 'packed bytes: 5' in out


@needs_tape
def test_worms_console_port_starts_and_presents_input_loop():
    source = SRC / 'assets' / 'forth-src' / 'ported' / 'worms.fth'
    out = TMP / 'rfc_worms.ssx'
    _compile(source.read_text(encoding='utf-8'), out)
    run = subprocess.run(
        [sys.executable, str(REF_SDK / 'rvm.py'), '--headless', '--no-cache', '--text',
         '--compat-keys', '--keys', 'd{ENTER}', '--frames', '12000',
         '--system', str(TAPE), str(out)], capture_output=True, text=True, timeout=180)
    assert run.returncode == 0
    assert 'Move with W A S D' in run.stdout
    assert 'Move:' in run.stdout
    assert '. . . O ' in run.stdout

PROG_B = """
." ij " 0 3 0 do 3 0 do i j + + loop loop . cr
variable v
create t 11 , 22 , 33 ,
create b 0 c,
." mem " 42 v ! v @ . 3 v +! v @ . 65 b c! b c@ . cr
." tbl " t @ . t cell+ @ . t 2 cells + @ . cr
." num " 12345 0 <# #s #> type space hex 255 . decimal cr
." fmt [" 42 5 .r ." ]" cr
." dbl " 1000 50 um* <# #s #> type space 10 20 7 */ . cr
." rs " 5 >r 10 r> + . 10 20 30 2 roll . 2drop cr
." ex " 5 ' 1+ execute . char A . cr
create s 65 c, 66 c, 32 c,
." tr [" s 3 -trailing type ." ]" cr
bye
"""
EXPECT_B = [
    'ij 18',
    'mem 42 45 65',
    'tbl 11 22 33',
    'num 12345 FF',
    'fmt [   42]',
    'dbl 50000 28',
    'rs 15 10',
    'ex 6 65',
    'tr [AB]',
]


@needs_tape
def test_program_a():
    out = run_forth(PROG_A, 'a')
    for exp in EXPECT_A:
        assert exp in out, 'missing %r in:\n%s' % (exp, out)


@needs_tape
def test_program_b():
    out = run_forth(PROG_B, 'b')
    for exp in EXPECT_B:
        assert exp in out, 'missing %r in:\n%s' % (exp, out)


# --------------------------------------------------------------------------
# negative: malformed sources must raise ForthError at compile time
# --------------------------------------------------------------------------
NEGATIVE = [
    '1 if 2 .',            # if without then
    ': foo 1 .',           # colon without ;
    'frobnicate',          # unknown word
    '3 then',              # then without if
    '." oops',             # unterminated string
    '5 loop',              # loop without do
    '5 constant',          # constant without name
    'begin 1 repeat',      # repeat without while
    '5 leave',             # leave without do
    '2 +loop',             # +loop without do
    '3 else 4 then',       # else without if
    'char',                # char without a character
    "' nosuchword",        # tick on unknown word
]


@pytest.mark.parametrize('src', NEGATIVE)
def test_negative(src):
    with pytest.raises(driver.ForthError):
        driver.compile_to_asm(src)


# --------------------------------------------------------------------------
# unit: every CFA the compiler emits is defined; number parser sanity
# --------------------------------------------------------------------------
def test_all_cfa_labels_defined():
    import re
    rt = driver.runtime_asm()
    defined = set(re.findall(r'(?m)^([A-Za-z_@][\w@]*):', rt))
    refs = set(driver.BUILTINS.values()) | {
        'docol', 'dovar_c', 'docon_c', 'fw_lit', 'fw_exit', 'fw_dotstr',
        'fw_zbranch', 'fw_branch', 'fw_pdo', 'fw_ploop', 'fw_pplusloop',
        'fw_leave', 'start', 'next'}
    missing = sorted(r for r in refs if r not in defined)
    assert missing == [], 'undefined CFA labels: %s' % missing


@pytest.mark.parametrize('word,expected', [
    ('5', 5), ('-7', -7), ('0', 0), ('32767', 32767),
    ('1_0', None), ('+5', None), ('5x', None), ('-', None), ('', None),
])
def test_number_parser(word, expected):
    assert driver._as_number(word) == expected


def test_f83_screen_blocks_restore_comment_line_endings():
    block = PROJ / 'reference' / 'upstream' / 'forth83-80' / 'clock.blk'
    if not block.exists():
        pytest.skip('F83 source corpus has not been fetched')
    text = driver.source_text(block)
    assert '\\ Months and Days' in text
    assert ('word', 'CLOCK?') in driver.tokenize(text)


def test_rejects_malformed_screen_block(tmp_path):
    block = tmp_path / 'bad.blk'
    block.write_bytes(b'x')
    with pytest.raises(driver.ForthError, match='multiple of 1024'):
        driver.source_text(block)


@pytest.mark.parametrize('name', [
    p.name for p in sorted((SRC / 'assets' / 'forth-src').rglob('*.fth'))
])
def test_examples_compile(name, tmp_path):
    matches = list((SRC / 'assets' / 'forth-src').rglob(name))
    assert len(matches) == 1, 'ambiguous corpus source name: ' + name
    src = matches[0]
    rc = driver.main([str(src), '-S', '-o', str(tmp_path / (name + '.s'))])
    assert rc == 0
