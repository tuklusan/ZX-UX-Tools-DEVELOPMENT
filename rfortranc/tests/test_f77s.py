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

    def test_subprogram_data_static_one_time_init(self):
        src=(ROOT/'tests/fortran/f77s_subdata.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('static int f_sd1_N;', c)
        self.assertIn('static int f_sdi1;', c)
        self.assertIn('if (!f_sdi1)', c)
        self.assertIn('f_sd1_N = 40;', c)
        self.assertIn('f_sdi1 = 1;', c)
        self.assertNotIn('int F_N;', c)

    def test_data_count_error(self):
        source=(ROOT / 'tests/negative/f77s_data_bad.f').read_text()
        with self.assertRaises(FortranError):
            convert(parse(source))

    def test_implicit_integer_and_override(self):
        src=(ROOT/'tests/fortran/f77s_implicit.f').read_text()
        units=parse(src, std='f77s')
        validate_source(src, units)
        c=convert(units)
        self.assertIn('int F_A;', c)
        self.assertIn('int F_I;', c)

    def test_implicit_default_real(self):
        src=(ROOT/'tests/fortran/f77s_real.f').read_text()
        units=parse(src, std='f77s')
        validate_source(src, units)
        self.assertIn('float F_A;', convert(units))

    def test_overlap_implicit_letters_rejected(self):
        src='      PROGRAM A\n      IMPLICIT INTEGER(A-H), REAL(G-I)\n      END\n'
        with self.assertRaises(FortranError):
            parse(src, std='f77s')

    def test_public_fcvs_theme_ports(self):
        for name in ('f77s_fc3', 'f77s_fc4', 'f77s_fc5'):
            with self.subTest(name=name):
                src=(ROOT/'tests/fortran'/(name+'.f')).read_text()
                units=parse(src,std='f77s')
                validate_source(src,units)
                self.assertIn('int main',convert(units))

    def test_fixed_dummy_arrays_and_reference_sequence(self):
        for name, part in [('f77s_dmarr', 'F_X[(f_index(3, 6))]'),
                           ('f77s_dmchain', 'f_STEP2(F_A);'),
                           ('f77s_dmreal', 'float *F_X')]:
            with self.subTest(name=name):
                source = (ROOT/'tests/fortran'/(name+'.f')).read_text()
                units = parse(source, std='f77s')
                validate_source(source, units)
                self.assertIn(part, convert(units))

    def test_dummy_array_argument_diagnostics(self):
        for declaration, actual_decl, actual in (
            ('INTEGER X(3)', 'INTEGER A(2)', 'A'),
            ('REAL X(3)', 'INTEGER A(3)', 'A'),
            ('INTEGER X(3)', 'INTEGER A', 'A'),
        ):
            src=('      PROGRAM BAD\n      ' + actual_decl + '\n'
                 + '      CALL SUB(' + actual + ')\n      END\n'
                 + '      SUBROUTINE SUB(X)\n      ' + declaration + '\n'
                 + '      RETURN\n      END\n')
            with self.subTest(declaration=declaration,actual_decl=actual_decl), self.assertRaises(FortranError):
                convert(parse(src, std='f77s'))

    def test_constant_array_element_sequence_actual(self):
        src = (ROOT/'tests/fortran/f77s_dmseq.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        self.assertIn('f_ADDSEQ(&F_A[2]);', convert(units))

    def test_dynamic_array_element_sequence_f77s(self):
        src = (ROOT/'tests/fortran/f77s_dmidx.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_seqcheck(', c)
        self.assertIn('f_ADDSEQ(&F_A[', c)

    def test_element_sequence_too_short_rejected(self):
        src = ('      PROGRAM BAD\n      INTEGER A(5)\n'
               '      CALL SUB(A(4))\n      END\n'
               '      SUBROUTINE SUB(B)\n      INTEGER B(3)\n'
               '      RETURN\n      END\n')
        with self.assertRaisesRegex(FortranError, 'array actual shorter'):
            convert(parse(src, std='f77s'))

    def test_element_sequence_dynamic_subscript_guarded(self):
        src = ('      PROGRAM BAD\n      INTEGER A(5),I\n'
               '      I=3\n      CALL SUB(A(I))\n      END\n'
               '      SUBROUTINE SUB(B)\n      INTEGER B(3)\n'
               '      RETURN\n      END\n')
        self.assertIn('f_seqcheck(', convert(parse(src, std='f77s')))

    def test_implicit_dummy_dimension_kept(self):
        src=('      PROGRAM DIMT\n      REAL A(3)\n      CALL SUB(A)\n'
             '      END\n      SUBROUTINE SUB(X)\n      DIMENSION X(3)\n'
             '      X(1)=3.0\n      RETURN\n      END\n')
        units = parse(src, std='f77s')
        self.assertEqual(units[1].vars['X'], ('REAL', 3))
        self.assertIn('float *F_X', convert(units))

    def test_burkardt_sort_and_binary_search_f77s_port(self):
        source = (ROOT/'tests/fortran/f77s_burksort.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('f_SRTINS(', c)
        self.assertIn('f_BINSRC(', c)
        self.assertIn('f_SRTINS(&(F_N), F_A);', c)
        self.assertIn('f_BINSRC(&(F_N), F_A, &(F_B), &(F_IND));', c)

    def test_burkardt_vector_library_f77s_port(self):
        source = (ROOT/'tests/fortran/f77s_burkvec.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('f_REVERS(', c)
        self.assertIn('f_VECSUM(', c)
        self.assertIn('f_REVERS(&(F_N), F_A);', c)
        self.assertIn('f_VECSUM(&(F_N), F_A, &(F_TOT));', c)

    def test_burkardt_prime_subroutine_f77s_port(self):
        source = (ROOT/'tests/fortran/f77s_burkprime.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('f_PRIMES(', c)
        self.assertIn('f_PRIMES(&(F_N), &(F_TOT));', c)

    def test_character_scalar_formatted_io(self):
        for name in ('f77s_char', 'f77s_charread'):
            with self.subTest(name=name):
                source = (ROOT / 'tests/fortran' / (name + '.f')).read_text()
                units = parse(source, std='f77s')
                validate_source(source, units)
                c = convert(units)
                self.assertIn('char F_A[6];' if name.endswith('read') else 'char F_B[6];', c)
                if name.endswith('read'):
                    self.assertIn('f_fmt_inchar(F_A, 5, 3);', c)
                else:
                    self.assertIn('f_char_cmp(F_B, 5, "HI", 2)', c)
                    self.assertIn('f_outcharw(F_B, 5, 7);', c)

    def test_character_rejects_unsupported_forms(self):
        for body in (
            ['CHARACTER*0 A'],
            ['CHARACTER*256 A'],
            ['CHARACTER*4 A(2)'],
            ['CHARACTER*3 A', "A='H' // 'I'"],
            ['CHARACTER*4 A', "A(1:2)='AB'"],
            ['CHARACTER*5 A', 'INTEGER N', 'N=A+1'],
            ['INTEGER A', 'WRITE(6,10) A', '10 FORMAT(A5)'],
            ['CHARACTER*2 A', 'WRITE(6,10) A', '10 FORMAT(I2)'],
        ):
            with self.subTest(body=body):
                self.check(body, False)

    def test_subset_save_named_common(self):
        source = (ROOT/'tests/fortran/f77s_save.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('static int f_com_FLAG_0;', c)
        self.assertNotIn('F_SAVE', c)
        self.assertNotIn('F_FLAG', c)

    def test_subset_save_rejects_invalid_forms(self):
        bodies = [
            ['INTEGER X', 'SAVE X'],
            ['INTEGER X', 'SAVE'],
            ['INTEGER X', 'SAVE /MISSING/'],
            ['INTEGER X', 'COMMON /YES/ X', 'SAVE /NO/'],
            ['INTEGER X', 'COMMON /YES/ X', 'SAVE /YES/,/YES/'],
        ]
        for body in bodies:
            with self.subTest(body=body):
                self.check(body, False)

    def test_equivalence_transitive_local_storage(self):
        src = (ROOT/'tests/fortran/f77s_equiv.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('int f_eq_0[4];', c)
        self.assertIn('f_eq_0[(f_index(3, 4))] =', c)
        self.assertIn('f_eq_0[1]', c)

    def test_equivalence_rejects_invalid_constraints(self):
        bodies = [
            ['INTEGER A(2),B', 'EQUIVALENCE (A(3),B)'],
            ['INTEGER A(2),B', 'EQUIVALENCE (A(2),B),(A(1),B)'],
            ['INTEGER A', 'REAL B', 'EQUIVALENCE (A,B)'],
            ['INTEGER A,B', 'COMMON /BLK/ A', 'EQUIVALENCE (A,B)'],
        ]
        for body in bodies:
            with self.subTest(body=body):
                self.check(body, False)

    def test_blank_common_positional_storage(self):
        src=(ROOT/'tests/fortran/f77s_blank.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('static int f_com_0_0;', c)
        self.assertIn('f_com_0_0 =', c)

    def test_bad_common_syntax_rejected(self):
        src='      PROGRAM BLNK\n      INTEGER N\n      COMMON /BLK N\n      END\n'
        with self.assertRaises(FortranError):
            convert(parse(src, std='f77s'))

    def test_common_array_rank_compatibility(self):
        src=(ROOT/'tests/fortran/f77s_comarr.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('static int f_com_BLK_0[6];', c)
        self.assertIn('f_com_BLK_0[', c)
        self.assertIn('f_index', c)

    def test_common_array_extent_mismatch(self):
        src="""      PROGRAM CMNT
      INTEGER N(4)
      COMMON /BLK/ N
      END
      SUBROUTINE SUB()
      INTEGER X(5)
      COMMON /BLK/ X
      END
"""
        with self.assertRaises(FortranError):
            convert(parse(src, std='f77s'))

    def test_common_scalar_alias(self):
        src=(ROOT/'tests/fortran/f77s_common.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('static int f_com_BLK_0;', c)
        self.assertIn('f_com_BLK_0 =', c)
        self.assertNotIn('int F_N;', c)
        self.assertNotIn('int F_X;', c)

    def test_common_type_mismatch(self):
        src="""      PROGRAM CMNT\n      INTEGER N\n      COMMON /BLK/ N\n      END\n      SUBROUTINE SUB()\n      REAL X\n      COMMON /BLK/ X\n      END\n"""
        with self.assertRaises(FortranError):
            convert(parse(src, std='f77s'))

    def test_dimension_separate_declaration(self):
        src=(ROOT/'tests/fortran/f77s_dim.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('int F_K[6];', c)
        self.assertIn('f_index(F_I, 2)', c)
        self.assertIn('f_index(F_J, 3)', c)

    def test_dimension_duplicate_rejected(self):
        src='      PROGRAM DIMT\n      INTEGER K(2)\n      DIMENSION K(3)\n      END\n'
        with self.assertRaises(FortranError):
            parse(src,std='f77s')

    def test_dimension_dummy_array_diagnostic(self):
        src='      PROGRAM DIMT\n      CALL SUB(1)\n      END\n' \
            + '      SUBROUTINE SUB(K)\n      DIMENSION K(3)\n      END\n'
        with self.assertRaises(FortranError):
            convert(parse(src,std='f77s'))

    def test_2d_column_major_flattening(self):
        src=(ROOT/'tests/fortran/f77s_2d.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('int F_A[6];',c)
        self.assertIn('f_index(F_I, 2)',c)
        self.assertIn('f_index(F_J, 3)',c)

    def test_3d_column_major_flattening(self):
        src=(ROOT/'tests/fortran/f77s_3d.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('int F_C[8];',c)
        self.assertIn(' * 4)',c)

    def test_4d_decl_rejected(self):
        src='      PROGRAM AR4D\n      INTEGER A(2,2,2,2)\n      END\n'
        with self.assertRaises(FortranError):
            parse(src,std='f77s')

    def test_adjustable_and_assumed_size_dummies(self):
        cases = (
            ('f77s_dmadj', 'f_ADJUST(int *F_N, int *F_B, int F__LEN_B)', 'f_extent((*F_N), (F__LEN_B / 1))'),
            ('f77s_dmstar', 'f_MODIFY(int *F_B, int F__LEN_B)', 'f_index(2, F__LEN_B)'),
            ('f77s_dmalt', 'f_SCLARR(int *F_N, int *F_B, int F__LEN_B)', 'f_extent((*F_N), (F__LEN_B / 1))'),
            ('f77s_burkadj', 'f_REVRSE(int *F_N, int *F_A, int F__LEN_A)', 'f_SUMVEC'),
        )
        for name, signature, body in cases:
            with self.subTest(name=name):
                source = (ROOT/'tests/fortran'/(name+'.f')).read_text()
                units = parse(source, std='f77s')
                validate_source(source, units)
                generated = convert(units)
                self.assertIn(signature, generated)
                self.assertIn(body, generated)
                self.assertIn('f_seqcheck(', generated)

    def test_ranked_adjustable_dummies(self):
        for name, signature, limit in (
            ('f77s_dm2ad', 'f_CHANG2(int *F_N, int *F_B, int F__LEN_B)', '(F__LEN_B / 2)'),
            ('f77s_dm3ad', 'f_CHANG3(int *F_N, int *F_B, int F__LEN_B)', '(F__LEN_B / 4)'),
            ('f77s_dm2st', 'f_CHAST2(int *F_B, int F__LEN_B)', 'f_seqcheck('),
            ('f77s_dm3st', 'f_CHAST3(int *F_B, int F__LEN_B)', 'f_seqcheck('),
        ):
            with self.subTest(name=name):
                source = (ROOT/'tests/fortran'/(name+'.f')).read_text()
                units = parse(source, std='f77s')
                validate_source(source, units)
                c = convert(units)
                self.assertIn(signature, c)
                self.assertIn(limit, c)

    def test_rank3_dynamic_element_sequence(self):
        source = (ROOT/'tests/fortran/f77s_dm3el.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('int F_A[12];', c)
        self.assertIn('f_seqcheck(', c)
        self.assertIn('f_SETSEQ(&F_A[', c)

    def test_burkardt_matrix_multiplication_port(self):
        source = (ROOT/'tests/fortran/f77s_burkmm.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('f_MATMUL(int *F_K, int *F_N, int *F_A, int *F_B, int *F_C, int F__LEN_B, int F__LEN_C)', c)
        self.assertIn('f_seqcheck(', c)

    def test_burkardt_matrix_flip_ports(self):
        src = (ROOT/'tests/fortran/f77s_burkflip.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('f_FLROWS(int *F_N, int *F_A, int F__LEN_A)', generated)
        self.assertIn('f_FLCOLS(int *F_N, int *F_A, int F__LEN_A)', generated)

    def test_ranked_adjustable_bounds_invalid(self):
        cases = ('INTEGER N,A(N,2)', 'INTEGER N,A(2,0,N)', 'INTEGER N,A(2,3,4,N)')
        for decl in cases:
            source=('      PROGRAM MAIN\n      INTEGER A(4)\n'
                    '      CALL ALTER(2,A)\n      END\n'
                    '      SUBROUTINE ALTER(N,A)\n      ' + decl +
                    '\n      RETURN\n      END\n')
            with self.subTest(decl=decl), self.assertRaises(FortranError):
                convert(parse(source, std='f77s'))

    def test_adjustable_bound_rejections(self):
        for declaration, args, declared, expected in (
            ('INTEGER N,A(N,2)', 'N,A', 'INTEGER A(5)', 'fixed leading dimensions'),
            ('INTEGER A(N)', 'A', 'INTEGER A(5)', 'bound must be a scalar dummy'),
            ('INTEGER A(N)', 'N,A', 'INTEGER A(5)', 'INTEGER scalar dummy'),
            ('INTEGER A(0)', 'A', 'INTEGER A(5)', 'out of bounds'),
        ):
            modifier = '      REAL N\n' if expected == 'INTEGER scalar dummy' else ''
            source = ('      PROGRAM MAIN\n      ' + declared + '\n'
                      '      CALL ALTER(' + ('3,A' if args == 'N,A' else 'A') + ')\n'
                      '      END\n      SUBROUTINE ALTER(' + args + ')\n'
                      + modifier + '      ' + declaration + '\n'
                      '      RETURN\n      END\n')
            with self.subTest(declaration=declaration, reason=expected), self.assertRaisesRegex(FortranError, expected):
                convert(parse(source, std='f77s'))

    def test_repeat_group_and_integer_descriptor(self):
        src=(ROOT/'tests/fortran/f77s_repeat.f').read_text()
        units=parse(src, std='f77s')
        validate_source(src, units)
        c=convert(units)
        self.assertEqual(c.count('f_fmt_int(3);'), 3)
        self.assertIn('f_outintw(F_S, 4);', c)

    def test_format_unsupported_or_excess_nesting(self):
        from rfortranc.translator import subset_format
        for fmt in ('I4.2', '3(2(2(I4)))', '256(I3)', '2F8.2'):
            with self.subTest(fmt=fmt), self.assertRaises(FortranError):
                subset_format(fmt, 10)

    def test_formatted_read_two_fields(self):
        src=(ROOT/'tests/fortran/f77s_read.f').read_text()
        units=parse(src, std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('F_N = f_fmt_int(4);', c)
        self.assertIn('f_fmt_skip(1);', c)
        self.assertIn('F_M = f_fmt_int(3);', c)

    def test_formatted_read_rejects_real_target(self):
        self.check(['REAL A','READ(5,10) A','10 FORMAT(I4)'],False)

    def test_formatted_read_rejects_unsupported_literal(self):
        self.check(['INTEGER N','READ(5,10) N',"10 FORMAT('HELLO',I4)"],False)

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
