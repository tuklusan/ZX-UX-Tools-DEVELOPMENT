# Porting notes — FORTRAN / C48 / ZX-UX

## Reference compilers

- Upstream language reference: https://github.com/tuklusan/fortran77-compiler
  (Python/Ply frontend, symbol table, semantic pass, constant-folding and EWVM
  stack-machine codegen). It currently emits EWVM `PUSHI`, `STOREG`, `JUMP`,
  `WRITE`, `STOP` etc.; **that VM is not the ZX Spectrum**. Its lexer treats
  the FIXED label column inconsistently and its grammar omits several F77 forms.
- Target SDK is supplied in `minizxuxport.zip`. Its source layout is
  `src/zx-ux-sdk/{rcc/,ras.py,rld.py,rtap.py,bin/,lib/,tools/}`.
- `rcc/driver.py` generates native Z80 or compact bytecode and performs size
  fitting; it calls `ras.assemble_text`, then `rld.link` with `lib/libc48.ssa`
  and `start`. `lib/crt0.asm` defines `start`, initializes screen and calls
  `@main`; `rld` builds SSX1. `rtap` wraps SSX1 in Spectrum TZX header + data
  cassette records. `rvm` boots the *actual* OS image to exercise binaries.

## Implementation choice

Original Python/Ply+EWVM code is not simply renamed. This port implements a
small, dependency-free frontend tracking the upstream grammar and performs
FORTRAN->C48 transformation instead of EMITTING EWVM. The C48 compiler
performs all native Z80 instruction selection, object relocation and libc
linking. No second 16-bit backend to maintain. Explicit PC-dispatch control
flow handles F77 numeric GOTO and labeled DO without depending on C48's
unsupported C `goto`/labels. The extra code can increase executable size;
`rcc`'s automatic fitting helps but cannot make arbitrary F77 programs fit 48K.

## Subprogram ABI milestone

Scalar FUNCTION and SUBROUTINE dummy arguments now use typed C48 pointers.
Actual variables and array elements pass their addresses. Literal or computed
actual arguments use private caller-side temporary locations; a modification
of such a temporary is not reflected in the original expression. Tests cover
integer and REAL dummy mutation in actual compiled Z80/ZX-UX execution.
Multidimensional and array dummy arguments, full aliasing conformance, and
separately compiled linkage remain unsupported.

## Remaining gates to production-grade **ANSI FORTRAN SUBSET (F77S)**

Target is Appendix D of X3.9-1978, not full F77. See `F77S-MATRIX.md`.

1. Complete F77S fixed-form lexical/label rules and all permitted scalar, INTEGER/REAL/LOGICAL and constant-length CHARACTER expressions; test negative rejections.
2. Finish required F77S storage: named and blank COMMON with complete sequence association, EQUIVALENCE beyond safe same-type local groups, SAVE restricted to common block names, DATA and adjustable dummy arrays.
3. Implement all F77S allowed formatted READ/WRITE and FORMAT descriptors, numeric and CHARACTER record semantics, limited direct-access unformatted OPEN and permitted intrinsics. Do not chase disallowed full-F77 features (COMPLEX, DOUBLE PRECISION, PRINT, etc.).
4. Validate every implemented type, by-reference call and legal storage alias against an independent compiler and test actual ZX-UX executable output, memory and error conditions.
5. Build a legally reviewed, versioned substantial **F77S-relevant** external test corpus. Record complete attempted, compiled, executed, correct and unsupported counts; adapted FCVS themes are not full FCVS passes.
6. Test SSX/TZX cassette loading, kernel integration and boundary behavior on real Spectrum 48K hardware and emulator; preserve executable hashes and machine output.
7. Verify release hashes and licensing notices on clean builds; record every milestone in repository-root `PROGRESS.MD`.

## Source attribution and licences

`rfortranc` models the subset implemented by
`tuklusan/fortran77-compiler` rather than incorporating its Python/Ply
source verbatim. The original project contains no LICENSE file at time of
review, so do not redistribute a copy without permission. The ZX-UX SDK
archive includes its own restrictive non-commercial licence and third-party
notices; **do not strip or replace either**. This folder does not vendor the
ZX-UX kernel, runtime archive, ROM, or original EWVM compiler.