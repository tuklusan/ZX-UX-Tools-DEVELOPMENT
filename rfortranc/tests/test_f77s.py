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

    def test_underscore_rejected_outside_character_literals(self):
        valid = ('      PROGRAM ABC\n'
                 '      CHARACTER*5 X\n'
                 "      X='A_B'\n"
                 '      END\n')
        units=parse(valid,std='f77s')
        validate_source(valid,units)
        for bad in (valid.replace('PROGRAM ABC','PROGRAM A_B'),
                    valid.replace('CHARACTER*5 X','CHARACTER*5 X_Y'),
                    valid.replace("X='A_B'","X=A_B")):
            with self.subTest(source=bad),self.assertRaisesRegex(FortranError,'underscore'):
                validate_source(bad,units)

    def test_label_digits_with_internal_spaces(self):
        source = '      PROGRAM FIXED\n1 2 3 CONTINUE\n      END\n'
        units = parse(source, std='f77s')
        validate_source(source, units)
        self.assertEqual(units[0].statements[0].label, '123')
        self.assertIn('int main', convert(units))

    def test_fixed_form_tab_is_not_ansi_source(self):
        source = ('      PROGRAM FIXED\n'
                  '      INTEGER N\n'
                  '      N=4\n'
                  '      END\n')
        units = parse(source, std='f77s')
        for bad in (source.replace('      N=4', '\tN=4'),
                    source.replace('      INTEGER N', '      INTE\tGER N')):
            with self.subTest(bad=bad),self.assertRaisesRegex(FortranError, 'tab is not'):
                validate_source(bad, units)

    def test_fixed_form_statement_label_cannot_be_zero(self):
        valid = ('      PROGRAM FIXED\n'
                 '   10 CONTINUE\n'
                 '      END\n')
        units = parse(valid, std='f77s')
        invalid = valid.replace('   10 CONTINUE', '00000 CONTINUE')
        with self.assertRaisesRegex(FortranError, 'statement label must be'):
            validate_source(invalid, units)

    def test_continuation_line_cannot_have_label(self):
        valid = ('      PROGRAM FIXED\n'
                 '      INTEGER N\n'
                 '      N=1+\n'
                 '     1 1\n'
                 '      END\n')
        invalid = valid.replace('     1 1', '   201 1')
        units = parse(valid, std='f77s')
        with self.assertRaisesRegex(FortranError, 'continuation line may not carry'):
            validate_source(invalid, units)

    def test_valid_fixed_form_continuation_without_label(self):
        source = ('      PROGRAM FIXED\n'
                  '      INTEGER N\n'
                  '      N=1+\n'
                  '     1 1\n'
                  '      END\n')
        units = parse(source, std='f77s')
        validate_source(source, units)
        self.assertIn('F_N =', convert(units))

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

    def test_subprogram_data_rank2_static_array(self):
        src=(ROOT/'tests/fortran/f77s_subarr.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('static int f_sd1_A[4];', c)
        self.assertIn('f_sd1_A[3] = 4;', c)
        self.assertIn('if (!f_sdi1)', c)

    def test_local_data_with_common_in_main_and_subprogram(self):
        src = (ROOT/'tests/fortran/f77s_datcom.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('F_LOCAL = 42;', generated)
        self.assertIn('static int f_sd1_TOTAL;', generated)
        self.assertIn('f_sd1_TOTAL = 40;', generated)
        self.assertIn('f_com_BLK_0', generated)

    def test_data_common_member_rejected_without_block_data(self):
        src = ("      PROGRAM BAD\n"
               "      INTEGER N,LOCAL\n"
               "      COMMON /BLK/ N\n"
               "      DATA N/42/\n"
               "      END\n")
        with self.assertRaisesRegex(FortranError, 'DATA cannot initialize COMMON member'):
            convert(parse(src, std='f77s'))

    def test_data_integer_range(self):
        for value in ('32768', '-32769', '100000'):
            src=('      PROGRAM BAD\n      INTEGER N\n'
                 + '      DATA N/' + value + '/\n      END\n')
            with self.subTest(value=value), self.assertRaisesRegex(FortranError, '16-bit range'):
                convert(parse(src,std='f77s'))
        src='      PROGRAM GOOD\n      INTEGER N\n      DATA N/-32768/\n      END\n'
        self.assertIn('F_N = -32768;', convert(parse(src,std='f77s')))

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

    def test_fixed_character_arrays_rank2_and_data(self):
        source = (ROOT/'tests/fortran/f77s_charray.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('char F_A[16];', c)
        self.assertIn('f_char_copy(F_A + 0 * 4, 3, "AB");', c)
        self.assertIn('f_char_copy(F_A + 3 * 4, 3, "Q");', c)
        self.assertIn('f_char_cmp(', c)
        self.assertIn('f_outcharw(', c)
        self.assertIn('f_index(F_I, 2)', c)
        self.assertIn('f_index(F_J, 2)', c)
        self.assertIn('static char f_sd1_T[6];', c)

    def test_logical_l_format_input_output(self):
        source = (ROOT/'tests/fortran/f77s_logio.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('f_outlogw(', generated)
        self.assertIn('f_fmt_logical(', generated)
        self.assertEqual(generated.count('f_fmt_logical(4)'), 2)
        self.assertIn('f_index(1, 2)', generated)

    def test_logical_l_format_rejects_wrong_type(self):
        from rfortranc.translator import subset_format
        with self.assertRaises(FortranError):
            subset_format('L256', 10)
        self.check(['INTEGER I', 'WRITE(6,10) I', '10 FORMAT(L4)'], False)
        self.check(['REAL X', 'READ(5,10) X', '10 FORMAT(L4)'], False)

    def test_real_abs_intrinsic_and_burkardt_l1_norm(self):
        source = (ROOT/'tests/fortran/f77s_burkl1.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('f_abs_real(', generated)
        self.assertIn('f_RVNML1(', generated)
        self.assertIn('f_extent(', generated)
        self.assertIn('f_seqcheck(', generated)

    def test_burkardt_real_dot_product_with_two_adjustable_tails(self):
        source = (ROOT/'tests/fortran/f77s_burkreal.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('f_RVDOTP(', generated)
        self.assertIn('f_extent(', generated)
        self.assertGreaterEqual(generated.count('f_seqcheck('), 2)
        self.assertIn('f_outrealw(', generated)

    def test_burkardt_real_minmax_adjustable_element_tail(self):
        source = (ROOT/'tests/fortran/f77s_burkmin.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('f_RVSMIN(', generated)
        self.assertIn('f_RVSMAX(', generated)
        self.assertIn('f_extent(', generated)
        self.assertIn('f_seqcheck(', generated)
        self.assertIn('f_outrealw(', generated)

    def test_burkardt_real_adjustable_mean_port(self):
        src = (ROOT/'tests/fortran/f77s_burkmean.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_RVMEAN(', c)
        self.assertIn('f_extent(', c)
        self.assertIn('f_outrealw(', c)
        self.assertIn('f_seqcheck(', c)

    def test_formatted_real_input_output_fields(self):
        src = (ROOT/'tests/fortran/f77s_realio.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_outrealw(F_A, 8, 2);', c)
        self.assertIn('F_B = f_fmt_real(8, 2);', c)
        self.assertEqual(c.count(' = f_fmt_real(8, 2);'), 2)
        self.assertIn('f_outrealw(F_C[', c)
        self.assertEqual(c.count('f_outrealw('), 6)

    def test_real_format_type_diagnostics(self):
        src = ('      PROGRAM BAD\n      INTEGER I\n'
               '      I=2\n      WRITE(6,10) I\n'
               '   10 FORMAT(F8.2)\n      END\n')
        with self.assertRaisesRegex(FortranError, 'REAL variable/element'):
            convert(parse(src, std='f77s'))

    def test_formatted_character_array_element_read(self):
        src = (ROOT/'tests/fortran/f77s_arrread.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        code = convert(units)
        self.assertIn('f_fmt_inchar((F_A +', code)
        self.assertIn('f_outcharw((F_A +', code)

    def test_rank3_character_column_major_storage(self):
        src = (ROOT/'tests/fortran/f77s_chr3d.f').read_text()
        c = convert(parse(src, std='f77s'))
        self.assertIn('char F_A[24];', c)
        self.assertIn('f_char_copy(F_A + 7 * 3, 2, "HH");', c)
        self.assertIn('f_index(F_K, 2)', c)

    def test_character_array_dummy_sequence_and_element_actual(self):
        src = (ROOT/'tests/fortran/f77s_chdummy.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        code = convert(units)
        self.assertIn('void f_CHPASS(char *F_B);', code)
        self.assertIn('f_seqcheck(', code)
        self.assertIn('void f_CHMOVE(char *F_B);', code)
        self.assertIn('f_CHSET((F_A + (', code)

    def test_character_array_byte_extent_overflow_rejected(self):
        src = ('      PROGRAM OVER\n'
               '      CHARACTER*255 A(200)\n'
               '      END\n')
        with self.assertRaisesRegex(FortranError, 'CHARACTER array byte extent'):
            parse(src, std='f77s')

    def test_adjustable_character_dummy_rejected(self):
        src = ("      PROGRAM MAIN\n      CHARACTER*3 A(5)\n"
               "      CALL ALTER(5,A)\n      END\n"
               "      SUBROUTINE ALTER(N,A)\n"
               "      INTEGER N\n      CHARACTER*3 A(N)\n"
               "      A(1)='HI'\n      END\n")
        with self.assertRaisesRegex(FortranError, 'adjustable CHARACTER dummy arrays'):
            convert(parse(src, std='f77s'))

    def test_character_dummy_array_short_tail_rejected(self):
        src = (ROOT/'tests/fortran/f77s_chdummy.f').read_text()
        src = src.replace('      I=2', '      I=3')
        self.assertIn('f_seqcheck(', convert(parse(src, std='f77s')))
        src = src.replace('      I=3', '      I=4')
        self.assertIn('f_seqcheck(', convert(parse(src, std='f77s')))
        src = src.replace('      CALL CHPASS(A(I))', '      CALL CHPASS(A(3))')
        with self.assertRaises(FortranError):
            convert(parse(src, std='f77s'))

    def test_character_rejects_unsupported_forms(self):
        for body in (
            ['CHARACTER*0 A'],
            ['CHARACTER*256 A'],
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

    def test_character_equivalence_total_storage_association(self):
        src = (ROOT/'tests/fortran/f77s_chequiv.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('char f_eq_0[12];', generated)
        self.assertIn('(f_eq_0 + 4)', generated)
        self.assertIn('(f_eq_0 + 8)', generated)

    def test_character_equivalence_requires_equal_element_length(self):
        invalid = ("      PROGRAM BAD\n"
                   "      CHARACTER*3 A\n"
                   "      CHARACTER*4 B\n"
                   "      EQUIVALENCE (A,B)\n"
                   "      END\n")
        with self.assertRaisesRegex(FortranError, 'mixed-type EQUIVALENCE'):
            convert(parse(invalid, std='f77s'))

    def test_subprogram_data_in_equivalence_static_lifetime(self):
        for fixture in ('f77s_eqdata', 'f77s_eqchdat'):
            source = (ROOT/'tests/fortran'/(fixture+'.f')).read_text()
            with self.subTest(fixture=fixture):
                units = parse(source, std='f77s')
                validate_source(source, units)
                c = convert(units)
                self.assertIn('if (!f_sdi1)', c)
                self.assertIn('f_e1_0', c)
                self.assertIn('static ' + ('int' if fixture == 'f77s_eqdata' else 'char') + ' f_e1_0', c)
                self.assertNotIn('    int f_eq_0[2];', c)

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
            ('f77s_dmadj', 'f_ADJUST(int *F_N, int *F_B, int F__LEN_B)', 'f_extent((*F_N), (F__LEN_B / (1)))'),
            ('f77s_dmstar', 'f_MODIFY(int *F_B, int F__LEN_B)', 'f_index(2, (F__LEN_B / (1)))'),
            ('f77s_dmalt', 'f_SCLARR(int *F_N, int *F_B, int F__LEN_B)', 'f_extent((*F_N), (F__LEN_B / (1)))'),
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
            ('f77s_dm2ad', 'f_CHANG2(int *F_N, int *F_B, int F__LEN_B)', 'F__LEN_B / ((1 * (2)))'),
            ('f77s_dm3ad', 'f_CHANG3(int *F_N, int *F_B, int F__LEN_B)', 'F__LEN_B / (((1 * (2)) * (2)))'),
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

    def test_burkardt_cumulative_min_max_port(self):
        source=(ROOT/'tests/fortran/f77s_burkcum.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        c=convert(units)
        self.assertIn('f_CUMVEC(',c)
        self.assertIn('f_MINVEC(',c)
        self.assertIn('f_MAXVEC(',c)
        self.assertIn('f_extent(',c)
        self.assertIn('f_seqcheck(',c)

    def test_burkardt_dot_product_adjustable_element_sequences(self):
        source=(ROOT/'tests/fortran/f77s_burkdot.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        generated=convert(units)
        self.assertIn('f_DOTVEC(',generated)
        self.assertIn('f_seqcheck(',generated)
        self.assertIn('f_extent(',generated)
        self.assertIn('f_idx_',generated)

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

    def test_adjustable_leading_dimensions_and_assumed_size(self):
        for fixture, dims in (('f77s_leaddim',( 'N', 3)),
                              ('f77s_ldstar', ('N', '*')),
                              ('f77s_ld3star', ('N', 2, '*'))):
            with self.subTest(fixture=fixture):
                src=(ROOT/'tests/fortran'/(fixture+'.f')).read_text()
                units=parse(src,std='f77s')
                validate_source(src,units)
                self.assertEqual(units[1].vars['B'][1], dims)
                lowered=convert(units)
                self.assertIn('f_extent((*F_N)', lowered)
                self.assertIn('F__LEN_B', lowered)
                self.assertIn('f_seqcheck(', lowered)

    def test_common_scalar_bound_on_ranked_dummy(self):
        src=(ROOT/'tests/fortran/f77s_cbound.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        self.assertEqual(units[1].vars['B'][1], ('N',3))
        c=convert(units)
        self.assertIn('f_extent(f_com_SIZE_0,',c)
        self.assertIn('F__LEN_B',c)
        separate=convert(units,emit_units={'ALTER'})
        self.assertIn('extern int f_com_SIZE_0;',separate)
        self.assertIn('f_seqcheck(0, F__LEN_B,', separate)
        bad=src.replace('INTEGER N,B(N,3),X','REAL N\n      INTEGER B(N,3),X')
        with self.assertRaisesRegex(FortranError,'INTEGER scalar dummy or COMMON'):
            convert(parse(bad,std='f77s'))

    def test_adjustable_leading_bound_wrong_type_rejected(self):
        src=(ROOT/'tests/fortran/f77s_leaddim.f').read_text()
        src=src.replace('INTEGER N,B(N,3),X','REAL N\n      INTEGER B(N,3),X')
        with self.assertRaisesRegex(FortranError,'INTEGER scalar dummy'):
            convert(parse(src,std='f77s'))

    def test_ranked_adjustable_bounds_invalid(self):
        cases = ('INTEGER N,A(N+1,2)', 'INTEGER N,A(2,0,N)', 'INTEGER N,A(2,3,4,N)')
        for decl in cases:
            source=('      PROGRAM MAIN\n      INTEGER A(4)\n'
                    '      CALL ALTER(2,A)\n      END\n'
                    '      SUBROUTINE ALTER(N,A)\n      ' + decl +
                    '\n      RETURN\n      END\n')
            with self.subTest(decl=decl), self.assertRaises(FortranError):
                convert(parse(source, std='f77s'))

    def test_adjustable_bound_rejections(self):
        for declaration, args, declared, expected in (
            ('INTEGER N,A(N+1,2)', 'N,A', 'INTEGER A(5)', 'adjustable bound must be'),
            ('INTEGER A(N)', 'A', 'INTEGER A(5)', 'adjustable bound must be a scalar dummy'),
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

    def test_six_decimal_f_format_input_output(self):
        source = (ROOT/'tests/fortran/f77s_f6.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        c = convert(units)
        self.assertIn('int digs[7];', c)
        self.assertIn('f_outrealw(F_A, 12, 6);', c)
        self.assertIn('F_A = f_fmt_real(12, 6);', c)
        with self.assertRaises(FortranError):
            from rfortranc.translator import subset_format
            subset_format('F12.7', 2)

    def test_format_unsupported_or_excess_nesting(self):
        from rfortranc.translator import subset_format
        for fmt in ('I4.2', '3(2(2(I4)))', '256(I3)', 'F8.7'):
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

    def test_rank2_dynamic_element_sequence(self):
        source = (ROOT/'tests/fortran/f77s_dm2el.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('int F_A[6];', generated)
        self.assertIn('f_SETSEQ(&F_A[', generated)
        self.assertIn('f_seqcheck(', generated)
        self.assertIn('f_index(F_I, 2)', generated)
        self.assertIn('f_index(F_J, 3)', generated)

    def test_burkardt_adjustable_gcd_array_port(self):
        source = (ROOT/'tests/fortran/f77s_burkgcd.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('f_GCDARR(', generated)
        self.assertIn('f_GCDVAL(', generated)
        self.assertIn('f_extent(', generated)
        self.assertIn('f_seqcheck(', generated)

    def test_character_data_storage_and_lifetime(self):
        source = (ROOT/'tests/fortran/f77s_chdata.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('f_char_copy(F_A, 5, "A/B");', generated)
        self.assertIn('static char f_sd1_S[4];', generated)
        self.assertIn('f_char_copy(f_sd1_S, 3, "AB");', generated)
        self.assertIn('if (!f_sdi1)', generated)

    def test_character_data_quote_and_slash(self):
        source = "      PROGRAM QCHAR\n      CHARACTER*5 A\n      DATA A/'A''/B'/\n      END\n"
        generated = convert(parse(source, std='f77s'))
        self.assertIn('f_char_copy(F_A, 5, "A\'/B");', generated)

    def test_character_data_wrong_type_rejected(self):
        source = ('      PROGRAM BAD\n      CHARACTER*3 A\n'
                  '      DATA A/123/\n      END\n')
        with self.assertRaises(FortranError):
            convert(parse(source, std='f77s'))

    def test_implicit_character_data(self):
        source = (ROOT/'tests/fortran/f77s_imchar.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        self.assertEqual(units[0].vars['C'], ('CHARACTER*5', None))
        generated = convert(units)
        self.assertIn('char F_C[6];', generated)
        self.assertIn('f_char_copy(F_C, 5, "A/B");', generated)

    def test_mixed_implicit_character_and_integer_ranges(self):
        source = ("      PROGRAM MIXED\n"
                  "      IMPLICIT CHARACTER*2 (A-B), INTEGER (C-D)\n"
                  "      A='HELLO'\n      C=42\n"
                  "      WRITE(6,10) A\n      WRITE(6,20) C\n"
                  "   10 FORMAT(A2)\n   20 FORMAT(I4)\n      END\n")
        units = parse(source, std='f77s')
        self.assertEqual(units[0].vars['A'], ('CHARACTER*2', None))
        self.assertEqual(units[0].vars['C'], ('INTEGER', None))
        self.assertIn('f_char_copy(F_A, 2, "HELLO");', convert(units))

    def test_implicit_character_bad_width(self):
        for width in (0, 256):
            source = ('      PROGRAM BAD\n      IMPLICIT CHARACTER*'
                      + str(width) + ' (C)\n      C=\'AB\'\n      END\n')
            with self.subTest(width=width), self.assertRaises(FortranError):
                convert(parse(source, std='f77s'))

    def test_character_scalar_dummy_by_reference(self):
        source = (ROOT/'tests/fortran/f77s_charg.f').read_text()
        units = parse(source, std='f77s')
        validate_source(source, units)
        generated = convert(units)
        self.assertIn('void f_CHPASS(char *F_C);', generated)
        self.assertIn('void f_CHSET(char *F_C);', generated)
        self.assertIn('f_CHPASS(F_A);', generated)
        self.assertIn('f_CHSET(F_C);', generated)
        self.assertIn('f_char_copy(F_C, 5, "HI");', generated)

    def test_character_scalar_dummy_mismatched_length_rejected(self):
        source = ("      PROGRAM BAD\n"
                  "      CHARACTER*3 A\n"
                  "      CALL CHSET(A)\n"
                  "      END\n"
                  "      SUBROUTINE CHSET(C)\n"
                  "      CHARACTER*5 C\n"
                  "      C='HI'\n"
                  "      END\n")
        with self.assertRaisesRegex(FortranError, 'CHARACTER dummy requires same-length'):
            convert(parse(source, std='f77s'))

    def test_character_constant_actual_readonly(self):
        src = (ROOT/'tests/fortran/f77s_chlit.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('f_SHOWN("HELLO")', generated)
        self.assertIn('f_outcharw(F_S, 5, 5)', generated)

    def test_character_dummy_non_variable_rejected(self):
        source = ("      PROGRAM BAD\n"
                  "      CALL CHSET('ABCDE')\n"
                  "      END\n"
                  "      SUBROUTINE CHSET(C)\n"
                  "      CHARACTER*5 C\n"
                  "      C='HI'\n"
                  "      END\n")
        with self.assertRaisesRegex(FortranError, 'CHARACTER constant actual cannot bind writable dummy'):
            convert(parse(source, std='f77s'))

    def test_burkardt_real_variance_sample_and_tails(self):
        src = (ROOT/'tests/fortran/f77s_burkvar.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_RVVARI(', c)
        self.assertIn('f_extent(', c)
        self.assertIn('f_seqcheck(', c)
        self.assertIn('f_outrealw(', c)

    def test_burkardt_real_scale_writes_to_adjustable_dummy(self):
        src = (ROOT/'tests/fortran/f77s_burkscale.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_RVSCL(', c)
        self.assertIn('F_A[f_seqcheck(', c)
        self.assertIn('f_extent(', c)
        self.assertIn('f_outrealw(', c)

    def test_real_sqrt_and_burkardt_l2_norm(self):
        src = (ROOT/'tests/fortran/f77s_burkl2.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('f_sqrt_real(', generated)
        self.assertIn('f_RVNML2(', generated)
        self.assertIn('return sqrt(x);', generated)
        self.assertIn('if (x < 0.0) exit(2);', generated)
        self.assertIn('f_seqcheck(', generated)

    def test_burkardt_real_copy_and_sort_with_adjustable_aliases(self):
        for name, entry in [('f77s_burkcopy.f','f_RVCOPY('),
                            ('f77s_burkrsrt.f','f_RVSORT(')]:
            src = (ROOT/'tests/fortran'/name).read_text()
            units = parse(src, std='f77s')
            validate_source(src, units)
            generated = convert(units)
            self.assertIn(entry, generated)
            self.assertIn('f_seqcheck(', generated)
            self.assertIn('f_extent(', generated)

    def test_cross_unit_scalar_type_mismatch_rejected(self):
        folder = ROOT/'tests/fortran/separate'
        main = (folder/'main.f').read_text()
        main = main.replace('INTEGER N', 'REAL N').replace('FORMAT(I4)', 'FORMAT(F7.2)')
        src = main + (folder/'step.f').read_text()
        with self.assertRaisesRegex(FortranError, 'scalar argument type mismatch'):
            convert(parse(src, std='f77s'))

    def test_separate_objects_preserve_external_abi(self):
        folder = ROOT/'tests/fortran/separate'
        src = (folder/'main.f').read_text()+(folder/'step.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        main_c = convert(units, emit_units={'SEPM'})
        sub_c = convert(units, emit_units={'STEPER'})
        self.assertIn('int main(void) {', main_c)
        self.assertNotIn('void f_STEPER(int *F_N) {', main_c)
        self.assertIn('void f_STEPER(int *F_N);', main_c)
        self.assertNotIn('int main(void) {', sub_c)
        self.assertIn('void f_STEPER(int *F_N) {', sub_c)

    def test_assigned_format_identifiers(self):
        src = (ROOT/'tests/fortran/f77s_afmt.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('if (F_K == 10)', c)
        self.assertIn('if (F_K == 20)', c)
        self.assertIn('f_outintw(F_X, 4);', c)
        self.assertIn('f_outintw(F_X, 6);', c)
        bad = ('      PROGRAM BAD\n      INTEGER K,X\n'
               '      ASSIGN 10 TO K\n      WRITE(6,K) X\n'
               '   10 CONTINUE\n      END\n')
        with self.assertRaisesRegex(FortranError, 'no assigned FORMAT label'):
            convert(parse(bad, std='f77s'))

    def test_unprefixed_function_implicit_result_type(self):
        src = (ROOT/'tests/fortran/f77s_barefn.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        self.assertEqual(units[1].type, 'REAL')
        generated = convert(units)
        self.assertIn('float f_SQUARE(float *F_X)', generated)
        self.assertIn('F_Y = f_SQUARE(', generated)

    def test_unprefixed_function_integer_result(self):
        src = ('      PROGRAM GOOD\n      INTEGER K\n'
               '      K=INCR(3)\n      END\n'
               '      FUNCTION INCR(I)\n      INTEGER I\n'
               '      INCR=I+1\n      END\n')
        units = parse(src, std='f77s')
        self.assertEqual(units[1].type, 'INTEGER')
        self.assertIn('int f_INCR(int *F_I)', convert(units))

    def test_character_constant_format_identifier(self):
        src = (ROOT/'tests/fortran/f77s_fmtch.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('f_outintw(F_N, 5);', generated)
        bad = "      PROGRAM BAD\n      INTEGER N\n      WRITE(6,'BAD') N\n      END\n"
        with self.assertRaisesRegex(FortranError, 'parenthesized format'):
            convert(parse(bad, std='f77s'))

    def test_blank_control_bn_bz(self):
        src = (ROOT/'tests/fortran/f77s_bnbz.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('f_fmt_bzero = 1;', generated)
        self.assertIn('f_fmt_bzero = 0;', generated)
        self.assertIn('static int f_fmt_bzero;', generated)

    def test_exponential_formatted_input(self):
        src = (ROOT/'tests/fortran/f77s_eread.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('F_A = f_fmt_ereal(16, 6);', generated)
        self.assertIn('F_B = f_fmt_ereal(16, 6);', generated)
        self.assertIn('static float f_fmt_ereal(int width, int places)', generated)

    def test_explicit_e_exponent_width(self):
        src = (ROOT/'tests/fortran/f77s_ewdee.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('f_outexpw(F_A, 16, 6, 3);', generated)
        self.assertIn('f_outexpw(F_B, 16, 6, 3);', generated)
        self.assertIn('f_outexpw(F_C, 16, 6, 3);', generated)
        for fmt in ('E8.6E3', 'E14.7E3', 'E300.3E3', 'E14.3E5'):
            bad = ('      PROGRAM BAD\n      REAL X\n'
                   '      WRITE(6,10) X\n   10 FORMAT('+fmt+')\n      END\n')
            with self.subTest(fmt=fmt), self.assertRaises(FortranError):
                convert(parse(bad, std='f77s'))

    def test_e_output_descriptor_and_strict_size_errors(self):
        src = (ROOT/'tests/fortran/f77s_expout.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_outexp(F_A, 14, 6);', c)
        self.assertIn('f_outexp(F_B, 14, 6);', c)
        for fmt in ('E5.6', 'E14.7', 'E300.6'):
            bad = ("      PROGRAM BAD\n"
                   "      REAL X\n"
                   "      WRITE (6,10) X\n"
                   "   10 FORMAT(" + fmt + ")\n"
                   "      END\n")
            with self.subTest(fmt=fmt):
                with self.assertRaisesRegex(FortranError, 'E field'):
                    convert(parse(bad, std='f77s'))

    def test_data_initialization_preceded_by_all_declarations(self):
        src = (ROOT/'tests/fortran/f77s_datado.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        data_pos = generated.index('F_A[0] = 3;')
        for declaration in ('int f_end_', 'int f_step_',
                            'int f_select_', 'float f_arth_'):
            self.assertIn(declaration, generated)
            self.assertLess(generated.index(declaration), data_pos)

    def test_real_specific_intrinsics_lowering_and_size_gating(self):
        src = (ROOT/'tests/fortran/f77s_trig.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        for name in ('sin', 'cos', 'exp', 'log'):
            self.assertIn('static float f_' + name + '_real(', generated)
        self.assertIn('if (x <= 0.0) exit(2);', generated)
        integer_source = "      PROGRAM NOP\n      INTEGER N\n      N=2\n      END\n"
        integer_c = convert(parse(integer_source, std='f77s'))
        for name in ('sin', 'cos', 'exp', 'log'):
            self.assertNotIn('static float f_' + name + '_real(', integer_c)

    def test_specific_maxmin_types_and_multiargument(self):
        source=(ROOT/'tests/fortran/f77s_maxmin.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        c=convert(units)
        for method in ('f_max0','f_min0','f_amax1','f_amin1'):
            self.assertIn('static ',c)
            self.assertIn(method+'(',c)
        for name in ('MAX0','MIN0','AMAX1','AMIN1','AMAX0','AMIN0','MAX1','MIN1'):
            for bad in (name+'(1)', name+'(1,2.5)', name+'(.TRUE.,.FALSE.)'):
                s='      PROGRAM BAD\n      REAL R\n      R='+bad+'\n      END\n'
                with self.subTest(expression=bad),self.assertRaises(FortranError):
                    convert(parse(s,std='f77s'))

    def test_sign_and_dim_specific_typing(self):
        src=(ROOT/'tests/fortran/f77s_sigdim.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        for name in ('f_isign','f_sign','f_idim','f_dim'):
            self.assertIn(name+'(',c)
        for bad_call in ('ISIGN(2.0,1)', 'SIGN(2,1.0)',
                         'IDIM(1,2.0)', 'DIM(1.0,1)', 'ISIGN(1)'):
            bad='      PROGRAM BAD\n      REAL X\n      X='+bad_call+'\n      END\n'
            with self.subTest(bad_call=bad_call),self.assertRaises(FortranError):
                convert(parse(bad,std='f77s'))

    def test_f77s_specific_hyperbolic_and_rounding_intrinsics(self):
        source=(ROOT/'tests/fortran/f77s_hyper.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        generated=convert(units)
        for helper in ('f_sinh_real(', 'f_cosh_real(', 'f_tanh_real(',
                       'f_nint_real(', 'f_log_real('):
            self.assertIn(helper,generated)
        self.assertIn('positive = f_exp_real(x);',generated)
        self.assertIn('negative = f_exp_real(-x);',generated)
        for expr in ('SINH(1)', 'COSH(1)', 'TANH(1)', 'ANINT(1)',
                     'ALOG(1)', 'REAL(.TRUE.)', 'COSH(1.0,2.0)'):
            with self.subTest(expr=expr),self.assertRaises(FortranError):
                convert(parse('      PROGRAM BAD\n      REAL R\n'
                              '      R='+expr+'\n      END\n',std='f77s'))

    def test_two_argument_real_specific_intrinsics(self):
        src=(ROOT/'tests/fortran/f77s_rmath.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('static float f_atan2_real(float y, float x)',c)
        self.assertIn('static float f_amod_real(float x, float y)',c)
        for expr in ('ATAN2(1,1.0)','ATAN2(1.0,2)','ATAN2(1.0)',
                     'AMOD(1.0,2)','AMOD(1.0)','AMOD(1.0,2.0,3.0)'):
            bad='      PROGRAM BAD\n      REAL X\n      X='+expr+'\n      END\n'
            with self.subTest(expr=expr),self.assertRaises(FortranError):
                convert(parse(bad,std='f77s'))

    def test_target_math_real_specific_and_domain_checks(self):
        src = (ROOT/'tests/fortran/f77s_invtrig.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        for name in ('asin', 'acos', 'atan', 'tan', 'alog10'):
            self.assertIn('static float f_' + name + '_real(', generated)
        self.assertIn('return asin(x);', generated)
        self.assertIn('return acos(x);', generated)
        self.assertIn('return atan(x);', generated)
        self.assertIn('return tan(x);', generated)
        self.assertIn('return log(x) * 0.4342944819;', generated)
        for intrinsic in ('ASIN','ACOS','ATAN','TAN','ALOG10'):
            for expression in (intrinsic+'(1)', intrinsic+'(.TRUE.)',intrinsic+'(1.0,2.0)'):
                bad='      PROGRAM BAD\n      REAL R\n      R='+expression+'\n      END\n'
                with self.subTest(expression=expression), self.assertRaises(FortranError):
                    convert(parse(bad, std='f77s'))

    def test_real_specific_intrinsics_wrong_arity(self):
        for func in ('SIN', 'COS', 'EXP', 'LOG'):
            for arguments in ('', '1.0,2.0'):
                source = ('      PROGRAM BAD\n'
                          '      REAL X\n'
                          '      X=' + func + '(' + arguments + ')\n'
                          '      END\n')
                with self.subTest(function=func, arguments=arguments):
                    with self.assertRaises(FortranError):
                        convert(parse(source, std='f77s'))

    def test_statement_function_local_scope_and_nesting(self):
        src = (ROOT/'tests/fortran/f77s_stfn.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        output = convert(units)
        self.assertNotIn('F_F =', output)
        self.assertNotIn('F_G =', output)
        self.assertIn('F_B = ', output)
        self.assertIn('F_A', output)

    def test_statement_function_order_and_arity_diagnostics(self):
        invalid = [
            ['REAL F,X', 'F(T)=T+1.0', 'X=F(1.0,2.0)'],
            ['REAL F,X', 'X=1.0', 'F(T)=T+1.0'],
            ['REAL F,X', 'DATA X/1.0/', 'F(T)=T+1.0'],
            ['REAL F,X', 'F(T)=T+1.0', 'REAL Y'],
            ['REAL F,X', 'F(T)=F(T)+1.0', 'X=F(2.0)'],
        ]
        for body in invalid:
            with self.subTest(body=body):
                src = '      PROGRAM BAD\n' + ''.join('      '+line+'\n' for line in body) + '      END\n'
                with self.assertRaises(FortranError):
                    convert(parse(src, std='f77s'))

    def test_real_power_typed_and_right_associative(self):
        src = (ROOT/'tests/fortran/f77s_rpow.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        output = convert(units)
        self.assertIn('f_ripow_real(', output)
        self.assertIn('f_rpow_real(', output)
        self.assertIn('f_ipow(3, 2)', output)
        self.assertIn('f_exp_real(', output)
        self.assertIn('f_log_real(', output)

    def test_assigned_goto_and_assign_label_validation(self):
        src = (ROOT/'tests/fortran/f77s_assgn.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        output = convert(units)
        self.assertIn('F_K = 30;', output)
        self.assertIn('F_K == 20', output)
        self.assertIn('F_K == 30', output)
        for body in [
            ['INTEGER K', 'ASSIGN 100 TO K'],
            ['REAL K', 'ASSIGN 10 TO K', '10 CONTINUE'],
            ['REAL K', 'GO TO K, (10)', '10 CONTINUE'],
            ['INTEGER K', 'GO TO K'],
            ['INTEGER K', 'ASSIGN 10 TO K', 'GO TO K, (20)', '10 CONTINUE'],
        ]:
            with self.subTest(body=body):
                source = '      PROGRAM BAD\n' + ''.join('      '+line+'\n' for line in body) + '      END\n'
                with self.assertRaises(FortranError):
                    convert(parse(source, std='f77s'))

    def test_fixed_implied_do_and_whole_array_io(self):
        src = (ROOT/'tests/fortran/f77s_iodo.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_outintw(F_A[(f_index(1, 3))], 4);', c)
        self.assertIn('f_outintw(F_A[(f_index(3, 3))], 4);', c)
        self.assertIn('F_I = 4;', c)

    def test_implied_do_formatted_read(self):
        src = (ROOT/'tests/fortran/f77s_iord.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        generated = convert(units)
        self.assertIn('F_A[(f_index(1, 3))] = f_fmt_int(3);', generated)
        self.assertIn('F_A[(f_index(3, 3))] = f_fmt_int(3);', generated)
        self.assertIn('F_I = 4;', generated)

    def test_runtime_implied_do_real_logical_character_e_formats(self):
        cases = [('f77s_varreal', 'f_fmt_real(', 'f_outrealw('),
                 ('f77s_varlc', 'f_fmt_logical(', 'f_outcharw('),
                 ('f77s_varexp', 'f_fmt_ereal(', 'f_outexpw(')]
        for filename, reader, writer in cases:
            source=(ROOT/'tests/fortran'/(filename+'.f')).read_text()
            with self.subTest(filename=filename):
                units=parse(source,std='f77s')
                validate_source(source,units)
                c=convert(units)
                self.assertIn(reader,c)
                self.assertIn(writer,c)
                self.assertIn('f_add_checked(',c)
        bad=('      PROGRAM BAD\n      REAL A(3)\n      INTEGER I,N\n'
             '      N=3\n      WRITE(6,10) (A(I),I=1,N)\n'
             '   10 FORMAT(2I4)\n      END\n')
        with self.assertRaisesRegex(FortranError,'FORMAT/array type mismatch'):
            convert(parse(bad,std='f77s'))

    def test_runtime_bound_io_implied_do_read_write(self):
        source=(ROOT/'tests/fortran/f77s_vario.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        c=convert(units)
        self.assertIn('f_iend_1 = F_N;',c)
        self.assertIn('F_I = F_N;',c)
        self.assertIn('f_fmt_int(3);',c)
        self.assertIn('f_add_checked(F_I, f_istep_',c)
        for ctrl in ('I=1,N,0', 'I=1,R', 'I=1,N,R'):
            bad=('      PROGRAM BAD\n      INTEGER A(5),I,N\n'
                 '      REAL R\n      WRITE(6,10) (A(I),'+ctrl+')\n'
                 '   10 FORMAT(2I4)\n      END\n')
            with self.subTest(ctrl=ctrl),self.assertRaises(FortranError):
                convert(parse(bad,std='f77s'))

    def test_io_implied_do_rejects_bad_controls_and_expressions(self):
        for item in ('(A(I),I=1,R)', '(A(I),I=1,3,0)', '(A(I),I=1,3,1+1)', 'A(1+1)', 'A(1)+1'):
            src = ('      PROGRAM BAD\n      INTEGER A(3),I,N\n      REAL R\n'
                   '      WRITE(6,10) ' + item + '\n'
                   '   10 FORMAT(3I4)\n      END\n')
            with self.subTest(item=item), self.assertRaises(FortranError):
                convert(parse(src, std='f77s'))

    def test_runtime_implied_do_with_integer_unit_variables(self):
        src=(ROOT/'tests/fortran/f77s_vuniio.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        lowered=convert(units)
        self.assertIn('if (F_INU != 5) exit(2);',lowered)
        self.assertIn('if (F_OUTU != 6) exit(2);',lowered)
        self.assertIn('f_iend_',lowered)
        self.assertIn('f_fmt_int(3);',lowered)

    def test_narrow_direct_unformatted_integer_scratch(self):
        src=(ROOT/'tests/fortran/f77s_directio.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        lowered=convert(units)
        self.assertIn('f_dopen(7, 4);',lowered)
        self.assertIn('f_dwritei(7, F_REC, F_A);',lowered)
        self.assertIn('F_B = f_dreadi(7, 2);',lowered)
        linked=convert(units,emit_units={'DREC'})
        self.assertIn('static int f_dh[10];',linked)
        self.assertIn('static int f_dl[10];',linked)
        for old,new in (
            ("OPEN(7,ACCESS='DIRECT',RECL=4)","OPEN(7,ACCESS='DIRECT',RECL=12)"),
            ("OPEN(7,ACCESS='DIRECT',RECL=4)","OPEN(7,FILE='X',ACCESS='DIRECT',RECL=4)"),
            ("WRITE(7,REC=REC) A","WRITE(7,REC=0) A"),
            ("WRITE(7,REC=REC) A","WRITE(7,REC=REC) A,B,REC"),
        ):
            with self.subTest(old=old,new=new), self.assertRaises(FortranError):
                convert(parse(src.replace(old,new),std='f77s'))

    def test_sparse_runtime_retains_scratch_file_handles(self):
        for name, handles in (('f77s_direct2',('f_dh[10]','f_dl[10]')),
                              ('f77s_endgoto',('f_sh[10]','f_sused[10]'))):
            with self.subTest(name=name):
                src=(ROOT/'tests/fortran'/(name+'.f')).read_text()
                units=parse(src,std='f77s')
                validate_source(src,units)
                c=convert(units,emit_units={units[0].name})
                for handle in handles:
                    self.assertIn('static int '+handle+';', c)

    def test_sequential_unformatted_rom_real_record(self):
        src=(ROOT/'tests/fortran/f77s_seqreal.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('f_swritef(7, F_A);',c)
        self.assertIn('f_sreadf(7);',c)
        self.assertIn('f_sreadfstat(7, &F_C);',c)
        self.assertIn('tail != 5',c)
        self.assertIn('write(f_sh[unit], &value, 5)',c)
        bad=src.replace('REAL A,B,C','REAL A,B,C\n      LOGICAL L').replace('WRITE(7) A','WRITE(7) L')
        with self.assertRaises(FortranError):
            convert(parse(bad,std='f77s'))

    def test_sequential_vector_records_and_variable_backspace(self):
        source=(ROOT/'tests/fortran/f77s_seqquad.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        c=convert(units)
        self.assertIn('f_swritev(7, 4,',c)
        self.assertIn('f_sreadv(7, 4,',c)
        self.assertIn('tail > 32',c)
        self.assertIn('F_S = -1;',c)
        for bad in ('READ(7) W,X,Y,1','WRITE(7) A,B,C,2.5'):
            src=source.replace('READ(7) W,X,Y,Z' if bad.startswith('READ') else 'WRITE(7) A,B,C,D',bad)
            with self.subTest(bad=bad),self.assertRaises(FortranError):
                convert(parse(src,std='f77s'))

    def test_sequential_triple_end_iostat(self):
        src=(ROOT/'tests/fortran/f77s_seqtri.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('f_swrite3(7, F_A, F_B, F_C);',c)
        self.assertIn('f_sread3stat(7, &F_X, &F_Y, &F_Z);',c)
        self.assertIn('f_sread3stat(7, &F_X, &F_Y, &F_Z);',convert(parse(src.replace('END=100,IOSTAT=S','IOSTAT=S,END=100'),std='f77s')))
        self.assertIn('F_S = -1;',c)
        sparse=convert(units,emit_units={units[0].name})
        self.assertIn('static int f_sused[10];',sparse)
        bad=src.replace('READ(7,IOSTAT=S) X,Y,Z','READ(7,IOSTAT=S) X,Y,S')
        self.assertIn('f_sread3stat', convert(parse(bad,std='f77s')))

    def test_sequential_pair_end_iostat(self):
        src=(ROOT/'tests/fortran/f77s_seqend2.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('f_sread2stat(7, &F_A, &F_B);',c)
        self.assertIn('F_S = -1;',c)
        reverse=src.replace('IOSTAT=S,END=100','END=100,IOSTAT=S')
        self.assertIn('f_sread2stat(7, &F_A, &F_B);',convert(parse(reverse,std='f77s')))

    def test_sequential_unformatted_two_integer_records(self):
        src=(ROOT/'tests/fortran/f77s_seqpair.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('f_swrite2(7, F_A, F_B);',c)
        self.assertIn('f_sread2(7, &F_C, &F_D);',c)
        self.assertIn('pos - tail - 8',c)
        separate=convert(units,emit_units={units[0].name})
        self.assertIn('static int f_sused[10];',separate)

    def test_unformatted_iostat_and_end_control(self):
        src=(ROOT/'tests/fortran/f77s_iostat.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('F_S = -1;',c)
        self.assertIn('f_sreadstat(7, &F_B);',c)
        reversed_controls=src.replace('IOSTAT=S,END=100','END=100,IOSTAT=S')
        self.assertIn('F_S = -1;',convert(parse(reversed_controls,std='f77s')))
        bad=src.replace('IOSTAT=S,END=100','IOSTAT=A,END=999')
        with self.assertRaisesRegex(FortranError,'undefined statement label'):
            convert(parse(bad,std='f77s'))

    def test_unformatted_end_branch_to_executable_label(self):
        src=(ROOT/'tests/fortran/f77s_endgoto.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('f_sreadstat(7, &F_A);',c)
        self.assertIn('if (!f_sok_',c)
        bad=src.replace('END=100', 'END=999')
        with self.assertRaisesRegex(FortranError,'undefined statement label'):
            convert(parse(bad,std='f77s'))

    def test_endfile_unformatted_scratch(self):
        source=(ROOT/'tests/fortran/f77s_endfile.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        c=convert(units)
        self.assertIn('f_send(7);',c)
        self.assertIn('f_srewind(7);',c)
        self.assertIn('F_B = f_sread(7);',c)

    def test_sequential_unformatted_positioning(self):
        source=(ROOT/'tests/fortran/f77s_sequnio.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        c=convert(units)
        for fragment in ('f_swrite(7, F_A);','F_B = f_sread(7);',
                         'f_sback(7);','f_srewind(7);'):
            self.assertIn(fragment,c)
        self.assertIn('if (tail != 4 || upper2 != 0) exit(2);',c)

    def test_direct_unformatted_two_integer_record(self):
        source=(ROOT/'tests/fortran/f77s_direct2.f').read_text()
        units=parse(source,std='f77s')
        validate_source(source,units)
        c=convert(units)
        self.assertIn('f_dopen(7, 8);',c)
        self.assertIn('f_dwrite2(7, 2, F_A, F_B);',c)
        self.assertIn('f_dread2(7, 1, &F_A, &F_B);',c)
        self.assertIn('if (f_dl[unit] != 8) exit(2);',c)

    def test_character_and_assigned_format_read(self):
        for name in ('f77s_fmtchr', 'f77s_afread'):
            source=(ROOT/'tests/fortran'/(name+'.f')).read_text()
            with self.subTest(name=name):
                units=parse(source,std='f77s')
                validate_source(source,units)
                generated=convert(units)
                self.assertIn('f_fmt_int(4);', generated)
                self.assertIn('f_outintw(F_A, 5);', generated)
                self.assertIn('f_outintw(F_B, 5);', generated)
                if name == 'f77s_afread':
                    self.assertIn('if (F_K == 10)',generated)

    def test_integer_variable_console_units(self):
        src = (ROOT/'tests/fortran/f77s_unitvar.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('if (F_INU != 5) exit(2);', c)
        self.assertIn('if (F_OUTU != 6) exit(2);', c)
        for decl in ('REAL INU', 'LOGICAL INU'):
            bad = src.replace('INTEGER INU,OUTU,N', decl+'\n      INTEGER OUTU,N')
            with self.subTest(decl=decl), self.assertRaisesRegex(FortranError,'unit must be INTEGER scalar'):
                convert(parse(bad,std='f77s'))
        for replacement in ('READ(7,10) N', 'READ(OUTU,10) N'):
            bad = src.replace('READ(INU,10) N', replacement)
            if replacement.startswith('READ(7'):
                with self.assertRaisesRegex(FortranError,'console unit 5'):
                    convert(parse(bad,std='f77s'))

    def test_rightmost_nested_format_reversion(self):
        src=(ROOT/'tests/fortran/f77s_nestrevert.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        generated=convert(units)
        self.assertIn('f_fmt_int(3)',generated)
        self.assertIn('f_fmt_int(5)',generated)
        self.assertIn('f_outintw(F_A[(f_index(10, 10))], 4)',generated)

    def test_simple_format_record_reversion(self):
        src=(ROOT/'tests/fortran/f77s_frevert.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('F_A[(f_index(5, 5))] = f_fmt_int(3);', c)
        self.assertIn('f_outintw(F_A[(f_index(5, 5))], 4);', c)
        grouped=src.replace('2I3','2(I3)')
        self.assertIn('f_fmt_int(3);',convert(parse(grouped,std='f77s')))

    def test_scalar_and_array_character_common_cross_unit(self):
        for file, declaration in (('f77s_chcommon.f','static char f_com_TEXT_0[5];'),
                                  ('f77s_chcomarr.f','static char f_com_TXT_0[8];')):
            src=(ROOT/'tests/fortran'/file).read_text()
            with self.subTest(file=file):
                units=parse(src,std='f77s')
                validate_source(src,units)
                merged=convert(units)
                self.assertIn(declaration,merged)
                main=convert(units,emit_units={units[0].name})
                sub=convert(units,emit_units={units[1].name})
                self.assertIn(declaration.replace('static ',''),main)
                self.assertIn(declaration.replace('static ','extern '),sub)
        src=(ROOT/'tests/fortran/f77s_chcommon.f').read_text()
        bad=src.replace('CHARACTER*4 C','CHARACTER*3 C')
        with self.assertRaisesRegex(FortranError, 'COMMON block .*mismatch'):
            convert(parse(bad,std='f77s'))

    def test_sparse_runtime_keeps_math_format_dependencies(self):
        folder = ROOT/'tests/fortran/separate'
        src = (folder/'math_main.f').read_text()+(folder/'math_sub.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src,units)
        sub = convert(units,emit_units={'MSUB'})
        self.assertIn('static float f_sqrt_real(float x)',sub)
        self.assertIn('static void f_outrealw(float value',sub)
        self.assertNotIn('static void f_outintw(',sub)
        main = convert(units,emit_units={'MATSEP'})
        self.assertNotIn('static float f_sqrt_real(',main)

    def test_blank_common_unequal_unit_views_and_sparse_runtime(self):
        src=(ROOT/'tests/fortran/f77s_blankvary.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        merged=convert(units)
        self.assertIn('static int f_com_0_2;',merged)
        sub=convert(units,emit_units={'INC'})
        self.assertIn('extern int f_com_0_2;',sub)
        self.assertIn('void f_INC(void) {',sub)
        self.assertNotIn('static void f_outint(',sub)
        self.assertNotIn('static int f_fmt_get(',sub)
        self.assertLess(len(sub),1500)
        invalid=('      PROGRAM BAD\n      INTEGER N\n'
                 '      COMMON N\n      END\n'
                 '      SUBROUTINE X()\n      REAL R\n'
                 '      COMMON R\n      END\n')
        with self.assertRaisesRegex(FortranError,'COMMON.*mismatch'):
            convert(parse(invalid,std='f77s'))

    def test_cross_unit_common_external_linkage(self):
        folder=ROOT/'tests/fortran/separate'
        src=(folder/'common_main.f').read_text()+(folder/'common_sub.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        main=convert(units,emit_units={'CMAIN'})
        sub=convert(units,emit_units={'ADD2'})
        self.assertIn('int f_com_BLK_0;',main)
        self.assertNotIn('extern int f_com_BLK_0;',main)
        self.assertIn('extern int f_com_BLK_0;',sub)
        self.assertIn('f_com_BLK_0 = ',sub)

    def test_external_and_intrinsic_declarations(self):
        src=(ROOT/'tests/fortran/f77s_exintr.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src,units)
        c=convert(units)
        self.assertIn('f_DOUBLE(', c)
        self.assertIn('f_sin_real(', c)
        self.assertIn('float f_DOUBLE(float *F_X)', c)
        bad=src.replace('REAL X,Y,DOUBLE','INTEGER DOUBLE\n      REAL X,Y')
        with self.assertRaisesRegex(FortranError, 'result type mismatch'):
            convert(parse(bad,std='f77s'))
        for decl in ('INTRINSIC UNKNOWN','EXTERNAL SIN','EXTERNAL AAAAAAA',
                     'INTRINSIC SIN,SIN'):
            bad='      PROGRAM BAD\n      '+decl+'\n      END\n'
            with self.subTest(decl=decl),self.assertRaises(FortranError):
                convert(parse(bad,std='f77s'))

    def test_pause_waits_for_key_and_rejects_expressions(self):
        src=(ROOT/'tests/fortran/f77s_pause.f').read_text()
        units=parse(src, std='f77s')
        validate_source(src, units)
        c=convert(units)
        self.assertIn('f_outstr("PAUSE 99")', c)
        self.assertIn('getchar();', c)
        for code in ('PAUSE X', 'PAUSE 100000', 'PAUSE 1+2'):
            bad='      PROGRAM BAD\n      '+code+'\n      END\n'
            with self.subTest(code=code), self.assertRaises(FortranError):
                convert(parse(bad,std='f77s'))

    def test_f_format_p_scale_input_output(self):
        src = (ROOT/'tests/fortran/f77s_pscale.f').read_text()
        units = parse(src, std='f77s')
        validate_source(src, units)
        c = convert(units)
        self.assertIn('f_outrealw(f_scale_real(F_A, 1), 8, 2)', c)
        self.assertIn('F_A = f_scale_real(f_fmt_real(8, 2), -1);', c)
        bad = ('      PROGRAM BAD\n      REAL A\n'
               '      WRITE(6,10) A\n   10 FORMAT(5P,F8.2)\n      END\n')
        with self.assertRaisesRegex(FortranError, 'P scale factor'):
            convert(parse(bad, std='f77s'))

    def test_integer_subscript_expression_types(self):
        src=(ROOT/'tests/fortran/f77s_idxexpr.f').read_text()
        units=parse(src, std='f77s')
        validate_source(src, units)
        c=convert(units)
        self.assertIn('F_A[(f_index(((F_I) + (1)), 3))]', c)
        for sub in ('R', 'I+R', 'A(I)', 'F(I)'):
            bad=('      PROGRAM BAD\n      INTEGER A(3),I\n'
                 '      REAL R\n      I=1\n      R=1.0\n'
                 '      A('+sub+')=3\n      END\n')
            with self.subTest(subscript=sub), self.assertRaises(FortranError):
                convert(parse(bad, std='f77s'))

    def test_specific_numeric_conversion_intrinsics(self):
        src=(ROOT/'tests/fortran/f77s_numcv.f').read_text()
        units=parse(src, std='f77s')
        validate_source(src, units)
        c=convert(units)
        self.assertIn('f_abs_int(', c)
        self.assertIn('f_nint_real(', c)
        self.assertIn('((float)(F_J))', c)
        for expr in ('SIN(1)', 'COS(2)', 'SQRT(3)', 'EXP(2)',
                     'LOG(.TRUE.)', 'FLOAT(1.0)', 'NINT(2)', 'IABS(-2.0)'):
            source='      PROGRAM BAD\n      REAL X\n      X='+expr+'\n      END\n'
            with self.subTest(expr=expr), self.assertRaisesRegex(FortranError, 'argument'):
                convert(parse(source, std='f77s'))

    def test_real_to_int_truncation_and_machine_guard(self):
        src=(ROOT/'tests/fortran/f77s_int.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src, units)
        c=convert(units)
        self.assertIn('static int f_int_real(float x)', c)
        self.assertIn('return (int)x;', c)
        self.assertIn('x >= 32768.0 || x <= -32769.0', c)
        self.assertIn('F_I = f_int_real(', c)
        self.assertIn('F_J = f_int_real(', c)
        self.assertIn('F_M = f_int_real(', c)

    def test_int_wrong_arity_rejected(self):
        for expression in ('INT()', 'INT(1.0,2.0)'):
            source=('      PROGRAM BAD\n      INTEGER I\n'
                    + '      I=' + expression + '\n      END\n')
            with self.subTest(expression=expression), self.assertRaises(FortranError):
                convert(parse(source, std='f77s'))

    def test_link_only_rejects_incompatible_frontend_modes(self):
        from rfortranc.driver import main as cli
        from contextlib import redirect_stderr
        from io import StringIO
        for flags in (['-S'], ['-c'], ['--bytecode'],
                      ['--separate'], ['--emit-c']):
            with self.subTest(flags=flags), redirect_stderr(StringIO()):
                self.assertEqual(cli(['--std', 'f77s', '--link-only']
                                     + flags + ['missing.sso']), 1)
        with redirect_stderr(StringIO()):
            self.assertEqual(cli(['--link-only', 'missing.sso']), 1)

    def test_original_machar_int_probe_parses_strict(self):
        src=(ROOT/'tests/fortran/f77s_machar.f').read_text()
        units=parse(src,std='f77s')
        validate_source(src, units)
        c=convert(units)
        self.assertIn('F_IBETA = f_int_real(', c)
        self.assertIn('f_outexp(', c)

if __name__=='__main__': unittest.main()
