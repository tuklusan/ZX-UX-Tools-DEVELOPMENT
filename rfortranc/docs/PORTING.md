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

## Remaining gates to production

1. Establish legally correct FORTRAN 77 syntax/semantics, including fixed form,
   labels and branches into and out of DO ranges, statement functions, and
   all implicit typing rules. Add negative compile tests for each rejection.
2. Add full F77 storage model: COMMON, EQUIVALENCE, SAVE, DATA, and arrays
   including multiple dimensions and adjusted/assumed sizes.
3. Validate the implemented by-reference scalar dummy arguments against
   F77 aliasing/typing rules; add array dummy arguments, procedure arguments,
   and external linking across separately compiled FORTRAN units.
4. Implement CHARACTER, COMPLEX, REAL and DOUBLE PRECISION I/O, FORMAT,
   OPEN/CLOSE/REWIND and record-oriented I/O using ZX-UX.
5. Validate 16-bit overflow, divide-by-zero, rounding, integer division,
   floating point special values, and stack/heap exhaustion.
6. Run NIST FCVS, GNU torture tests, Netlib BLAS/LINPACK and numeric suites
   against gfortran on a desktop, with expected result hashes, then in `rvm`,
   then on Spectrum hardware. Record unsupported tests as failures, not skips
   hidden inside a pass percentage.
7. Package from the SDK source tree and verify matching `.ssx/.tzx` and
   manifest hashes in an independent clean build; check legal notices.

## Source attribution and licences

`rfortranc` models the subset implemented by
`tuklusan/fortran77-compiler` rather than incorporating its Python/Ply
source verbatim. The original project contains no LICENSE file at time of
review, so do not redistribute a copy without permission. The ZX-UX SDK
archive includes its own restrictive non-commercial licence and third-party
notices; **do not strip or replace either**. This folder does not vendor the
ZX-UX kernel, runtime archive, ROM, or original EWVM compiler.
