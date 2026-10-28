"""Strict ANSI subset-specific rejections + supported formatted I/O smoke test."""
import sys
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rfortranc.f77s import validate_source
from rfortranc.translator import parse, convert, FortranError

class F77SChecks(unittest.TestCase):
    def check(self, body, accepted):
        def fixed(line):
            m = re.fullmatch(r'\s*(\d+)\s+(.+)', line)
            return (m.group(1).rjust(5) + ' ' + m.group(2)) if m else '      ' + line
        source = '      PROGRAM F77S\n' + '\n'.join(fixed(x) for x in body) + '\n      END\n'
        if accepted:
            units = parse(source)
            validate_source(source, units)
            self.assertIn('int main', convert(units))
        else:
            with self.assertRaises(FortranError):
                units = parse(source)
                validate_source(source, units)
                convert(units)

    def test_fixed_form_formatted_write(self):
        self.check(['INTEGER N','N=42','WRITE(6,10) N','   10 FORMAT(I4)'],True)

    def test_print_is_not_subset(self):
        self.check(["PRINT *, 'HI'"],False)

    def test_list_directed_read_is_not_subset(self):
        self.check(['INTEGER N','READ *, N'],False)

    def test_do_limits_restricted(self):
        self.check(['INTEGER I,N','N=3','DO 10 I=1,N+1','10 CONTINUE'],False)

    def test_computed_goto_constant_not_subset(self):
        self.check(['GO TO (10,20), 2','10 CONTINUE','20 CONTINUE'],False)

    def test_valid_computed_goto(self):
        self.check(['INTEGER I','I=2','GO TO (10,20),I','10 CONTINUE','20 CONTINUE'],True)

    def test_name_length(self):
        self.check(['INTEGER TOOLONG','TOOLONG=1'],False)

    def test_data_array_and_scalar(self):
        source=(ROOT / 'tests/fortran/f77s_data.f').read_text()
        units=parse(source)
        validate_source(source, units)
        c=convert(units)
        self.assertIn('F_A[0] = 1;', c)
        self.assertIn('F_A[2] = 3;', c)
        self.assertIn('F_N = 9;', c)

    def test_data_count_error(self):
        source=(ROOT / 'tests/negative/f77s_data_bad.f').read_text()
        with self.assertRaises(FortranError):
            convert(parse(source))

    def test_free_form_rejected(self):
        src='PROGRAM F77S\nINTEGER I\nEND\n'
        with self.assertRaises(FortranError):
            validate_source(src,parse(src))

    def test_comment_before_continuation(self):
        src='      PROGRAM F77S\n      INTEGER N\nC comment\n     +,I\n      END\n'
        with self.assertRaises(FortranError):
            validate_source(src,parse(src))

    def test_10_continuations_rejected(self):
        src='      PROGRAM F77S\n      INTEGER A\n'+''.join('     +1\n' for _ in range(10))+'      END\n'
        with self.assertRaises(FortranError):
            validate_source(src,parse(src))

if __name__=='__main__': unittest.main()
