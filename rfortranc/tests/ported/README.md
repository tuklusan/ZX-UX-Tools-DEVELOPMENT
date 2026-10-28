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
| [John Burkardt `prime_serial/prime_serial.f`](https://github.com/johannesgerer/jburkardt-f77/blob/master/prime_serial/prime_serial.f), `PRIME_NUMBER` | `a35f7c57c38c4d79a49c1e421620dd5fdd610ee0` | [`../fortran/f77s_burkprime.f`](../fortran/f77s_burkprime.f) | **GNU LGPL** as marked by original author (John Burkardt, 20 May 2009); modified for F77S: remove free-form/F90 DO/END DO, remove IMPLICIT NONE, use numbered DO and 6-character symbol names, fixed 72-column source, and replace large performance benchmark with N=10 and N=100 reference counts. Original `timestamp` routine is **not** incorporated. |

Keep LGPL notices and attribution with this test port. This is a genuine
adaptation of a publicly released numerical subroutine, not an FCVS
conformance certificate. Expected PRIME_NUMBER counts from original source:
N=10 -> 4 and N=100 -> 25. The differential harness checks the entire
actual RVM output against an independently compiled host gfortran run.
