# F77S source-of-truth and regression scope

**Mandatory target:** ANSI X3.9-1978 **subset FORTRAN** (F77S), not the full F77 language. Primary authority is the *subset-facing* text of the ANSI document and Appendix D, rather than the full-language pages.

## Stable reference pointers

1. ANSI X3.9-1978 as reproduced by NIST/FIPS: https://nvlpubs.nist.gov/nistpubs/Legacy/FIPS/fipspub69-1.pdf
2. Searchable standard with Appendix D, **D1–D4**: https://www.sternwarte.uni-erlangen.de/~ai05/vorlesungen/astrocomp/f77-standard.pdf
3. Section and Appendix D HTML index: https://www.ndp77.net/x3J9/rjcnf0001.html
4. User-provided `F77-SUBSET-SPEC.txt` is a **pointer/summary**, not a complete normative specification; use the ANSI text to settle every actual decision.

**Important correction:** the attached summary says DOUBLE PRECISION is permitted; Appendix D3.7 of the official standard explicitly excludes the `DOUBLE PRECISION` statement (as well as `COMPLEX`). The accepted subset data types are INTEGER, REAL, LOGICAL and restricted CHARACTER. Trust the actual standard where the summary differs.

## Non-negotiable rules confirmed by Appendix D

- D3.3: fixed-form, at most nine continuation lines; observe exact statement/comment layout.
- D3.4/D3.7: exclude DOUBLE PRECISION and COMPLEX; D3.7 also removes PRINT, CLOSE, INQUIRE, ENTRY, BLOCK DATA, PARAMETER statements.
- D3.5: arrays limited to three dimensions and default lower bounds of 1. Dummy bounds and subscript expressions are constrained.
- D3.6: no .EQV. or .NEQV.; constant expressions only where a general expression is accepted.
- D3.8: COMMON, EQUIVALENCE, DIMENSION, IMPLICIT, EXTERNAL, INTRINSIC remain required subset features. SAVE has reduced form, allowing only named common blocks.
- D3.9: DATA is allowed, with no implied-DO DATA lists and no implicit DATA type conversions.
- D3.11: DO variable integer; DO parameters must be integer constants or variables; computed GO TO selector is an integer variable.
- D3.12: **no PRINT or list-directed READ/WRITE**. Formatted READ/WRITE remain required, with restricted I/O lists. OPEN exists but is limited; do not drop all file I/O as “full F77.”
- D3.13: reduced FORMAT descriptors and nesting limits.
- D3.15: no ENTRY/alternate returns/generic intrinsic references.
- D3.19: CHARACTER subset is mandatory but excludes substrings, concatenation and character functions.

## Implementation vs language

`rfortranc --std f77s` currently implements only a **portion** of the required language; it must fail explicitly on unsupported constructs. The default `--std zxux` mode contains helpful **non-F77S extensions** (e.g., PRINT and list-directed I/O). An `--std zxux` test pass is never reported as an F77S conformance pass.

The source-of-truth feature checklist lives in `docs/F77S-MATRIX.md`. Follow it in this order after end-to-end regressions: formatted READ / FORMAT, required storage (COMMON/EQUIVALENCE/SAVE), dummy arrays, restricted CHARACTER, remaining numeric/implicit and I/O semantics. **Do not chase full-F77-only features.** Test with small fixed-format subset-conforming programs and independently compare executed ZX-UX output against gfortran, then add vetted historical FCVS subset programs. Keep an attempted/compiled/executed/correct/unsupported count and hashes in committed reports.

Keep all runnable proof and PROGRESS.MD in this repository, never only in a chat or /mnt/data.
