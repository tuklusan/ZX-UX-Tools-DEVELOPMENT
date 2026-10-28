# Public FORTRAN compiler validation sources (candidate matrix)

These are **source candidates**, not results. All outside sources must be
licensed and fetched separately before test integration. The existing local
suite is only a smoke check; no public corpus has passed the new compiler.

| Priority | Source | Why | Legal/use note | Expected current result |
|---|---|---|---|---|
| P0 | [NIST FORTRAN Compiler Validation System (FCVS)](https://github.com/gklimowicz/FCVS_95) | Historical F77 conformance and defined expected results | NIST public-domain notice with acknowledgement; FCVS_95 is modified for F95 | Predominantly unsupported: FORMAT, I/O, storage |
| P0 | [GCC gfortran torture / dg](https://github.com/lazy-fortran/gfortran-testsuite) | Huge set of positive, negative, optimization tests | GPL-3.0-or-later; do not vendor into restrictive SDK | Select only F77 fixed-form cases; most fail |
| P1 | [Netlib reference BLAS](https://www.netlib.org/blas/) | Arithmetic, arrays, subroutine ABI, memory | Attribution requested; modifications require renamed routines | Unsupported: REAL/DOUBLE, multidimensional arrays, by-reference |
| P1 | [Netlib LAPACK](https://www.netlib.org/lapack/) | Heavier realistic numerical integration and regression | Modified BSD; preserve copyright/license | Unsupported for current subset |
| P1 | [LINPACK in Netlib](https://www.netlib.org/linpack/) | Linear systems, dense math and performance | Verify license for each downloaded source | Unsupported for current subset |
| P2 | [John Burkardt F77 collections](https://people.sc.fsu.edu/~jburkardt/f77_src/) | Breadth of scientific and combinatorial workloads | Check per-program author/license; many pages marked MIT | Select tiny integer programs first |
| Excluded | [SPEC CPU 2017](https://www.spec.org/cpu2017/) | Industry-grade performance | Fee/licence; cannot vendor as public corpus | Not included |
| Conditional | [Netlib ACM CALGO/TOMS](https://www.netlib.org/toms/) | Advanced numerical algorithms | ACM Software Copyright and License Agreement; inspect individually | Not included by default |

## Production certification criteria

- Host parse/semantic tests and compiled Z80 assembly/object/SSX/TZX checks.
- Run exact reference outputs against a known-good desktop F77 compiler.
- Boot every eligible test via `rvm` using the matching signed/verified kernel.
- Physical 48K Spectrum regression across tape, keyboard, screen, and memory.
- Document unsupported language features and fail-fast diagnostics.
- Require 100% on a published, fixed, versioned F77 conformance subset before
  declaring that subset production-ready; full F77 requires broader results.
- Fix random seeds, collect run time, stack and image size, and retain SHA256
  manifest plus compiler/kernel revision for every execution.
