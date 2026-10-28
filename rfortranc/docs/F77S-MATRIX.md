# ANSI FORTRAN SUBSET (F77S) — implementation and test contract

**Target:** subset level of ANSI X3.9-1978 / X3J3/90.4, **not full FORTRAN 77**.
Primary normative cross-checks: §§1.4.1, 1.6, Appendix D (§§D1–D4):
- https://www.sternwarte.uni-erlangen.de/~ai05/vorlesungen/astrocomp/f77-standard.pdf (Appendix D pages D-1 to D-6)
- https://nvlpubs.nist.gov/nistpubs/Legacy/FIPS/fipspub69-1.pdf (NBS/FIPS subset-language edition)
- https://www.ndp77.net/x3J9/rjcnf0001.html (HTML standard section index)

**Conformance boundary:** `rfortranc --std f77s` is **only a partial syntax restriction gate**.
It does **not** implement or certify the required full subset. Default `--std zxux`
retains intentional ZX-UX conveniences and legacy test sources (including `PRINT *`).
An accepted source is not thereby F77S conforming. Remaining required features
are tracked below rather than discarded as full-F77-only work.

| Subset rule (Appendix D) | Current state | Required work |
|---|---|---|
| Fixed source cols 1–72; up to **9** continuations; no comment before continuation (D3.3) | Fixed lexer partial; strict gate rejects selected violations | Exact lexical rules, no layout ambiguity; conformance cases |
| Symbolic names 1–6 letters/digits (standard §2.2) | Strict gate validates declared names | Check every identifier, all contexts |
| INTEGER, REAL, LOGICAL and constant-length CHARACTER; no DOUBLE/COMPLEX (D3.4, D3.19) | INTEGER/LOGICAL, partial REAL; CHARACTER not implemented | Numeric semantics; constant-length CHARACTER |
| Up to **3** dimensions; no explicit lower bounds; integer constants/variable dimension bounds; restricted subscripts (D3.5) | Fixed-extent 1D/2D/3D numeric arrays; separate DIMENSION declaration, column-major and runtime bounds checks | Adjustable dummy arrays, variable dimension extents and complete subscript typing |
| Mixed arithmetic; no .EQV./.NEQV. (D3.6) | Partial operators and floating support | Full permitted conversions and intrinsics |
| No PRINT, CLOSE, INQUIRE, ENTRY, BLOCK DATA, PARAMETER, DOUBLE PRECISION, COMPLEX (D3.7) | Strict gate rejects a subset of forms | Enforce all excluded variants robustly |
| COMMON, EQUIVALENCE, DIMENSION, IMPLICIT, EXTERNAL, INTRINSIC are **subset features** (D3.8, unchanged otherwise) | IMPLICIT defaults, letter ranges, fixed DIMENSION and typed **named scalar COMMON** shared across program units; EQUIVALENCE, SAVE, general COMMON and external declarations not implemented | Implicit CHARACTER, storage layout and external declarations |
| SAVE only names of common blocks in slash delimiters (D3.8) | Not implemented | Implement specified form |
| DATA permitted without implied DO and without type conversion (D3.9) | Partial: typed INTEGER/REAL/LOGICAL scalar and fixed-size 1D/2D/3D arrays in main program; repeated values, strict type checks and initialization order. Subprogram DATA rejected | Saved subprogram storage, remaining types, numeric overflow cases |
| Arithmetic IF, logical/block IF, computed GOTO. Computed selector must be integer variable (D3.11) | Arithmetic/computed GOTO implemented; selector gated | More flow edge cases and reference output checks |
| DO variable INTEGER; all DO control values integer constants or variables (D3.11) | Numbered DO implemented; strict gate checks operand forms | More invalid control tests and overflow cases |
| Formatted READ/WRITE; **no list-directed READ/WRITE or PRINT** (D3.12) | `WRITE(6,label)` limited Iw, X, literals, slash | Formatted READ; general permitted FORMAT and I/O |
| Formatted I/O list items variables, array names/elements; **not constants/expressions** (D3.12) | Strict gate checks limited READ/WRITE variable lists; Iw/X and slash for numeric input | Check all supported I/O forms |
| Limited OPEN only for direct-access *unformatted* units; no named files (D3.12) | Not implemented | ZX-UX device mapping and record semantics |
| No FORMAT `Iw.m`, `Dw.d`, `Gw.d`, `Gw.dEe`, `Tc`, `TLc`, `TRc`, `S`, `SP`, `SS`, colon; <=3 parenthesis levels (D3.13) | Supports Iw/X/slash/literal descriptors, positive repeat counts and up to three nested levels; rejects unsupported | Add other required descriptors and full record semantics |
| No ENTRY/alternate returns/generic intrinsic refs; no complex/double intrinsics (D3.15) | By-reference scalar calls; limited functions | Required permitted argument types and intrinsic functions |
| CHARACTER subset includes constant-length variables/arrays, assignment/comparison and I/O; excludes substrings, concatenation, character functions (D3.19) | Not implemented | Implement subset CHARACTER, not forbidden extras |

## Test expectations

1. `python -m unittest discover -s rfortranc/tests -p 'test_f77s.py'` — standards-specific **partial-gate tests**; must pass.
2. `python rfortranc/bin/rfortranc --std f77s --emit-c rfortranc/tests/fortran/f77s_fmt.f` — format-Iw smoke test.
3. `python rfortranc/tests/run_tests.py --sdk <sdk> --rvm <matching rvm> --report <JSON>` — compiler/runtime smoke tests; most current fixtures are **ZX-UX extension mode**.
4. NIST FCVS `FMxxx` tests described specifically as subset tests form the candidate **external conformance corpus**. Track attempted, unsupported, compiled, executed, correct, incorrect; no silent filtering. Normalize only platform I/O through clearly documented port patches. Preserve source attribution and checksums. Desktop gfortran comparison remains separate from actual ZX-UX execution.
5. All actual Spectrum 48K, kernel and cassette tests must preserve hardware/emulator version, output and image SHA-256 in a committed run manifest.
