# Public FCVS subset test-theme ports

These are **new reduced ZX-UX/F77S programs**, derived from the test themes
in historical NIST FORTRAN Compiler Validation System (FCVS). They are **not**
verbatim copies, not an exhaustive port, and do **not** confer NIST certification.
A full feature-complete FM00x routine also tests formatted reports and other
constructs not yet implemented by this compiler. Passing these distilled tests
is only evidence for the exact language behavior exercised here.

| Source | Pinned original Git blob SHA | Local adaptation | Behavior exercised |
|---|---|---|---|
| [FM003.f](https://github.com/gklimowicz/FCVS_95/blob/main/FM003.f) | `d927d1d905616fdcdb9b84d04fe3d3b2990fd068` | `../fortran/f77s_fc3.f` | CONTINUE labels, GO TO, computed GO TO, arithmetic IF, labelled DO |
| [FM004.f](https://github.com/gklimowicz/FCVS_95/blob/main/FM004.f) | `e22d0c5e318d6705579a5c016baeac327cd41abc` | `../fortran/f77s_fc4.f` | Arithmetic IF negative, zero, positive branches |
| [FM005.f](https://github.com/gklimowicz/FCVS_95/blob/main/FM005.f) | `3a3a18478130c60da2b148233a3eb6bcf04e1adc` | `../fortran/f77s_fc5.f` | Formatted INTEGER Iw widths and asterisks on overflow |

Upstream FCVS texts identify the US government/NBS test development work.
Keep source attribution and any upstream notices. These files consist of
independently rewritten reduced cases; no proprietary test data is included.

Validation: compile each .f using `--std f77s`, execute the ZX-UX SSX1 on the
matching emulator, independently compile with gfortran -std=legacy
-ffixed-form, and compare exact relevant output lines. The differential
harness under `../compare_f77s.py` records both executions and SHA-256s.

Future work: actual full FCVS subset routine coverage, not just these theme
samples, must be catalogued with attempted/unsupported/compiled/executed/
correct counts. Do not infer certification from this directory.

## External FORTRAN numerical algorithm ports

| Original | Pinned upstream blob | F77S ZX-UX adaptation | Licence and changes |
|---|---|---|---|
| [John Burkardt `i4lib/i4lib.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/i4lib/i4lib.f), `I4VEC_SORT_INSERT_A` + `I4VEC_SEARCH_BINARY_A` | `e0a7be6024463bc0d34ec036080d875ed66f4c31` | [`../fortran/f77s_burksort.f`](../fortran/f77s_burksort.f) | **GNU LGPL** (John Burkardt; insertion sort modified 25 Jul 2010, binary search 31 Aug 2008). Port rewrites implicit-none/F90-style DO to labelled loops, fixes dummy length 9, short names. Positive and negative searches verified; no original benchmark claimed. |
| [John Burkardt `i4lib/i4lib.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/i4lib/i4lib.f), `I4VEC_REVERSE` and `I4VEC_SUM` | `e0a7be6024463bc0d34ec036080d875ed66f4c31` | [`../fortran/f77s_burkvec.f`](../fortran/f77s_burkvec.f) | **GNU LGPL** as marked in original source (John Burkardt; reverse 25 Jun 2009, sum 3 Jan 2007). New F77S port: 6-character names, numbered INTEGER DO and fixed array dimension 5; `I4VEC_SUM` changed to by-reference SUBROUTINE because FUNCTION array dummy calls are not yet supported. Outputs 15,13,11 and sum 65. Preserve LGPL attribution; not a verbatim upstream file. |
| [John Burkardt `prime_serial/prime_serial.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/prime_serial/prime_serial.f), `PRIME_NUMBER` | `a35f7c57c38c4d79a49c1e421620dd5fdd610ee0` | [`../fortran/f77s_burkprime.f`](../fortran/f77s_burkprime.f) | **GNU LGPL** as marked by original author (John Burkardt, 20 May 2009); modified for F77S: remove free-form/F90 DO/END DO, remove IMPLICIT NONE, use numbered DO and 6-character symbol names, fixed 72-column source, and replace large performance benchmark with N=10 and N=100 reference counts. Original `timestamp` routine is **not** incorporated. |

Keep LGPL notices and attribution with this test port. This is a genuine
adaptation of a publicly released numerical subroutine, not an FCVS
conformance certificate. Expected PRIME_NUMBER counts from original source:
N=10 -> 4 and N=100 -> 25. The differential harness checks the entire
actual RVM output against an independently compiled host gfortran run.

| [John Burkardt `i4lib/i4lib.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/i4lib/i4lib.f), `I4VEC_REVERSE` and `I4VEC_SUM` | `e0a7be6024463bc0d34ec036080d875ed66f4c31` | [`../fortran/f77s_burkadj.f`](../fortran/f77s_burkadj.f) | **GNU LGPL**. Generalized the previous fixed-extent port to F77S adjustable `A(N)` dummy arrays; renames to 6-letter `REVRSE` and `SUMVEC`, converts `DO` into labelled INTEGER-bound loops and `I4VEC_SUM` to result-by-reference. Host gfortran and real ZX-UX output checked for N=5 and N=7. |

| [John Burkardt `i4lib/i4lib.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/i4lib/i4lib.f), `I4MAT_MM` | `e0a7be6024463bc0d34ec036080d875ed66f4c31` | [`../fortran/f77s_burkmm.f`](../fortran/f77s_burkmm.f) | **GNU LGPL**. Simplified integer matrix multiplication adapted to ANSI F77S, with a fixed two-row leading extent and variable N columns, 6-character names and labelled INTEGER DO loops. Computes A(2,2) x B(2,N) -> C(2,N) with dynamic caller bound N=3 and N=1, verifies outputs 7,22,23 and 7. Provenance and original licensing preserved; independently compiled with gfortran and native ZX-UX. |

| [John Burkardt `i4lib/i4lib.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/i4lib/i4lib.f), `I4MAT_FLIP_ROWS` and `I4MAT_FLIP_COLS` | `e0a7be6024463bc0d34ec036080d875ed66f4c31` | [`../fortran/f77s_burkflip.f`](../fortran/f77s_burkflip.f) | **GNU LGPL**. Recast matrix row/column reversal operations with F77S fixed source, six-character subroutine names, numbered loops, 2xN INTEGER dummy array bounds; apply both operations and then reverse them. Both gfortran and ZX-UX RVM show 6,5,2,1 and restored 1,6. |

| [John Burkardt `i4lib/i4lib.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/i4lib/i4lib.f), `I4VEC_CUM`, `I4VEC_MIN` and `I4VEC_MAX` | `e0a7be6024463bc0d34ec036080d875ed66f4c31` | [`../fortran/f77s_burkcum.f`](../fortran/f77s_burkcum.f) | **GNU LGPL**, original author John Burkardt. Adapted accumulation, minimum and maximum over variable-length INTEGER A(N), 6-character names, separate SUBROUTINE output arguments, numbered DO and F77S fixed form. Exercises N=5 followed by N=3. Source originally declares I4VEC_CUM modified 25 Jun 2011, I4VEC_MIN and I4VEC_MAX 19 Jan 2007. |

