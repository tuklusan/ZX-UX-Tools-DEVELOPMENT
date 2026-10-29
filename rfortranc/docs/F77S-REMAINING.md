# Still-missing ANSI F77S compiler requirements

Source inspection date 2026-10-28; compiler source revision `e03c72542a5048469110c100f502856b708f5f87` (audit-only commits after that). This is **Subset FORTRAN**, not full F77, using Appendix D of ANSI X3.9-1978. Status is *missing*, *partial*, or *unproven*; neither syntax acceptance nor previous 95-case runtime smoke tests prove complete conformance.

| Priority | Status | Required remaining work |
|---|---|---|
| P0 | Missing | Specific numerical intrinsics: SIN, COS, EXP, LOG and other permitted §15.10 functions; add argument/result typing, domain/accuracy tests. Only restricted INT, ABS, SQRT, MOD exist. |
| P0 | Partial | Numeric expression/type semantics: mixed INTEGER/REAL, typed power, negative or noninteger powers where standard permits, conversions, precedence, overflow and numeric edge cases. |
| P0 | Partial | General formatted sequential READ/WRITE, internal CHARACTER file I/O, unformatted sequential/direct I/O, legal unit identifiers (including integer variables and non-5/6 units), EOF and permitted control specifiers. |
| P0 | Partial | FORMAT: required Ew.dEe, Ew.d input, unrestricted permitted F/E cases, P scale, BN/BZ, reversion/record handling, and assigned-integer/CHARACTER-constant format identifiers. **Gw.dEe excluded, Ew.dEe required.** |
| P0 | Missing | I/O implied-DO with integer-control restrictions; whole-array I/O lists and permitted repetition/reversion. Do not accept general expressions as strict F77S I/O items. |
| P0 | Missing | Statement functions, including local dummy-name scope; original NEWTON sample blocked. |
| P1 | Missing | EXTERNAL/INTRINSIC declarations, procedure dummy/actual arguments, unprefixed FUNCTION, and complete specific external-function result typing and calls. |
| P1 | Partial | COMMON storage association with mixed permitted numeric types, alternate matching storage views, different-sized blank COMMON and CHARACTER COMMON. |
| P1 | Partial | EQUIVALENCE with permitted numeric-type storage association, named COMMON overlap and same-width CHARACTER total association. No forbidden partial CHARACTER association. |
| P1 | Partial | DATA initializer storage association and lifetime; local DATA must be allowed in units also declaring COMMON. DATA of named COMMON requires full-language BLOCK DATA, which F77S **excludes**. |
| P1 | Partial | Rank-1..3 dummy arrays with variable *leading* bounds, bounds from COMMON, full legal element/whole-array association and integer-only subscript expression checks. |
| P1 | Partial | CHARACTER constant actual arguments, full total association across dummy/COMMON/EQUIVALENCE, adjustable CHARACTER dummy extents, internal/unformatted I/O. Fixed arrays and fixed-width dummy arrays **already work** in tested cases. |
| P1 | Missing | ASSIGN and assigned GO TO; PAUSE plus all control/label edge cases. Numbered DO, arithmetic IF, computed GO TO already exist for tested cases. |
| P1 | Missing | Limited legal OPEN for direct-access unformatted records; REWIND, BACKSPACE and ENDFILE. Named-file OPEN, CLOSE, INQUIRE and formatted direct access are **not F77S requirements**. |
| P1 | Partial | Exact cols 1-72 fixed source, nine continuations, comments/continuations, identifiers everywhere, statements in correct order, and rejecting all full-only forms consistently. |
| P2 | Partial | Separate compilation and linking of F77S program units, cross-unit external ABI/type checking and procedure calling conventions. |
| Proof | Unproven | Published strict F77S FCVS/subset corpus and substantial ported numerical library; actual Spectrum 48K + cassette boot; peak RAM including stack/kernel and target numerical accuracy/runtime. |

**Out of scope:** full-F77-only DOUBLE/COMPLEX, PRINT, list-directed READ/WRITE, PARAMETER, BLOCK DATA, ENTRY/alternate returns, generic intrinsic references, CLOSE/INQUIRE, .EQV./.NEQV., character substrings/concatenation/functions, partial CHARACTER association, D/G/T/TL/TR/S/SP/SS edit families, Iw.m, and the FORMAT colon. See the standard for exact exclusions.

**Sources checked:** `rfortranc/rfortranc/translator.py`, `f77s.py`, `data_init.py`, `common.py`, `equivalence.py`, `implicit.py`, `rfortranc/docs/F77S-MATRIX.md`, `rfortranc/README.md`, ANSI Appendix D and §§9.2/13.5.9.2.2. The longer source-level audit is `F77S-GAP-AUDIT-2026-10-28.md` with corrections in `F77S-GAP-AUDIT-CORRECTIONS.md`.

**Next code milestone:** REAL SIN and original WHETSTONE native ZX-UX vs gfortran validation, followed by COS/EXP. This source audit did not execute new regression tests. All other developers' files remain untouched.
